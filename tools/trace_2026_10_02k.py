#!/usr/bin/env python3
"""Round-k TRACE tables (diagnostics, not branches): theta_S back to the seeds; a unit audit of every FSOT leaf that carries a unit
(which leaves are derived from the m_e = h nu_Cs/c^2 exp(...) anchor and which are pure numbers read in a human unit); link tests of the
MeV-read pion/kaon leaves against m_e, m_p and the round-j Lambda_QCD; the pion-leaf lineage in the hub git history; the m_s/m_ud gap;
and the internal consistency of the FSOT cosmology pins (T_CMB, z_eq, Omega_m, H0, Omega_r, N_eff, Omega_b h^2, eta_b).
Existing frozen values only; nothing is tuned or scored here.

  python tools/trace_2026_10_02k.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/trace_2026-10-02k.tsv
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, sqrt, pi, ln, fabs, nstr
from mpmath import exp, sin, degrees
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves(); P = X.pins(); R = Path(__file__).resolve().parents[1]
rows = []
def t(sec, n, qty, v, c=None, s=None, src="", note=""):
    vs = nstr(v, 12) if v is not None else "none"
    z = nstr(fabs(v - c) / s, 4) if (s and v is not None and c is not None) else "-"
    rows.append([sec, n, qty, vs, nstr(c, 10) if c is not None else "-", nstr(s, 4) if s else "-", src or "-", z, note])
MeV = lambda kg: X.kg_to_GeV(kg) * 1000
alpha = 1 / L["alpha_inv"]; me = MeV(L["m_e_kg"]); mp = MeV(L["m_p_kg"])
sj = {}
for line in open(R / "audit/score_2026-10-02j.tsv", encoding="utf-8"):
    f = line.rstrip("\n").split("\t")
    if len(f) > 3 and f[0] == "FSOT" and f[1].startswith("J-1 Lambda^("): sj[f[1][12]] = mpf(f[3])
L5, L3 = sj["5"], sj["3"]
# ---- A theta_S back to the seeds
s = "A theta_S"
t(s, 1, "psi_con = 1 - e^-1", F.PSI_CON, note="math: P(N>=1) for a Poisson count of mean 1; the fraction of a first-order relaxation completed after one time constant. Hub label: consciousness parameter. No particle-physics counterpart")
t(s, 2, "eta_eff = 1/(pi - 1)", F.ETA_EFF, note="math: diameter / (circumference - diameter) of a circle. Hub label: efficiency. No particle-physics counterpart")
arg = F.PSI_CON * F.ETA_EFF
t(s, 3, "argument psi_con * eta_eff [rad]", arg, note=f"= {nstr(degrees(arg), 8)} deg")
t(s, 4, "theta_S = sin(psi_con eta_eff)", F.THETA_S, note="a sine VALUE that the hub then also uses as an ANGLE (sin theta_S in C_eff, B_in; cos theta_S in P_var, Suction; Lean lemma phase_variance = cos theta_S)")
t(s, 5, "comparison: sin theta_C = |V_us|", F.THETA_S, mpf("0.22501"), mpf("0.00068"), "PDG 2024", note="not the Cabibbo angle; listed only to exclude it")
t(s, 6, "comparison: sin^2 theta_W (MSbar)", F.THETA_S, mpf("0.23129"), mpf("0.00004"), "PDG 2024", note="not the weak angle; excluded")
t(s, 7, "comparison: QCD vacuum angle theta-bar", F.THETA_S, note="|theta-bar| < 1e-10 (neutron EDM); excluded. No known physical angle equals 0.2909: theta_S has no established physical representation")
# ---- B unit audit
s = "B unit audit"
SIfac = mpf(10)**6 * X.E_CHARGE / (X.H_PLANCK * 9192631770)
t(s, 0, "1 MeV / (h nu_Cs) = 1e6 e[C] / (h nu_Cs) (SI 2019 exact)", SIfac, note="contains e = 1.602176634e-19 C, a defined number fixed in 2019 to continue the historical coulomb: a convention, not physics")
t(s, "0b", "1 MeV / (m_e c^2) = 1/m_e[MeV] on the FSOT anchor", 1 / me, 1 / mpf("0.51099895069"), mpf("0.00000000016") / mpf("0.51099895069")**2, "CODATA 2022",
  note="= SI factor / exp(23.3215823...): the factor every MeV-read leaf would need to be tied to the m_e anchor")
aud = [("m_e", me, "MeV", "anchor: h nu_Cs/c^2 exp(...)"), ("m_mu", MeV(L["m_mu_kg"]), "MeV", "m_e x seed ratio"), ("m_tau", L["m_tau_MeV"], "MeV", "m_e x seed ratio"),
       ("m_p", mp, "MeV", "m_e x seed ratio"), ("m_n", MeV(L["m_n_kg"]), "MeV", "m_p x (1 + excess)"),
       ("m_pi+-", L["m_pi_pm_MeV"], "MeV", "UNIT-READ pure number"), ("m_K+-", L["m_K_pm_MeV"], "MeV", "UNIT-READ"), ("m_D+-", L["m_D_pm_MeV"], "MeV", "UNIT-READ"),
       ("m_W", L["m_W_MeV"], "MeV", "UNIT-READ"), ("m_Z", L["m_Z_MeV"], "MeV", "UNIT-READ (W leaf / cos)"), ("m_H", L["m_H_MeV"], "MeV", "UNIT-READ"),
       ("B(4He)", L["B_He4_MeV"], "MeV", "UNIT-READ"), ("B(3H)", L["B_H3_MeV"], "MeV", "UNIT-READ"), ("B(2H) sqrt(e)/e + phi", sqrt(F.E) / F.E + F.PHI, "MeV", "UNIT-READ"),
       ("r_p", L["r_p_fm"], "fm", "UNIT-READ (femtometre)"), ("dm2_32", L["dm2_32"], "eV^2", "UNIT-READ"), ("T_CMB", P["wave1|T_CMB"], "K", "UNIT-READ (kelvin; k_B defined)"),
       ("H0", P["wave1|H0"], "km/s/Mpc", "UNIT-READ")]
for i, (nm, v, u, how) in enumerate(aud, 1):
    note = how
    if u == "MeV": note += f"; ratio to FSOT m_e = {nstr(v / me, 12)}"
    t(s, i, f"{nm} [{u}]", v, note=note)
# ---- C link tests
s = "C link tests"
mpi, mK = L["m_pi_pm_MeV"], L["m_K_pm_MeV"]
PDGpi, PDGK, PDGp, PDGe = mpf("139.57039"), mpf("493.677"), mpf("938.27208943"), mpf("0.51099895069")
t(s, 1, "m_pi/m_e", mpi / me, PDGpi / PDGe, mpf("0.00018") / PDGe, "PDG/CODATA", note="unit-free; reproduces only because the leaf matches 139.57 in MeV")
t(s, 2, "m_pi/m_p", mpi / mp, PDGpi / PDGp, mpf("0.00018") / PDGp, "PDG", note="hub pin wave2|m_pi/m_p = K P_new ln(pi) = " + nstr(P["wave2|m_pi/m_p"], 8) + " is a different closed form (pi0/p 0.14386)")
t(s, 3, "m_pi/Lambda^(5) (FSOT Lambda from J-1)", mpi / L5, PDGpi / 213, PDGpi * 8 / 213**2, "FLAG 2024 Lambda^(5) 213(8)", note="QCD: m_pi^2 ~ 2 B m_ud, so m_pi/Lambda measures m_ud/Lambda (a free QCD parameter); the 3.8 % Lambda error cannot test an exact factor")
t(s, 4, "m_pi/Lambda^(3) (FSOT Lambda, external thresholds)", mpi / L3, PDGpi / 338, PDGpi * 10 / 338**2, "FLAG 2024 Lambda^(3) 338(10)", note="close to sqrt2 - 1 = 0.41421 (noted; one of many simple numbers inside the 3 % band: not claimed)")
t(s, 5, "m_K/m_e", mK / me, PDGK / PDGe, mpf("0.015") / PDGe, "PDG")
t(s, 6, "m_K/Lambda^(3)", mK / L3, PDGK / 338, PDGK * 10 / 338**2, "FLAG")
targets = {"m_pi/m_e": mpi / me, "m_pi/m_p": mpi / mp, "m_pi/Lambda5": mpi / L5, "m_pi/Lambda3": mpi / L3, "m_K/m_e": mK / me, "1/m_e[MeV]": 1 / me}
pinvals = [(k, v) for k, v in P.items() if v != 0]
for j, (nm, v) in enumerate(targets.items(), 7):
    hits = [k for k, pv in pinvals if fabs(pv / v - 1) < mpf("1e-6")]
    t(s, j, f"any AEB2AD pin within 1 ppm of {nm}?", v, note=("hits: " + ", ".join(hits)) if hits else f"none of {len(pinvals)} pins")
# ---- D pion lineage (hub git history, 6f9c2560)
s = "D pion lineage"
for i, (when, what) in enumerate([
    ("2026-07-14 856694ca (archive import)", "FSOT SMILES Lab dataset (Damian desktop project) S66 Particle Masses Tier 18: pion_pm = e^5 - pi^2 = 138.5436 'MeV' vs target 139.57 (0.74 %), same formula for pi0"),
    ("2026-07-11 5c0653c1 / 07-12 b9660cd5", "data/pdg_particle_properties_benchmark.json: pion_pm 'THETA^-4 - THETA^2' = 139.5669 vs measured 139.57 MeV; the file holds many THETA/OMEGA/POOF power combinations (a formula-search catalog)"),
    ("2026-09-29 71fa2e3f", "added alpha/(pi-1): the gap / alpha was 0.474 and eta_eff = 0.467; 139.570341, z 0.27"),
    ("all stages", "the target was the PDG number in MeV, so the MeV is the unit of the search target; no stage multiplies by m_e, m_p or any scale")], 1):
    rows.append([s, i, when, "-", "-", "-", "hub git log", "-", what])
# ---- E m_s/m_ud gap
s = "E m_s/m_ud"
x, y = P["wave7|m_u/m_d"], P["wave7|m_s/m_d"]; mud_md = (1 + x) / 2
t(s, 1, "m_u/m_d (pin sqrt3 - sqrt phi)", x, mpf("0.465"), mpf("0.024"), "FLAG 2024 2+1+1", note="2+1: 0.485(19), z " + nstr(fabs(x - mpf("0.485")) / mpf("0.019"), 3))
t(s, 2, "m_s/m_d (pin e^3 + gamma^4)", y, mpf("27.227") * (1 + mpf("0.465")) / 2, mpf("27.227") / 2 * sqrt((mpf("0.081") / 27.227 * (1 + mpf("0.465")))**2 + mpf("0.024")**2),
  "derived from FLAG 2+1+1 m_s/m_ud and m_u/m_d", note="FLAG does not average m_s/m_d; the hub SS-407 note quotes '20.203(76) FLAG' (not found in FLAG 2024 Table 1)")
t(s, 3, "m_s/m_ud = (m_s/m_d) 2/(1 + m_u/m_d)", y / mud_md, mpf("27.227"), mpf("0.081"), "FLAG 2024 2+1+1", note="2+1: 27.42(12), z " + nstr(fabs(y / mud_md - mpf("27.42")) / mpf("0.12"), 3))
t(s, 4, "R = (m_s - m_ud)/(m_d - m_u)", (y - mud_md) / (1 - x), mpf("35.9"), mpf("1.7"), "FLAG 2024 eq. 52 (2+1+1)")
Q = sqrt((y**2 - mud_md**2) / (1 - x**2))
t(s, 5, "Q = sqrt((m_s^2 - m_ud^2)/(m_d^2 - m_u^2))", Q, mpf("22.5"), mpf("0.5"), "FLAG 2024 eq. 52 (2+1+1)", note="eta->3pi: 22.1(0.7)")
t(s, 6, "m_s/m_d that m_s/m_ud = 27.227 needs at FSOT m_u/m_d", mpf("27.227") * mud_md, note="-1.6 % from the pin")
t(s, 7, "m_u/m_d that m_s/m_ud = 27.227 needs at FSOT m_s/m_d", 2 * y / mpf("27.227") - 1, mpf("0.485"), mpf("0.019"), "FLAG 2+1 m_u/m_d", note="vs 2+1+1 0.465(24): z " + nstr(fabs(2 * y / mpf("27.227") - 1 - mpf("0.465")) / mpf("0.024"), 3))
t(s, 8, "physics", None, note="m_s/m_ud is fixed by the isospin-averaged K/pi masses (QCD only; lattice-precise, 0.3 %); m_u/m_d needs the EM-corrected kaon splitting (5 %). The FSOT pair satisfies Q and R; the z 5.4 is the precise m_s/m_ud combination")
# ---- F cosmology consistency (standard relations; PDG 2024 cosmological parameters review conventions)
s = "F cosmology"
T, H0, Om, Neff, zeq, Orr, Obh2, ODh2, eta = (P["wave1|T_CMB"], P["wave1|H0"], P["wave2|Omega_m"], P["wave2|N_eff"], P["wave3|z_eq"], P["wave9|Omega_r"],
                                              P["wave1|Omega_b_h2"], P["wave2|Omega_DM_h2"], P["wave10|eta_baryon_photon"])
h2 = (H0 / 100)**2; fnu = 1 + mpf("0.22711") * Neff; OgH = mpf("2.4728e-5")
t(s, 1, "T_CMB leaf phi^2 + P_base|S_cosm| [K]", T, mpf("2.7255"), mpf("0.0006"), "FIRAS (PDG 2024)", note="pure number read in kelvin (k_B defined): same unit question as the MeV leaves")
t(s, 2, "Omega_m h^2 = Omega_m (H0/100)^2", Om * h2, Obh2 + ODh2, None, "FSOT Omega_b h^2 + Omega_DM h^2", note=f"{nstr((Om * h2 / (Obh2 + ODh2) - 1) * 100, 4)} % apart (nu mass ~0.0006 cannot close it); Planck 2018 0.1430(11)")
t(s, 3, "Omega_r from T, H0, N_eff: 2.4728e-5 (T/2.7255)^4 (1 + 0.22711 N_eff)/h^2", OgH * (T / mpf("2.7255"))**4 * fnu / h2, Orr, None, "FSOT pin wave9|Omega_r",
  note=f"{nstr((OgH * (T / mpf('2.7255'))**4 * fnu / h2 / Orr - 1) * 100, 4)} %")
t(s, 4, "z_eq = Omega_m / Omega_r - 1 (pins)", Om / Orr - 1, zeq, None, "FSOT pin wave3|z_eq", note=f"{nstr(((Om / Orr - 1) / zeq - 1) * 100, 4)} %")
Orc = OgH * (T / mpf("2.7255"))**4 * fnu / h2
t(s, 5, "z_eq = Omega_m / Omega_r(T, H0, N_eff) - 1", Om / Orc - 1, zeq, None, "FSOT pin z_eq", note=f"{nstr(((Om / Orc - 1) / zeq - 1) * 100, 4)} %; Planck 2018 z_eq 3387(21)")
def T_from_Orh2(x): return mpf("2.7255") * (x / fnu / OgH) ** (mpf(1) / 4)
t(s, 6, "T implied by z_eq, Omega_m, H0, N_eff", T_from_Orh2(Om * h2 / (1 + zeq)), mpf("2.7255"), mpf("0.0006"), "FIRAS")
t(s, 7, "T implied by z_eq, Omega_b h^2 + Omega_DM h^2, N_eff", T_from_Orh2((Obh2 + ODh2) / (1 + zeq)), mpf("2.7255"), mpf("0.0006"), "FIRAS")
t(s, 8, "T implied by Omega_r, H0, N_eff", T_from_Orh2(Orr * h2), mpf("2.7255"), mpf("0.0006"), "FIRAS")
t(s, 9, "T implied by eta_b, Omega_b h^2 (eta10 = 274 Omega_b h^2 at 2.7255 K)", mpf("2.7255") * (274 * Obh2 / (eta * 10**10)) ** (mpf(1) / 3), mpf("2.7255"), mpf("0.0006"), "FIRAS",
  note="as in round h; systematic only (274 rounded)")
t(s, 10, "conclusion", None, note="the FSOT cosmology pins are mutually inconsistent at the 1-4 % level under standard relations; the T_CMB leaf itself (z 1.31) is closer to FIRAS than any T they imply")
with open(a.out, "w", encoding="utf-8", newline="\n") as f:
    f.write("# round-k trace (diagnostics, not branches); FSOT values from hub 6f9c2560 leaves / AEB2AD pins; Lambda from audit/score_2026-10-02j.tsv\n")
    f.write("section\tstep\tquantity\tFSOT\tcounterpart\tsigma\tsource\tz\tnote\n")
    for r_ in rows: f.write("\t".join(str(x) for x in r_) + "\n")
print(f"trace rows {len(rows)}")
