#!/usr/bin/env python3
"""Round-j branch scores under audit/FREEZE_2026-10-02j (committed first). Validations (PDG/FLAG inputs) are computed and written before
the FSOT-input numbers; the downstream (KSRF/VMD, deuteron) gate is evaluated exactly as frozen.

  python tools/score_2026_10_02j.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02j.tsv
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, sqrt, pi, ln, fabs, nstr
from mpmath import mp, zeta, quad, findroot, cbrt
mp.dps = 30
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves(); P = X.pins(); Z3 = zeta(3)
rows = []
def emit(sec, name, inputs, v, c, s, tol=None, note=""):
    z = fabs(v - c) / s; rel = (v - c) / c
    if tol is None: verdict = "PASS" if z <= 1 else "FAIL"
    elif tol[0] == "abs": verdict = "PASS" if fabs(v - c) <= tol[1] else "FAIL"
    else: verdict = "PASS" if fabs(rel) <= tol[1] else "FAIL"
    rows.append([sec, name, inputs, nstr(v, 12), nstr(c, 10), nstr(s, 4), nstr(z, 5), verdict, nstr(rel * 100, 5) + " %", note]); return verdict
def info(sec, name, inputs, v, note=""): rows.append([sec, name, inputs, nstr(v, 12), "-", "-", "-", "info", "-", note])
def rec(sec, name, verdict, note): rows.append([sec, name, "-", "-", "-", "-", "-", verdict, "-", note])

# ---------------- J-1 machinery: exact-integral MSbar Lambda with the 4-loop beta function
def bcoef(nf):
    b0 = (33 - 2 * nf) / (12 * pi); b1 = (153 - 19 * nf) / (24 * pi**2)
    b2 = (2857 - mpf(5033) / 9 * nf + mpf(325) / 27 * nf**2) / (128 * pi**3)
    b3 = ((mpf(149753) / 6 + 3564 * Z3) - (mpf(1078361) / 162 + mpf(6508) / 27 * Z3) * nf + (mpf(50065) / 162 + mpf(6472) / 81 * Z3) * nf**2
          + mpf(1093) / 729 * nf**3) / (256 * pi**4)
    return b0, b1, b2, b3
def lnmu2_over_L2(al, nf):
    b0, b1, b2, b3 = bcoef(nf)
    R = lambda x: -1 / (x**2 * (b0 + b1 * x + b2 * x**2 + b3 * x**3)) + 1 / (b0 * x**2) - b1 / (b0**2 * x)
    return 1 / (b0 * al) + b1 / b0**2 * ln(b0 * al) + quad(R, [0, al])
def Lam(al, mu, nf): return mu * mp.exp(-lnmu2_over_L2(al, nf) / 2)
def alpha_at(mu, Lm, nf):  # bisection (f decreasing in alpha on (0.05, 0.6)); 90 halvings
    lo, hi, t = mpf("0.05"), mpf("0.6"), 2 * ln(mu / Lm)
    for _ in range(90):
        m = (lo + hi) / 2
        if lnmu2_over_L2(m, nf) > t: lo = m
        else: hi = m
    return (lo + hi) / 2
def decouple(al, nl):  # alpha^(nl) from alpha^(nl+1) at mu = m(m), 3-loop (Chetyrkin-Kniehl-Steinhauser)
    x = al / pi; c3 = mpf(564731) / 124416 - mpf(82043) / 27648 * Z3 - mpf(2633) / 31104 * nl
    return al * (1 + mpf(11) / 72 * x**2 + c3 * x**3)
def lambdas(asMZ, MZ, mb, mc):
    L5 = Lam(asMZ, MZ, 5); a5b = alpha_at(mb, L5, 5); a4b = decouple(a5b, 4); L4 = Lam(a4b, mb, 4)
    a4c = alpha_at(mc, L4, 4); a3c = decouple(a4c, 3); L3 = Lam(a3c, mc, 3)
    return [x * 1000 for x in (L5, L4, L3)]
mb, mc = mpf("4.200"), mpf("1.280")
FL = [(mpf(213), mpf(8)), (mpf(295), mpf(10)), (mpf(338), mpf(10))]
# PDG/FLAG-side constants
mp_, mn_, mpi_ = mpf("938.27208943"), mpf("939.56542194"), mpf("139.57039"); mN = (mp_ + mn_) / 2
Fpi, sFpi = mpf("130.2") / sqrt(2), mpf("0.8") / sqrt(2); fpi, sfpi = mpf("130.2"), mpf("0.8")
gA, sgA = mpf("1.2754"), mpf("0.0013")
fc2, sfc2 = mpf("0.0769"), sqrt(mpf("0.0005")**2 + mpf("0.0009")**2)
gref = sqrt(4 * pi * fc2) * (mp_ + mn_) / mpi_; sgref = gref * sfc2 / (2 * fc2)
mud, Sig, sSig = mpf("3.427"), mpf(272), mpf(5)
V = {}
# ================= VALIDATIONS (PDG/FLAG inputs) =================
s = "VALIDATION"
v = lambdas(mpf("0.1183"), mpf("91.1880"), mb, mc)
V["J-1"] = all(emit(s, f"J-1 Lambda^({n}) from FLAG alpha_s 0.1183", "FLAG alpha_s, PDG M_Z, FLAG m_b(m_b), m_c(m_c)", v[i], FL[i][0], FL[i][1],
                    ("abs", FL[i][1]), "tolerance = FLAG sigma") == "PASS" for i, n in enumerate((5, 4, 3)))
V["J-2a"] = emit(s, "J-2a F_pi = m_N/(4 pi)", "PDG m_N", mN / (4 * pi), Fpi, sFpi, ("rel", mpf("0.05")), "tol 5 %") == "PASS"
V["J-2b"] = emit(s, "J-2b f_pi = m_N/(4 pi)", "PDG m_N", mN / (4 * pi), fpi, sfpi, ("rel", mpf("0.05")), "tol 5 %") == "PASS"
gA_a, gA_b = mpf(5) / 3, mpf(5) / 3 * mpf("0.6531")
V["J-3a"] = emit(s, "J-3a g_A = 5/3", "none", gA_a, gA, sgA, ("rel", mpf("0.05")), "tol 5 %") == "PASS"
V["J-3b"] = emit(s, "J-3b g_A = (5/3)(1-2 delta) MIT bag", "none", gA_b, gA, sgA, ("rel", mpf("0.05")), "tol 5 %") == "PASS"
V["J-4"] = emit(s, "J-4 GT g_piNN = g_A m_N / F_pi", "PDG g_A, PDG m_N, FLAG F_pi", gA * mN / Fpi, gref, sgref, ("rel", mpf("0.03")),
                "tol 3 %; ref from Reinert et al. f_c^2") == "PASS"
SigG = cbrt(Fpi**2 * mpi_**2 / (2 * mud))
V["J-5"] = emit(s, "J-5 GMOR Sigma^(1/3) = (F^2 m_pi^2 / 2 m_ud)^(1/3)", "FLAG F_pi, FLAG m_ud, PDG m_pi+-", SigG, Sig, sSig, ("rel", mpf("0.10")),
                "tol 10 %; ref FLAG 2019 N_f=2+1") == "PASS"
# ================= FSOT INPUTS =================
s = "FSOT"
asF = 2 * (F.POOF / F.PSI_CON) ** 2; MZF = L["m_Z_MeV"] / 1000
vF = lambdas(asF, MZF, mb, mc)
j1 = emit(s, "J-1 Lambda^(5) from FSOT alpha_s(M_Z)", "FSOT alpha_s seed, FSOT M_Z leaf", vF[0], FL[0][0], FL[0][1], None,
          "FSOT-native; agree iff J-1 validation passes and z <= 1")
for i, n in ((1, 4), (2, 3)):
    emit(s, f"J-1 Lambda^({n}) from FSOT alpha_s(M_Z)", "FSOT alpha_s, M_Z; FLAG m_b, m_c thresholds (external)", vF[i], FL[i][0], FL[i][1], None,
         "frozen-pending at best (external thresholds)")
mNF = (X.kg_to_GeV(L["m_p_kg"]) + X.kg_to_GeV(L["m_n_kg"])) * 500
FpiF = mNF / (4 * pi)
j2a = emit(s, "J-2a F_pi = m_N/(4 pi)", "FSOT m_p, m_n leaves", FpiF, Fpi, sFpi, ("rel", mpf("0.05")), "validation " + ("passed" if V["J-2a"] else "FAILED"))
j2b = emit(s, "J-2b f_pi = m_N/(4 pi)", "FSOT m_p, m_n leaves", FpiF, fpi, sfpi, ("rel", mpf("0.05")), "validation " + ("passed" if V["J-2b"] else "FAILED"))
emit(s, "J-3a g_A = 5/3", "none (no FSOT term)", gA_a, gA, sgA, ("rel", mpf("0.05")), "identical to validation")
emit(s, "J-3b g_A MIT bag", "none (no FSOT term)", gA_b, gA, sgA, ("rel", mpf("0.05")), "identical to validation")
FpiOK = (V["J-2a"] and j2a == "PASS") or (V["J-2b"] and j2b == "PASS"); gAOK = V["J-3a"] or V["J-3b"]
gF = gA_a * mNF / FpiF
if FpiOK and gAOK and V["J-4"]: emit(s, "J-4 GT g_piNN (FSOT)", "validated FSOT F_pi, g_A", gF, gref, sgref, ("rel", mpf("0.03")))
else:
    info(s, "J-4 GT g_piNN with J-2a F_pi and J-3a g_A (information)", "FSOT m_N; 5/3", gF, f"ref {nstr(gref,6)}; route does not close: "
         "no validated FSOT F_pi" + ("" if gAOK else " and no validated g_A"))
for tag, val, txt in (("a", mpf(250), "Sigma^(1/3) = 0.25 GeV (hub reference reading)"), ("b", X.kg_to_GeV(L["m_p_kg"]) * 250, "Sigma^(1/3) = m_p/4"),
                      ("c", X.kg_to_GeV(L["m_p_kg"]) * 1000 / cbrt(4), "Sigma = m_p^3/4")):
    rel = fabs(val - Sig) / Sig; z = fabs(val - Sig) / sSig
    verdict = "agree" if (V["J-5"] and z <= 1) else ("frozen-pending (within 10 %)" if rel <= mpf("0.10") else "fail")
    emit(s, f"J-5{tag} {txt}", "Quark_condensate pin 1/4" + ("" if tag == "a" else ", FSOT m_p"), val, Sig, sSig, ("rel", mpf("0.10")), verdict)
info(s, "J-5 mixed: F_pi from reading (a) + FLAG m_ud 3.427 (information)", "pin 1/4 (GeV), FSOT m_pi, FLAG m_ud",
     sqrt(2 * mud * mpf(250)**3) / L["m_pi_pm_MeV"], "not FSOT-native (needs an absolute m_ud)")
info(s, "J-5 mixed: m_ud from reading (a) + FLAG F_pi (information)", "pin 1/4 (GeV), FSOT m_pi, FLAG F_pi",
     Fpi**2 * L["m_pi_pm_MeV"]**2 / (2 * mpf(250)**3), "MeV; LO GMOR; not FSOT-native (needs F_pi); FLAG m_ud 3.427(51)")
s = "GATE"
gate = FpiOK and gAOK and V["J-4"]
rec(s, "downstream KSRF/VMD -> Delta alpha_had -> Gamma_Z/M_Z", "run" if gate else "NOT RUN",
    "frozen gate: needs validated FSOT-native F_pi and g_piNN" + ("" if gate else f" (F_pi ok={FpiOK}, g_A ok={gAOK}, GT validation={V['J-4']})"))
rec(s, "downstream deuteron (P_D, mu_n, MEC, binding)", "run" if gate else "NOT RUN", "same gate")
rec(s, "J-1 Lambda^(5) status", "agree (new FSOT-derived quantity, not a record row)" if (V["J-1"] and j1 == "PASS") else
    ("frozen-pending" if V["J-1"] else "validation failed"), "Lambda is not among the 91 rows")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02j.py under audit/FREEZE_2026-10-02j (committed first)\n"
            "#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tnote\n")
    for r in rows: o.write("\t".join(str(x) for x in r) + "\n")
print("validations:", {k: ("PASS" if v else "FAIL") for k, v in V.items()}, "gate:", gate)
