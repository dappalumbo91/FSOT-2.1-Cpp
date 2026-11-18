# IRONOUT-1: first iron-out pass (Damian t995u / t987u, 2026-11-11)

Branch `ironout-1` from `2fd608d` (§43.5vt fold). Everything is **local**: nothing is pushed or merged. Every physics fix is
DERIVED from rows the engine already has in bar. Nothing measured is pasted in, no parameter is fitted, and no formula is
retuned to a target. The authority closed forms (`closed_forms*.gen.inc`) and the parity column are untouched. Every row
touched here has archive status "numerically reproduced"; none is Lean-verified, so no Lean expression is altered.

| # | commit | what |
|---|---|---|
| 1 | b6ea9fe | Γ_Z/M_Z is scored from the tip in-bar leaf (φ⁵/e⁶)(1−α/φ) (`gz:Gamma_Z_over_M_Z`) and never from the vt SM-parity G_F. The A1-at-vt-G_F stays a BEFORE_AFTER §4 diagnostic. G_F, τ_n and τ_μ still carry the vt G_F. |
| 2 | 36b5e3b | Critical exponents (d = 3) by Josephson / Rushbrooke / Fisher / Widom. 3D Ising comes from the in-bar `Ising3D_nu_dyn`/`Ising3D_beta_dyn`, and O(2) β, γ from the in-bar `XY_nu`/`XY_eta`. The wave3 `Ising2D_*` rows are relabeled 3D (archive key kept, targets unchanged). |
| 3 | 4b6a1d2 | IE_H from the leaves R∞, α, m_p/m_e: reduced-mass Dirac 1s minus the one-loop 1s Lamb shift. |
| 6 | b6c34e3, eb1a269, d13fdcb | CRITERIA only (docs/single_engine/SCORING_CRITERIA_IRONOUT_1.md, reference/scoring_criteria_ironout1.tsv). |
| — | (this commit) | tests/test_ironout1.cpp (ctest `ironout1`) and this document. |

Archive tool (outside this repo, /workspace/fsot_unified master, local): `2aaf690` check.py [10] exempts IRONOUT-1 rows from the archive's D-02/D-04 sensitivity flags. Only Ising2D_gamma was D-04-sensitive, and the derived row no longer reads S_QUANT.

## Formulas
- 3D Ising (ν, β = dynamical_systems ν_dyn, β_dyn):
  - α = 2 − 3ν
  - γ = 3ν − 2β
  - η = 2 − γ/ν
  - δ = 1 + γ/β
  - wave3 β, ν are the dyn values.
- O(2) (ν, η = wave7 XY_nu, XY_eta):
  - β = ν(1+η)/2
  - γ = ν(2−η)
- IE_H = μc²[1 − √(1−α²)] − (4α⁵mc²/3π)μ³[ln α⁻² − ln k₀(1s) + 19/30]
  - mc² = 2R∞hc/α²
  - μ = 1/(1 + m_e/m_p)
  - ln k₀(1s) = 2.984128555765 is the Bethe logarithm, a pure number of the Coulomb problem.
  - Without the Lamb term, IE_H = 13.598468, z +0.34, still in bar.

