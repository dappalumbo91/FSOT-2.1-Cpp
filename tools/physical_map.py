#!/usr/bin/env python3
"""Generate docs/PHYSICAL_MAP.md from audit/precision_2026-10-02.tsv (the 91 record rows) and the derivation-branch scores (rounds l-n).
Stdlib only; regenerate each round:  python tools/physical_map.py --out docs/PHYSICAL_MAP.md
"""
import argparse, csv, math, re
from pathlib import Path
R = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
rows = [x for x in csv.DictReader(open(R / "audit/precision_2026-10-02.tsv", encoding="utf-8"), delimiter="\t") if x["record"] == "1"]
me = float(next(x["value"] for x in rows if x["#id"] == "m_e_kg"))
c, h, e, kB, NA = 299792458.0, 6.62607015e-34, 1.602176634e-19, 1.380649e-23, 6.02214076e23
hb = h / (2 * math.pi); E0 = me * c * c; L0 = hb / (me * c); T0 = hb / E0; Mpc = 3.0856775814913673e22
A = {"kg": (me, "m_e"), "J": (E0, "m_e c^2"), "MeV": (E0 / e / 1e6, "m_e c^2"), "GeV": (E0 / e / 1e9, "m_e c^2"), "eV^2": ((E0 / e)**2, "(m_e c^2)^2"),
     "m": (L0, "hbar/(m_e c)"), "fm": (L0 * 1e15, "hbar/(m_e c)"), "m^-1": (1 / L0, "m_e c/hbar"), "m^2": (L0 * L0, "(hbar/(m_e c))^2"),
     "J T^-1": (e * hb / (2 * me), "e hbar/(2 m_e)"), "m^3 kg^-1 s^-2": (hb * c / me**2, "hbar c/m_e^2"), "kg mol^-1": (me * NA, "m_e N_A"),
     "s": (T0, "hbar/(m_e c^2)"), "Gyr": (T0 / (3.15576e16), "hbar/(m_e c^2)"), "km s^-1 Mpc^-1": (1 / T0 * Mpc / 1e3, "m_e c^2/hbar"),
     "Mpc": (L0 / Mpc, "hbar/(m_e c)"), "K": (E0 / kB, "m_e c^2/k_B"), "rad": (1.0, "dimensionless"), "1": (1.0, "dimensionless")}
HELD = {"m_pi_pm_MeV": "L-A1: K0 497.597 (-0.003 %); M-2a: pi0 134.397 (-0.43 %); eta/eta' fail",
        "m_K_pm_MeV": "L-A1 / M-2b: K0 -0.003 % / +0.13 %", "r_p_fm": "L-C1: r_p m_p c/hbar = 4.00006 (coefficient not derived)",
        "B_H3_MeV": "Tjon LO 4.61 ratio fails (+38 %)", "B_He4_MeV": "Tjon LO 4.61 ratio fails (+38 %)",
        "pin:wave3|Deuteron_binding_MeV": "N-3 LO pionless radius -22.7 % (effective range missing)", "pin:wave5|Gamma_Z/M_Z": "Delta alpha_had chain gated (g_A open)",
        "pin:wave8|Deuteron_mu_muN": "needs an FSOT mu_n leaf", "m_Z_MeV": "D_eff/S map tests l/m/n fail (factor follows the unit)",
        "m_W_MeV": "D_eff/S map tests l/m/n fail", "m_H_MeV": "D_eff/S map tests l/m/n fail", "m_D_pm_MeV": "D_eff/S map tests fail; HQET branch open"}
