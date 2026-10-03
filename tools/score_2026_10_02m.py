#!/usr/bin/env python3
"""Round-m scores under audit/FREEZE_2026-10-02m (committed first). Validations first; gates exactly as frozen.

  python tools/score_2026_10_02m.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02m.tsv
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, sqrt, pi, fabs, nstr
from mpmath import log, matrix, eigsy, atan
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves(); P = X.pins(); R = Path(__file__).resolve().parents[1]
rows = []
def emit(sec, name, inputs, v, c, s, tol, cls="", note=""):
    rel = (v - c) / c; verdict = "PASS" if fabs(rel) <= tol else "FAIL"
    rows.append([sec, name, inputs, nstr(v, 12), nstr(c, 10), nstr(s, 4), nstr(fabs(v - c) / s, 5), verdict, nstr(rel * 100, 5) + " %", cls, note]); return verdict == "PASS"
def info(sec, name, inputs, v, cls="", note=""): rows.append([sec, name, inputs, nstr(v, 12), "-", "-", "-", "info", "-", cls, note])
def rec(sec, name, verdict, note): rows.append([sec, name, "-", "-", "-", "-", "-", verdict, "-", "-", note])
def tk(key):
    for line in open(R / "audit/trace_2026-10-02k.tsv", encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) > 3 and f[2].startswith(key): return mpf(f[3])
F1a = None
for line in open(R / "audit/score_2026-10-02k.tsv", encoding="utf-8"):
    f = line.rstrip("\n").split("\t")
    if len(f) > 3 and f[0] == "FSOT" and f[1] == "K-1a F_pi": F1a = mpf(f[3])
me = X.kg_to_GeV(L["m_e_kg"]) * 1000; mp = X.kg_to_GeV(L["m_p_kg"]) * 1000; alpha = 1 / L["alpha_inv"]
x, y = P["wave7|m_u/m_d"], P["wave7|m_s/m_d"]
mud = (1 + x) / 2; Qf = sqrt((y**2 - mud**2) / (1 - x**2))
ref = {"pi0": (mpf("134.9768"), mpf("0.0005")), "K0": (mpf("497.611"), mpf("0.013")), "eta": (mpf("547.862"), mpf("0.017")), "etap": (mpf("957.78"), mpf("0.06"))}
Fpdg, sF = mpf("130.2") / sqrt(2), mpf("0.8") / sqrt(2); chi = mpf(191)**4
def dgmly(Fv, al): return 12 * pi * al * log(2) * Fv**2
def kaon(MKp, Dpi, eps, Mpi0, Q):
    DK = (1 + eps) * Dpi; split = mpf(0)
    for _ in range(60):
        MhK2 = MKp**2 - DK + split / 2; split = MhK2 * (MhK2 - Mpi0**2) / (Q**2 * Mpi0**2)
    return sqrt(MKp**2 - DK + split), MhK2
def u3(Mpi0, MhK2, Fv):
    Bm = Mpi0**2 / 2; Bs = MhK2 - Bm; M0 = 6 * chi / Fv**2
    M = matrix([[(2 * (Bm + 2 * Bs)) / 3, -(2 * sqrt(2) / 3) * (Bs - Bm)], [-(2 * sqrt(2) / 3) * (Bs - Bm), (2 * (2 * Bm + Bs)) / 3 + M0]])
    E, Q_ = eigsy(M); return sqrt(E[0]), sqrt(E[1]), atan(Q_[1, 0] / Q_[0, 0]) * 180 / pi
V = {}
# ---------- validation
s = "VALIDATION"; Mpi_p, MK_p = mpf("139.57039"), mpf("493.677")
Dv = dgmly(Fpdg, 1 / mpf("137.035999084")); p0v = sqrt(Mpi_p**2 - Dv)
V["M-2a"] = emit(s, "M-2a M_pi0 = sqrt(M_pi+^2 - 12 pi alpha ln2 F^2)", "PDG M_pi+, FLAG F_pi, CODATA alpha", p0v, *ref["pi0"], mpf("0.02"), "", "tol 2 %; Delta_pi = " + nstr(Dv, 6) + " MeV^2 (physical 1261)")
k0v, MhK2v = kaon(MK_p, Dv, 0, p0v, mpf("22.5"))
V["M-2b"] = emit(s, "M-2b M_K0 (Q route, eps = 0)", "PDG M_K+, FLAG Q 22.5, M-2a", k0v, *ref["K0"], mpf("0.02"), "", "tol 2 %")
e1, e2, th = u3(p0v, MhK2v, Fpdg)
V["M-2c eta"] = emit(s, "M-2c M_eta (U(3) + Witten-Veneziano)", "validation chain, chi^1/4 191", e1, *ref["eta"], mpf("0.05"), "", "tol 5 %; theta = " + nstr(th, 5) + " deg")
V["M-2c etap"] = emit(s, "M-2c M_eta'", "same", e2, *ref["etap"], mpf("0.05"), "", "tol 5 %")
V["M-3a"] = emit(s, "M-3a F = m_p/(2 sqrt3 pi)", "PDG m_p", mpf("938.27208943") / (2 * sqrt(3) * pi), Fpdg, sF, mpf("0.10"), "", "tol 10 %")
# ---------- FSOT
s = "FSOT"; Mpi, MK = L["m_pi_pm_MeV"], L["m_K_pm_MeV"]
F3 = mp / (2 * sqrt(3) * pi)
emit(s, "M-3a F = m_p/(2 sqrt3 pi) vs physical F_pi", "FSOT m_p (anchored), N_c = 3", F3, Fpdg, sF, mpf("0.10"), "FSOT", "validation " + ("passed" if V["M-3a"] else "FAILED") + "; F/m_e = " + nstr(F3 / me, 9))
F0 = Fpdg / mpf("1.062")
emit(s, "M-3a F vs chiral-limit F_0 = F_pi/1.062", "same", F3, F0, F0 * sqrt((sF / Fpdg)**2 + (mpf("0.007") / mpf("1.062"))**2), mpf("0.10"), "FSOT (comparison HYBRID)", "quark-level sigma model is a chiral-limit relation")
rec(s, "M-3b g_A", "no FSOT form", "lattice 1.263 retained (EXTERNAL)")
info(s, "M-3c g_piNN = g_A m_N/F (M-3a F, lattice g_A)", "HYBRID", mpf("1.263") * (X.kg_to_GeV(L["m_p_kg"]) + X.kg_to_GeV(L["m_n_kg"])) * 500 / F3, "HYBRID", "ref 13.17")
for tag, Fv, cls in (("K-1a F", F1a, "HYBRID"), ("M-3a F", F3, "FSOT")):
    D = dgmly(Fv, alpha); p0 = sqrt(Mpi**2 - D)
    emit(s, f"M-2a M_pi0 HELD-OUT ({tag}; /m_e = {nstr(p0 / me, 9)})", "FSOT alpha, M_pi+ leaf", p0, *ref["pi0"], mpf("0.02"), cls, "validation " + ("passed" if V["M-2a"] else "FAILED") + "; Delta_pi = " + nstr(D, 6))
    for eps, ecls in ((0, cls), (mpf("0.79"), "HYBRID")):
        k0, MhK2 = kaon(MK, D, eps, p0, Qf)
        emit(s, f"M-2b M_K0 HELD-OUT ({tag}, eps = {eps})", "FSOT Q " + nstr(Qf, 7) + ", M_K+ leaf", k0, *ref["K0"], mpf("0.02"), ecls, "validation " + ("passed" if V["M-2b"] else "FAILED"))
        if eps == 0:
            e1, e2, th = u3(p0, MhK2, Fv)
            emit(s, f"M-2c M_eta HELD-OUT ({tag})", "M-2a/b, chi lattice", e1, *ref["eta"], mpf("0.05"), "HYBRID", "validation " + ("passed" if V["M-2c eta"] else "FAILED") + "; theta = " + nstr(th, 5) + " deg")
            emit(s, f"M-2c M_eta' HELD-OUT ({tag})", "same", e2, *ref["etap"], mpf("0.05"), "HYBRID", "validation " + ("passed" if V["M-2c etap"] else "FAILED"))
# ---------- M-1
s = "M-1"; G = 1 / me
rec(s, "definition note", "corrected", "FREEZE_2026-10-02m writes r = leaf / 1.956952 but defines r as the pure m_e multiple; the m_e multiple is leaf x 1.956952 (= leaf/m_e[MeV]); scored with the m_e multiple; fit slopes b are identical under either reading (constant shift of ln r); 0/6 under both")
Dm = {"PP": (5, F.domain_scalar("Particle_Physics")), "HEP": (6, F.domain_scalar("High_Energy_Physics")), "NUC": (12, F.domain_scalar("Nuclear_Physics"))}
ML = [("m_pi+-", Mpi, "PP", mpf("139.57039"), mpf("0.00018"), "train"), ("m_W", L["m_W_MeV"], "HEP", mpf("80369.2"), mpf("13.3"), "train"),
      ("B(2H)", tk("B(2H)"), "NUC", mpf("2.224566"), mpf("1e-6"), "train"), ("m_K+-", MK, "PP", mpf("493.677"), mpf("0.015"), "held"),
      ("m_D+-", L["m_D_pm_MeV"], "PP", mpf("1869.66"), mpf("0.05"), "held"), ("m_Z", L["m_Z_MeV"], "HEP", mpf("91187.6"), mpf("2.1"), "held"),
      ("m_H", L["m_H_MeV"], "HEP", mpf("125200"), mpf("110"), "held"), ("B(3H)", L["B_H3_MeV"], "NUC", mpf("8.481798"), mpf("1e-6"), "held"),
      ("B(4He)", L["B_He4_MeV"], "NUC", mpf("28.295674"), mpf("1e-6"), "held")]
for l_ in ML: info(s, f"r({l_[0]}) = leaf x 1.956952 [m_e units]", l_[2] + " D_eff " + str(Dm[l_[2]][0]), l_[1] * G, "FSOT", "measured/m_e = " + nstr(l_[3] / me, 10))
info(s, "HEP: r_Z/r_W vs 1/(m_W/m_Z leaf)", "internal", (L["m_Z_MeV"] / L["m_W_MeV"]) * L["m_W_over_m_Z"], "FSOT", "1 = the Z leaf is the W leaf over the W/Z ratio")
info(s, "NUC: r(3H)/r(2H)", "leaves", L["B_H3_MeV"] / tk("B(2H)"), "FSOT", "measured 3.81284")
info(s, "NUC: r(4He)/r(3H)", "leaves", L["B_He4_MeV"] / L["B_H3_MeV"], "FSOT", "measured 3.33601")
emit(s, "Tjon LO unitary ratio: B(4He) = 4.61 B(3H leaf)", "B(3H) leaf", mpf("4.61") * L["B_H3_MeV"], mpf("28.295674"), mpf("1e-6"), mpf("0.02"), "FSOT", "AME2020")
fams = {"R1": lambda d: mpf(Dm[d][0]), "R2": lambda d: log(mpf(Dm[d][0])), "R3": lambda d: Dm[d][1]}
for fn, u in fams.items():
    tr = [l_ for l_ in ML if l_[5] == "train"]; n = len(tr)
    xs = [u(l_[2]) for l_ in tr]; ys = [log(l_[1] * G) for l_ in tr]
    Sx, Sy, Sxx, Sxy = sum(xs), sum(ys), sum(v * v for v in xs), sum(p * q for p, q in zip(xs, ys))
    bb = (n * Sxy - Sx * Sy) / (n * Sxx - Sx**2); aa = (Sy - bb * Sx) / n
    info(s, f"{fn} fit ln r = a + b u (a)", "training pi, W, B(2H)", aa, "FSOT map", "b = " + nstr(bb, 10))
    k = 0
    for l_ in ML:
        if l_[5] == "held": k += emit(s, f"{fn} held-out {l_[0]}", "m_e x exp(a + b u)", me * mpf(2.718281828459045235360287)**(aa + bb * u(l_[2])), l_[3], l_[4], mpf("0.02"), "FSOT map", "")
    rec(s, f"{fn} D_eff/S organizes the ratios", "YES" if k == 6 else "NO", f"{k}/6 held-out within 2 %")
rec("GATE", "KSRF/VMD -> Delta alpha_had -> Gamma_Z/M_Z; deuteron", "NOT RUN", "frozen gate: g_A has no FSOT form (and F must validate within 2 %)")
rec("GATE", "record rows of the 91", "unchanged", "no round-m quantity is a record row")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02m.py under audit/FREEZE_2026-10-02m (committed first)\n"
            "#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("validations:", {k: ("PASS" if v else "FAIL") for k, v in V.items()})