## Before → after (scorecard logic, gf_trace_20261111/scorecard/ironout1/build_ironout1.py; before = the same logic on 2fd608d)
| row | FSOT before → after | target before → after | z before → after | verdict before → after | cause |
|---|---|---|---|---|---|
| `43.5pp-DM2_21_SOLAR [V_tip_pathA]` | 7.524671245e-05 → 7.524671245e-05 | 6.1e-05±9.5e-06 → 7.49e-05±1.9e-06 | +1.50 → +0.18 | BEYOND-SM → IN-BAR | #6 criteria: world-average primary |
| `43.5pq-DM2_21_KAMLAND [V_tip_pathA]` | 7.524671245e-05 → 7.524671245e-05 | 7.53e-05±1.8e-06 → 7.49e-05±1.9e-06 | -0.03 → +0.18 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5pt-MW_CMS [V_tip_MeV]` | 80368.75192 → 80368.75192 | 80360.2±9.9 → 80369.2±13.3 | +0.86 → -0.03 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5pu-MW_ATLAS [V_tip_MeV]` | 80368.75192 → 80368.75192 | 80366.5±15.9 → 80369.2±13.3 | +0.14 → -0.03 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5pv-MW_LEP [V_tip_MeV]` | 80368.75192 → 80368.75192 | 80376±33 → 80369.2±13.3 | -0.22 → -0.03 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5py-MTAU_BELLE2 [V_tip_MeV]` | 1777.00164 → 1777.00164 | 1777.09±0.136015 → 1776.93±0.09 | -0.65 → +0.80 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5pz-MTAU_BESIII [V_tip_MeV]` | 1777.00164 → 1777.00164 | 1776.91±0.176918 → 1776.93±0.09 | +0.52 → +0.80 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5qa-MTAU_KEDR [V_tip_MeV]` | 1777.00164 → 1777.00164 | 1776.81±0.291548 → 1776.93±0.09 | +0.66 → +0.80 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5qd-MZ_ALEPH [V_tip_MeV]` | 91187.37036 → 91187.37036 | 91188.5±3.1 → 91188±2 | -0.36 → -0.31 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5qe-MZ_DELPHI [V_tip_MeV]` | 91187.37036 → 91187.37036 | 91186.3±2.8 → 91188±2 | +0.38 → -0.31 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5qf-MZ_L3 [V_tip_MeV]` | 91187.37036 → 91187.37036 | 91189.8±3.1 → 91188±2 | -0.78 → -0.31 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5qg-MZ_OPAL [V_tip_MeV]` | 91187.37036 → 91187.37036 | 91185.2±3 → 91188±2 | +0.72 → -0.31 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5qj-GZ_ALEPH_TIP [V_tip_MeV]` | 2495.415672 → 2495.415672 | 2495.1±4.3 → 2495.5±2.3 | +0.07 → -0.04 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5qk-GZ_DELPHI_TIP [V_tip_MeV]` | 2495.415672 → 2495.415672 | 2487.6±4.1 → 2495.5±2.3 | +1.91 → -0.04 | OUTSIDE-ACCEPTED → IN-BAR | #6 criteria: world-average primary |
| `43.5ql-GZ_L3_TIP [V_tip_MeV]` | 2495.415672 → 2495.415672 | 2502.4±4.2 → 2495.5±2.3 | -1.66 → -0.04 | SM-PARITY → IN-BAR | #6 criteria: world-average primary |
| `43.5qm-GZ_OPAL_TIP [V_tip_MeV]` | 2495.415672 → 2495.415672 | 2494.8±4.1 → 2495.5±2.3 | +0.15 → -0.04 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5qp-DPM_KEDR_TIP [V_tip_MeV]` | 1869.660259 → 1869.660259 | 1869.56±0.307937 → 1869.66±0.05 | +0.33 → +0.01 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5qq-DPM_ACCMOR_TIP [V_tip_MeV]` | 1869.660259 → 1869.660259 | 1870±1.11803 → 1869.66±0.05 | -0.30 → +0.01 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5qr-DPM_SPEAR_TIP [V_tip_MeV]` | 1869.660259 → 1869.660259 | 1869.4±0.6 → 1869.66±0.05 | +0.43 → +0.01 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5qw-MK_LUM_TIP [V_tip_MeV]` | 493.6802113 → 493.6802113 | 493.64±0.054 → 493.677±0.015 | +0.74 → +0.21 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5qx-MK_BARKOV_TIP [V_tip_MeV]` | 493.6802113 → 493.6802113 | 493.67±0.029 → 493.677±0.015 | +0.35 → +0.21 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5qy-MK_CHENG_TIP [V_tip_MeV]` | 493.6802113 → 493.6802113 | 493.657±0.02 → 493.677±0.015 | +1.16 → +0.21 | BEYOND-SM → IN-BAR | #6 criteria: world-average primary |
| `43.5qz-MK_BACKENSTOSS_TIP [V_tip_MeV]` | 493.6802113 → 493.6802113 | 493.691±0.04 → 493.677±0.015 | -0.27 → +0.21 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5rc-RP_CREMA2013_TIP [V_tip_fm]` | 0.841248541 → 0.841248541 | 0.84087±0.00039 → 0.84075±0.00064 | +0.97 → +0.78 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5rd-RP_PRAD_TIP [V_tip_fm]` | 0.841248541 → 0.841248541 | 0.831±0.01389 → 0.84075±0.00064 | +0.74 → +0.78 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5re-RP_BEZGINOV_TIP [V_tip_fm]` | 0.841248541 → 0.841248541 | 0.833±0.01 → 0.84075±0.00064 | +0.82 → +0.78 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5rf-RP_BEYER_TIP [V_tip_fm]` | 0.841248541 → 0.841248541 | 0.8335±0.0095 → 0.84075±0.00064 | +0.82 → +0.78 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5rh-RP_GRININ_TIP [V_tip_fm]` | 0.841248541 → 0.841248541 | 0.8482±0.0038 → 0.84075±0.00064 | -1.83 → +0.78 | SM-PARITY → IN-BAR | #6 criteria: world-average primary |
| `43.5rl-MH_ATLAS2023_TIP [V_tip_GeV]` | 125.1580977 → 125.1580977 | 125.11±0.11 → 125.2±0.11 | +0.44 → -0.38 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5rm-MH_CMS2024_TIP [V_tip_GeV]` | 125.1580977 → 125.1580977 | 125.04±0.12 → 125.2±0.11 | +0.98 → -0.38 | IN-BAR → IN-BAR | #6 criteria: world-average primary |
| `43.5rn-MH_CMS2020_TIP [V_tip_GeV]` | 125.1580977 → 125.1580977 | 125.38±0.14 → 125.2±0.11 | -1.59 → -0.38 | BEYOND-SM → IN-BAR | #6 criteria: world-average primary |
| `Z-2 Gamma_Z/M_Z (A1 width) [Gamma_Z/M_Z [vt P2 G_F]]` | 0.02727599459 → (removed) | 0.02736653946±2.523e-05 → — | -3.59 → — | OUTSIDE-ACCEPTED → — | #1 tip leaf, G_F-independent |
| `Z-2 Gamma_Z/M_Z (A1 width) [Gamma_Z/M_Z [vt P1 G_F]]` | 0.02727937287 → (removed) | 0.02736653946±2.523e-05 → — | -3.45 → — | OUTSIDE-ACCEPTED → — | #1 tip leaf, G_F-independent |
| `τ_n tip engine (vk P1, G_F,Z2)` | 880.1412523 → 880.1412523 | 877.82±0.287 → 877.82±0.287 | +8.09 → +8.09 | OUTSIDE-ACCEPTED → SUPERSEDED-SEED | vt fold 2fd608d (not IRONOUT) |
| `G_μ from tip G_F,Z2 (ppm vs MuLan)` | -852.4 → -852.4 | 0±0.5 → 0±0.5 | -1704.80 → -1704.80 | SM-PARITY → SUPERSEDED-SEED | vt fold 2fd608d (not IRONOUT) |
| `τ_μ from tip G_F,Z2 (ppm vs MuLan)` | 1712.6 → 1712.6 | 0±1 → 0±1 | +1712.60 → +1712.60 | SM-PARITY → SUPERSEDED-SEED | vt fold 2fd608d (not IRONOUT) |
| `wave3|Ising2D_beta` | 0.3265324014 → 0.3264189719 | 0.326419±3e-06 → 0.326419±3e-06 | +37.80 → -0.01 | OUTSIDE-ACCEPTED → IN-BAR | #2 scaling relations |
| `wave3|Ising2D_nu` | 0.6299845063 → 0.629970966 | 0.629971±4e-06 → 0.629971±4e-06 | +3.38 → -0.01 | OUTSIDE-ACCEPTED → IN-BAR | #2 scaling relations |
| `wave3|Ising2D_gamma` | 1.237642523 → 1.237074954 | 1.237075±1e-05 → 1.237075±1e-05 | +56.75 → -0.00 | OUTSIDE-ACCEPTED → IN-BAR | #2 scaling relations |
| `wave7|Ising3D_eta` | 0.036408194 → 0.03629846295 | 0.0362978±2e-06 → 0.0362978±2e-06 | +55.20 → +0.33 | OUTSIDE-ACCEPTED → IN-BAR | #2 scaling relations |
| `wave7|Ising3D_alpha` | 0.1100487274 → 0.110087102 | 0.110087±1.2e-05 → 0.110087±1.2e-05 | -3.19 → +0.01 | OUTSIDE-ACCEPTED → IN-BAR | #2 scaling relations |
| `wave7|Ising3D_delta` | 4.788746754 → 4.789837788 | 4.78984±1e-05 → 4.78984±1e-05 | -109.32 → -0.22 | OUTSIDE-ACCEPTED → IN-BAR | #2 scaling relations |
| `wave8|XY_beta` | 0.3485875997 → 0.348637435 | 0.348697±6e-05 → 0.348697±6e-05 | -1.82 → -0.99 | OUTSIDE-ACCEPTED → IN-BAR | #2 scaling relations |
| `wave8|XY_gamma` | 1.317731712 → 1.317698136 | 1.317855±0.0002 → 1.317855±0.0002 | -0.62 → -0.78 | IN-BAR → IN-BAR | #2 scaling relations |
| `chemistry_ionization|IE_H` | 13.58842989 → 13.59843474 | 13.5984346±0.0001 → 13.5984346±0.0001 | -100.05 → +0.00 | OUTSIDE-ACCEPTED → IN-BAR | #3 leaves R∞, α, m_p/m_e |
| `Gamma_Z/M_Z (tip leaf, G_F-independent) [Gamma_Z/M_Z]` | (new) → 0.02736580364 | — → 0.02736653946±2.523e-05 | — → -0.03 | — → IN-BAR | #1 tip leaf, G_F-independent |
The vt-fold rows (`τ_n tip engine (vk P1)` and `G_μ/τ_μ from tip G_F,Z2`) were superseded by 2fd608d, not by this pass. They are now counted as SUPERSEDED-SEED.