MEAN = {"u_over_m_e": "atomic mass unit / electron mass", "m_Z_MeV": "Z boson mass", "m_tau_MeV": "tau lepton mass", "r_p_fm": "proton rms charge radius",
 "m_pi_pm_MeV": "charged pion mass (pseudo-Goldstone)", "m_D_pm_MeV": "charged D meson mass (heavy-light)", "m_K_pm_MeV": "charged kaon mass (pseudo-Goldstone)",
 "m_c_over_m_b": "charm/bottom quark mass ratio", "m_W_MeV": "W boson mass", "m_W_over_m_Z": "W/Z mass ratio (cos theta_W on shell)", "m_pi_over_m_p": "pion/proton mass ratio",
 "m_H_MeV": "Higgs boson mass", "m_t_over_m_W": "top/W mass ratio", "sin2_theta_W_MSbar": "weak mixing angle (MSbar, M_Z)", "m_tau_over_m_e": "tau/electron mass ratio",
 "dm2_32": "atmospheric neutrino mass splitting", "B_He4_MeV": "4He nuclear binding energy", "B_H3_MeV": "3H nuclear binding energy", "alpha_s_MZ": "strong coupling at M_Z",
 "H0": "Hubble constant", "T_CMB": "CMB temperature today", "n_s": "scalar spectral index", "Omega_b_h2": "baryon density", "Omega_Lambda": "dark-energy density fraction",
 "Omega_m": "matter density fraction", "Omega_DM_h2": "dark-matter density", "sigma_8": "matter fluctuation amplitude", "tau_reion": "reionization optical depth",
 "N_eff": "effective number of neutrino species", "Age_Gyr": "age of the Universe", "z_eq": "matter-radiation equality redshift", "r_star_Mpc": "sound horizon at recombination",
 "Deuteron_binding_MeV": "deuteron binding energy", "Neutron_lifetime_s": "neutron lifetime", "m_H/m_W": "Higgs/W mass ratio", "sin2_theta12": "solar mixing angle",
 "sin2_theta23": "atmospheric mixing angle", "sin2_theta13": "reactor mixing angle", "Dm2_21/Dm2_31": "neutrino splitting ratio", "Jarlskog_J": "CKM CP-violation invariant",
 "w0": "dark-energy equation of state", "Gamma_Z/M_Z": "Z width / Z mass", "R_b": "Z -> bb fraction of hadronic width", "R_c": "Z -> cc fraction of hadronic width",
 "A_FB_ell": "lepton forward-backward asymmetry at the Z", "A_ell_SLD": "lepton left-right asymmetry (SLD)", "m_H/m_t": "Higgs/top mass ratio", "Y_p_He4": "primordial helium mass fraction",
 "D_H_ratio": "primordial D/H", "m_u/m_d": "up/down quark mass ratio", "m_tau/m_mu": "tau/muon mass ratio", "delta_CP_PMNS": "leptonic CP phase", "BR_Z_ee": "Z -> ee branching ratio",
 "BR_Z_had": "Z -> hadrons branching ratio", "BR_Z_inv": "Z -> invisible branching ratio", "S_8": "clustering amplitude S_8", "z_reion": "reionization redshift",
 "eta_baryon_photon": "baryon-to-photon ratio"}
def meaning(x):
    k = x["#id"].split("|")[-1]
    if x["#id"].startswith("CKM_"): return "CKM matrix element |" .replace("|", "") + x["#id"][4:]
    if k in MEAN: return MEAN[k]
    m = re.search(r'"([^"]+)"', x["source"])
    return m.group(1) if m else x["#id"].replace("pin:", "").replace("|", " ").replace("_", " ")
def status(x):
    if x["pass_z<=1"] == "PASS": return "confirmed"
    try:
        if x["refined_z"] and float(x["refined_z"]) <= 1: return "frozen-pending"
    except ValueError: pass
    return "open"
out = ["# FSOT physical map (generated by `tools/physical_map.py`; do not edit by hand)", "",
       "For scientists and mathematicians: what each FSOT quantity represents, how it acquires units, how it is derived, its frozen value and source, its status, and its held-out tests.", "",
       "## Units path", "",
       "- **Anchor.** m_e = (h ν_Cs/c²) × exp(e^π + (C K ln2)² + G P_new ψ_con − α⁵φ²/ln²2) (FSOT seed leaf; ν_Cs and h are SI-exact). Every dimensional quantity is written as **anchor unit × dimensionless ratio**, where the anchor unit is built from m_e, ħ, c, e, k_B and N_A (table column 'anchor unit').",
       "- **Unit-read leaves.** The π, K, D, W, Z, H and nuclear-binding leaves are pure numbers read in MeV or GeV. Their m_e multiple is leaf × 1.956952 (= leaf/m_e[MeV]). That factor contains the SI-defined e, and it follows the unit a leaf is read in, not its domain (rounds l–n).",
       "- **D_eff and S.** The domain effective dimension (D_eff = round(5·5^{g/(G−1)})) and the domain scalar S = K(T1+T2+T3) were tested as the carrier of dimension (round l, 3 families, 0/10), as an organizer of the m_e-multiple ratios (round m, 3 families, 0/6), and on one reference leaf per domain (round n, 2 families, 0/3). None of these maps carries the scale. D_eff/S remain the fold variables of each domain's S, and the ratios are derived within each domain (e.g. L-A1 for the mesons, α² for the Hartree energy).",
       "- **Status legend.** confirmed = record row with z ≤ 1 at pin AEB2AD; frozen-pending = a frozen refinement passes but is not adopted; hybrid = uses a non-FSOT (lattice/FLAG) input; open = not yet within its gate.", "",
       "## The 91 record rows", "",
       "| id | physical quantity | anchor unit | ratio to anchor | FSOT route | frozen value | unit | measured (source) | z | status | held-out tests |",
       "|---|---|---|---|---|---|---|---|---|---|---|"]
