#!/usr/bin/env python3
"""Round-l scores under audit/FREEZE_2026-10-02l (committed first). Validations first; gates exactly as frozen.
Also writes the frozen restatement table audit/derive_2026-10-02l.tsv (every unit-read leaf as a ratio to its natural anchor).

  python tools/score_2026_10_02l.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02l.tsv
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
F1a = None
for line in open(R / "audit/score_2026-10-02k.tsv", encoding="utf-8"):
    f = line.rstrip("\n").split("\t")
    if len(f) > 3 and f[0] == "FSOT" and f[1] == "K-1a F_pi": F1a = mpf(f[3])
Lf = {}
for line in open(R / "audit/score_2026-10-02j.tsv", encoding="utf-8"):
    f = line.rstrip("\n").split("\t")
    if len(f) > 3 and f[0] == "FSOT" and f[1].startswith("J-1 Lambda^("): Lf[f[1][12]] = mpf(f[3])
me = X.kg_to_GeV(L["m_e_kg"]) * 1000; mp = X.kg_to_GeV(L["m_p_kg"]) * 1000
x, y = P["wave7|m_u/m_d"], P["wave7|m_s/m_d"]
def octet(Mpi, MK, x, y):
    b = (MK**2 - Mpi**2) / (y - 1); D = Mpi**2 - b * (1 + x)
    return b, D, sqrt(b * (1 + x)), sqrt(b * (1 + y)), sqrt(b * (x + 1 + 4 * y) / 3)
ref = {"pi0": (mpf("134.9768"), mpf("0.0005")), "K0": (mpf("497.611"), mpf("0.013")), "eta": (mpf("547.862"), mpf("0.017"))}
V = {}
# ---- validation (PDG charged masses, FLAG 2+1 ratios)
xv = mpf("0.485"); yv = mpf("27.42") * (1 + xv) / 2
bv, Dv, p0, k0, et = octet(mpf("139.57039"), mpf("493.677"), xv, yv)
s = "VALIDATION"
for n, v in (("pi0", p0), ("K0", k0), ("eta", et)):
    V["L-A1 " + n] = emit(s, f"L-A1 M_{n} (LO ChPT + Dashen)", "PDG M_pi+, M_K+; FLAG 2+1 m_u/m_d 0.485, m_s/m_ud 27.42", v, *ref[n], mpf("0.02"), "", "tol 2 %")
info(s, "L-A1 D_EM [MeV^2]", "same", Dv, "", "physical pi+-pi0 EM shift M_pi+^2 - M_pi0^2 = 1261 MeV^2")
Fv, Sv = mpf("130.2") / sqrt(2), mpf(272)
V["L-B1"] = emit(s, "L-B1 m_ud = b F^2/Sigma (1+x)/2", "validation b; FLAG F_pi 92.07; FLAG 2019 Sigma^1/3 272", bv * Fv**2 / Sv**3 * (1 + xv) / 2, mpf("3.387"), mpf("0.039"), mpf("0.10"), "", "tol 10 %")
# ---- FSOT
s = "FSOT"; Mpi, MK = L["m_pi_pm_MeV"], L["m_K_pm_MeV"]
info(s, "L-A1 restated input M_pi+/m_e", "seed leaf / anchor", Mpi / me, "FSOT", "pi+- leaf as a ratio to the m_e anchor")
info(s, "L-A1 restated input M_K+/m_e", "seed leaf / anchor", MK / me, "FSOT", "K+- leaf as a ratio to the m_e anchor")
b, D, p0, k0, et = octet(Mpi, MK, x, y)
info(s, "L-A1 b = B m_d [MeV^2]", "(M_K+^2 - M_pi+^2)/(y - 1)", b, "FSOT", "b/m_e^2 = " + nstr(b / me**2, 10))
info(s, "L-A1 D_EM [MeV^2]", "M_pi+^2 - b(1+x)", D, "FSOT", "physical 1261 MeV^2 (from PDG pi+ - pi0)")
info(s, "L-A1 Goldstone fraction of M_pi+^2", "b(1+x)/M_pi+^2", b * (1 + x) / Mpi**2, "FSOT", "quark-mass (Goldstone) share; remainder EM")
info(s, "L-A1 strange share of M_K+^2", "b y/M_K+^2", b * y / MK**2, "FSOT", "why the kaon is heavier")
A = {}
for n, v in (("pi0", p0), ("K0", k0), ("eta", et)):
    A[n] = emit(s, f"L-A1 M_{n} HELD-OUT (/m_e = {nstr(v / me, 9)})", "FSOT M_pi+, M_K+, m_u/m_d, m_s/m_d", v, *ref[n], mpf("0.02"), "FSOT", "validation " + ("passed" if V["L-A1 " + n] else "FAILED"))
info(s, "L-A1 M_K0 - M_K+ [MeV]", "held-out", k0 - MK, "FSOT", "PDG 3.934(20) MeV (LO, EM by Dashen)")
for tag, S3, txt, cls in (("a", mpf(250), "Sigma^1/3 = 0.25 GeV (pin 1/4)", "HYBRID"), ("b", mpf(272) / 338 * Lf["3"], "Sigma^1/3 = (272/338) FSOT Lambda3", "HYBRID"),
                          ("c", mp / 4, "Sigma^1/3 = m_p/4", "HYBRID")):
    md = b * F1a**2 / S3**3
    emit(s, f"L-B1{tag} m_ud ({txt})", "L-A1 b, K-1a F_pi", md * (1 + x) / 2, mpf("3.387"), mpf("0.039"), mpf("0.10"), cls, "validation " + ("passed" if V["L-B1"] else "FAILED") + "; F_pi is K-1a hybrid")
    emit(s, f"L-B1{tag} m_s = y m_d", "same", md * y, mpf("92.4"), mpf("1.0"), mpf("0.10"), cls, "FLAG 2024 2+1; m_d = " + nstr(md, 6) + ", m_u = " + nstr(md * x, 6))
info(s, "L-B2 f_pi (K-1a, round k)", "frozen", F1a, "HYBRID", "")
info(s, "L-B4 g_piNN (K-4, round k)", "frozen", mpf("1.263") * (X.kg_to_GeV(L["m_p_kg"]) + X.kg_to_GeV(L["m_n_kg"])) * 500 / F1a, "HYBRID", "")
rp = 4 * mpf("197.3269804") / mp
emit(s, "L-C1 r_p = 4 hbar/(m_p c) [fm]", "anchored m_p", rp, mpf("0.8409"), mpf("0.0004"), mpf("0.02"), "FSOT (coefficient not derived)", "known coincidence; noticed before freeze; look-elsewhere 8")
# ---- L-M: D_eff -> unit map (FREEZE_2026-10-02lm)
def tk0(key):
    for line in open(R / "audit/trace_2026-10-02k.tsv", encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) > 3 and f[2].startswith(key): return mpf(f[3])
from mpmath import log, exp as mexp, matrix, lu_solve
hc0, kB0, hbar0, Mpc0 = mpf("197.3269804"), mpf("8.617333262e-11"), mpf("6.582119569e-22"), mpf("3.0856775814913673e19")
Dm = {"PP": (5, F.domain_scalar("Particle_Physics")), "HEP": (6, F.domain_scalar("High_Energy_Physics")), "NUC": (12, F.domain_scalar("Nuclear_Physics")),
      "COS": (25, F.domain_scalar("Cosmology"))}
# leaf: (N, domain, A_unit expressed in the measured unit, measured, sigma, role)
ML = [("m_pi+-", Mpi, "PP", me, mpf("139.57039"), mpf("0.00018"), "train"), ("B(2H)", tk0("B(2H)"), "NUC", me, mpf("2.224566"), mpf("1e-6"), "train"),
      ("T_CMB", tk0("T_CMB"), "COS", me / kB0, mpf("2.7255"), mpf("0.0006"), "train"),
      ("m_K+-", MK, "PP", me, mpf("493.677"), mpf("0.015"), "held"), ("m_D+-", L["m_D_pm_MeV"], "PP", me, mpf("1869.66"), mpf("0.05"), "held"),
      ("r_p", L["r_p_fm"], "PP", hc0 / me, mpf("0.8409"), mpf("0.0004"), "held"), ("dm2_32", tk0("dm2_32"), "PP", (me * 10**6)**2, mpf("2.455e-3"), mpf("0.028e-3"), "held"),
      ("m_W", L["m_W_MeV"], "HEP", me, mpf("80369.2"), mpf("13.3"), "held"), ("m_Z", L["m_Z_MeV"], "HEP", me, mpf("91187.6"), mpf("2.1"), "held"),
      ("m_H", L["m_H_MeV"], "HEP", me, mpf("125200"), mpf("110"), "held"), ("B(3H)", L["B_H3_MeV"], "NUC", me, mpf("8.481798"), mpf("1e-6"), "held"),
      ("B(4He)", L["B_He4_MeV"], "NUC", me, mpf("28.295674"), mpf("1e-6"), "held"), ("H0", tk0("H0"), "COS", me / hbar0 * Mpc0, mpf("67.4"), mpf("0.5"), "held")]
fams = {"M1": lambda d: log(mpf(Dm[d][0]) / 5), "M2": lambda d: mpf(Dm[d][0] - 5), "M3": lambda d: Dm[d][1]}
for leaf in ML: info("L-M", f"required g for {leaf[0]} ({leaf[2]}, D_eff {Dm[leaf[2]][0]})", "measured/(N A_unit)", leaf[4] / (leaf[1] * leaf[3]), "", "g each leaf needs; " + leaf[6])
for fn, u in fams.items():
    tr = [l_ for l_ in ML if l_[6] == "train"]
    Sxx = sum(u(l_[2])**2 for l_ in tr); Sx = sum(u(l_[2]) for l_ in tr); n = len(tr)
    ys = [log(l_[4] / (l_[1] * l_[3])) for l_ in tr]; Sy = sum(ys); Sxy = sum(u(l_[2]) * y_ for l_, y_ in zip(tr, ys))
    bb = (n * Sxy - Sx * Sy) / (n * Sxx - Sx**2); aa = (Sy - bb * Sx) / n
    res = max(fabs(mexp(aa + bb * u(l_[2])) * l_[1] * l_[3] / l_[4] - 1) for l_ in tr)
    info("L-M", f"{fn} fit a, b (max training rel residual {nstr(res * 100, 4)} %)", "training pi+-, B(2H), T_CMB", aa, "FSOT map", "b = " + nstr(bb, 10))
    npass = 0
    for l_ in ML:
        if l_[6] != "held": continue
        npass += emit("L-M", f"{fn} held-out {l_[0]}", f"N x A_unit x g({l_[2]})", mexp(aa + bb * u(l_[2])) * l_[1] * l_[3], l_[4], l_[5], mpf("0.02"), "FSOT map", "")
    rec("L-M", f"{fn} consistent D_eff -> unit map", "YES" if npass == 10 else "NO", f"{npass}/10 held-out within 2 %")
rec("GATE", "D: Delta alpha_had -> Gamma_Z/M_Z; deuteron", "NOT RUN", "frozen gate: needs non-hybrid F_pi and g_piNN")
rec("GATE", "record rows of the 91", "unchanged", "held-out mesons and quark masses are not among the 91; r_p row already confirmed by its leaf")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02l.py under audit/FREEZE_2026-10-02l (committed first)\n"
            "#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
# ---- restatement table
hc, kB, hbar = mpf("197.3269804"), mpf("8.617333262e-11"), mpf("6.582119569e-22")
def tk(key):
    for line in open(R / "audit/trace_2026-10-02k.tsv", encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) > 3 and f[2].startswith(key): return mpf(f[3])
Mpc = mpf("3.0856775814913673e19")
T = [("m_pi+-", Mpi / me, "M/m_e", "pseudo-Goldstone: M^2 ~ B(m_u+m_d) + EM (L-A1)"),
     ("m_K+-", MK / me, "M/m_e", "pseudo-Goldstone with strange quark: M^2 ~ B(m_u+m_s) + EM (L-A1)"),
     ("m_D+-", L["m_D_pm_MeV"] / me, "M/m_e", "heavy-light: m_c + Lambda-bar + O(1/m_c); next branch HQET with FSOT m_c/m_b"),
     ("m_W", L["m_W_MeV"] / me, "M/m_e", "M_W = g v/2; next branch: (pi alpha/(sqrt2 G_F))^(1/2)/sin theta_W with G_F m_e^2 restated"),
     ("m_Z", L["m_Z_MeV"] / me, "M/m_e", "M_W/cos theta_W"), ("m_H", L["m_H_MeV"] / me, "M/m_e", "sqrt(2 lambda) v"),
     ("B(2H)", tk("B(2H)") / me, "B/m_e", "shallow S-wave: B = hbar^2 gamma^2/(2 mu), pionless EFT"),
     ("B(3H)", L["B_H3_MeV"] / me, "B/m_e", "Tjon/Phillips correlation with B(2H)"), ("B(4He)", L["B_He4_MeV"] / me, "B/m_e", "Tjon line B(4He) ~ 4.7 B(3H)"),
     ("r_p", L["r_p_fm"] * mp / hc, "r_p m_p c/hbar", "L-C1 (4.00)"),
     ("T_CMB", tk("T_CMB") * kB / me, "k_B T/(m_e c^2)", "photon temperature today; next branch Saha recombination T_* = z_* scaling"),
     ("H0", tk("H0") / Mpc * hbar / me, "hbar H0/(m_e c^2)", "expansion rate in electron units"),
     ("dm2_32", tk("dm2_32") / (me * 1e6)**2, "dm^2/m_e^2", "seesaw scale v^2/M_R")]
with open(R / "audit/derive_2026-10-02l.tsv", "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02l.py: unit-read leaves restated against the natural anchor\n#leaf\tratio\tdefinition\tgoverning physics / branch\n")
    for t in T: o.write(f"{t[0]}\t{nstr(t[1], 12)}\t{t[2]}\t{t[3]}\n")
print("validations:", {k: ("PASS" if v else "FAIL") for k, v in V.items()})
