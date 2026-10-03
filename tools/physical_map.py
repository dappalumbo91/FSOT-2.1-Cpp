#!/usr/bin/env python3
"""Generate docs/PHYSICAL_MAP.md from audit/precision_2026-10-02.tsv (the 91 record rows) and the derivation-branch scores (rounds l-q).
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
        "pin:wave3|Deuteron_binding_MeV": "N-3 LO radius -22.7 %; O-3 OPE + core (B input): r_d -4.1 %, Q_d -14 %, eta -7.3 % (fail)", "pin:wave5|Gamma_Z/M_Z": "Delta alpha_had chain gated (g_A = 1.1755, -7.8 %, P-1)",
        "pin:wave8|Deuteron_mu_muN": "O-3b SU(6) mu_d +3.8 %; P-2 soliton mu_d -14 %; Q-1 (m_pi) soliton mu_p -0.96 %, mu_n +0.67 % (late validation passed, round r) -> R-0 mu_d -5.7 % (fail; P_D/meson-exchange currents next)", "m_Z_MeV": "D_eff/S map tests l/m/n fail (factor follows the unit)",
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
       "- **Status legend.** confirmed = record row with z ≤ 1 at pin AEB2AD; frozen-pending = a frozen refinement passes but is not adopted; external = uses a non-FSOT (lattice/FLAG/fit) input and is scaffolding only, listed in its own table and never counted; open = not yet within its gate.", "",
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
        "## Derivation-branch quantities (rounds l–s; FSOT inputs only; not record rows)", "",
        "| quantity | physical meaning | FSOT derivation | frozen value | ratio to m_e | measured (source) | rel | class | held-out / status | freeze |",
        "|---|---|---|---|---|---|---|---|---|---|",
        "| M_K0 | neutral kaon (pseudo-Goldstone, m_d + m_s) | LO ChPT + Dashen from π±, K± leaves and pins m_u/m_d, m_s/m_d | 497.597 MeV | 973.773 | 497.611(13) PDG 2024 | −0.003 % | FSOT | held-out, agrees | l (9c6dbbc) |",
        "| M_K0 (Q route) | same, via L5/L8-free Q | Q = 22.7315 from pins + EM | 498.272 MeV | — | 497.611(13) | +0.13 % | FSOT | held-out, agrees | m (21db984) |",
        "| M_pi0 | neutral pion; π±−π0 splitting is EM | Δ_π = 12π α ln2 F² (DGMLY + Weinberg + N_c=3 LMD) | 134.397 MeV | 263.008 | 134.9768(5) PDG 2024 | −0.43 % | FSOT | held-out, agrees (2 % gate) | m |",
        "| F (chiral limit) | pion decay constant, chiral limit | F = m_p/(2√3π) (quark-level σ model, M_Q = m_p/3, N_c = 3) | 86.216 MeV | 168.721 | F_0 = 86.69 (FLAG ratio) | −0.55 % | FSOT | agrees | m |",
        "| F_π (physical) | pion decay constant | F[1 + M_π² l̄₄/(16π²F²)], l̄₄ = N_c (tree σ exchange) | 90.508 MeV | 177.121 | 92.07(57) FLAG | −1.69 % | FSOT | agrees (2 % gate) | n (e9b1405) |",
        "| g_A | nucleon axial coupling | valence chiral quark soliton, M = m_p/3, DPP profile | 1.1777 | — | 1.2754(13) PDG | −7.7 % | FSOT | open | n |",
        "| g_πNN | pion–nucleon coupling | Goldberger–Treiman g_A m_N/F_π | 12.22 | — | 13.17(5) | −7.2 % | FSOT | open | n |",
        "| Λ^(5) | QCD scale | FSOT α_s run | 209.52 MeV | — | 213(8) FLAG | z 0.43 | FSOT | agrees | j |",
        "| Λ^(4), Λ^(3) (FSOT thresholds) | QCD scales below m_b, m_c | J-1 4-loop running from FSOT α_s, M_Z with FSOT-only decoupling at m_b = m_t/(m_t/m_b) = 4.222 GeV, m_c = 1.284 GeV | 292.07 / 334.43 MeV | — | 295(10) / 338(10) FLAG | z 0.29 / 0.36 | FSOT | agree (replaces the external-threshold J-1 rows); Λ^(0)/Λ^(3) is an open derivation (needs an FSOT pure-gauge hadronic scale) | s2 |",
        "| χ_top^{1/4} (gluon condensate) | topological susceptibility | pin ⟨(α_s/π)G²⟩ = C_cosm − e⁻³ (read in GeV⁴) → instanton density n = ⟨(α_s/π)G²⟩/8 → χ = n | 200.13 MeV | — | 185.3(5.7) quenched | +8.0 % | FSOT | passes 10 % (validation SVZ +6.2 % passed); Λ^(0) = 294.2 MeV via DP | t |",
        "| M_η, M_η′ (LO U(3)+WV, FSOT χ) | η/η′ masses | round-p mass block, M0² = 6χ/F_π², F_π FSOT (P-4), χ from condensate | 524.9 / 1153.5 MeV | — | 547.862 / 957.78 | −4.2 % / +20.4 % | FSOT | validation failed (LO matrix η′ +18 % even at SVZ χ); F_K/F_π for next order is an open derivation | t |",
        "| r_d (LO) | deuteron point radius | 1/(√8 γ), γ from B(2H) leaf | 1.5265 fm | — | 1.97507(78) | −22.7 % | FSOT | open (needs effective range) | n |",
        "| g_A^(0) (full sea) | nucleon axial coupling, leading order in Ω | chiral quark soliton, Kahana–Ripka basis, Dirac sea + PV (M_PV = √e M), M = m_p/3 | 0.7424 | — | 1.2754(13) PDG | −41.8 % | FSOT | open (soliton unbound, E = 3.41 M; g_A^(1) not included) | o (f393948) |",
        "| M_Δ − M_N | rotational splitting 3/(2I) | same soliton, cranking inertia | 177.2 MeV | — | 293.1 | −39.5 % | FSOT | held-out, fails | o |",
        "| r_d, Q_d, η (OPE) | deuteron radius, quadrupole, D/S ratio | 3S1–3D1 with FSOT g_πNN, m_π; core R = ħc/M_Q fitted to B(2H) leaf | 1.8946 fm / 0.2451 fm² / 0.02373 | — | 1.97507 / 0.285699 / 0.0256 | −4.1 / −14.2 / −7.3 % | FSOT | held-out, fail (validation passes Q_d, η) | o |",
        "| μ_n | neutron magnetic moment | SU(6) −(2/3) μ_p with FSOT μ_p leaf | −1.86190 μ_N | — | −1.91304276 CODATA | −2.67 % | FSOT | fails 2 % gate | o |",
        "| μ_d | deuteron magnetic moment | μ_p + μ_n − (3/2)(μ_S − ½) P_D, P_D = 6.28 % | 0.89035 μ_N | — | 0.8574382335 CODATA | +3.84 % | FSOT | fails | o |",
        "| g_A (Ω⁰ + Ω¹) | nucleon axial coupling incl. 1/N_c rotational term | full-sea soliton, DPP profile, g_A^(1) from time-ordered collective operators | 1.1755 | — | 1.2754(13) | −7.8 % | FSOT | open (validation 1.2046 passes 10 %) | p (98cd271) |",
        "| μ_p, μ_n (soliton) | nucleon magnetic moments | isoscalar Ω¹ + isovector Ω⁰ + Ω¹, chiral limit | 3.273 / −2.513 μ_N | — | 2.7928 / −1.9130 | +17 % / +31 % | FSOT | fail | p |",
        "| g_A, μ_p, μ_n (physical m_π) | nucleon axial coupling and magnetic moments | full-sea soliton with meson mass term (π± leaf), massive DPP profile, D 10 / k 10 / K 8 | 1.3912 / 2.7660 / −1.9258 | — | 1.2754 / 2.7928 / −1.9130 | +9.1 % / −0.96 % / +0.67 % | FSOT | g_A fails; μ_p, μ_n within 2 % at K 8 with the late validation passing (round r), but NOT basis-stable: at K 12 (round t) μ_p −5.4 %, μ_n −6.2 % | q (d7a9af6), r, t |",
        "| g_A separation (chiral, K 8) | nucleon axial coupling, diagnostic | chiral DPP in the round-q basis | 1.1547 | — | 1.2754 | −9.5 % | FSOT | basis cap −1.8 %; pion-mass step +20.5 % via the Dirac-sea axial sum (0.011 → 0.156) and g_A^(1) (+22 %); fix deferred | s |",
        "| g_A, μ_p, μ_n (physical m_π, K 12) | basis check of the round-q soliton | massive DPP at D 12 / k 12 / K 12 | 1.4327 / 2.6417 / −1.7947 | — | 1.2754 / 2.7928 / −1.9130 | +12.3 % / −5.4 % / −6.2 % | FSOT | all fail: the round-q K 8 μ_p, μ_n agreement (round r) is not basis-stable; Δ−N 177.5 MeV; ordering/surface corrections open | t |",
        "| F_π (one-loop LσM l̄₄) | pion decay constant | l̄₄ = N_c + ln(m_σ²/M_π²) − (19 − 3√3π)/2 = 4.662 (Nyffeler–Schenk) | 92.887 MeV | — | 92.07(57) | +0.89 % | FSOT | agrees (2 %), validation passes; pre-freeze evaluation disclosed | p |",
        "| μ_d (soliton m_π) | deuteron magnetic moment | Q-1 μ_p + μ_n, round-o P_D | 0.80815 μ_N | — | 0.857438 | −5.7 % | FSOT | fails 2 % (K 8 inputs; not basis-stable) | r |",
        "| T_CMB (own physics) | CMB temperature | n_γ = Ω_b h² ρ_c100/(u η) | 2.73233 K | — | 2.7255(6) | +0.25 % (z 11) | FSOT | fail z ≤ 1 | p |",
        "| F_π (l̄₄ = 1 + ln M_Q²/M_π²) | pion decay constant | PV quark loop: dF²/dM² = 0 at the FSOT point | 89.956 MeV | — | 92.07(57) FLAG | −2.29 % | FSOT | fails 2 % gate (l̄₄ = 2.61) | o |",
        "", "## External-input scaffolding (not FSOT results; never in confirmed or agreeing counts)", "",
        "Owner directive 2026-10-03 01:44 ET: anything using an outside lattice/fit number is scaffolding only. Verdicts below are kept for the record but are not FSOT agreements.", "",
        "| quantity | physical meaning | route (external input named) | value | ratio to m_e | measured (source) | rel | class | held-out / status | freeze |",
        "|---|---|---|---|---|---|---|---|---|---|",
        "| M_eta, M_eta' | η8/η1 mixing with U(1)_A anomaly | U(3) LO + Witten–Veneziano (lattice χ_top) | 523.2 / 1136.3 MeV | — | 547.862 / 957.78 | −4.5 % / +18.6 % | external | open | m |",
        "| m_ud, m_s (MSbar 2 GeV) | light-quark masses | GMOR with b from L-A1, F (K-1a), Σ = (272/338) Λ⁽³⁾ | 3.603 / 99.68 MeV | — | 3.387(39) / 92.4(1.0) FLAG | +6.4 % / +7.9 % | external | within 10 % | l |",
        "| χ_top^{1/4} | topological susceptibility | DP instanton liquid 0.65 e^{1/22} Λ^(3) | 229.2 MeV | — | 185.3(5.7) quenched | +23.7 % | external | fail | p |",
        "| χ_top^{1/4} (quenched Λ) | topological susceptibility | trace: DP density, size, packing and e^{1/22} are pure-gauge; fix Λ^(0) = R Λ^(3), R = 0.624/0.808 (FLAG 2021, r0) | 177.0 MeV | — | 185.3(5.7) | −4.5 % | external | passes 10 % (validation passed); η −7.6 %, η′ +5.8 % with the LO U(3)+WV matrix (next step) | r |",
        "| M_η, M_η′ (FKS, next order) | η/η′ masses | quark-flavour mixing, f_q = FSOT F_π, f_s = f_q√(2r²−1) (FLAG F_K/F_π), a² = 2χ/f_q², χ from R-1 | 538.4 / 882.6 MeV | — | 547.862 / 957.78 | −1.7 % / −7.9 % | external | η passes 5 %, η′ fails (a² 0.228 vs 0.265 GeV²: χ is the remaining step); φ = 37.7° | s |", ""]
Path(a.out).write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n") if False else open(a.out, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print("rows", len(rows), n)