n = {"confirmed": 0, "frozen-pending": 0, "open": 0}
for x in rows:
    u = x["unit"]; an, nm = A.get(u, (1.0, "?"))
    try: ratio = "%.9g" % (float(x["value"]) / an)
    except ValueError: ratio = "-"
    st = status(x); n[st] += 1
    src = re.sub(r"\s*https?://\S+", "", x["source"]).strip().replace("|", "/")[:70]
    out.append(f"| `{x['#id'].replace('|', '/')}` | {meaning(x)} | {nm} | {ratio} | {x['route']} | {x['value']} | {u} | {x['central']} ({src}) | {x['z']} | {st} | {HELD.get(x['#id'], '-')} |")
out += ["", f"**Totals:** {n['confirmed']}/91 confirmed, {n['confirmed'] + n['frozen-pending']}/91 including frozen-pending, {n['open'] - 0}/91 open.", "",
        "## Derivation-branch quantities (rounds l–n; not record rows)", "",
        "| quantity | physical meaning | FSOT derivation | frozen value | ratio to m_e | measured (source) | rel | class | held-out / status | freeze |",
        "|---|---|---|---|---|---|---|---|---|---|",
        "| M_K0 | neutral kaon (pseudo-Goldstone, m_d + m_s) | LO ChPT + Dashen from π±, K± leaves and pins m_u/m_d, m_s/m_d | 497.597 MeV | 973.773 | 497.611(13) PDG 2024 | −0.003 % | FSOT | held-out, agrees | l (9c6dbbc) |",
        "| M_K0 (Q route) | same, via L5/L8-free Q | Q = 22.7315 from pins + EM | 498.272 MeV | — | 497.611(13) | +0.13 % | FSOT | held-out, agrees | m (21db984) |",
        "| M_pi0 | neutral pion; π±−π0 splitting is EM | Δ_π = 12π α ln2 F² (DGMLY + Weinberg + N_c=3 LMD) | 134.397 MeV | 263.008 | 134.9768(5) PDG 2024 | −0.43 % | FSOT | held-out, agrees (2 % gate) | m |",
        "| M_eta, M_eta' | η8/η1 mixing with U(1)_A anomaly | U(3) LO + Witten–Veneziano (lattice χ_top) | 523.2 / 1136.3 MeV | — | 547.862 / 957.78 | −4.5 % / +18.6 % | hybrid | open | m |",
        "| F (chiral limit) | pion decay constant, chiral limit | F = m_p/(2√3π) (quark-level σ model, M_Q = m_p/3, N_c = 3) | 86.216 MeV | 168.721 | F_0 = 86.69 (FLAG ratio) | −0.55 % | FSOT | agrees | m |",
        "| F_π (physical) | pion decay constant | F[1 + M_π² l̄₄/(16π²F²)], l̄₄ = N_c (tree σ exchange) | 90.508 MeV | 177.121 | 92.07(57) FLAG | −1.69 % | FSOT | agrees (2 % gate) | n (e9b1405) |",
        "| g_A | nucleon axial coupling | valence chiral quark soliton, M = m_p/3, DPP profile | 1.1777 | — | 1.2754(13) PDG | −7.7 % | FSOT | open | n |",
        "| g_πNN | pion–nucleon coupling | Goldberger–Treiman g_A m_N/F_π | 12.22 | — | 13.17(5) | −7.2 % | FSOT | open | n |",
        "| m_ud, m_s (MSbar 2 GeV) | light-quark masses | GMOR with b from L-A1, F (K-1a), Σ = (272/338) Λ⁽³⁾ | 3.603 / 99.68 MeV | — | 3.387(39) / 92.4(1.0) FLAG | +6.4 % / +7.9 % | hybrid | within 10 % | l |",
        "| Λ^(5) | QCD scale | FSOT α_s run | 209.52 MeV | — | 213(8) FLAG | z 0.43 | FSOT | agrees | j |",
        "| r_d (LO) | deuteron point radius | 1/(√8 γ), γ from B(2H) leaf | 1.5265 fm | — | 1.97507(78) | −22.7 % | FSOT | open (needs effective range) | n |", ""]
Path(a.out).write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n") if False else open(a.out, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print("rows", len(rows), n)
