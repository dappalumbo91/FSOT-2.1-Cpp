#!/usr/bin/env python3
"""Round-an scores under audit/FREEZE_2026-10-02an (committed first). z-only, dimensionless ratios; FSOT-only inputs.
AN-1 level-B shell-average job status; AN-2 f_rho from two vector-correlator FESRs (FSOT alpha_s, finite rho width) -> Delta alpha_had, G_F, Gamma_Z/M_Z.
  python tools/score_2026_10_02an.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02an.tsv
"""
import argparse, json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, sqrt, pi, ln, fabs, nstr
from mpmath import zeta
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves(); P = X.pins(); ref = X.refs(); R_ = Path(__file__).resolve().parents[1]
rows = []
def emitz(sec, name, inputs, v, c, s, th=0, cls="", note=""):
    v, c, s, th = mpf(v), mpf(c), mpf(s), mpf(th); sig = sqrt(s**2 + th**2); z = fabs(v - c) / sig
    rows.append([sec, name, inputs, nstr(v, 12), nstr(c, 10), nstr(sig, 4), nstr(z, 5), "agrees" if z <= 1 else "miss", nstr((v - c) / c * 100, 5) + " %", cls, note]); return z
def info(sec, name, inputs, v, cls="", note=""): rows.append([sec, name, inputs, nstr(mpf(v), 12), "-", "-", "-", "info", "-", cls, note])
def rec(sec, name, verdict, note): rows.append([sec, name, "-", "-", "-", "-", "-", verdict, "-", "-", note])
J = lambda f: json.loads((R_ / f).read_text(encoding="utf-8"))
mpM = X.kg_to_GeV(L["m_p_kg"]) * 1000
def col(path, sec, key):
    for line in open(R_ / path, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) > 3 and f[0] == sec and f[1].startswith(key): return mpf(f[3])
# ---------------- AN-1 (sample set fixed at commit time so this score stays byte-identical when later samples are committed)
s = "AN-1"; AT_COMMIT = [0, 1, 2]; ROT_AT_COMMIT = False
for j in AT_COMMIT:
    e_ = J("audit/shellavg_2026-10-02am_B_j%d.json" % j)
    info(s, "AN-1 level B sample j=%d (kmax 14, D %s)" % (j, nstr(mpf(e_["D"]), 8)), "round-ag kmax-12 profile, K 14", e_["E_sol"], "diagnostic",
         "E_sol; g_A^(0) %s; I %s; xat_sea %s; %s s active" % (nstr(mpf(e_["gA0"]), 8), nstr(mpf(e_["I"]), 8), nstr(mpf(e_["xat_sea"]), 7), e_["seconds"]))
rec(s, "AN-1 level-B job", "running at commit time (carries to the next round)", "samples committed %d/4, rotational sums %s; the frozen round-al rules are applied in the round the job finishes" % (len(AT_COMMIT), "done" if ROT_AT_COMMIT else "pending"))
# ---------------- AN-2
s = "AN-2"; src = (R_ / "tools/score_2026_10_02i.py").read_text(encoding="utf-8").split("\n")
i0 = next(i for i, l in enumerate(src) if l.startswith("# ---- HAD-2: quark-hadron duality")); i1 = next(i for i, l in enumerate(src) if l.startswith("def dalpha_had"))
ns = {"math": math}; exec("\n".join(src[i0:i1]), ns); AlphaS, GX, GW = ns["AlphaS"], ns["GX"], ns["GW"]
def pole(m, AS): return m * (1 + 4 * AS(m) / (3 * math.pi))
def cont(alpha, MZ, asMZ, mtau, s0, mK, mD, mB):  # round-i/y duality integral, u and d thresholds at s0
    AS = AlphaS(asMZ, MZ, mB, mD, mtau)
    flav = [(s0, 4 / 9), (s0, 1 / 9), (4 * mK**2, 1 / 9), (4 * mD**2, 4 / 9), (4 * mB**2, 1 / 9)]; MZ2 = MZ**2
    def R(s):
        open_ = [q for th, q in flav if s > th]; nf = len(open_); aa = AS(math.sqrt(s)) / math.pi
        K = 1 + aa + (1.9857 - 0.1152 * nf) * aa**2 + (-6.63694 - 1.20013 * nf - 0.00518 * nf**2) * aa**3
        return 3 * sum(open_) * K
    RZ = R(MZ2); smin = min(th for th, _ in flav)
    def g(t):
        s = math.exp(t); return (R(s) - RZ) * MZ2 / (MZ2 - s) if abs(MZ2 - s) > 1e-9 * MZ2 else 0.0
    edges = sorted({math.log(th) for th, _ in flav} | {math.log(MZ2)}); pts = []
    for lo, hi in zip(edges, edges[1:]):
        n = max(1, int(math.ceil((hi - lo) / 0.5))); pts += [lo + (hi - lo) * k / n for k in range(n + 1)][:-1]
    pts.append(edges[-1]); top = math.log(MZ2) + 40.0; n = 80; pts += [edges[-1] + (top - edges[-1]) * k / n for k in range(1, n + 1)]
    tot = 0.0
    for lo, hi in zip(pts, pts[1:]):
        c, w = 0.5 * (hi + lo), 0.5 * (hi - lo); tot += w * sum(wi * g(c + w * xi) for xi, wi in zip(GX, GW))
    tot += RZ * math.log((MZ2 - smin) / smin)
    return alpha / (3 * math.pi) * tot
