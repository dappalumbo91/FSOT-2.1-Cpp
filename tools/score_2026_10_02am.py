#!/usr/bin/env python3
"""Round-am scores under audit/FREEZE_2026-10-02am (committed first). z-only, dimensionless ratios; FSOT-only inputs.
AM-1 kmax-14 shell-average job status (tools/shellavg_bg_2026_10_02am.py); AM-2 Delta alpha_had via soliton-radius VMD + LMD duality couplings -> G_F, Gamma_Z/M_Z (round-z chain).
  python tools/score_2026_10_02am.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02am.tsv
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
# ---------------- AM-1 status of the level-B shell-average job
s = "AM-1"
rec(s, "AM-1 level-B job (FREEZE_2026-10-02am budget change)", "running at commit time (carries to the next round)",
    "tools/shellavg_bg_2026_10_02am.py started detached after the freeze; per-sample files audit/shellavg_2026-10-02am_B_j<j>.json are committed and scored (mu_p, mu_n, two-level rule) in the round the job finishes; this row is static so the round-am score stays byte-identical")
# ---------------- AM-2
s = "AM-2"; src = (R_ / "tools/score_2026_10_02i.py").read_text(encoding="utf-8").split("\n")
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
def am2(alpha, MZ, asMZ, mtau, MV, mK, mc, mb):
    AS0 = AlphaS(asMZ, MZ, mb, mc, mtau); mcp, mbp = pole(mc, AS0), pole(mb, AS0); s0 = 2 * MV**2
    res = {V: 4 * math.pi * alpha * (cV * s0 / (12 * math.pi**2)) / MV**2 * MZ**2 / (MZ**2 - MV**2) for V, cV in (("rho", 1.5), ("omega", 1 / 6))}
    gee = {V: 4 * math.pi * alpha**2 * (cV * s0 / (12 * math.pi**2)) / (3 * MV) for V, cV in (("rho", 1.5), ("omega", 1 / 6))}
    c_ = cont(alpha, MZ, asMZ, mtau, s0, mK, mcp, mbp)
    return float("%.10g" % (res["rho"] + res["omega"] + c_)), res, c_, gee, s0
dv, rv, cv, gv, s0v = am2(1 / 137.035999177, 91.1880, 0.1180, 1.77693, 0.77526, 0.493677, 1.2730, 4.183)
VAL = abs(dv - 0.02783) <= 0.00029
emitz("VALIDATION", "AM-2 Delta alpha_had^(5), VMD+LMD route with PDG M_rho and round-y PDG inputs", "PDG M_rho 0.77526, alpha_s 0.1180, m_c 1.2730, m_b 4.183", dv, "0.02783", "0.00006", 0, "",
      "rho %.6g + omega %.6g + continuum (u,d from s0 = %.5g GeV^2) %.7g; Gamma_ee(rho) %.4g keV (PDG 7.04(6)), Gamma_ee(omega) %.4g keV (PDG 0.60(2)); round-i gate |dev| <= 0.00029: %s" % (rv["rho"], rv["omega"], s0v, cv, gv["rho"] * 1e6, gv["omega"] * 1e6, "PASS" if VAL else "FAIL"))
MW, MZ, al = L["m_W_MeV"] / 1000, L["m_Z_MeV"] / 1000, 1 / L["alpha_inv"]; s2 = 1 - (MW / MZ) ** 2; c2 = 1 - s2
mt = L["m_t_over_m_W"] * MW; mb = mt / P["wave8|m_t/m_b"]; mc = L["m_c_over_m_b"] * mb; mH = L["m_H_MeV"] / 1000; als = 2 * (F.POOF / F.PSI_CON) ** 2; mtau = L["m_tau_MeV"] / 1000
LamV = col("audit/score_2026-10-02ag.tsv", "AG-3", "AG-3 Lambda_V/m_p"); MV = LamV * mpM / 1000
dF, rF, cF, gF_, s0F = am2(float(al), float(MZ), float(als), float(mtau), float(MV), float(L["m_K_pm_MeV"]) / 1000, float(mc), float(mb))
info(s, "AM-2 M_V/m_p = sqrt6/r_V (round-ag soliton valence radius, VMD)", "round ag AG-3", LamV, "FSOT · intermediate", "M_V %s MeV byproduct (PDG M_rho 775.26, M_omega 782.66); s0 = 2 M_V^2 = %.5g GeV^2" % (nstr(MV * 1000, 6), s0F))
info(s, "AM-2 rho + omega narrow terms (LMD duality couplings)", "c_rho 3/2, c_omega 1/6", rF["rho"] + rF["omega"], "FSOT · intermediate",
     "rho %.6g, omega %.6g (= 2 alpha c_V/(3 pi) x M_Z^2/(M_Z^2 - M_V^2), M_V-independent at LO); Gamma_ee(rho) %.4g keV, Gamma_ee(omega) %.4g keV byproducts" % (rF["rho"], rF["omega"], gF_["rho"] * 1e6, gF_["omega"] * 1e6))
info(s, "AM-2 continuum (u,d from s0, s from 4 m_K^2, pole c, b)", "round-y duality integrand", cF, "FSOT · intermediate", "")
dh = mpf(dF)
emitz(s, "AM-2 Delta alpha_had^(5)(M_Z^2) (VMD+LMD, FSOT)", "FSOT only", dh, "0.02783", "0.00006", 0, "FSOT · measured", "validation %s; round-y quark-pole duality gave z 8.1" % ("passed" if VAL else "FAILED"))
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
info(s, "AM-2 Delta r (round-z Z-2 primary chain, AM-2 Delta alpha_had)", "FSOT chain", 1 - omr, "model-computed", "Delta rho " + nstr(drho, 8) + "; Delta alpha " + nstr(da, 8))
emitz(s, "AM-2 G_F (round-z chain with AM-2 Delta alpha_had)", "FSOT only", GF, *ref("G_F_GeVm2"), 0, "measured", "round z (quark-pole Delta alpha_had): " + nstr(col("audit/score_2026-10-02z.tsv", "Z-2", "Z-2 G_F"), 10))
Rc = X.compute(hub, F, GF_override=GF)
zG = emitz(s, "AM-2 Gamma_Z/M_Z (authority A1 width, AM-2 G_F)", "FSOT only", Rc["GZ_over_MZ_A1"], *ref("Gamma_Z_over_M_Z"), 0, "measured",
           "round z: " + nstr(col("audit/score_2026-10-02z.tsv", "Z-2", "Z-2 Gamma_Z/M_Z"), 10) + "; record row not edited here (owner/hub decision if z <= 1 with validation passing)")
rec("GATE", "record rows of the 91", "unchanged", "z-only; 88/91 since owner record commit b99fc29; Gamma_Z/M_Z route %s" % ("passes (report to owner/hub)" if (zG <= 1 and VAL) else "does not pass (z %s, validation %s)" % (nstr(zG, 4), "passed" if VAL else "failed")))
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02am.py under audit/FREEZE_2026-10-02am (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
