#!/usr/bin/env python3
"""Round-n scores under audit/FREEZE_2026-10-02n (committed first). Validations first; gates exactly as frozen.

  python tools/score_2026_10_02n.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02n.tsv
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
import cqsm_valence as C
from fsot02d import mpf, sqrt, pi, fabs, nstr
from mpmath import log
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves(); R = Path(__file__).resolve().parents[1]
rows = []
def emit(sec, name, inputs, v, c, s, tol, cls="", note=""):
    rel = (v - c) / c; verdict = "PASS" if fabs(rel) <= tol else "FAIL"
    rows.append([sec, name, inputs, nstr(v, 12), nstr(c, 10), nstr(s, 4), nstr(fabs(v - c) / s, 5), verdict, nstr(rel * 100, 5) + " %", cls, note]); return verdict == "PASS"
def info(sec, name, inputs, v, cls="", note=""): rows.append([sec, name, inputs, nstr(v, 12), "-", "-", "-", "info", "-", cls, note])
def rec(sec, name, verdict, note): rows.append([sec, name, "-", "-", "-", "-", "-", verdict, "-", "-", note])
def r9(v): return mpf(float("%.9g" % v))
def tk(key):
    for line in open(R / "audit/trace_2026-10-02k.tsv", encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) > 3 and f[2].startswith(key): return mpf(f[3])
Nc = 3
me = X.kg_to_GeV(L["m_e_kg"]) * 1000; mp = X.kg_to_GeV(L["m_p_kg"]) * 1000; mn = X.kg_to_GeV(L["m_n_kg"]) * 1000
mp_pdg, mpi_pdg = mpf("938.27208943"), mpf("139.57039")
Fpi, sF = mpf("130.2") / sqrt(2), mpf("0.8") / sqrt(2)
def lbar4(MQ, Mpi, form): return Nc + (log(4 * MQ**2 / Mpi**2) if form == "a" else 0)
def fpi(MQ, Mpi, form):
    F0 = MQ * sqrt(Nc) / (2 * pi); lb = lbar4(MQ, Mpi, form)
    return F0 * (1 + Mpi**2 * lb / (16 * pi**2 * F0**2)), F0, lb
V = {}; s = "VALIDATION"
for form in ("a", "b"):
    fv, F0v, lbv = fpi(mp_pdg / 3, mpi_pdg, form)
    V["N-1" + form] = emit(s, f"N-1{form} F_pi/F", "PDG m_p, M_pi+", fv / F0v, mpf("1.062"), mpf("0.007"), mpf("0.02"), "", "tol 2 %; lbar4 = " + nstr(lbv, 6))
solv = C.soliton(float(mp_pdg / 3), float(Fpi), Nc)
if solv["bound"]:
    V["N-2"] = emit(s, "N-2 g_A valence chiral quark soliton", "PDG m_p/3, FLAG F_pi", r9(solv["g_A"]), mpf("1.2754"), mpf("0.0013"), mpf("0.10"), "", f"tol 10 %; r0 M = {solv['x']:.6f}, E_val/M = {solv['E_val']:.6f}, E_sol = {solv['E_sol']:.4f} MeV")
else:
    V["N-2"] = False; rec(s, "N-2 g_A", "no soliton", f"no interior minimum (edge x = {solv['x']})")
gam_v = sqrt((mp_pdg + mpf("939.56542194")) / 2 * mpf("2.224566")) / mpf("197.3269804")
V["N-3d"] = emit(s, "N-3 deuteron LO r_d = 1/(sqrt8 gamma)", "PDG m_N, AME2020 B(2H)", 1 / (sqrt(8) * gam_v), mpf("1.97507"), mpf("0.00078"), mpf("0.02"), "", "tol 2 %")
s = "FSOT"; Mpi = L["m_pi_pm_MeV"]; MQ = mp / 3
FF = {}
for form in ("a", "b"):
    fv, F0, lb = fpi(MQ, Mpi, form); FF[form] = fv
    ok = emit(s, f"N-1{form} F_pi (/m_e = {nstr(fv / me, 9)})", "FSOT m_p, pi+- leaf, N_c = 3", fv, Fpi, sF, mpf("0.02"), "FSOT", "validation " + ("passed" if V["N-1" + form] else "FAILED"))
    FF[form + "ok"] = ok and V["N-1" + form]
    emit(s, f"N-1{form} lbar4", "same", lb, mpf("4.40"), mpf("0.28"), mpf("0.10"), "FSOT", "FLAG 2+1 information")
F3 = mp / (2 * sqrt(3) * pi)
sol = C.soliton(float(MQ), float(F3), Nc)
gok = False
if sol["bound"]:
    gA = r9(sol["g_A"])
    gok = emit(s, "N-2 g_A valence chiral quark soliton", "M = m_p/3, F = m_p/(2 sqrt3 pi), N_c = 3", gA, mpf("1.2754"), mpf("0.0013"), mpf("0.02"), "FSOT",
               "validation " + ("passed" if V["N-2"] else "FAILED") + f"; r0 M = {sol['x']:.6f}, E_val/M = {sol['E_val']:.6f}, axial ratio {sol['axial']:.6f}") and V["N-2"]
    info(s, "N-2 soliton mass", "N_c E_val + E_sea", r9(sol["E_sol"]), "FSOT", "MeV (gradient-order sea; information, no rotational/CM corrections)")
    gpiNN = gA * (mp + mn) / 2 / FF["b"]
    info(s, "N-2 GT g_piNN = g_A m_N/F_pi (N-1b F_pi)", "FSOT-only chain", gpiNN, "FSOT", "ref 13.17(5) (f^2 = 0.0769)")
else:
    rec(s, "N-2 g_A", "no soliton", f"no interior minimum (edge x = {sol['x']})")
gam = sqrt((mp + mn) / 2 * tk("B(2H)")) / mpf("197.3269804")
emit(s, "N-3 deuteron LO r_d (FSOT B(2H) leaf)", "FSOT m_N, B(2H)", 1 / (sqrt(8) * gam), mpf("1.97507"), mpf("0.00078"), mpf("0.02"), "FSOT", "validation " + ("passed" if V["N-3d"] else "FAILED") + "; LO misses the effective-range factor")
rec(s, "N-3 mu_d", "not computable", "no FSOT mu_n leaf")
fok = FF["aok"] or FF["bok"]
if fok and gok:
    fsel = FF["a"] if FF["aok"] else FF["b"]
    emit("GATE", "N-3 LMD m_rho = 2 sqrt2 pi F_pi", "FSOT F_pi", 2 * sqrt(2) * pi * fsel, mpf("775.26"), mpf("0.23"), mpf("0.01"), "FSOT", "frozen 1 % gate for Delta alpha_had")
    rec("GATE", "Delta alpha_had -> Gamma_Z/M_Z", "NOT RUN" if fabs(2 * sqrt(2) * pi * fsel / mpf("775.26") - 1) > mpf("0.01") else "RUN", "frozen gate")
else:
    rec("GATE", "KSRF/VMD -> Delta alpha_had -> Gamma_Z/M_Z", "NOT RUN", f"frozen gate: F_pi agree {fok}, g_A agree {gok}")
    info("GATE", "information: LMD m_rho with N-1b F_pi", "not a gate input", 2 * sqrt(2) * pi * FF["b"], "FSOT", "PDG 775.26(23)")
# N-5
s = "N-5"; c2 = mpf(299792458)**2
refs = {"PP": (Mpi / me, mpf("139.57039") / me, 5, F.domain_scalar("Particle_Physics")),
        "HEP": (L["m_W_MeV"] / me, mpf("80369.2") / me, 6, F.domain_scalar("High_Energy_Physics")),
        "NUC": (tk("B(2H)") / me, mpf("2.224566") / me, 12, F.domain_scalar("Nuclear_Physics")),
        "ATOM": (L["E_h"] / (L["m_e_kg"] * c2), mpf("4.3597447222060e-18") / (mpf("9.1093837015e-31") * c2), 6, F.domain_scalar("Atomic_Physics"))}
for k_, v in refs.items(): info(s, f"reference ratio {k_} (D_eff {v[2]}, S {nstr(v[3], 8)})", "leaf / m_e", v[0], "FSOT", "measured " + nstr(v[1], 10))
y1, y2 = log(refs["PP"][0]), log(refs["NUC"][0]); b1 = (y2 - y1) / 7; a1 = y1 - 5 * b1
k1 = 0
for k_ in ("HEP", "ATOM"):
    k1 += emit(s, f"P1 held-out {k_}", "ln r = a + b D_eff (pi, 2H)", mpf(2.718281828459045235360287)**(a1 + b1 * refs[k_][2]), refs[k_][1], refs[k_][1] * mpf("1e-6"), mpf("0.02"), "FSOT map", "ratio to m_e")
rec(s, "P1 map", "YES" if k1 == 2 else "NO", f"{k1}/2 within 2 %")
from mpmath import matrix, lu_solve
A = matrix([[1, refs[k_][2], refs[k_][3]] for k_ in ("PP", "HEP", "NUC")]); yv = matrix([log(refs[k_][0]) for k_ in ("PP", "HEP", "NUC")])
cf = lu_solve(A, yv); pr = mpf(2.718281828459045235360287)**(cf[0] + cf[1] * 6 + cf[2] * refs["ATOM"][3])
k2 = emit(s, "P2 held-out ATOM", "ln r = a + b D_eff + c S (pi, W, 2H)", pr, refs["ATOM"][1], refs["ATOM"][1] * mpf("1e-6"), mpf("0.02"), "FSOT map", f"a, b, c = {nstr(cf[0], 8)}, {nstr(cf[1], 8)}, {nstr(cf[2], 8)}")
rec(s, "P2 map", "YES" if k2 else "NO", f"{int(k2)}/1 within 2 %")
rec("GATE", "N-4 eta/eta'", "not built", "no physically grounded FSOT chi_top (frozen)")
rec("GATE", "record rows of the 91", "unchanged", "no round-n quantity is a record row")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02n.py under audit/FREEZE_2026-10-02n (committed first)\n"
            "#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("validations:", {k: ("PASS" if v else "FAIL") for k, v in V.items()})
