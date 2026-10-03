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
def kind(x):
    """owner directive 2026-10-03 02:39: reference type of each row"""
    i = x["#id"]
    if any(k in i for k in ("H0", "Neutron_lifetime")): return "contested (deferred)"
    if any(k in i for k in ("MSbar", "alpha_s", "m_c_over_m_b", "m_u/m_d", "m_t_over_m_W", "m_H/m_t")): return "scheme-dependent"
    if "T_CMB" not in i and i.startswith(("pin:wave1", "pin:wave2", "od2:wave2", "pin:wave3/Age", "pin:wave3/z_eq", "pin:wave3/r_star", "pin:wave4/w0", "pin:wave5/Y_p", "pin:wave5/D_H", "pin:wave8/S_8", "pin:wave8/z_reion", "pin:wave10")):
        return "model-computed (cosmological fit)"
    if i.startswith("CKM_") or "Jarlskog" in i or "delta_CP" in i or "sin2_theta1" in i or "sin2_theta23" in i or "dm2" in i or "Dm2" in i: return "model-computed (global fit / theory input)"
    return "measured"

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
       "- **Reference type (owner directive 2026-10-03 02:39).** FSOT scores against observations. Every row carries a type: measured, model-computed (fit or theory input), lattice-computed, scheme-dependent, or contested (deferred: H0, neutron lifetime). Computed quantities (χ_top, Λ^(0), the condensate, string tension, r0) are intermediate FSOT quantities, scored only through the observables they feed (χ_top through M_η′ via Witten–Veneziano). A gap to a lattice value is information, not a miss. In the derivation and scaffolding tables the type is the last word of the class column.\n- **Status legend.** confirmed = record row with z ≤ 1 at pin AEB2AD; owner standing rule: only z ≤ 1 against the published uncertainty agrees, percentage gates never count as a pass; frozen-pending = a frozen refinement passes but is not adopted; external = uses a non-FSOT (lattice/FLAG/fit) input and is scaffolding only, listed in its own table and never counted; open = not yet within its gate.", "",
       "## The 91 record rows", "",
       "| id | physical quantity | anchor unit | ratio to anchor | FSOT route | frozen value | unit | measured (source) | z | status | reference type | held-out tests |",
       "|---|---|---|---|---|---|---|---|---|---|---|---|"]
n = {"confirmed": 0, "frozen-pending": 0, "open": 0}
for x in rows:
    u = x["unit"]; an, nm = A.get(u, (1.0, "?"))
    try: ratio = "%.9g" % (float(x["value"]) / an)
    except ValueError: ratio = "-"
    st = status(x); n[st] += 1
    src = re.sub(r"\s*https?://\S+", "", x["source"]).strip().replace("|", "/")[:70]
    out.append(f"| `{x['#id'].replace('|', '/')}` | {meaning(x)} | {nm} | {ratio} | {x['route']} | {x['value']} | {u} | {x['central']} ({src}) | {x['z']} | {st} | {kind(x)} | {HELD.get(x['#id'], '-')} |")