## Verdict counts (all 522 → 521 rows; the two Z-2 A1 rows became one leaf row)
| | IN-BAR | SM-PARITY | BEYOND-SM | OUTSIDE-ACCEPTED | NO-BAR | SUPERSEDED-SEED |
|---|---|---|---|---|---|---|
| before (2fd608d) | 209 | 43 | 13 | 103 (36 physics + 67 math) | 132 | 22 |
| after (ironout-1) | 224 | 39 | 10 | 91 (24 physics + 67 math) | 132 | 25 |

## Tried and NOT adopted (candidates, with numbers)
**#4 atomic IE O/N/Ne/Cl/He.** The engine has no nuclear pairing or shell-closure term to reuse: the nuclear binding rows are
standalone closed forms. As an upper bound, the least-squares-FITTED coefficient was computed for each shape over the
whole IE family He…Ca. That fit is forbidden for adoption; it only shows the best a derived coefficient could possibly do.

| shape | best coefficient | χ² ratio | rows better / worse |
|---|---|---|---|
| nuclear-style pairing (−1)^Z/√Z | +0.0237 eV | 0.958 | 5 / 14 |
| p-subshell pairing (# paired p e⁻) | +0.0089 eV | 0.936 | 2 / 4; O still −0.171 eV |
| shell closure (He, Ne, Ar) | +0.0044 eV | 0.998 | 1 / 2 |
| half-filled p³ (N, P) | +0.0091 eV | 0.995 | 1 / 1 |

Even a fitted coefficient fails the "improves the whole family" test, so no derived one can pass. The residuals (He +0.018, N −0.019, O −0.180, Ne −0.032, Cl +0.017 eV) have no common sign or shell pattern. They come from per-element closed forms, not from a missing universal term.

He-like correlation candidate: IE_He = (E_nr(He) + 2)·E_h·μ_He + rel/QED, with E_nr = −2.903724377 E_h (computed Hylleraas eigenvalue).
- Before rel/QED this gives ≈ 24.5885 eV, against NIST 24.58739, so z ≈ +11 at σ 1e-4.
- It needs an engine He-4 nuclear-mass leaf (there is none) and the He relativistic/QED terms (≈ −1.1 meV).
- **Damian decision**: may computed Coulomb-problem numbers (He eigenvalue, Bethe logs) count as "derived"? IE_H uses ln k₀, but its verdict doesn't depend on it.

**#5 πH Γ1s.** The route already uses the standard Deser formula, Γ1s = 8α³μ_c²q₀(1+1/P)[a⁻(1+δ_Γ)]², on the in-bar a⁻ leaf (85.594e-3, z −0.56). The invented NLO LEC only enters a⁻, and there is no other in-bar a⁻ (the LO WT 78.2e-3 is Soft-EXCLUDED). The Deser route therefore gives exactly 806.58 meV, so there is nothing to adopt.
- Computed SM benchmark (criteria #6): 816.1 ± 18.9 meV at a⁻ = 86.1(9).
- Gate B threshold = max(|856 − 816.1|, 18.9) = 39.9 meV. The FSOT miss is 49.4 meV, so the row stays OUTSIDE.
- Root cause: Γ ∝ a⁻², so the −0.6 % a⁻ becomes −1.2 % plus the mainstream's own +4.9 % tension with Hirtl.

## Needs Damian
1. τ_n world-average primary (PDG 878.4(5)) is PROPOSED, NOT APPLIED. Ruling t992u fixes the UCNτ/Pattie gates. The switch would move vt P2 from z +0.10 to z −1.10, which is SM-PARITY.
2. sinθ_C: three FSOT Cabibbo values, and the target 0.22759 has an unknown origin.
3. Whether computed Coulomb-problem constants (Bethe log, He eigenvalue) count as derived (see #4).
4. XY β is in bar at z −0.993 against a propagated σ estimate (6e-5), so it is fragile.
5. m_t/m_b (wave8, rel 0.38 %) was only "scored" against the authority's claimed-z tag and now needs a published-σ pin.

## What is left (physics OUTSIDE-ACCEPTED, 24) and why
- **IE He/N/O/Ne/Cl**: see #4.
- **HCl dipole** −2.6 % against the corrected 1.1086 D: the formula was fit to the stale 1.08 and is not retuned.
- **Heisenberg ν/η/β/γ**: the engine has no in-bar O(3) pair to derive from.
- **Percolation thresholds (sq/SC/BCC/FCC/honeycomb), SAW μ²/ν/γ, KT T/J, Madelung CsCl/ZnS/CaF₂**: per-constant numerology against high-precision numerics or exact lattice sums. There is no in-bar engine row to derive from. The Madelung constants are exactly computable lattice sums, but replacing them would paste mainstream math (Damian decision).
- **πH Γ1s**: see #5.

## #7 Mathematics misses (ranked by relative error; mainstream exact; nothing changed, nothing fitted)
| rank | row | FSOT | exact | rel |
|---|---|---|---|---|
| 1 | Reciprocal_Fib | 3.372628799 | 3.359885666 | 3.8e-3 |
| 2 | Henon_Lyapunov (numerics) | 0.4201087636 | 0.41922 | 2.1e-3 |
| 3 | gamma1_Stieltjes | −0.07274094507 | −0.07281584548 | 1.0e-3 |
| 4 | Erdos_Tenenbaum_Ford | 0.08600611375 | 0.08607133206 | 7.6e-4 |
| 5 | Laplace_limit | 0.6631479957 | 0.6627434193 | 6.1e-4 |
| 6 | gamma_2_Stieltjes | −0.00968634527 | −0.00969036319 | 4.2e-4 |
| 7 | Foias_alpha | 1.187068842 | 1.187452351 | 3.2e-4 |
| 8 | Spanning_tree_sq (= 4G/π) | 1.166078356 | 1.166243616 | 1.4e-4 |
| 9 | Twin_prime_C2 | 0.6600788064 | 0.6601618158 | 1.3e-4 |
| 10 | Apollonian_dim | 1.305585467 | 1.305686728 | 7.8e-5 |

Of 74 scored math rows, 67 sit above 1e-12. Each is a standalone closed form for a constant that mainstream knows exactly or to high precision. The only non-fitting fix is to compute the constant itself (e.g. 4G/π, (4/3)^{3/2}), which replaces the FSOT form, so that is a Damian decision.

## Tests
- ctest: 110/111 pass (the new `ironout1` passes). The only failure is the known pre-existing long-double golden row `Chain_consistency_%`, rel 1.4e-12 (identical on 2fd608d).
- `tools/check.py` (archive): PASS. [10] reports 22 moved rows, all in BEFORE_AFTER, 9 of them IRONOUT-1.
