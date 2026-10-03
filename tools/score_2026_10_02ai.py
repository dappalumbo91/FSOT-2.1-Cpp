#!/usr/bin/env python3
"""Round-ai scores under audit/FREEZE_2026-10-02ai (committed first). z-only, dimensionless ratios; FSOT-only inputs.
AI-1 two-subtraction Pauli-Villars (audit/pv2_2026-10-02ai_k*.json); AI-2 sigma-mode projected scalar density (audit/sigproj_2026-10-02ai.json).
  python tools/score_2026_10_02ai.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02ai.tsv
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
# ---------------- AD-1
def col(path, sec, key):
    for line in open(R_ / path, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) > 3 and f[0] == sec and f[1].startswith(key): return mpf(f[3])
Hw = J("audit/heavy_2026-10-02ab_wide_K12.json")
# ---------------- AI-1
s = "AI-1"
Hq = J("audit/heavy_2026-10-02q.json"); rq = Hq["Q1_sanity_M420_F93"]; oq = rq["DPP"]; Iq = mpf(oq["I_times_M"]); qq = mpf(rq["M_N_MeV"]) / mpf(rq["M_MeV"])
SG = {"g1": 1 if mpf(oq["A_im"]) / Iq > 0 else -1, "muS": 1 if qq * mpf(oq["B_re"]) / (6 * Iq) > 0 else -1, "muV1": 1 if qq * mpf(oq["Amu_im"]) / Iq > 0 else -1}
m1, m2, c1, c2 = mpf("1.340129576"), mpf("6.959685111"), mpf("-0.5663113338"), mpf("3.523179412e-4")
chkA = 1 + c1 * m1**2 + c2 * m2**2; chkB = 1 + c1 * m1**4 + c2 * m2**4
FM2 = -(3 / (4 * pi**2)) * (c1 * m1**2 * ln(m1**2) + c2 * m2**2 * ln(m2**2)); QQ = -(3 / (4 * pi**2)) * (c1 * m1**4 * ln(m1**2) + c2 * m2**4 * ln(m2**2))
info(s, "AI-1 two-subtraction PV: F/M from (c)", "m_1 1.340129576, m_2 6.959685111, c_1 -0.5663113338, c_2 3.523179412e-4", sqrt(FM2), "derivation",
     "conditions (a) %s, (b) %s (zero); condensate <qq>/M^3 negative, |<qq>|^(1/3)/M %s (pin 1/4 m_p / M = %s); single-PV F/M 0.2005555" % (nstr(chkA, 3), nstr(chkB, 3), nstr((-QQ) ** (mpf(1) / 3), 8), nstr(mpf("0.25") / mpf("0.4581682005"), 8)))
def evalk(path, sch):
    d_ = J(path); Mr_ = mpf(d_["inputs"]["M_over_mp"]); qN = 1 / Mr_; ev_ = mpf(d_["eps_val"]); per = d_["per"]
    if sch == "single": cs = {"m1s": -(1 / mpf(d_["masses"]["m1s"]))**2}
    else: cs = {"m1": c1, "m2": c2}
    def reg(key, ix=None):
        g_ = lambda k, t: (mpf(per["%s_%s" % (k, t)][key]) if ix is None else mpf(per["%s_%s" % (k, t)][key][ix]))
        return (g_("m0", "sol") - g_("m0", "vac")) + sum(c_ * (g_(k, "sol") - g_(k, "vac")) for k, c_ in cs.items())
    E = 3 * ev_ - mpf("1.5") * reg("esum")
    I_ = mpf(d_["I_val_plus_sea0"]) + sum(c_ * mpf(per["%s_sol" % k]["I_sea"]) for k, c_ in cs.items())
    gA0_ = -(mpf(3) / 3) * (mpf(d_["gA0_val_d"]) + reg("gA0"))
    rot = lambda nm, ix: (mpf(d_["%s_tot_m0" % nm][ix]) - mpf(per["m0_sol"][nm][ix])) + reg(nm, ix)
    gA_ = gA0_ + SG["g1"] * rot("A", 1) / I_
    mV0 = -qN / 3 * (mpf(d_["xat_val"]) + reg("xat")); muV = mV0 + SG["muV1"] * qN * rot("Amu", 1) / I_; muS = SG["muS"] * qN * rot("B", 0) / (6 * I_)
    return {"E": E, "ev": ev_, "I": I_, "gA": gA_, "mV0": mV0, "mup": (muS + muV) / 2, "mun": (muS - muV) / 2, "DN": 3 * Mr_ / (2 * I_)}
k12 = "audit/pv2_2026-10-02ai_k12.json"; RS = {}
for sch in ("single", "double"):
    RS[sch] = evalk(k12, sch); v_ = RS[sch]
    info(s, "AI-1 kmax 12 (K 14, D 14, fixed profile) %s PV: E_sol/M" % sch, "audit/pv2_2026-10-02ai_k12.json", v_["E"], "check",
         "eps_val %s; I M %s; g_A %s; mu_V^(0) %s; mu_p %s, mu_n %s; Delta-N/m_p %s" % tuple(nstr(v_[k], 7) for k in ("ev", "I", "gA", "mV0", "mup", "mun", "DN")))
tol = all(fabs(RS["double"][k] / RS["single"][k] - 1) <= mpf("0.02") for k in ("E", "ev", "I", "gA"))
rec(s, "AI-1 tolerance check (E, eps_val, I, g_A within 2 % of single PV)", "passes" if tol else "fails",
    ", ".join("%s %s %%" % (k, nstr((RS["double"][k] / RS["single"][k] - 1) * 100, 3)) for k in ("E", "ev", "I", "gA")))
ks = [k12] + [p_ for p_ in ("audit/pv2_2026-10-02ai_k14.json", "audit/pv2_2026-10-02ai_k16.json") if (R_ / p_).exists()]
DR = [evalk(p_, "double") for p_ in ks]
for p_, v_ in zip(ks[1:], DR[1:]):
    info(s, "AI-1 %s double PV: mu_V^(0)" % p_.split("_")[-1].replace(".json", ""), p_, v_["mV0"], "kmax step", "mu_p %s, mu_n %s; g_A %s; I M %s; E/M %s" % tuple(nstr(v_[k], 7) for k in ("mup", "mun", "gA", "I", "E")))
if len(DR) < 2:
    rec(s, "AI-1 mu_p, mu_n", "not scored", "kmax-14 run missing")
else:
    chg = {k: [(DR[i + 1][k] - DR[i][k]) / DR[i + 1][k] for i in range(len(DR) - 1)] for k in ("mup", "mun", "mV0")}
    txt = "; ".join("%s %s" % (k, ", ".join(nstr(c_ * 100, 3) + " %" for c_ in v_)) for k, v_ in chg.items())
    if tol and all(fabs(c_) <= mpf("0.02") for k in ("mup", "mun") for c_ in chg[k]):
        th_ = {k: max(fabs(DR[i + 1][k] - DR[i][k]) for i in range(len(DR) - 1)) for k in ("mup", "mun")}
        emitz(s, "AI-1 mu_p (two-subtraction PV, kmax %s)" % ks[-1].split("_k")[-1].replace(".json", ""), "FSOT inputs", DR[-1]["mup"], "2.79284734463", "0.00000001", th_["mup"], "FSOT · measured", "kmax changes: " + txt)
        emitz(s, "AI-1 mu_n (two-subtraction PV, kmax %s)" % ks[-1].split("_k")[-1].replace(".json", ""), "FSOT inputs", DR[-1]["mun"], "-1.91304276", "0.00000045", th_["mun"], "FSOT · measured", "kmax changes: " + txt)
    else:
        rec(s, "AI-1 mu_p, mu_n", "not scored", ("tolerance check fails; " if not tol else "") + "kmax changes: " + txt)
# ---------------- AI-2
s = "AI-2"
SPj = J("audit/sigproj_2026-10-02ai.json"); sch = "double" if tol else "single"
Fr = col("audit/score_2026-10-02p.tsv", "FSOT", "P-4 F_pi with lbar4") / mpM; Mq = mpf(Hw["inputs"]["M_over_mp"])
for r_ in SPj["runs"]:
    for nm in ("single", "double"):
        e_ = r_[nm]; gs2p = (mpf(e_["Q_sigma"]) * Mq / Fr)**2 / (4 * pi)
        info(s, "AI-2 kmax %g, %s PV: Integral rho_sigma" % (r_["kmax"], nm), "round-ab soliton, K 12, D 12", e_["Q_sigma"], "FSOT · intermediate",
             "valence part %s; unprojected scalar charge %s; chiral-circle depletion S_vac(cos-1) %s; r_sigma^2 M^2 %s; s_P %+d (stationarity ratio %s); g_sigma^2/4pi would be %s" % (nstr(mpf(e_["Q_sigma_val"]), 6), nstr(mpf(e_["Q_scalar_unprojected"]), 6), nstr(mpf(e_["depletion_Svac_cos_minus_1"]), 6), nstr(mpf(e_["r2_sigma"]), 6), e_["s_P"], nstr(mpf(e_["stationarity_ratio"]), 3), nstr(gs2p, 5)))
a12, a14 = SPj["runs"][0][sch], SPj["runs"][1][sch]; ch2 = (mpf(a14["Q_sigma"]) - mpf(a12["Q_sigma"])) / mpf(a14["Q_sigma"])
cu = (mpf(SPj["runs"][1][sch]["Q_scalar_unprojected"]) - mpf(SPj["runs"][0][sch]["Q_scalar_unprojected"])) / mpf(SPj["runs"][1][sch]["Q_scalar_unprojected"])
if mpf(a12["Q_sigma"]) > 0 and mpf(a12["r2_sigma"]) > 0 and fabs(ch2) <= mpf("0.02"):
    rec(s, "AI-2 sigma-projected g_sigmaNN (%s PV)" % sch, "adopted", "kmax change %s %%" % nstr(ch2 * 100, 3))
else:
    rec(s, "AI-2 sigma-projected g_sigmaNN (%s PV)" % sch, "not adopted; deuteron not rerun, nothing scored", "Integral rho_sigma kmax 12 -> 14 change %s %% > 2 %% (unprojected scalar charge changes %s %%)" % (nstr(ch2 * 100, 3), nstr(cu * 100, 3)))
rec("GATE", "record rows of the 91", "unchanged", "z-only")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02ai.py under audit/FREEZE_2026-10-02ai (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