out += ["", f"**Totals:** {n['confirmed']}/91 confirmed, {n['confirmed'] + n['frozen-pending']}/91 including frozen-pending, {n['open'] - 0}/91 open.", "",
        "## Derivation-branch quantities (rounds l–s; FSOT inputs only; not record rows)", "",
        "| quantity | physical meaning | FSOT derivation | frozen value | ratio to m_e | measured (source) | rel | class | held-out / status | freeze |",
        "|---|---|---|---|---|---|---|---|---|---|",
        "| M_K0 | neutral kaon (pseudo-Goldstone, m_d + m_s) | LO ChPT + Dashen from π±, K± leaves and pins m_u/m_d, m_s/m_d | 497.597 MeV | 973.773 | 497.611(13) PDG 2024 | −0.003 % | FSOT · measured | held-out, miss at z 1.08 (σ 0.013 MeV) | l (9c6dbbc) |",
        "| M_K0 (Q route) | same, via L5/L8-free Q | Q = 22.7315 from pins + EM | 498.272 MeV | — | 497.611(13) | +0.13 % | FSOT · measured | held-out, miss (z 51) | m (21db984) |",
        "| M_pi0 | neutral pion; π±−π0 splitting is EM | Δ_π = 12π α ln2 F² (DGMLY + Weinberg + N_c=3 LMD) | 134.397 MeV | 263.008 | 134.9768(5) PDG 2024 | −0.43 % | FSOT · measured | held-out, miss (z 1160; the 2 % gate does not count) | m |",
        "| F (chiral limit) | pion decay constant, chiral limit | F = m_p/(2√3π) (quark-level σ model, M_Q = m_p/3, N_c = 3) | 86.216 MeV | 168.721 | F_0 = 86.69 (FLAG ratio) | −0.55 % | FSOT · lattice-computed | agrees at z 0.61 (σ 0.78 from FLAG F_π and F_π/F) | m |",
        "| F_π (physical) | pion decay constant | F[1 + M_π² l̄₄/(16π²F²)], l̄₄ = N_c (tree σ exchange) | 90.508 MeV | 177.121 | 92.07(57) FLAG | −1.69 % | FSOT · measured | miss (z 2.74; the 2 % gate does not count) | n (e9b1405) |",
        "| g_A | nucleon axial coupling | valence chiral quark soliton, M = m_p/3, DPP profile | 1.1777 | — | 1.2754(13) PDG | −7.7 % | FSOT · measured | open | n |",
        "| g_πNN | pion–nucleon coupling | Goldberger–Treiman g_A m_N/F_π | 12.22 | — | 13.17(5) | −7.2 % | FSOT · measured | open | n |",
        "| Λ^(5) | QCD scale | FSOT α_s run | 209.52 MeV | — | 213(8) FLAG | z 0.43 | FSOT · scheme-dependent (intermediate; scored via α_s(M_Z)) | agrees | j |",
        "| Λ^(4), Λ^(3) (FSOT thresholds) | QCD scales below m_b, m_c | J-1 4-loop running from FSOT α_s, M_Z with FSOT-only decoupling at m_b = m_t/(m_t/m_b) = 4.222 GeV, m_c = 1.284 GeV | 292.07 / 334.43 MeV | — | 295(10) / 338(10) FLAG | z 0.29 / 0.36 | FSOT · scheme-dependent (intermediate; scored via α_s(M_Z)) | agree (replaces the external-threshold J-1 rows); Λ^(0)/Λ^(3) is an open derivation (needs an FSOT pure-gauge hadronic scale) | s2 |",
        "| χ_top^{1/4} (gluon condensate) | topological susceptibility | pin ⟨(α_s/π)G²⟩ = C_cosm − e⁻³ (read in GeV⁴) → instanton density n = ⟨(α_s/π)G²⟩/8 → χ = n | 200.13 MeV | — | 185.3(5.7) quenched | +8.0 % | FSOT · lattice-computed (intermediate; scored via M_η′) | miss (z 2.60; the 10 % gate does not count); Λ^(0) = 294.2 MeV via DP | t |",
        "| χ_top^{1/4} (trace anomaly, ε fixed) | quenched topological susceptibility | n_0 = (b₃/b₀) ⟨(α_s/π)G²⟩/8 = (9/11)·pin/8 (vacuum energy ε = −(b/32)⟨(α_s/π)G²⟩ held fixed); Λ^(0)/Λ^(3)_FSOT = 0.837 (round t 0.880; lattice r0-fixed 0.772, residual 0.923 = ε- vs r0-matching) | 190.34 MeV | — | 185.3(5.7) quenched | +2.7 % | FSOT · lattice-computed (intermediate; scored via M_η′) | z 0.88, agrees, but the route was chosen post hoc after round t (disclosed; look-elsewhere 3) | u |",
        "| M_η, M_η′ (LO, ε-fixed χ) | η/η′ masses | LO U(3)+WV, FSOT F_π | 514.7 / 1067.0 MeV | — | 547.862 / 957.78 | −6.1 % / +11.4 % | FSOT · measured | miss (LO matrix fails validation; next order needs F_K/F_π) | u |",
        "| M_η, M_η′ (LO U(3)+WV, FSOT χ) | η/η′ masses | round-p mass block, M0² = 6χ/F_π², F_π FSOT (P-4), χ from condensate | 524.9 / 1153.5 MeV | — | 547.862 / 957.78 | −4.2 % / +20.4 % | FSOT · measured | validation failed (LO matrix η′ +18 % even at SVZ χ); F_K/F_π for next order is an open derivation | t |",
        "| g_A, μ_p, μ_n, Δ−N (K → ∞) | nucleon axial coupling, magnetic moments, Δ−N splitting | massive DPP soliton at D = k = K 12/14/16 (windowed scan, validated to 3.8e-10 vs round t); pre-registered Richardson 1/K² from K 14–16, theory unc. = |v_∞ − v_16| | 1.502 / 3.185 / −2.341 / 180.8 MeV | — | 1.2754 / 2.7928 / −1.9130 / 293.1 | +17.8 % / +14.1 % / +22.4 % / −38.3 % | FSOT · measured | g_A miss (z 5.6), Δ−N miss (z 41); μ_p, μ_n z 0.91 / 1.00 count as agrees under the frozen rule, but only because the K 16 jump (μ_p 2.624 → 2.756) makes the theory unc. 7× larger; the sequence does not converge (3-point fit gives 3.97 / −3.11), so this is not evidence of agreement; classical-ordering g_A 0.944 (z 11.6) | v |",
        "| F_K/F_π | kaon/pion decay-constant ratio | one-loop SU(3) ChPT, 4L5^r = l4^r + ν_K/2 (L4 = 0, large N_c), FSOT l̄₄ 4.662, F_π 92.887, μ = 770 MeV | 1.2734 | — | 1.1932(21) FLAG | +6.7 % | FSOT · lattice-computed | miss (z 38); validation with FLAG l̄₄ gives 1.234, so the L4 = 0 step fails; pre-freeze estimate 1.25–1.27 disclosed. Directive (b): next round score via measured F_K/F_π from K_ℓ2/π_ℓ2 (|V_us| route) | v |",
        "| M_η, M_η′ (FKS, FSOT χ) | η/η′ masses | Feldmann–Kroll–Stech, f_q, f_s from V-2, χ from the round-u ε-fixed route (intermediate) | 574.4 / 951.2 MeV | — | 547.862 / 957.78 | +4.8 % / −0.69 % | FSOT · measured | both miss (z 1560 / 110); φ = 45.9°; M_η′ is the observable through which χ_top is scored (directive b) | v |",
        "| μ oscillation (diagnostic) | basis behaviour of the μ_V^(0) sea sum | fixed DPP profile x = 0.8 at D = k = K 12/14/16 | sea sum −0.704 / −0.569 / −0.822 | — | — | — | FSOT · diagnostic | numerics: ε_val (0.629965), I_val (2.2223) and I_sea (0.350→0.359) are K-stable; only the μ_V^(0) sea sum moves, because its grand-spin sectors give ±14–18 near the cutoff and the per-K net (±0.1–0.27) does not decay; driven by the grand-spin cutoff K (D = k 12→16 at K 12 moves it only −0.022, K 12→16 at D = k 16 moves it −0.096); not dynamical; fix (an energy-cutoff mode sum consistent with PV) is next round | w |",
        "| M_Δ − M_N (trace) | rotational splitting 3/(2I) | I M = I_val M + I_sea M = 2.222 + 0.350 at K 12; required 1.600 | 176–183 MeV | — | 293.1 | −38 % | FSOT · measured | the valence inertia alone exceeds the requirement; the weakly bound valence level (ε = 0.63 M) at M = m_p/3 is the failing step (the round-q run at M = 420 MeV gives 296.7 MeV); a J-dependent profile (rotational response) lowers it further, to 152 MeV, and moves μ_p 2.657→2.583 (away from the measured value) | w |",
        "| L5, L8, L4 (scalar saturation) | NLO chiral couplings | L5 = F²/(4M_S²), L8 = F²/(16M_S²), L4 = 0 from a degenerate quark-level scalar nonet, M_S = 2m_p/3 | 4.75e-3 / 1.19e-3 / 0 | — | — | — | FSOT · intermediate (scored via F_K/F_π, η/η′) | F_K/F_π 1.506 (z 149), η 601.0 (z 3128), η′ 907.6 (z 836): all miss; the M_S = 980 MeV validation also gives 1.359, so saturation at one loop overshoots | w |",
        "| WV combination | M_η² + M_η′² − 2M_K² | 6χ/F_π², FSOT χ (intermediate) and F_π | 9.127e5 MeV² | — | 7.301e5 | +25.0 % | FSOT · measured (scores χ_top) | miss; the lattice-χ gap (+2.7 %) is now information only | w |",
        "| M(0) | dynamical quark mass at zero momentum (soliton quark mass) | Diakonov–Petrov instanton-vacuum gap equation, FSOT n (condensate pin, n^{1/4} = 200.13 MeV), ρ = R/3 | 346.07 MeV | — | — | — | FSOT · intermediate (scored via Δ−N, g_A) | validation: DP inputs give 345.8 vs 345 MeV; R/ρ = 3 is the one model constant (disclosed) | x |",
        "| M_Δ − M_N, g_A at M(0) | rotational splitting, axial coupling | massive DPP soliton at M = M(0), F/M = √3/(2π) (frozen), K 12 | 199.7 MeV / 1.4275 | — | 293.1 / 1.2754 | −31.9 % / +11.9 % | FSOT · measured | both miss (z 47 / 117; K 12 only); I M stays at 2.60, because with F/M tied to M the model is nearly scale-free and Δ−N ∝ M; next: keep the FSOT F = 86.2 MeV and set M_PV from the PV condition (the M = 420 / F = 93 MeV run gives I M 2.12) | x |",
        "| energy-cutoff μ sea sum | μ_V^(0) sea sum with |e| < 0.75 k M | fixed profile x = 0.8 | +0.908 (K 12) / −0.700 (K 14) | — | — | — | FSOT · diagnostic | not converged (K 16 not run); the cut changes the sum by O(1), so the high-energy states carry it; μ not rescored | x |",
        "| Γ_Z/M_Z trace | Z width / Z mass | round-i chain: α, M_Z, M_W, m_t, m_H, α_s leaves; Freitas/ACFW SM parametrisations; HAD-2 Δα_had | 0.0273494 | — | 0.0273665(25) | −0.06 % (z 0.68) | FSOT · measured | first diverging step Δα_had^(5) (0.02672, z 18); with the measured Δα_had Γ_Z/M_Z is 0.0273830 (z 0.65), so Γ_Z/M_Z is insensitive to it, but G_F then moves to z ≈ 2000 (second divergence, M_W/Δr step); those coefficients and m_B are hybrids (standing rule), so this chain is scaffolding; see round y | x |",
        "| (M_Δ − M_N)/m_p, g_A (proton units) | rotational splitting, axial coupling | soliton with M/m_p = 0.36883 (gap equation), F/m_p = 1/(2√3π) fixed, M_PV/M = 1.5044 from the PV condition, K 12/14 | 0.24404 (229.0 MeV) / 1.4793 | — | 0.31236 / 1.2754 | −21.9 % / +16.0 % | FSOT · measured | both miss (z 31.5 / 9.0); K-stable (0.24365 → 0.24404); I M 2.267 against the 1.771 needed; μ not scored | y |",
        "| Δα_had^(5) (quark-pole duality) | hadronic vacuum polarisation at M_Z | duality R-ratio with the c, b thresholds at 2 m_Q(pole) from FSOT m_c, m_b (global duality puts the narrow J/ψ, ψ′, Υ below open flavour) | 0.027344 | — | 0.02783(6) | −1.75 % | FSOT · measured | miss (z 8.1; validation 0.027370 fails the unchanged 0.00029 gate); the fix recovers 58 % of the round-i deficit; the rest is the light-quark (ρ/ω) region | y |",
        "| Γ_Z/M_Z (FSOT one-loop chain) | Z width / Z mass | round-f one-loop Δr (Hioki), Δρ × QCD, Y-2 Δα_had, authority A1 width; no fit coefficients | 0.0271726 | — | 0.0273665(25) | −0.71 % | FSOT · measured | miss (z 7.7); next divergent step: Δr = 0.03277 against the SM 0.03685 (G_F z 6494), i.e. the two-loop/higher-order Δr pieces are missing | y |",
        "| soliton inertia I M (trace) | cranking moment of inertia in units of 1/M | round-y inputs, K 12: valence + bare sea + PV at x = 0.70 / 0.92 / 1.20 | 3.025 / 2.271 / 2.130 | — | 1.771 needed | — | FSOT · diagnostic | the valence part alone (1.82 at the minimum) exceeds the need; shrinking the valence part by enlarging the soliton is offset by the sea (bare 3.09 → 5.75 against PV −2.64 → −5.07), so I M stays ≥ 2.1 at every size; Δ−N/m_p ≈ 0.68 (M/m_p), and the diverging step is the absolute quark-mass ratio M/m_p = 0.369 (gap equation, ρ = R/3, GeV⁴ pin reading); no FSOT fix derived, nothing rescored | z |",
        "| Γ_Z/M_Z (higher-order FSOT chain) | Z width / Z mass | Δr with CHJ resummation, O(αα_s²) and O(G_F²m_t⁴) Δρ (FJT ρ^(2), r = M_H/m_t), Hioki Δr_rem, round-y Δα_had, A1 width | 0.0272404 | — | 0.0273665(25) | −0.46 % | FSOT · measured | miss (z 5.0, from 7.7); Δr 0.03518 against the SM 0.03685; G_F z 1657; remaining: Δα_had (−0.0005) and the higher-order Δr_rem | z |",
        "| T_CMB (radiation density) | CMB temperature | Ω_γ = Ω_r/(1 + 0.2271 N_eff), ρ_γ = Ω_γ ρ_c, Stefan–Boltzmann; FSOT Ω_r, N_eff, H0 | 2.74345 K | — | 2.7255(6) | +0.66 % | FSOT · measured | information (post-freeze; uses the deferred H0); FSOT Ω_r h² is 2.7 % above the FIRAS-implied value | z |",
        "| M/m_p (unit-free condensate reading) | dynamical quark mass / proton mass | DP gap equation, ⟨(α_s/π)G²⟩/m_p⁴ = C_cosm − e⁻³, ρ = R/3 | 0.346067 | — | ≈0.46 (diagnostic from Δ−N) | — | FSOT · intermediate | scored via Δ−N/m_p 0.2118 (z 47.2) and g_A 1.438 (z 124.7); moves away from the diagnostic | aa |",
        "| Δα_had^(5) (KSRF light quarks) | hadronic vacuum polarisation at M_Z | narrow ρ + ω (VMD, KSRF m_ρ² = 2g²F², g² = 12π²/N_c) below s0 = 16π²F², u,d continuum above; FSOT P-4 F_π | 0.025825 | — | 0.02783(6) | −7.2 % | FSOT · measured | miss (z 33.4); validation fails (0.025877); g²/4π = π underestimates Γ(ρ→ee) | aa |",
        "| kT_rec/(m_e α²) (Saha) | recombination temperature | hydrogen Saha x_e = 1/2 with FSOT η, α | 0.011915 | — | — | — | FSOT · model-computed | information; no FSOT z_* or Ω_b h² pin, so no T_CMB route without H0 | aa |",
        "| R/ρ̄ (DP variational) | instanton spacing / size | n ρ̄⁴ = ν/(β(ρ̄)γ²), one-loop β, FSOT n and round-t Λ^(0) | 2.468 | — | 3 (DP model) | — | FSOT · intermediate | M/m_p 0.4582 → Δ−N/m_p 0.3356 (z 10.9, edge), g_A 1.498 (z 171); β 5.2, packing 0.27 (not dilute) | ab |",
        "| B_d (central OPE + σ + ω) | deuteron binding | 3S1 central point Yukawas: GT f² with soliton g_A, σ (2M, 3M/F), ω (KSRF, 6π) | unbound | — | 2.22456623 MeV | — | FSOT · measured | trace step 1: OPE central unbound, +σ too deep, +ω unbound; tensor force next | ab |",
        "| B_d (tensor OPE + σ + ω, soliton FF) | deuteron binding | 3S1–3D1, monopole Λ = √6/r_B = 0.893 m_p from the soliton baryon radius; soliton g_A; σ (2M, 3M/F), ω (KSRF, 6π) | unbound | — | 2.22456623 MeV | — | FSOT · measured | miss; OPE alone 4.0 MeV, +σ 234 MeV, +ω unbound: σ/ω couplings diverge first | ac |",
        "| Ω_m/Ω_b (FSOT) | matter-to-baryon density ratio | (Ω_DM h² + Ω_b h²)/Ω_b h², FSOT pins | 6.3685 | — | 6.364 (Planck, info) | — | FSOT · intermediate | feeds T_ls = 3501 K (Saha + τ = 1, info); T_CMB still needs T_0 | ac |",
        "| g_A (PV-regularised rotational term) | axial coupling | g_A^(0) 0.9037 + time-ordered g1 with PV-subtracted sea (Im A_reg 0.7944, I M 2.0862), M/m_p 0.458168, K 12 | 1.28451 | — | 1.2754(13) | +0.71 % | FSOT · measured | miss (z 7.0; was z 202 unregularised) | ad |",
        "| B_d (soliton σ, ω, tensor OPE) | deuteron binding | σNN from the valence scalar charge 0.508 with r_S form factor; ω 6π (baryon number); OPE with g_A 1.2845 | unbound | — | 2.22456623 MeV | — | FSOT · measured | miss; OPE+σ 7.5 MeV, +ω unbound (ω form factor next) | ad |",
        "| T_CMB (FSOT age) | CMB temperature | t_0 = ∫dT/(T H), FSOT age, r_mb 6.3685, Ω_Λ h² via Ω_m, η, N_eff; no H0 pin | 2.72847 K | — | 2.7255(6) | +0.11 % | FSOT · measured | miss (z 4.96) | ad |",
        "| r_d (LO) | deuteron point radius | 1/(√8 γ), γ from B(2H) leaf | 1.5265 fm | — | 1.97507(78) | −22.7 % | FSOT · measured | open (needs effective range) | n |",
        "| g_A^(0) (full sea) | nucleon axial coupling, leading order in Ω | chiral quark soliton, Kahana–Ripka basis, Dirac sea + PV (M_PV = √e M), M = m_p/3 | 0.7424 | — | 1.2754(13) PDG | −41.8 % | FSOT · measured | open (soliton unbound, E = 3.41 M; g_A^(1) not included) | o (f393948) |",
        "| M_Δ − M_N | rotational splitting 3/(2I) | same soliton, cranking inertia | 177.2 MeV | — | 293.1 | −39.5 % | FSOT · measured | held-out, fails | o |",
        "| r_d, Q_d, η (OPE) | deuteron radius, quadrupole, D/S ratio | 3S1–3D1 with FSOT g_πNN, m_π; core R = ħc/M_Q fitted to B(2H) leaf | 1.8946 fm / 0.2451 fm² / 0.02373 | — | 1.97507 / 0.285699 / 0.0256 | −4.1 / −14.2 / −7.3 % | FSOT · measured | held-out, fail (validation passes Q_d, η) | o |",
        "| μ_n | neutron magnetic moment | SU(6) −(2/3) μ_p with FSOT μ_p leaf | −1.86190 μ_N | — | −1.91304276 CODATA | −2.67 % | FSOT · measured | fails 2 % gate | o |",
        "| μ_d | deuteron magnetic moment | μ_p + μ_n − (3/2)(μ_S − ½) P_D, P_D = 6.28 % | 0.89035 μ_N | — | 0.8574382335 CODATA | +3.84 % | FSOT · measured | fails | o |",
        "| g_A (Ω⁰ + Ω¹) | nucleon axial coupling incl. 1/N_c rotational term | full-sea soliton, DPP profile, g_A^(1) from time-ordered collective operators | 1.1755 | — | 1.2754(13) | −7.8 % | FSOT · measured | open (validation 1.2046 passes 10 %) | p (98cd271) |",
        "| μ_p, μ_n (soliton) | nucleon magnetic moments | isoscalar Ω¹ + isovector Ω⁰ + Ω¹, chiral limit | 3.273 / −2.513 μ_N | — | 2.7928 / −1.9130 | +17 % / +31 % | FSOT · measured | fail | p |",
        "| g_A, μ_p, μ_n (physical m_π) | nucleon axial coupling and magnetic moments | full-sea soliton with meson mass term (π± leaf), massive DPP profile, D 10 / k 10 / K 8 | 1.3912 / 2.7660 / −1.9258 | — | 1.2754 / 2.7928 / −1.9130 | +9.1 % / −0.96 % / +0.67 % | FSOT · measured | g_A fails; μ_p, μ_n within 2 % at K 8 with the late validation passing (round r), but NOT basis-stable: at K 12 (round t) μ_p −5.4 %, μ_n −6.2 % | q (d7a9af6), r, t |",
        "| g_A separation (chiral, K 8) | nucleon axial coupling, diagnostic | chiral DPP in the round-q basis | 1.1547 | — | 1.2754 | −9.5 % | FSOT · diagnostic | basis cap −1.8 %; pion-mass step +20.5 % via the Dirac-sea axial sum (0.011 → 0.156) and g_A^(1) (+22 %); fix deferred | s |",
        "| g_A, μ_p, μ_n (physical m_π, K 12) | basis check of the round-q soliton | massive DPP at D 12 / k 12 / K 12 | 1.4327 / 2.6417 / −1.7947 | — | 1.2754 / 2.7928 / −1.9130 | +12.3 % / −5.4 % / −6.2 % | FSOT · measured | all fail: the round-q K 8 μ_p, μ_n agreement (round r) is not basis-stable; Δ−N 177.5 MeV; ordering/surface corrections open | t |",
        "| F_π (one-loop LσM l̄₄) | pion decay constant | l̄₄ = N_c + ln(m_σ²/M_π²) − (19 − 3√3π)/2 = 4.662 (Nyffeler–Schenk) | 92.887 MeV | — | 92.07(57) | +0.89 % | FSOT · measured | miss (z 1.43; the 2 % gate does not count); pre-freeze evaluation disclosed | p |",
        "| μ_d (soliton m_π) | deuteron magnetic moment | Q-1 μ_p + μ_n, round-o P_D | 0.80815 μ_N | — | 0.857438 | −5.7 % | FSOT · measured | fails 2 % (K 8 inputs; not basis-stable) | r |",
        "| T_CMB (own physics) | CMB temperature | n_γ = Ω_b h² ρ_c100/(u η) | 2.73233 K | — | 2.7255(6) | +0.25 % (z 11) | FSOT · measured | fail z ≤ 1 | p |",
        "| F_π (l̄₄ = 1 + ln M_Q²/M_π²) | pion decay constant | PV quark loop: dF²/dM² = 0 at the FSOT point | 89.956 MeV | — | 92.07(57) FLAG | −2.29 % | FSOT · measured | fails 2 % gate (l̄₄ = 2.61) | o |",
        "", "## External-input scaffolding (not FSOT results; never in confirmed or agreeing counts)", "",
        "Owner directive 2026-10-03 01:44 ET: anything using an outside lattice/fit number is scaffolding only. Verdicts below are kept for the record but are not FSOT agreements.", "",
        "| quantity | physical meaning | route (external input named) | value | ratio to m_e | measured (source) | rel | class | held-out / status | freeze |",
        "|---|---|---|---|---|---|---|---|---|---|",
        "| Γ_Z/M_Z (round-i GZ-1) | Z width / Z mass | Freitas and ACFW SM fit-formula coefficients; m_B = 5.279 GeV open-bottom threshold in HAD-2 | 0.0273494 | — | 0.0273665(25) | −0.06 % | external · measured | z 0.68 is not an FSOT result (hybrid under the standing rule; moved round y) | i, y |",
        "| M_eta, M_eta' | η8/η1 mixing with U(1)_A anomaly | U(3) LO + Witten–Veneziano (lattice χ_top) | 523.2 / 1136.3 MeV | — | 547.862 / 957.78 | −4.5 % / +18.6 % | external · measured | open | m |",
        "| m_ud, m_s (MSbar 2 GeV) | light-quark masses | GMOR with b from L-A1, F (K-1a), Σ = (272/338) Λ⁽³⁾ | 3.603 / 99.68 MeV | — | 3.387(39) / 92.4(1.0) FLAG | +6.4 % / +7.9 % | external · scheme-dependent | within 10 % | l |",
        "| χ_top^{1/4} | topological susceptibility | DP instanton liquid 0.65 e^{1/22} Λ^(3) | 229.2 MeV | — | 185.3(5.7) quenched | +23.7 % | external · lattice-computed (intermediate; scored via M_η′) | fail | p |",
        "| χ_top^{1/4} (quenched Λ) | topological susceptibility | trace: DP density, size, packing and e^{1/22} are pure-gauge; fix Λ^(0) = R Λ^(3), R = 0.624/0.808 (FLAG 2021, r0) | 177.0 MeV | — | 185.3(5.7) | −4.5 % | external · lattice-computed (intermediate; scored via M_η′) | miss (z 1.46); η −7.6 %, η′ +5.8 % with the LO U(3)+WV matrix (next step) | r |",
        "| M_η, M_η′ (FKS, next order) | η/η′ masses | quark-flavour mixing, f_q = FSOT F_π, f_s = f_q√(2r²−1) (FLAG F_K/F_π), a² = 2χ/f_q², χ from R-1 | 538.4 / 882.6 MeV | — | 547.862 / 957.78 | −1.7 % / −7.9 % | external · measured | η passes 5 %, η′ fails (a² 0.228 vs 0.265 GeV²: χ is the remaining step); φ = 37.7° | s |", ""]
Path(a.out).write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n") if False else open(a.out, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print("rows", len(rows), n)