def gl(f, a, b, n=40):
    h = (b - a) / n; tot = 0.0
    for k in range(n):
        c, w = a + (k + 0.5) * h, 0.5 * h; tot += w * sum(wi * f(c + w * xi) for xi, wi in zip(GX, GW))
    return tot
def an2(alpha, MZ, asMZ, mtau, MV, Fpi, mpi, mK, mc, mb, width=True, qcd=True):
    AS0 = AlphaS(asMZ, MZ, mb, mc, mtau); mcp, mbp = pole(mc, AS0), pole(mb, AS0); AS = AlphaS(asMZ, MZ, mbp, mcp, mtau)
    thr = 4 * mpi**2; g = MV / (math.sqrt(2) * Fpi); M2 = MV**2
    def K(s):
        if not qcd: return 1.0
        aa = AS(math.sqrt(s)) / math.pi; nf = 3
        return 1 + aa + (1.9857 - 0.1152 * nf) * aa**2 + (-6.63694 - 1.20013 * nf - 0.00518 * nf**2) * aa**3
    def Gam(s): return g**2 * max(s / 4 - mpi**2, 0.0) ** 1.5 / (6 * math.pi * s)
    def bw(s): G = Gam(s); return math.sqrt(s) * G / ((s - M2)**2 + s * G**2)
    def mom(s0, n, f, lo): return gl(lambda s: s**n * f(s), lo, s0)
    if width:
        def ratio(s0): return mom(s0, 1, bw, thr) / mom(s0, 0, bw, thr) - mom(s0, 1, K, 0.0) / mom(s0, 0, K, 0.0)
        lo_, hi_ = 1.02 * M2, 8.0 * M2
        for _ in range(60):
            mid_ = 0.5 * (lo_ + hi_)
            if ratio(lo_) * ratio(mid_) <= 0: hi_ = mid_
            else: lo_ = mid_
        s0 = 0.5 * (lo_ + hi_); N0 = mom(s0, 0, bw, thr)
    else:
        def ratio(s0): return M2 - mom(s0, 1, K, 0.0) / mom(s0, 0, K, 0.0)
        lo_, hi_ = 1.02 * M2, 8.0 * M2
        for _ in range(60):
            mid_ = 0.5 * (lo_ + hi_)
            if ratio(lo_) * ratio(mid_) <= 0: hi_ = mid_
            else: lo_ = mid_
        s0 = 0.5 * (lo_ + hi_)
    fQ2 = 1.5 * mom(s0, 0, K, 0.0) / (12 * math.pi**2)
    if width: drho = alpha / (3 * math.pi) * MZ**2 * gl(lambda s: 12 * math.pi**2 * fQ2 * bw(s) / N0 / (s * (MZ**2 - s)), thr, s0)
    else: drho = 4 * math.pi * alpha * fQ2 / M2 * MZ**2 / (MZ**2 - M2)
    dom = 4 * math.pi * alpha * (fQ2 / 9) / M2 * MZ**2 / (MZ**2 - M2)
    c_ = cont(alpha, MZ, asMZ, mtau, s0, mK, mcp, mbp)
    return {"d": float("%.10g" % (drho + dom + c_)), "rho": drho, "omega": dom, "cont": c_, "s0": s0, "fQ2": fQ2, "Gee": 4 * math.pi * alpha**2 * fQ2 / (3 * MV), "Grho": Gam(M2), "s0_over_M2": s0 / M2}
