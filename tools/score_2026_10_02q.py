#!/usr/bin/env python3
"""Round-q scores under audit/FREEZE_2026-10-02q (committed first). Reads audit/heavy_2026-10-02q.json (tools/heavy_2026_10_02q.py). mpmath/stdlib only.

  python tools/score_2026_10_02q.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02q.tsv
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, fabs, nstr
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves(); R = Path(__file__).resolve().parents[1]
H = json.loads((R / "audit/heavy_2026-10-02q.json").read_text(encoding="utf-8"))
rows = []
def emit(sec, name, inputs, v, c, s, tol, cls="", note=""):
    v, c, s, tol = mpf(v), mpf(c), mpf(s), mpf(tol)
    rel = (v - c) / c; verdict = "PASS" if fabs(rel) <= tol else "FAIL"
    rows.append([sec, name, inputs, nstr(v, 12), nstr(c, 10), nstr(s, 4), nstr(fabs(v - c) / s, 5), verdict, nstr(rel * 100, 5) + " %", cls, note]); return verdict == "PASS"
def info(sec, name, inputs, v, cls="", note=""): rows.append([sec, name, inputs, nstr(mpf(v), 12), "-", "-", "-", "info", "-", cls, note])
def rec(sec, name, verdict, note): rows.append([sec, name, "-", "-", "-", "-", "-", verdict, "-", "-", note])
Nc = 3; mp = X.kg_to_GeV(L["m_p_kg"]) * 1000
GA, sGA = mpf("1.2754"), mpf("0.0013"); DN = mpf("1232") - (mpf("938.27208943") + mpf("939.56542194")) / 2
MUP, sMUP, MUN, sMUN = mpf("2.79284734463"), mpf("0.00000000082"), mpf("-1.91304276"), mpf("0.00000045")
def prim(c):
    if c.get("SC_converged") and "SC" in c and -1 < c["SC"]["eps_val"] < 1: return "SC", c["SC"]
    return "DPP", c["DPP"]
def raw(c, o):
    M, MN = mpf(c["M_MeV"]), mpf(c["M_N_MeV"]); I = mpf(o["I_times_M"]); q = MN / M
    return {"g1": Nc * mpf(o["A_im"]) / (3 * I), "muS": Nc * q * mpf(o["B_re"]) / (18 * I), "muV1": Nc * q * mpf(o["Amu_im"]) / (3 * I), "muV0": -Nc * q / 9 * (mpf(o["xat_val"]) + mpf(o["xat_sea"]))}
san = H["Q1_sanity_M420_F93"]; rs = raw(san, prim(san)[1])
SG = {k: (1 if rs[k] > 0 else -1) for k in ("g1", "muS", "muV1")}
def derive(c):
    tag, o = prim(c); r = raw(c, o); M = mpf(c["M_MeV"]); I = mpf(o["I_times_M"])
    g1, muS, muV1, muV0 = SG["g1"] * r["g1"], SG["muS"] * r["muS"], SG["muV1"] * r["muV1"], r["muV0"]; muV = muV0 + muV1
    return {"profile": tag, "gA0": mpf(o["gA0"]), "gA1": g1, "gA": mpf(o["gA0"]) + g1, "DN": 3 * M / (2 * I), "E": mpf(o["E_sol_over_M"]), "Em": mpf(o["E_m_over_M"]),
            "muS": muS, "muV0": muV0, "muV1": muV1, "mup": (muS + muV) / 2, "mun": (muS - muV) / 2, "bound": o["E_sol_over_M"] < 3 and -1 < o["eps_val"] < 1}
def note(c, d):
    h = [x for x in c.get("SC_history", []) if x[1] is not None]
    return (f"profile {d['profile']} (SC converged {c.get('SC_converged')}, {len(h)} its, last max|dtheta| {h[-1][3]:.3g}, lowest E/M {min(x[1] for x in h):.6g}); " if h else f"profile {d['profile']}; ") + \
           f"E/M = {float(d['E']):.6g} (E_m/M {float(d['Em']):.4g}); g_A^(0) = {nstr(d['gA0'], 6)}, g_A^(1) = {nstr(d['gA1'], 6)}; mu_S = {nstr(d['muS'], 6)}, mu_V^(0) = {nstr(d['muV0'], 6)}, mu_V^(1) = {nstr(d['muV1'], 6)}"
V = {}; s = "VALIDATION"; ds = derive(san)
rec(s, "Q-1 sanity M = 420, m_pi = 140, F = 93: g_A in [1.1, 1.5]", "PASS" if 1.1 <= ds["gA"] <= 1.5 else "FAIL", "g_A = " + nstr(ds["gA"], 6) + "; " + note(san, ds))
rec(s, "Q-1 sanity: M_Delta - M_N in [200, 350] MeV", "PASS" if 200 <= ds["DN"] <= 350 else "FAIL", "Delta-N = " + nstr(ds["DN"], 6))
rec(s, "Q-1 sanity: mu_p in [1.6, 2.6], mu_n in [-2.0, -1.0]", "PASS" if (1.6 <= ds["mup"] <= 2.6 and -2.0 <= ds["mun"] <= -1.0) else "FAIL", f"mu_p = {nstr(ds['mup'], 6)}, mu_n = {nstr(ds['mun'], 6)} (literature 2.03, -1.41)")
if "Q1_validation" in H:
    cv = H["Q1_validation"]; dv = derive(cv)
    rec(s, "Q-1 validation soliton bound (E < N_c M)", "YES" if dv["bound"] else "NO", note(cv, dv))
    V["gA"] = emit(s, "Q-1 g_A", "PDG m_p/3, PDG m_pi+, M_PV from FLAG F_pi", dv["gA"], GA, sGA, "0.10", "", "tol 10 %")
    V["DN"] = emit(s, "Q-1 M_Delta - M_N", "same", dv["DN"], DN, "2", "0.15", "", "tol 15 %")
    V["mup"] = emit(s, "Q-1 mu_p", "same", dv["mup"], MUP, sMUP, "0.10", "", "tol 10 %")
    V["mun"] = emit(s, "Q-1 mu_n", "same", dv["mun"], MUN, sMUN, "0.10", "", "tol 10 %")
else:
    for k in ("gA", "DN", "mup", "mun"): V[k] = False
    rec(s, "Q-1 validation", "not run", "time box: the run was stopped before this case")
def vn(k): return "validation " + ("passed" if V[k] else "FAILED")
s = "FSOT"; c = H["Q1_FSOT"]; d = derive(c)
rec(s, "Q-1 soliton bound at M = m_p/3 with physical m_pi (E < N_c M)", "YES" if d["bound"] else "NO", note(c, d))
gok = emit(s, "Q-1 g_A = g_A^(0) + g_A^(1) (physical m_pi)", "M = m_p/3, M_PV = sqrt(e) M, m_pi = pi+- leaf, F = M sqrt3/(2 pi)", d["gA"], GA, sGA, "0.02", "FSOT", vn("gA")) and V["gA"]
emit(s, "Q-1 M_Delta - M_N (held-out)", "same", d["DN"], DN, "2", "0.15", "FSOT", vn("DN"))
emit(s, "Q-1 mu_p", "same, M_N = FSOT m_p", d["mup"], MUP, sMUP, "0.02", "FSOT", vn("mup"))
emit(s, "Q-1 mu_n", "same", d["mun"], MUN, sMUN, "0.02", "FSOT", vn("mun"))
info(s, "Q-1 soliton energy E/M incl. meson mass term", "same", d["E"], "FSOT", "threshold N_c = 3; N_c M = " + nstr(mp, 9) + " MeV")
rec("GATE", "downstream (deuteron rerun, KSRF/VMD -> Delta alpha_had -> Gamma_Z/M_Z)", "deferred to round r", f"frozen; g_A agrees within 2 % with passing validation: {gok}")
rec("GATE", "record rows of the 91", "unchanged", "no record row recomputed")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02q.py under audit/FREEZE_2026-10-02q (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("validations:", {k: ("PASS" if v else "FAIL") for k, v in V.items()})
