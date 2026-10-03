#!/usr/bin/env python3
"""Round-o scores under audit/FREEZE_2026-10-02o (committed first). Validations first; gates exactly as frozen.
O-1 and O-3 numbers come from audit/heavy_2026-10-02o.json (tools/heavy_2026_10_02o.py, numpy/scipy, run alone);
O-3b, O-4 and O-6 are computed here with mpmath.

  python tools/score_2026_10_02o.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02o.tsv
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, sqrt, pi, fabs, nstr
from mpmath import log
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves(); R = Path(__file__).resolve().parents[1]
H = json.loads((R / "audit/heavy_2026-10-02o.json").read_text(encoding="utf-8"))
rows = []
def emit(sec, name, inputs, v, c, s, tol, cls="", note=""):
    v, c, s, tol = mpf(v), mpf(c), mpf(s), mpf(tol)
    rel = (v - c) / c; verdict = "PASS" if fabs(rel) <= tol else "FAIL"
    rows.append([sec, name, inputs, nstr(v, 12), nstr(c, 10), nstr(s, 4), nstr(fabs(v - c) / s, 5), verdict, nstr(rel * 100, 5) + " %", cls, note]); return verdict == "PASS"
def info(sec, name, inputs, v, cls="", note=""): rows.append([sec, name, inputs, nstr(mpf(v), 12), "-", "-", "-", "info", "-", cls, note])
def rec(sec, name, verdict, note): rows.append([sec, name, "-", "-", "-", "-", "-", verdict, "-", "-", note])
Nc = 3
me = X.kg_to_GeV(L["m_e_kg"]) * 1000; mp = X.kg_to_GeV(L["m_p_kg"]) * 1000; Mpi = L["m_pi_pm_MeV"]
GA, sGA, DN = mpf("1.2754"), mpf("0.0013"), mpf("1232") - (mpf("938.27208943") + mpf("939.56542194")) / 2
def sol_note(r): return (f"r0 M = {r['x']:.6g}, E_sol/M = {r['E_sol_over_M']:.6g} (N_c = 3 threshold), eps_val/M = {r['eps_val']}, "
                         f"g_val = {r['gA0_val']:.6g}, g_sea = {r['gA0_sea']:.6g}, I M = {r['I_times_M']:.6g}, edge minimum {r['edge_minimum']}")
V = {}
# ---------------- VALIDATION
s = "VALIDATION"
rv = H["O1_validation"]
rec(s, "O-1 soliton bound (E < N_c M, interior minimum)", "YES" if rv["bound"] else "NO", sol_note(rv))
V["O-1 gA"] = emit(s, "O-1 g_A^(0) full-sea CQSM", "PDG m_p/3, M_PV from FLAG F_pi", rv["gA0"], GA, sGA, "0.10", "", "tol 10 %; leading order (no g_A^(1))") and rv["bound"]
V["O-1 DN"] = emit(s, "O-1 M_Delta - M_N = 3/(2I)", "same", rv["Delta_N_MeV"], DN, "2", "0.15", "", "tol 15 %") and rv["bound"]
rs = H["O1_sanity_M420_F93"]
inside = 0.7 <= rs["gA0"] <= 1.0
rec(s, "O-1 literature sanity M = 420, F = 93: g_A^(0) in [0.7, 1.0]", "PASS" if inside else "FAIL", f"g_A^(0) = {rs['gA0']:.6g}; Delta-N = {rs['Delta_N_MeV']:.6g} MeV; " + sol_note(rs))
d = H["O3_validation"]
if d["solved"]:
    V["O-3 r"] = emit(s, "O-3 deuteron r_d (OPE + core)", "g 13.17, PDG m_pi, m_N, B 2.224566", d["r_m"], "1.97507", "0.00078", "0.02", "", f"tol 2 %; C = {d['C_MeV']:.6g} MeV, P_D = {d['P_D']:.6g}")
    V["O-3 Q"] = emit(s, "O-3 deuteron Q_d", "same", d["Q_d"], "0.285699", "0.000015", "0.05", "", "tol 5 %")
    V["O-3 eta"] = emit(s, "O-3 deuteron eta = A_D/A_S", "same", d["eta"], "0.0256", "0.0004", "0.05", "", "tol 5 %")
else:
    V["O-3 r"] = V["O-3 Q"] = V["O-3 eta"] = False; rec(s, "O-3 deuteron", "no solution", str(d))
mpi_pdg, mp_pdg = mpf("139.57039"), mpf("938.27208943"); MPV2v = None
def lbar4(MQ, Mp): return 1 + log(MQ**2 / Mp**2)
def fpi(MQ, Mp):
    F0 = MQ * sqrt(Nc) / (2 * pi); lb = lbar4(MQ, Mp); return F0 * (1 + Mp**2 * lb / (16 * pi**2 * F0**2)), F0, lb
fv, F0v, lbv = fpi(mp_pdg / 3, mpi_pdg)
V["O-4"] = emit(s, "O-4 F_pi/F with lbar4 = ln(M_PV^2/M_pi^2)", "PDG m_p, M_pi+", fv / F0v, "1.062", "0.007", "0.02", "", "tol 2 %; lbar4 = " + nstr(lbv, 6))
# ---------------- FSOT
s = "FSOT"
r1 = H["O1_FSOT"]; rc = H["O1_FSOT_conv"]
rec(s, "O-1 soliton bound at M = m_p/3, M_PV = sqrt(e) M", "YES" if r1["bound"] else "NO", sol_note(r1))
gok = emit(s, "O-1 g_A^(0) full-sea CQSM (scan minimum)", "M = m_p/3, M_PV = sqrt(e) M, N_c = 3", r1["gA0"], GA, sGA, "0.02", "FSOT",
           "validation " + ("passed" if V["O-1 gA"] else "FAILED") + f"; bound {r1['bound']}; convergence run (D 14, k 14, K 14): g_A^(0) = {rc['gA0']:.6g}") and V["O-1 gA"] and r1["bound"]
emit(s, "O-1 M_Delta - M_N = 3/(2I) (held-out)", "same", r1["Delta_N_MeV"], DN, "2", "0.15", "FSOT", "validation " + ("passed" if V["O-1 DN"] else "FAILED") + f"; convergence run {rc['Delta_N_MeV']:.6g} MeV")
info(s, "O-1 soliton energy", "N_c eps_val + E_sea (PV)", r1["E_sol_over_M"] * mp / 3, "FSOT", f"MeV; N_c M = {nstr(mp, 9)}; convergence run E/M = {rc['E_sol_over_M']:.6g}")
rec("GATE", "O-2 KSRF/VMD -> Delta alpha_had -> Gamma_Z/M_Z", "RUN" if gok else "NOT RUN", f"frozen gate: O-1 g_A within 2 % with passing validation: {gok}")
d = H["O3_FSOT_primary"]; PD = None
if d["solved"]:
    PD = mpf(d["P_D"]); note = "validation " + ("passed" if V["O-3 r"] else "FAILED")
    emit(s, "O-3 deuteron r_d (held-out)", "FSOT g_piNN, pi+- leaf, m_N, B(2H) leaf, R = hbar c/M_Q", d["r_m"], "1.97507", "0.00078", "0.02", "FSOT", note + f"; C = {d['C_MeV']:.6g} MeV, R = {d['R']:.6g} fm")
    emit(s, "O-3 deuteron Q_d (held-out)", "same", d["Q_d"], "0.285699", "0.000015", "0.05", "FSOT", "validation " + ("passed" if V["O-3 Q"] else "FAILED"))
    emit(s, "O-3 deuteron eta (held-out)", "same", d["eta"], "0.0256", "0.0004", "0.05", "FSOT", "validation " + ("passed" if V["O-3 eta"] else "FAILED"))
    info(s, "O-3 deuteron P_D", "same", d["P_D"], "FSOT", "model-dependent (not an observable); used in mu_d")
    for t in ("half", "double"):
        dv = H["O3_FSOT_" + t]
        info(s, f"O-3 variant R {t}: r_d", "look-elsewhere variant", dv["r_m"] if dv["solved"] else 0, "FSOT", (f"Q_d = {dv['Q_d']:.6g}, eta = {dv['eta']:.6g}, P_D = {dv['P_D']:.6g}" if dv["solved"] else "no solution"))
else:
    rec(s, "O-3 deuteron", "no solution", str(d))
mup = L["mu_p_over_mu_N"]; mun = -mpf(2) / 3 * mup
emit(s, "O-3b mu_n = -(2/3) mu_p (SU(6))", "FSOT mu_p leaf", mun, "-1.91304276", "0.00000045", "0.02", "FSOT", "disclosed before freeze: about -2.7 %")
if PD is not None:
    muS = mup + mun
    emit(s, "O-3b mu_d = mu_S - (3/2)(mu_S - 1/2) P_D", "FSOT mu_p, SU(6) mu_n, O-3 P_D", muS - mpf(3) / 2 * (muS - mpf(1) / 2) * PD, "0.8574382335", "0.0000000022", "0.02", "FSOT", "record row Deuteron_mu")
    muSm = mpf("2.79284734463") + mpf("-1.91304276")
    info(s, "O-3b mu_d with CODATA mu_p, mu_n and O-3 P_D", "information", muSm - mpf(3) / 2 * (muSm - mpf(1) / 2) * PD, "", "isolates the P_D part")
F0, MQ = mp / 3 * sqrt(Nc) / (2 * pi), mp / 3
fF, _, lb = fpi(MQ, Mpi)
emit(s, "O-4 F_pi with lbar4 = 1 + ln(M_Q^2/M_pi^2)", "FSOT m_p, pi+- leaf", fF, mpf("130.2") / sqrt(2), mpf("0.8") / sqrt(2), "0.02", "FSOT", "validation " + ("passed" if V["O-4"] else "FAILED") + "; disclosed before freeze: about -2.3 %")
emit(s, "O-4 lbar4", "same", lb, "4.40", "0.28", "0.10", "FSOT", "FLAG 2+1 information")
rec("GATE", "O-5 chi_top / eta, eta'", "not built", "frozen: no FSOT instanton density without an external ratio")
c2 = mpf(299792458)**2; Eh = (1 / L["alpha_inv"])**2 * L["m_e_kg"] * c2
emit("O-6", "Atomic E_h = alpha^2 m_e c^2 (own physics)", "FSOT alpha_inv, m_e leaves", Eh, "4.3597447222060e-18", "0.0000000000048e-18", "0.000001", "FSOT", "gate z <= 1: z column; E_h leaf " + nstr(L["E_h"], 15))
rec("O-6", "Atomic own-physics z <= 1", "YES" if fabs(Eh - mpf("4.3597447222060e-18")) <= mpf("0.0000000000048e-18") else "NO", "rel to E_h leaf " + nstr((Eh - L["E_h"]) / L["E_h"], 5))
rec("O-6", "other domains", "no own-physics derivation", "Particle, HEP, Nuclear, Cosmology (frozen)")
rec("GATE", "record rows of the 91", "see notes", "Deuteron_mu is a record row; E_h already confirmed")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02o.py under audit/FREEZE_2026-10-02o (committed first)\n"
            "#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("validations:", {k: ("PASS" if v else "FAIL") for k, v in V.items()})