PD = (1 / 137.035999177, 91.1880, 0.1180, 1.77693, 0.77526, 0.09207, 0.13957039, 0.493677, 1.2730, 4.183)
for tag, w_, q_ in (("LO narrow (round-am limit)", False, False), ("+ alpha_s (narrow)", False, True), ("+ alpha_s + finite width [AN-2]", True, True)):
    r_ = an2(*PD, width=w_, qcd=q_)
    info("TRACE", "AN-2 trace, PDG inputs: " + tag, "PDG M_rho, F_pi, m_pi; round-y PDG inputs", r_["Gee"] * 1e6, "diagnostic",
         "Gamma_ee(rho) keV (PDG 7.04(6)); (f_rho Q_rho) %.5g GeV, s0/M^2 %.5g, s0 %.5g GeV^2, Gamma_rho %.4g GeV (PDG 0.1491); Delta alpha_had %.7g (rho %.6g, omega %.6g, continuum %.7g)" % (math.sqrt(r_["fQ2"]), r_["s0_over_M2"], r_["s0"], r_["Grho"], r_["d"], r_["rho"], r_["omega"], r_["cont"]))
rec("TRACE", "AN-2 post-freeze correction (disclosed)", "applied before any result was seen", "the frozen Breit-Wigner normalisation on [4 m_pi^2, infinity) diverges logarithmically for Gamma(s) = g^2 p^3/(6 pi s) (integrand -> const/s); F is normalised on [4 m_pi^2, s0], the resonance region of the duality ansatz")
V = an2(*PD); VAL = abs(V["d"] - 0.02783) <= 0.00029
emitz("VALIDATION", "AN-2 Delta alpha_had^(5), FESR f_rho route with PDG inputs", "PDG M_rho, F_pi, m_pi; round-y PDG inputs", V["d"], "0.02783", "0.00006", 0, "", "round-i gate |dev| <= 0.00029: %s" % ("PASS" if VAL else "FAIL"))
emitz("TRACE", "AN-2 Gamma_ee(rho)/M_rho with PDG inputs (byproduct)", "PDG inputs", V["Gee"] / 0.77526, mpf("7.04e-6") / mpf("0.77526"), mpf("0.06e-6") / mpf("0.77526"), 0, "information, not a gate", "keV %.4g" % (V["Gee"] * 1e6))
MW, MZ, al = L["m_W_MeV"] / 1000, L["m_Z_MeV"] / 1000, 1 / L["alpha_inv"]; s2 = 1 - (MW / MZ) ** 2; c2 = 1 - s2
mt = L["m_t_over_m_W"] * MW; mb = mt / P["wave8|m_t/m_b"]; mc = L["m_c_over_m_b"] * mb; mH = L["m_H_MeV"] / 1000; als = 2 * (F.POOF / F.PSI_CON) ** 2; mtau = L["m_tau_MeV"] / 1000
LamV = col("audit/score_2026-10-02ag.tsv", "AG-3", "AG-3 Lambda_V/m_p"); MV = LamV * mpM / 1000
Fr = col("audit/score_2026-10-02p.tsv", "FSOT", "P-4 F_pi with lbar4") / mpM
FS = an2(float(al), float(MZ), float(als), float(mtau), float(MV), float(Fr * mpM / 1000), float(L["m_pi_pm_MeV"]) / 1000, float(L["m_K_pm_MeV"]) / 1000, float(mc), float(mb))
info(s, "AN-2 inputs: M_V/m_p (soliton VMD), F_pi/m_p (round p)", "rounds ag, p", LamV, "FSOT · intermediate", "F_pi/m_p %s; g_rho_pipi (KSRF, width only) %.5g" % (nstr(Fr, 8), float(LamV / (sqrt(2) * Fr))))
info(s, "AN-2 f_rho Q_rho / M_V (FESR, FSOT)", "two FESRs, FSOT alpha_s, finite width", math.sqrt(FS["fQ2"]) / float(MV), "FSOT · intermediate",
     "f_rho Q_rho %.5g GeV; s0/M_V^2 %.5g; Gamma_ee(rho) %.4g keV; Gamma_rho/M_V %.5g; rho %.6g, omega %.6g, continuum %.7g" % (math.sqrt(FS["fQ2"]), FS["s0_over_M2"], FS["Gee"] * 1e6, FS["Grho"] / float(MV), FS["rho"], FS["omega"], FS["cont"]))
