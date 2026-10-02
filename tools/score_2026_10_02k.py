#!/usr/bin/env python3
"""Round-k branch scores under audit/FREEZE_2026-10-02k (committed first). Validations first; gates exactly as frozen. Lambda values are read
from audit/score_2026-10-02j.tsv (round-j J-1, validated method), both the FLAG-alpha_s validation values and the FSOT values.

  python tools/score_2026_10_02k.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02k.tsv
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, sqrt, pi, fabs, nstr
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves(); P = X.pins(); R = Path(__file__).resolve().parents[1]
rows = []
def emit(sec, name, inputs, v, c, s, tol, cls="", note=""):
    rel = (v - c) / c; verdict = "PASS" if fabs(rel) <= tol else "FAIL"
    rows.append([sec, name, inputs, nstr(v, 12), nstr(c, 10), nstr(s, 4), nstr(fabs(v - c) / s, 5), verdict, nstr(rel * 100, 5) + " %", cls, note]); return verdict == "PASS"
def info(sec, name, inputs, v, cls="", note=""): rows.append([sec, name, inputs, nstr(v, 12), "-", "-", "-", "info", "-", cls, note])
def rec(sec, name, verdict, note): rows.append([sec, name, "-", "-", "-", "-", "-", verdict, "-", "-", note])
Lv, Lf = {}, {}
for line in open(R / "audit/score_2026-10-02j.tsv", encoding="utf-8"):
    f = line.rstrip("\n").split("\t")
    if len(f) > 3 and f[0] in ("VALIDATION", "FSOT") and f[1].startswith("J-1 Lambda^("): (Lv if f[0] == "VALIDATION" else Lf)[f[1][12]] = mpf(f[3])
Fpi, sF = mpf("130.2") / sqrt(2), mpf("0.8") / sqrt(2)
r3, r5 = Fpi / 338, Fpi / 213
gAlat, gApdg = mpf("1.263"), mpf("1.2754")
mp_, mn_, mpi_ = mpf("938.27208943"), mpf("939.56542194"), mpf("139.57039"); mN = (mp_ + mn_) / 2
fc2, sfc2 = mpf("0.0769"), sqrt(mpf("0.0005")**2 + mpf("0.0009")**2)
gref = sqrt(4 * pi * fc2) * (mp_ + mn_) / mpi_; sg = gref * sfc2 / (2 * fc2)
Sig, mud_ref, smud = mpf(272), mpf("3.387"), mpf("0.039"); sigr = Sig / 338
mrho, smrho = mpf("775.26"), mpf("0.23"); lmd = sqrt(24 * pi**2 / 3)
V = {}
s = "VALIDATION"
V["K-1a"] = emit(s, "K-1a F_pi = (F/Lambda3)_lat x Lambda3", "J-1 Lambda3 from FLAG alpha_s; ratio 0.27239", r3 * Lv["3"], Fpi, sF, mpf("0.035"), "", "tol 3.5 %; weak (ratio from FLAG)")
V["K-1b"] = emit(s, "K-1b F_pi = (F/Lambda5)_lat x Lambda5", "J-1 Lambda5 from FLAG alpha_s; ratio 0.43225", r5 * Lv["5"], Fpi, sF, mpf("0.04"), "", "tol 4 %; weak")
V["K-2"] = emit(s, "K-2 Skyrme F_pi (ANW 1983, literature)", "m_N, m_Delta fit", mpf("64.5"), Fpi, sF, mpf("0.10"), "", "tol 10 %")
V["K-2g"] = emit(s, "K-2 Skyrme g_A (ANW 1983, literature)", "m_N, m_Delta fit", mpf("0.61"), gApdg, mpf("0.0013"), mpf("0.10"), "", "tol 10 %")
V["K-3"] = emit(s, "K-3 g_A lattice (FLAG 2+1+1)", "FLAG", gAlat, gApdg, mpf("0.0013"), mpf("0.02"), "", "tol 2 %")
V["K-4"] = emit(s, "K-4 GT g_piNN", "FLAG g_A, PDG m_N, FLAG F_pi", gAlat * mN / Fpi, gref, sg, mpf("0.03"), "", "tol 3 %")
V["K-5"] = emit(s, "K-5 GMOR m_ud = F^2 m_pi^2/(2 Sigma)", "FLAG F_pi, FLAG 2019 Sigma, PDG m_pi", Fpi**2 * mpi_**2 / (2 * Sig**3), mud_ref, smud, mpf("0.10"), "", "tol 10 %")
s = "FSOT"
mNF = (X.kg_to_GeV(L["m_p_kg"]) + X.kg_to_GeV(L["m_n_kg"])) * 500; mpiF = L["m_pi_pm_MeV"]
F1a = r3 * Lf["3"]; F1b = r5 * Lf["5"]
k1a = emit(s, "K-1a F_pi", "FSOT Lambda3 (ext. thresholds) x lattice ratio", F1a, Fpi, sF, mpf("0.035"), "HYBRID", "validation " + ("passed" if V["K-1a"] else "FAILED"))
k1b = emit(s, "K-1b F_pi", "FSOT Lambda5 x lattice ratio", F1b, Fpi, sF, mpf("0.04"), "HYBRID", "validation " + ("passed" if V["K-1b"] else "FAILED"))
rec(s, "K-2 Skyrme", "not computable", "needs m_Delta (absent in FSOT); validation failed")
info(s, "K-3 g_A", "none (lattice)", gAlat, "EXTERNAL", "no FSOT input")
g4 = gAlat * mNF / F1a
k4 = emit(s, "K-4 GT g_piNN", "lattice g_A, FSOT m_N, K-1a F_pi", g4, gref, sg, mpf("0.03"), "HYBRID", "validation " + ("passed" if V["K-4"] else "FAILED"))
for tag, S3, txt in (("a", sigr * Lf["3"], "Sigma^1/3 = (272/338) x FSOT Lambda3"), ("b", mpf(250), "Sigma^1/3 = 0.25 GeV (pin 1/4)")):
    mud = F1a**2 * mpiF**2 / (2 * S3**3)
    emit(s, f"K-5{tag} m_ud ({txt})", "K-1a F_pi, FSOT m_pi", mud, mud_ref, smud, mpf("0.10"), "HYBRID", "validation " + ("passed" if V["K-5"] else "FAILED"))
    info(s, f"K-5{tag} m_s = FSOT m_s/m_ud x m_ud", "FSOT ratios", P["wave7|m_s/m_d"] * 2 / (1 + P["wave7|m_u/m_d"]) * mud, "HYBRID", "MeV; FLAG 2+1 92.4(1.0); information")
s = "GATE"
g1 = V["K-1a"] and k1a
if g1:
    vD1 = emit("VALIDATION", "D-1 LMD m_rho = sqrt(24 pi^2/N_c) F_pi", "FLAG F_pi", lmd * Fpi, mrho, smrho, mpf("0.01"), "", "tol 1 % (Delta alpha_had accuracy)")
    emit("FSOT", "D-1 LMD m_rho", "K-1a F_pi", lmd * F1a, mrho, smrho, mpf("0.01"), "HYBRID", "validation " + ("passed" if vD1 else "FAILED"))
    rec(s, "VMD Delta alpha_had -> Gamma_Z/M_Z", "run" if vD1 else "NOT RUN", "frozen gate: D-1 validation must pass" + ("" if vD1 else " (it failed)"))
else:
    rec(s, "D-1 m_rho", "NOT RUN", "K-1a did not validate/score"); rec(s, "VMD Delta alpha_had -> Gamma_Z/M_Z", "NOT RUN", "gate")
rec(s, "deuteron (binding, P_D, mu_n, MEC)", "NOT RUN", "frozen precision gate: rows need 2e-7 / 2.6e-9 relative; chiral EFT uses B_d as input, mu_d ~1e-3, P_D not observable, mu_n needs c6")
rec(s, "record rows of the 91", "unchanged", "every round-k result is HYBRID or EXTERNAL or failed validation")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02k.py under audit/FREEZE_2026-10-02k (committed first)\n"
            "#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x) for x in r_) + "\n")
print("validations:", {k: ("PASS" if v else "FAIL") for k, v in V.items()})
