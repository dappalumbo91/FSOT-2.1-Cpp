#!/usr/bin/env python3
"""Round-aa scores under audit/FREEZE_2026-10-02aa (committed first). z-only, dimensionless ratios; FSOT-only inputs.
AA-1 soliton with M/m_p from the proton-unit condensate reading (audit/heavy_2026-10-02aa_K12.json); AA-2 KSRF light-quark Delta alpha_had -> G_F, Gamma_Z/M_Z; AA-3 H0-free recombination temperature (information).
  python tools/score_2026_10_02aa.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02aa.tsv
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
# ---------------- AA-1
s = "AA-1"; GJ = J("audit/gap_2026-10-02aa.json"); Hq = J("audit/heavy_2026-10-02q.json")
info(s, "AA-1 M/m_p (DP gap equation, condensate pin read as <(alpha_s/pi)G^2>/m_p^4, rho = R/3)", "FSOT wave9 pin, unit-free", GJ["M_over_mp"], "FSOT · intermediate (scored via Delta-N, g_A)", "n^(1/4)/m_p " + nstr(mpf(GJ["n_quarter_over_mp"]), 9) + "; M0/n^(1/4) " + nstr(mpf(GJ["M0_over_n_quarter"]), 9) + "; round y (GeV^4 reading) " + nstr(mpf(GJ["round_y_M_over_mp"]), 9) + "; MeV byproduct " + nstr(mpf(GJ["M_MeV_byproduct"]), 7))
def raw(c, o):
    I = mpf(o["I_times_M"]); return {"g1": mpf(o["A_im"]) / I}
SGg1 = 1 if raw(None, Hq["Q1_sanity_M420_F93"]["DPP"])["g1"] > 0 else -1
DNc = (mpf("1232") - (mpf("938.27208943") + mpf("939.56542194")) / 2) / mpf("938.27208943")
hp = R_ / "audit/heavy_2026-10-02aa_K12.json"
if hp.exists() and "DPP" in J("audit/heavy_2026-10-02aa_K12.json").get("AA1_pu_massive_K12", {}):
    H = J("audit/heavy_2026-10-02aa_K12.json"); d = H["AA1_pu_massive_K12"]; o = d["DPP"]; Mr = mpf(H["inputs"]["M_over_mp"]); IM = mpf(o["I_times_M"])
    DN = 3 * Mr / (2 * IM); gA = mpf(o["gA0"]) + SGg1 * raw(d, o)["g1"]
    nt = "I M " + nstr(IM, 6) + "; E/M " + nstr(mpf(o["E_sol_over_M"]), 6) + "; eps_val/M " + nstr(mpf(o["eps_val"]), 6) + "; x_DPP " + nstr(mpf(d["x_DPP"]), 5) + (" EDGE" if d["edge_minimum"] else "") + "; K 12 only: no theory unc. (frozen)"
    emitz(s, "AA-1 (M_Delta - M_N)/m_p (K 12)", "proton units, FSOT inputs", DN, DNc, mpf(2) / mpf("938.27208943"), 0, "FSOT · measured", nt + "; MeV byproduct " + nstr(DN * mpM, 6))
    emitz(s, "AA-1 g_A time-ordered (K 12)", "proton units, FSOT inputs", gA, "1.2754", "0.0013", 0, "FSOT · measured", "classical " + nstr(mpf(o["gA0"]), 6) + "; round-y convention")
else:
    rec(s, "soliton at the AA-1 M/m_p", "not run", "")
s = "AA-2"; src = (R_ / "tools/score_2026_10_02i.py").read_text(encoding="utf-8").split("\n")
i0 = next(i for i, l in enumerate(src) if l.startswith("# ---- HAD-2: quark-hadron duality")); i1 = next(i for i, l in enumerate(src) if l.startswith("def f10"))
ns = {"math": math}; exec("\n".join(src[i0:i1]), ns); dalpha_had = ns["dalpha_had"]
def pole(m, AS): return m * (1 + 4 * AS(m) / (3 * math.pi))
def dah_pole(alpha, MZ, asMZ, mtau, mpi, mK, mc, mb):
    AS0 = ns["AlphaS"](asMZ, MZ, mb, mc, mtau)  # flavour switching at the MSbar masses for the pole conversion only
    mcp, mbp = pole(mc, AS0), pole(mb, AS0)
    d, AS = dalpha_had(alpha, MZ, asMZ, mtau, mpi, mK, mcp, mbp)
    return d, mcp, mbp
dv, mcpv, mbpv = dah_pole(1 / 137.035999177, 91.1880, 0.1180, 1.77693, 0.13957039, 0.493677, 1.2730, 4.183)
# ---- AA-2 KSRF light-quark replacement (FREEZE_2026-10-02aa): u,d continuum from s0 = 8 pi^2 m_rho^2/g^2, narrow rho + omega below
def col(path, sec, key):
    for line in open(R_ / path, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) > 3 and f[0] == sec and f[1].startswith(key): return mpf(f[3])
G2K = 12 * math.pi**2 / 3
def dalpha_ksrf(alpha, MZ, asMZ, mtau, Fpi, mK, mD, mB):
    AS = ns["AlphaS"](asMZ, MZ, mB, mD, mtau); GX, GW = ns["GX"], ns["GW"]
    mr2 = 2 * G2K * Fpi**2; s0 = 8 * math.pi**2 * mr2 / G2K
    flav = sorted([(s0, 4 / 9), (s0, 1 / 9), (4 * mK**2, 1 / 9), (4 * mD**2, 4 / 9), (4 * mB**2, 1 / 9)])
    MZ2 = MZ**2
    def R(s):
        open_ = [q for th, q in flav if s > th]; nf = len(open_)
        aa = AS(math.sqrt(s)) / math.pi
        K = 1 + aa + (1.9857 - 0.1152 * nf) * aa**2 + (-6.63694 - 1.20013 * nf - 0.00518 * nf**2) * aa**3
        return 3 * sum(open_) * K
    RZ = R(MZ2); smin = flav[0][0]
    def g(t):
        s = math.exp(t); return (R(s) - RZ) * MZ2 / (MZ2 - s) if abs(MZ2 - s) > 1e-9 * MZ2 else 0.0
    edges = sorted({math.log(th) for th, _ in flav} | {math.log(MZ2)})
    pts = []
    for lo, hi in zip(edges, edges[1:]):
        n = max(1, int(math.ceil((hi - lo) / 0.5))); pts += [lo + (hi - lo) * k / n for k in range(n + 1)][:-1]
    pts.append(edges[-1]); top = math.log(MZ2) + 40.0
    n = 80; pts += [edges[-1] + (top - edges[-1]) * k / n for k in range(1, n + 1)]
    tot = 0.0
    for lo, hi in zip(pts, pts[1:]):
        c, w = 0.5 * (hi + lo), 0.5 * (hi - lo)
        tot += w * sum(wi * g(c + w * xi) for xi, wi in zip(GX, GW))
    tot += RZ * math.log((MZ2 - smin) / smin)
    res = 12 * math.pi**2 / G2K * (1 + 1 / 9) * MZ2 / (MZ2 - mr2)
    return alpha / (3 * math.pi) * (tot + res), alpha / (3 * math.pi) * res, s0, math.sqrt(mr2)
def dah_ksrf(alpha, MZ, asMZ, mtau, Fpi, mK, mc, mb):
    AS0 = ns["AlphaS"](asMZ, MZ, mb, mc, mtau); mcp, mbp = pole(mc, AS0), pole(mb, AS0)
    return dalpha_ksrf(alpha, MZ, asMZ, mtau, Fpi, mK, mcp, mbp) + (mcp, mbp)
kv = dah_ksrf(1 / 137.035999177, 91.1880, 0.1180, 1.77693, 0.09207, 0.493677, 1.2730, 4.183)
VALK = abs(kv[0] - 0.02783) <= 0.00029
emitz("VALIDATION", "AA-2 Delta alpha_had^(5), KSRF light quarks, PDG inputs", "PDG F_pi 92.07 MeV, m_c 1.2730, m_b 4.183, alpha_s 0.1180", float("%.10g" % kv[0]), "0.02783", "0.00006", 0, "", "rho+omega %.6g; s0 %.5g GeV^2; m_rho(KSRF) %.5g GeV; round-i gate |dev| <= 0.00029: %s" % (kv[1], kv[2], kv[3], "PASS" if VALK else "FAIL"))

VAL = abs(dv - 0.02783) <= 0.00029
info("VALIDATION", "Y-2 quark-pole validation (reference)", "PDG", float("%.10g" % dv), "", "round y: FAIL") if False else None
emitz("VALIDATION", "AA-2 reference: Y-2 Delta alpha_had^(5), quark-pole thresholds, PDG inputs", "PDG m_c 1.2730, m_b 4.183, alpha_s 0.1180", float("%.10g" % dv), "0.02783", "0.00006", 0, "", "pole m_c %.5g, m_b %.5g GeV; round-i gate |dev| <= 0.00029: %s" % (mcpv, mbpv, "PASS" if VAL else "FAIL"))
MW, MZ, al = L["m_W_MeV"] / 1000, L["m_Z_MeV"] / 1000, 1 / L["alpha_inv"]; s2 = 1 - (MW / MZ) ** 2; c2 = 1 - s2
mt = L["m_t_over_m_W"] * MW; mb = mt / P["wave8|m_t/m_b"]; mc = L["m_c_over_m_b"] * mb; mH = L["m_H_MeV"] / 1000; als = 2 * (F.POOF / F.PSI_CON) ** 2; mtau = L["m_tau_MeV"] / 1000
dF, mcp, mbp = dah_pole(float(al), float(MZ), float(als), float(mtau), float(L["m_pi_pm_MeV"]) / 1000, float(L["m_K_pm_MeV"]) / 1000, float(mc), float(mb))
dhy = mpf(float("%.10g" % dF))
Ffs = col("audit/score_2026-10-02p.tsv", "FSOT", "P-4 F_pi with lbar4") / 1000
kf = dah_ksrf(float(al), float(MZ), float(als), float(mtau), float(Ffs), float(L["m_K_pm_MeV"]) / 1000, float(mc), float(mb)); dh = mpf(float("%.10g" % kf[0]))
info(s, "Delta alpha_had^(5), round-y quark-pole duality (reference)", "FSOT", dhy, "FSOT · measured", "round y z 8.1; validation %s" % ("passed" if VAL else "FAILED"))
emitz(s, "AA-2 Delta alpha_had^(5) (KSRF light quarks, FSOT inputs)", "FSOT alpha, M_Z, alpha_s, m_tau, P-4 F_pi, m_K, m_c, m_b", dh, "0.02783", "0.00006", 0, "FSOT · measured", "rho+omega %.6g; s0 %.5g GeV^2; m_rho(KSRF) %.5g GeV (m_rho/m_p byproduct); validation %s" % (kf[1], kf[2], kf[3], "passed" if VALK else "FAILED"))
z3 = zeta(3); ml = [X.kg_to_GeV(L["m_e_kg"]), X.kg_to_GeV(L["m_mu_kg"]), mtau]
da_lep = al / (3 * pi) * sum(ln(MZ**2 / m**2) - mpf(5) / 3 for m in ml) + (al / pi) ** 2 * sum(ln(MZ**2 / m**2) / 4 + z3 - mpf(5) / 24 for m in ml)
da_top = -(al / pi) * mpf(4) / 45 * MZ**2 / mt**2
rem = -(al / (16 * pi * s2)) * 4 * (c2 / s2 - mpf(1) / 3 - 3 * mb**2 / (s2 * MZ**2)) * ln(mt / MZ) + 11 * al / (24 * pi * s2) * ln(mH / MZ) + al / (4 * pi * s2) * (6 + (7 - 4 * s2) / (2 * s2) * ln(c2))

AS0 = ns["AlphaS"](float(als), float(MZ), float(mb), float(mc), float(mtau)); mbp_ = pole(float(mb), AS0); mcp_ = pole(float(mc), AS0)
ASt = ns["AlphaS"](float(als), float(MZ), mbp_, mcp_, float(mtau)); a_s = mpf(ASt(float(mt))) / pi
r = mH / mt
rho2 = 19 - mpf(33) / 2 * r + mpf(43) / 12 * r**2 + mpf(7) / 120 * r**3 - pi * sqrt(r) * (4 - mpf(3) / 2 * r + mpf(3) / 32 * r**2 + r**3 / 256) - pi**2 * (2 - 2 * r + r**2 / 2) - ln(r) * (3 * r - r**2 / 2)
q1 = 1 - mpf("2.8599") * a_s; q2 = q1 - mpf("14.594") * a_s**2
da = da_lep + dh + da_top
def solve(two_loop, qcd2, resum):
    GF = pi * al / (sqrt(2) * MW**2 * s2)
    for _ in range(300):
        xt = GF * mt**2 / (8 * sqrt(2) * pi**2); drho = 3 * xt * (1 + (xt * rho2 if two_loop else 0)) * (q2 if qcd2 else q1)
        omr = (1 - da) * (1 + c2 / s2 * drho) - rem if resum else 1 - (da - c2 / s2 * drho + rem)
        new = pi * al / (sqrt(2) * MW**2 * s2 * omr)
        if fabs(new - GF) / GF < mpf(10) ** -30: GF = new; break
        GF = new
    return GF, 1 - omr, drho
info(s, "inputs: alpha_s(m_t), r = M_H/m_t, rho2(r)", "FSOT seed, leaves", a_s * pi, "intermediate", "r " + nstr(r, 6) + "; rho2 " + nstr(rho2, 6) + "; Delta r_rem " + nstr(rem, 8) + "; Delta alpha " + nstr(da, 8))
for tag, args in (("one loop (alpha_s at m_t)", (False, False, False)), ("+ resummation", (False, False, True)), ("+ resummation + O(alpha alpha_s^2)", (False, True, True)), ("+ resummation + O(alpha alpha_s^2) + O(G_F^2 m_t^4)  [AA-2 primary]", (True, True, True))):
    GF_, dr_, drho_ = solve(*args)
    info(s, "Delta r, " + tag, "FSOT chain", dr_, "model-computed", "Delta rho " + nstr(drho_, 8) + "; G_F " + nstr(GF_, 10) + "; PDG SM Delta r 0.03685(20) for reference")
GFz, drz, _ = solve(True, True, True)
emitz(s, "AA-2 G_F (round-z higher-order chain, KSRF Delta alpha_had)", "FSOT only", GFz, *ref("G_F_GeVm2"), 0, "measured")
Rc = X.compute(hub, F, GF_override=GFz)
emitz(s, "AA-2 Gamma_Z/M_Z (authority A1 width, AA-2 G_F)", "FSOT only", Rc["GZ_over_MZ_A1"], *ref("Gamma_Z_over_M_Z"), 0, "measured", "record row changes only if z <= 1 with the Delta alpha_had validation passing (validation: KSRF construction above)")
# ---------------- AA-3 H0-free recombination temperature (information)
from mpmath import findroot, exp
eta = P["wave10|eta_baryon_photon"]; me = X.kg_to_GeV(L["m_e_kg"]) * 10**9; z3_ = zeta(3)
def saha(u):  # u = T/(m_e alpha^2); hydrogen only, n_H = eta n_gamma, x_e = 1/2: x^2/(1-x) = (1/n_H)(m_e T/2pi)^(3/2) e^(-B/T)
    t = u * al**2  # T/m_e
    return ln(mpf(1) / 2) - (ln(pi**2 / (2 * z3_ * eta)) + mpf(3) / 2 * ln(1 / (2 * pi * t)) - 1 / (2 * u))
u = findroot(saha, (mpf("0.005"), mpf("0.03")), solver="anderson"); kB_eV = mpf("8.617333262e-5"); Trec = u * me * al**2 / kB_eV
info("AA-3", "kT_rec/(m_e alpha^2), Saha x_e = 1/2, hydrogen only (H0-free)", "FSOT eta, alpha", u, "model-computed", "T_rec = " + nstr(Trec, 6) + " K (byproduct via m_e)")
info("AA-3", "T_0 = T_rec/(1 + z_*) with Planck z_* = 1089.80 (outside number; info only)", "AA-3 T_rec, Planck z_*", Trec / mpf("1090.80"), "information", "FIRAS 2.7255 K: " + nstr((Trec / mpf("1090.80") / mpf("2.7255") - 1) * 100, 4) + " %; Saha equilibrium x_e = 1/2 is not the last-scattering surface (known to sit higher than the Peebles freeze-out), so not a route; FSOT has no z_* pin: no H0-free T_0 route")
rec("GATE", "record rows of the 91", "unchanged", "z-only")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02aa.py under audit/FREEZE_2026-10-02aa (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