dh = mpf(FS["d"])
emitz(s, "AN-2 Delta alpha_had^(5)(M_Z^2) (FESR f_rho, FSOT)", "FSOT only", dh, "0.02783", "0.00006", 0, "FSOT · measured", "validation %s; round am 0.02633548 (z 24.9)" % ("passed" if VAL else "FAILED"))
z3 = zeta(3); ml = [X.kg_to_GeV(L["m_e_kg"]), X.kg_to_GeV(L["m_mu_kg"]), mtau]
da_lep = al / (3 * pi) * sum(ln(MZ**2 / m**2) - mpf(5) / 3 for m in ml) + (al / pi) ** 2 * sum(ln(MZ**2 / m**2) / 4 + z3 - mpf(5) / 24 for m in ml)
da_top = -(al / pi) * mpf(4) / 45 * MZ**2 / mt**2
rem = -(al / (16 * pi * s2)) * 4 * (c2 / s2 - mpf(1) / 3 - 3 * mb**2 / (s2 * MZ**2)) * ln(mt / MZ) + 11 * al / (24 * pi * s2) * ln(mH / MZ) + al / (4 * pi * s2) * (6 + (7 - 4 * s2) / (2 * s2) * ln(c2))
AS0 = AlphaS(float(als), float(MZ), float(mb), float(mc), float(mtau)); mbp_ = pole(float(mb), AS0); mcp_ = pole(float(mc), AS0)
ASt = AlphaS(float(als), float(MZ), mbp_, mcp_, float(mtau)); a_s = mpf(ASt(float(mt))) / pi
r = mH / mt
rho2 = 19 - mpf(33) / 2 * r + mpf(43) / 12 * r**2 + mpf(7) / 120 * r**3 - pi * sqrt(r) * (4 - mpf(3) / 2 * r + mpf(3) / 32 * r**2 + r**3 / 256) - pi**2 * (2 - 2 * r + r**2 / 2) - ln(r) * (3 * r - r**2 / 2)
q1 = 1 - mpf("2.8599") * a_s; q2 = q1 - mpf("14.594") * a_s**2
da = da_lep + dh + da_top
GF = pi * al / (sqrt(2) * MW**2 * s2)
for _ in range(300):
    xt = GF * mt**2 / (8 * sqrt(2) * pi**2); drho = 3 * xt * (1 + xt * rho2) * q2
    omr = (1 - da) * (1 + c2 / s2 * drho) - rem; new = pi * al / (sqrt(2) * MW**2 * s2 * omr)
    if fabs(new - GF) / GF < mpf(10) ** -30: GF = new; break
    GF = new
info(s, "AN-2 Delta r (round-z Z-2 primary chain, AN-2 Delta alpha_had)", "FSOT chain", 1 - omr, "model-computed", "Delta rho " + nstr(drho, 8) + "; Delta alpha " + nstr(da, 8))
emitz(s, "AN-2 G_F (round-z chain with AN-2 Delta alpha_had)", "FSOT only", GF, *ref("G_F_GeVm2"), 0, "measured", "round z (quark-pole Delta alpha_had): " + nstr(col("audit/score_2026-10-02z.tsv", "Z-2", "Z-2 G_F"), 10))
Rc = X.compute(hub, F, GF_override=GF)
zG = emitz(s, "AN-2 Gamma_Z/M_Z (authority A1 width, AN-2 G_F)", "FSOT only", Rc["GZ_over_MZ_A1"], *ref("Gamma_Z_over_M_Z"), 0, "measured",
           "round z: " + nstr(col("audit/score_2026-10-02z.tsv", "Z-2", "Z-2 Gamma_Z/M_Z"), 10) + "; record row not edited here (owner/hub decision if z <= 1 with validation passing)")
rec("GATE", "record rows of the 91", "unchanged", "z-only; 88/91 since owner record commit b99fc29; level-B job status in AN-1; Gamma_Z/M_Z route %s" % ("passes (report to owner/hub)" if (zG <= 1 and VAL) else "does not pass (z %s, validation %s)" % (nstr(zG, 4), "passed" if VAL else "failed")))
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02an.py under audit/FREEZE_2026-10-02an (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
