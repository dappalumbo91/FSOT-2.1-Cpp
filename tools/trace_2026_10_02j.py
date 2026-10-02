#!/usr/bin/env python3
"""Round-j TRACE tables (diagnostics, not branches): how FSOT obtains absolute MeV (m_e chain, m_p/m_e, the MeV-read pion/kaon leaves)
and what physical content each term has next to its lattice/ChPT/PDG counterpart (FLAG 2024 arXiv:2411.04268, PDG 2024). Existing
frozen values only; nothing is tuned and nothing here is scored.

  python tools/trace_2026_10_02j.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/trace_2026-10-02j.tsv
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, sqrt, pi, ln, fabs, nstr
from mpmath import exp, e as E, sin, cbrt
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves(); P = X.pins()
rows = []
def t(sec, n, qty, v, c=None, s=None, src="", note=""):
    vs = nstr(v, 12) if v is not None else "none"
    if c is None: rows.append([sec, n, qty, vs, "-", "-", src or "no physical counterpart", "-", note]); return
    z = nstr(fabs(v - c) / s, 4) if (s and v is not None) else "-"
    rows.append([sec, n, qty, vs, nstr(c, 10), nstr(s, 4) if s else "-", src, z, note])
MeV = lambda kg: X.kg_to_GeV(kg) * 1000
alpha = 1 / L["alpha_inv"]; psi = F.PSI_CON; phi = F.PHI
# ---- A: absolute scale (electron)
s = "A m_e chain"
t(s, 1, "SI-exact h, c, nu_Cs (=9192631770 Hz): h nu_Cs / c^2 [kg]", X.H_PLANCK * 9192631770 / X.C_LIGHT**2, src="SI 2019 definitions (exact)",
  note="the only dimensionful input; it is the Cs hyperfine unit, not a QCD scale")
me = MeV(L["m_e_kg"]); X0 = ln(L["m_e_kg"] / (X.H_PLANCK * 9192631770 / X.C_LIGHT**2))
t(s, 2, "exponent total ln(m_e c^2 / h nu_Cs)", X0, src="", note="pure number reproduced by FSOT; physically m_e = y_e v/sqrt2 (Higgs Yukawa, electroweak sector)")
t(s, "2a", "  e^pi", exp(pi), note="carries 99.2 % of the exponent")
t(s, "2b", "  (C_factor K ln2)^2 + G P_new psi_con - alpha^5 phi^2/ln^2 2", X0 - exp(pi), note="0.18 = remaining 0.8 % of the exponent")
t(s, 3, "m_e [MeV]", me, mpf("0.51099895069"), mpf("0.00000000016"), "CODATA 2022", note="absolute anchor of every FSOT MeV value that is derived (not read) in MeV")
# ---- B: proton ratio
s = "B m_p/m_e"
r = L["m_p_over_m_e"]; t1 = 6 * pi**5; t2 = ln(2) / E**3; t3 = r - t1 - t2
t(s, 1, "6 pi^5 (Lenz, Phys. Rev. 82, 554 (1951) coincidence)", t1, note="99.998 % of the ratio; no QCD content identifiable (not a binding/quark-mass split)")
t(s, 2, "ln2/e^3", t2, note=f"= {nstr(t2*me,6)} MeV of m_p (19 ppm)")
t(s, 3, "alpha^2 (1 + psi_con/e^3)", t3, note=f"= {nstr(t3*me,6)} MeV of m_p (an O(alpha^2) piece; physical EM self-energy of p is ~+0.6 MeV, Gasser-Leutwyler)")
t(s, 4, "m_p/m_e total", r, mpf("1836.152673426"), mpf("0.000000032"), "CODATA 2022")
mp = MeV(L["m_p_kg"]); mn = MeV(L["m_n_kg"])
t(s, 5, "m_p [MeV] = ratio x m_e", mp, mpf("938.27208943"), mpf("0.00000029"), "PDG 2024")
t(s, "P1", "physical: light-quark sigma term sigma_piN (m_ud <N|uu+dd|N>)", None, mpf("42.2"), mpf("2.4"), "FLAG 2024 N_f=2+1 (60.9(6.5) for 2+1+1)",
  note="4.5-6.5 % of m_p; no FSOT term of this size (term 2 is 0.018 MeV)")
t(s, "P2", "physical: chiral-limit nucleon mass m_0 (~ m_p - sigma_piN - ...)", None, note="~ 0.87-0.9 GeV, QCD binding (trace anomaly), lattice-computed; FSOT has no counterpart")
t(s, "P3", "physical: constituent quark mass ~ m_p/3", mp / 3, note="model concept (DGG); FSOT does not split m_p into constituents")
# ---- C: theta_S and the pion leaf
s = "C pion leaf"
th = F.THETA_S; assert fabs(th - sin(psi * F.ETA_EFF)) < mpf(10)**-40
t(s, 1, "theta_S = sin(psi_con eta_eff)", th, note="pure number from seeds; not a QCD quantity (cf. sin theta_C 0.2250: unrelated, no claim)")
t(s, 2, "theta_S^-4", th**-4, note="99.94 % of the leaf")
t(s, 3, "-theta_S^2 + alpha/(pi-1)", -th**2 + alpha / (pi - 1))
t(s, 4, "pion leaf (pure number read as MeV)", L["m_pi_pm_MeV"], mpf("139.57039"), mpf("0.00018"), "PDG 2024 m_pi+-",
  note="NOT multiplied by m_e or h nu_Cs: the MeV is a unit reading, so FSOT's pion carries no derived scale (m_pi/m_e follows only via CODATA MeV)")
t(s, 5, "m_pi/m_p from leaves", L["m_pi_pm_MeV"] / mp, mpf("139.57039") / mpf("938.27208943"), mpf("0.00018") / mpf("938.27208943"), "PDG 2024 ratio", note="pin wave2|m_pi/m_p is a separate closed form = " + nstr(P["wave2|m_pi/m_p"], 10) + " (vs pi0/p 0.14386)")
t(s, "P1", "physical: GMOR m_pi^2 F^2 = m_ud |<qq>| (x2 with F=f/sqrt2)", None, note="m_pi^2 is linear in m_ud; FSOT's leaf has no quark-mass or F_pi factor")
# ---- D: kaon / quark ratios
s = "D kaon, quark ratios"
t(s, 1, "kaon leaf G^-7 + P_base^-4 - pi^-4 (read as MeV)", L["m_K_pm_MeV"], mpf("493.677"), mpf("0.015"), "PDG 2024", note="also a unit reading")
mud_ratio = P["wave7|m_s/m_d"] * 2 / (1 + P["wave7|m_u/m_d"])
t(s, 2, "m_u/m_d pin sqrt3 - sqrt phi", P["wave7|m_u/m_d"], mpf("0.465"), mpf("0.024"), "FLAG 2024 N_f=2+1+1", note="2+1: 0.485(19)")
t(s, 3, "m_s/m_ud = (m_s/m_d) 2/(1+m_u/m_d)", mud_ratio, mpf("27.227"), mpf("0.081"), "FLAG 2024 N_f=2+1+1", note="2+1: 27.42(12)")
lo = 2 * L["m_K_pm_MeV"]**2 / L["m_pi_pm_MeV"]**2 - 1
t(s, 4, "LO ChPT m_s/m_ud = 2 m_K^2/m_pi^2 - 1 from FSOT leaves", lo, mpf("27.227"), mpf("0.081"), "FLAG 2024",
  note="LO without EM/NLO is ~12 % low with PDG masses as well; diagnostic only")
t(s, 5, "absolute m_ud, m_s, m_u, m_d", None, mpf("3.427"), mpf("0.051"), "FLAG 2024 m_ud (2+1+1), MSbar 2 GeV", note="FSOT has ratios only: no absolute light-quark mass")
# ---- E: strong-sector scale carriers
s = "E chiral-scale carriers"
t(s, 1, "f_pi (F_pi = f_pi/sqrt2)", None, mpf("92.07"), mpf("0.57"), "FLAG 2024 f_pi 130.2(8) N_f=2+1", note="absent in FSOT")
t(s, 2, "Quark_condensate pin 1/4 (hub reference 0.250: reads as |<qq>|^1/3 in GeV)", P["wave8|Quark_condensate"], mpf("0.272"), mpf("0.005"),
  "FLAG 2019 Sigma^1/3 N_f=2+1 (FLAG 2024 dropped the LEC section)", note="unit reading; no m_ud to close GMOR")
t(s, 3, "Gluon_condensate pin C_cosm - e^-3 (hub reference 0.012: GeV^4 reading)", P["wave9|Gluon_condensate"], mpf("0.012"), mpf("0.006"),
  "SVZ 1979 <alpha_s/pi G^2> (~50 % uncertainty conventional)", note="present (round-i inventory listed it absent: corrected here); usable only in sum rules")
t(s, 4, "alpha_s(M_Z) seed 2(POOF/psi_con)^2", mpf(2) * (F.POOF / psi) ** 2, mpf("0.1183"), mpf("0.0007"), "FLAG 2024",
  note="the only FSOT quantity that fixes a QCD scale: Lambda_QCD in units of M_Z (branch J-1)")
t(s, 5, "g_A", None, mpf("1.2754"), mpf("0.0013"), "PDG 2024 lambda = g_A/g_V", note="absent (FLAG 2024 lattice g_A^u-d 1.263(10))")
t(s, 6, "g_piNN", None, mpf("13.24"), mpf("0.09"), "Reinert-Krebs-Epelbaum PRL 126 092501 f_c^2 0.0769(10)", note="absent")
with open(a.out, "w", encoding="utf-8", newline="\n") as f:
    f.write("# round-j trace (diagnostics, not branches); FSOT values from hub 6f9c2560 leaves / AEB2AD pins\n")
    f.write("section\tstep\tquantity\tFSOT\tcounterpart\tsigma\tsource\tz\tnote\n")
    for r_ in rows: f.write("\t".join(str(x) for x in r_) + "\n")
print(f"trace rows {len(rows)}")
