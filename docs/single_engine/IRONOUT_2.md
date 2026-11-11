# Iron-out pass 2 (Damian t999u, 2026-11-11 1:46 PM EST; parent steering 1:55 and 1:59 PM EST)

Ruling: "score everything against the best observed value, the world average where one exists. SM parity is only a
temporary floor; FSOT should aim to be more accurate than the SM." Local branch `ironout-2` (on ironout-1, rebased onto
origin/main db2bc8f). Nothing pushed. `single-engine`, /workspace/mainC and /workspace/refine_bots untouched (read-only
imports only).

## Commits
| commit | content |
|---|---|
| a698a6b | criteria: world average primary; sin θ_C = \|V_us\| 0.22431(85); CKM on PDG 2024 direct values (Eqs. 12.7–12.15); SCAFFOLD flags |
| c72e0a5 | unify: one engine-wide value per quantity (30 table rows), IE_H ln k0 SCAFFOLD_PENDING_FSOT_DERIVATION |
| e455e95 | criteria fix: τ_n primary = pdgLive 878.3 ± 0.4 s (a698a6b had 878.4 ± 0.5); PDG 2024, UCNτ, Pattie secondary |
| **1e161b5** | **G_F fold swap: carried route = vv P3 G_F + vw P3 ΔR^V** (vt P2/P1 alternates) |
| 578ff0a | unify τ_n: catalog τ_n row reads the carried chain |
| fsot_unified a381108 | tools/check.py [10]: IRONOUT-* exemption; escaped \| in row names |

Tests: ctest 110/111 (only `golden` Chain_consistency_% long-double rel 1.4e-12, known). tools/check.py PASS.

## 1. Criteria (SCORING_CRITERIA_IRONOUT_2.md, reference/scoring_criteria_ironout2.tsv)
- τ_n primary pdgLive 878.3 ± 0.4 s (S=1.8; https://pdglive.lbl.gov/DataBlock.action?node=S017T). Secondary: PDG 2024
  878.4 ± 0.5, UCNτ 877.82 ± 0.287, Pattie 877.7 ± 0.76. Gate B threshold vs world average 1.583 s.
- sin θ_C = \|V_us\| 0.22431 ± 0.00085 (PDG 2024 Eq. 12.8); fit 0.22501 secondary.
- CKM: PDG 2024 direct values; the unitarity global fit is secondary. J has no direct value (fit kept, flagged).
- The frozen precision audit 2026-10-02 is not rewritten; the scorecard applies the targets.

## 2. G_F route swap (commit 1e161b5)
| quantity | vt P2 (was carried) | vv P3 + vw P3 (carried) | Tracer FOLD |
|---|---|---|---|
| G_F [GeV⁻²] | 1.16690544271959e-5 | 1.16689392890418e-5 | 1.16689392890418e-5 |
| G_F vs G_μ | +451.52 ppm | +441.65 ppm (Gate B ACCEPT ≤ 809.87) | +441.65 |
| τ_n [s] | 877.8484108 | 878.4325396 | 878.4325396 |
| z vs pdgLive 878.3(4) | −1.13 | **+0.33** | +0.331 |
| z vs PDG 2024 / UCNτ / Pattie | −1.10 / +0.10 / +0.19 | +0.07 / +2.13 / +0.96 | +0.0651 / +2.1310 / +0.96187 |
| τ_μ strict MuLan z (diag) | −901.2 | −882.71 (PDG eq.(10.9) direct, W term in Δr; G_μ-ratio scaling −882.53; before the W term −881.67 / −881.50) | −883.24 (vRS form: double-counts the W propagator, omits H2 √ρ and H3; see below) |

- vv P3 G: fixed point G = G0[1/(1 − Δr_A) + Δr_P1 − Δr_A], solved live (Hooks::vv_p3). Reproduces vv score.py to rel
  5e-51 (G_chain), G_F to 3e-50 of the banked value.
- vw P3: τ_vk rebuilt with ΔR^V 0.02446134516 → 0.02380031545 (Hooks::tau_vk_override 880.709526723 s). τ_n reproduces
  vw score.py tau_of to rel 7e-32.
- Coefficients: golden/vv_vw_package.tsv from tools/gen_vv_vw_package.py (read-only import). Stamped sha256:
  vv score.py 74db1004…, results 2dc1e274…, DONE 56a8d211…; vw score.py eb03ab5a…, results 69329adc…, DONE 2e4a2c39…,
  validate_run 4c66f06d….
- vv P3 only (no vw): 877.8657345 s (z −1.09). Kept as an alternate row.
- Flag SM_PARITY_REFINE_LATER stays on the G_F / τ_μ rows. vt P2 and vt P1 stay as alternates, and they are
  bit-identical (test_vt_gf).
- Why a new hook: vv P3's remainder is G-dependent and sits outside the resummation. Neither a constant vv_rem_add nor a
  vv_route term switch expresses it, so Hooks::vv_p3 was added next to them.
- **γW-box discrepancy node** (vw FOLD §2, documented in vt_gf.hpp):
  - The engine's non-Born box is overstated by +0.343 α/π (ΔR^V +7.97e-4, τ_n lever −0.683 s): 73 % below m_A and 27 %
    in the one-loop C_dis.
  - The engine total was offset by three things: the omitted CMS eq.(19) QED enhancement (+3.59e-4), a low vector
    constant (−0.81e-4) and a low Born term (0.7848 vs 0.85, −1.5e-4).
  - vw P3 corrects only the box. The three offsets remain open.
- **vw validate bars, derived by GB under the principle Damian accepted in t1004s4215 (no Damian-named numbers).**
  Tracer audited the bars at 1f0192f and found none tailored. Their fixes F0–F5 are applied, and the brief "P + 8 ulp"
  continuity variant from 9ca5aac is superseded. The former FAILs were mis-set bars, and no scored number moves. The
  bars are in `reference/vw_validate_bars.tsv`, derived in `tools/vw_validate_bars.py` (which does not use the
  measured residual; checks are two-sided, |value| ≤ bar) and checked by ctest `vw_validate_bars`:

  | check | measured | old bar | bar | kind | derivation |
  |---|---|---|---|---|---|
  | (iii) a², a³ vs analytic | 0.00293579 | 5e-4 | 9.8e-3 | input precision | half-ULP of each printed CMS/BCK coefficient × n_f^k; recomputed live |
  | (iv) α_s continuity at m_c | 1.04385e-11 | 1e-12 | 1.24149e-11 | probe bias | e·\|β₃ − β₄\| |
  | (iv) α_s continuity at m_b | 2.92672e-12 | 1e-12 | 3.54397e-12 | probe bias | e·\|β₄ − β₅\| |
  | (iv) α_s continuity at m_t | 5.88029e-13 | 1e-12 | 7.19305e-13 | probe bias | e·\|β₅ − β₆\| (same rule at all three thresholds; Tracer quoted 7.21e-13) |
  | (iv) runner vs tip AlphaS | 2.02652e-6 | 1e-6 | 2.05608e-6 | input-fixed grid | the tip grid's n_f straddle at m_b plus h²/8\|α''\|, maximum over the 8 validate scales |

  - **Continuity rows (probe-bias bars).** The frozen check subtracts 1.01·2e\|β_hi\|, while a continuous runner
    moves e(\|β_lo\| + \|β_hi\|) across the probe. So even with zero true jump the statistic carries the probe bias
    P = e(\|β_lo\| − 1.02\|β_hi\|).
    - Effective tolerance on the true jump (bar − P): 1.98e-12 at m_c, 6.17e-13 at m_b, 1.31e-13 at m_t.
    - Offset-corrected true jump from a live re-run of Tracer's runner: −1.5e-17, +2.9e-18, −5.4e-18.
    - The 64εα round-off term is dropped: it is ≤ 4.9e-15, far below every effective tolerance.
  - **Runner vs tip AlphaS (input-fixed grid).** The actual step is h = 0.99999719e-3, and m_b sits at grid position
    x = 5963.915, so the straddle fraction is f = 0.085, fixed by the inputs (not the worst case ½). The resulting bar
    reproduces the measured 2.0265e-6 / 1.6607e-6 / 1.4773e-6 at µ = 2 / 3 / 4 GeV and stays sensitive to any real
    disagreement.
  - Tracer's full `score.py --validate`, re-run in a /tmp copy with these bars, gives **no FAIL** (validate_run sha256
    8b4c5ea6…). The ledger's frozen record (4c66f06d) is not edited.
- **M_W diagnostic:** the host M_W leaf 80.3687519 GeV is kept (z −0.03; the seed closed form 80.354537 has z −1.1).
  Had the seed M_W been used, the carried G_F would move −2.30 ppm and τ_n would be 878.4366 s. Since M_W is not changed,
  the vt/vv G_F chain is unchanged by unification.

## 3. Engine-wide value per quantity (chosen = closest FSOT value to the best observed value)
| quantity | candidates (z vs primary) | chosen | rows moved |
|---|---|---|---|
| τ_n | carried chain 878.4325 (+0.33); closed form π⁷θ_S 878.5929 (+0.73); vv P3 only 877.8657 (−1.09); vt P2 877.8484 (−1.13); vt P1 877.6310 (−1.67); G_F=G_μ 878.6415 (+0.85) | carried chain | wave3 Neutron_lifetime_s (closed form kept in parity column) |
| M_W | host leaf 80.36875 (−0.03); seed (M_W/M_Z)·M_Z 80.35454 (−1.1) | host leaf | wave2 M_W/M_Z → leaf ratio |
| g_A | 1.27506 (τ_n chain, vs PDG λ 1.2754(13): −0.26); profile 1.29169 (+12.5) | **not unified (CONFLICT)** | unifying to 1.27506 pushes MINERvA bin 8 [Q² 0.3–0.4] out of bar: z −0.953 → −1.048 (pred 0.72383 → 0.7141 vs 0.821 ± 0.102); bin 5 comes in (−1.069 → −0.98), χ²_cov/dof 0.746 → 0.732; πH a⁻ shift not computed |
| V_ud | hosted √(1−λ²) 0.974324 (+2.04 vs 0.97367(32)); closed form A_in − ln2 0.973707 (+0.12) | **EXCLUDED (steering)**; hosted stays | none. Swapping would move τ_vk by (0.974324/0.973707)² = 1.001268 |
| λ = sin θ_C = V_us | wave3 \|V_us\| closed form 0.224495 (+0.22); CKM leaf 0.225150 (+0.99); old sin θ_C form 0.227591 (+3.86) | sin θ_C row → 0.224495; **CKM leaf NOT changed (CONFLICT)** | wave3 sin_theta_C. Leaf λ → 0.224495 would keep every CKM row in its direct bar (V_cd +1.04 → +0.87 comes in), but it changes the mainC tip leaf and V_ud = √(1−λ²) 0.974324 → 0.974475 inside τ_vk (τ_n ×0.99969 → 878.16 s) |
| V_cd, V_cs | (superseded by r4, see below) closed forms 0.221008 (+0.00), 0.974913 (−0.01) vs leaf 0.225150 (+1.04), 0.973423 (−0.26) against PDG 2024 | was CONFLICT; **r4: rows take the leaf** | wave8 \|V_cd\|, \|V_cs\| |
| V_ub, V_tb, V_cb, V_td, V_ts, J | leaf closer than the closed forms (e.g. V_ts −0.37 vs −1.11) | tip CKM leaf | wave4 \|V_ub\|, \|V_td\|, \|V_ts\|, Jarlskog_J, wave3 \|V_cb\|, wave9 \|V_tb\| |
| m_μ/m_e | leaf 206.76828158 (−0.24); lepton_ratios 206.76828192 (−0.17); seed 206.76964 (+295) | leaf (lepton_ratios closer but **CONFLICT**: tip leaf) | wave10 seed → leaf |
| m_τ/m_μ | leaf ratio 16.818370 (+0.80); lepton_ratios 16.817285 (−0.48); seed 16.816910 (−0.92) | leaf ratio (lepton_ratios closer but **CONFLICT**: inconsistent with the m_τ/m_e and m_μ/m_e leaves) | wave7 seed → leaf ratio |
| m_τ/m_e | leaf 3477.50546 (+0.80); lepton_ratios 3477.51318 (+0.84) | leaf | lepton_ratios row → leaf |
| water angle | validation 104.5368 (+0.54); wave8 104.4405 (−1.39) | validation | wave8 H2O_bond_angle |
| golden angle | validation 137.5077640500 (exact); wave7 137.5060188 | validation | wave7 Golden_angle_deg |
| Feigenbaum δ, α | wave4 4.66919796 / 2.50290815 (closer to exact); validation 4.66921091 / 2.50296714 | wave4 | validation_suite rows (both stay OUTSIDE, exact math) |
| 19 further seeds | α_s, T_CMB, sin²θ_W ×2, 1/α, m_π/m_p, B_d, Δm² ratio, μ_p, m_c/m_b, Γ_Z/M_Z, B_He4, B_H3, μ_d, a_e, … | scored pin / tip leaf (closer in every case) | seed → pin |

No unification pushed an in-bar row out of its bar. Rows that leave the bar do so because the criteria changed:
- CKM_V_ud / pin wave8 \|V_ud\|: z −0.16 → +2.04 (fit → direct).
- CKM_V_cd / pin wave8 \|V_cd\|: z +0.41 → +1.04.

Scaffolding: the IE_H 1s Bethe log ln k0 = 2.984128555765 and the IE_He eigenvalue candidate (not adopted) are flagged
SCAFFOLD_PENDING_FSOT_DERIVATION.

## 4. Verdict counts (scorecard build_ironout2.py)
| | IN-BAR | SM-PARITY | BEYOND-SM | OUTSIDE (phys + math) | NO-BAR | SUPERSEDED | total |
|---|---|---|---|---|---|---|---|
| pass 1 after | 224 | 39 | 10 | 91 (24 + 67) | 132 | 25 | 521 |
| pass 2 after | 215 | 42 | 13 | 90 (24 + 66) | 132 | 4 | 496 |

Why the total drops by 25 (31 rows removed, 6 added):
- 19 SUPERSEDED-SEED rows collapse onto their scored pin or leaf.
- 12 in-bar duplicate rows are now carried by a single row:
  - 6 pin rows now carried by their source row: τ_n closed form, lepton m_τ/m_e, wave3 |V_cb|, wave4 |V_td|, wave4 |V_ts|, J;
  - the wave7 m_τ/m_μ seed;
  - the 4 vt per-gate τ_n rows;
  - the duplicate ledger vt P2 row.
- 6 rows are added: 1 τ_n row per vt route (2), the vv P3 + vw P3 τ_n, the vv P3-only τ_n, the vv P3 G_F and the vv P3 τ_μ diagnostic.

Unification moved no quantity from in bar to out of bar. The new out-of-bar rows come from the criteria changes only:
- V_ud and V_cd against the direct values;
- the vt P1/P2 alternates and the vv-only τ_n against pdgLive.

## 5. Moved rows, pass-1 after → pass-2 after
| change | id | FSOT before | obs before | z before | verdict before | FSOT after | obs after | z after | verdict after |
|---|---|---|---|---|---|---|---|---|---|
| added | 43.5vt-TAU_N_GF_Z2_MU_CONSISTENT_DR2_COMPLETION_INVENT_EXTEND [tau_n [P1]] |  |  |  |  | 877.6309982 | 878.3 | -1.67 | SM-PARITY |
| added | 43.5vt-TAU_N_GF_Z2_MU_CONSISTENT_DR2_COMPLETION_INVENT_EXTEND [tau_n [P2]] |  |  |  |  | 877.8484108 | 878.3 | -1.13 | SM-PARITY |
| removed | 43.5vt-TAU_N_GF_Z2_MU_CONSISTENT_DR2_COMPLETION_INVENT_EXTEND [tau_n_s Pattie [P1]] | 877.6309982 | 877.7 | -0.09 | IN-BAR |  |  |  | (unified/deduplicated) |
| removed | 43.5vt-TAU_N_GF_Z2_MU_CONSISTENT_DR2_COMPLETION_INVENT_EXTEND [tau_n_s Pattie [P2]] | 877.8484108 | 877.7 | +0.19 | IN-BAR |  |  |  | (unified/deduplicated) |
| removed | 43.5vt-TAU_N_GF_Z2_MU_CONSISTENT_DR2_COMPLETION_INVENT_EXTEND [tau_n_s UCNtau [P1]] | 877.6309982 | 877.82 | -0.66 | IN-BAR |  |  |  | (unified/deduplicated) |
| removed | 43.5vt-TAU_N_GF_Z2_MU_CONSISTENT_DR2_COMPLETION_INVENT_EXTEND [tau_n_s UCNtau [P2]] | 877.8484108 | 877.82 | +0.10 | IN-BAR |  |  |  | (unified/deduplicated) |
| added | 43.5vv-TAU_N_GF_DR_TWO_LOOP_REMAINDER_COMPLETION_INVENT_EXTEND [G_F_GeVm2 [vvP3]] |  |  |  |  | 1.166893929e-05 | 1.1663787e-05 | +858.71 | SM-PARITY |
| added | 43.5vv-TAU_N_GF_DR_TWO_LOOP_REMAINDER_COMPLETION_INVENT_EXTEND [tau_n [vvP3 only]] |  |  |  |  | 877.8657345 | 878.3 | -1.09 | SM-PARITY |
| added | 43.5vw-TAU_N_DRV_GAMMA_W_BOX_BJSR_INTERPOLATOR_INVENT_EXTEND [tau_n [vvP3+vwP3]] |  |  |  |  | 878.4325396 | 878.3 | +0.33 | IN-BAR |
| moved | CKM_V_cb | 0.04189391912 | 0.04183 | +0.08 | IN-BAR | 0.04189391912 | 0.0411 | +0.66 | IN-BAR |
| moved | CKM_V_cd | 0.225149539 | 0.22487 | +0.41 | IN-BAR | 0.225149539 | 0.221 | +1.04 | BEYOND-SM |
| moved | CKM_V_cs | 0.9734231272 | 0.97349 | -0.42 | IN-BAR | 0.9734231272 | 0.975 | -0.26 | IN-BAR |
| moved | CKM_V_tb | 0.9991224498 | 0.999118 | +0.15 | IN-BAR | 0.9991224498 | 1.01 | -0.40 | IN-BAR |
| moved | CKM_V_td | 0.008601365578 | 0.00858 | +0.11 | IN-BAR | 0.008601365578 | 0.0086 | +0.01 | IN-BAR |
| moved | CKM_V_ts | 0.04116968754 | 0.04111 | +0.08 | IN-BAR | 0.04116968754 | 0.0415 | -0.37 | IN-BAR |
| moved | CKM_V_ub | 0.003741993473 | 0.003732 | +0.11 | IN-BAR | 0.003741993473 | 0.00382 | -0.39 | IN-BAR |
| moved | CKM_V_ud | 0.9743242197 | 0.97435 | -0.16 | IN-BAR | 0.9743242197 | 0.97367 | +2.04 | BEYOND-SM |
| moved | CKM_V_us | 0.225149539 | 0.22501 | +0.21 | IN-BAR | 0.225149539 | 0.22431 | +0.99 | IN-BAR |
| removed | pin:lepton_ratios/m_tau/m_e_lepton | 3477.51318 | 3477.365262 | +0.84 | IN-BAR |  |  |  | (unified/deduplicated) |
| removed | pin:wave3/Neutron_lifetime_s | 878.5928514 | 878.4 | +0.39 | IN-BAR |  |  |  | (unified/deduplicated) |
| removed | pin:wave3//V_cb/ | 0.04214351157 | 0.04183 | +0.40 | IN-BAR |  |  |  | (unified/deduplicated) |
| moved | pin:wave3//V_us/ | 0.2244946092 | 0.22501 | -0.76 | IN-BAR | 0.2244946092 | 0.22431 | +0.22 | IN-BAR |
| removed | pin:wave4/Jarlskog_J | 3.072771787e-05 | 3.12e-05 | -0.36 | IN-BAR |  |  |  | (unified/deduplicated) |
| removed | pin:wave4//V_td/ | 0.00857080098 | 0.00858 | -0.05 | IN-BAR |  |  |  | (unified/deduplicated) |
| removed | pin:wave4//V_ts/ | 0.04050330472 | 0.04111 | -0.79 | IN-BAR |  |  |  | (unified/deduplicated) |
| moved | pin:wave4//V_ub/ | 0.003741993473 | 0.003732 | +0.11 | IN-BAR | 0.003741993473 | 0.00382 | -0.39 | IN-BAR |
| moved | pin:wave8//V_cd/ | 0.225149539 | 0.22487 | +0.41 | IN-BAR | 0.225149539 | 0.221 | +1.04 | BEYOND-SM |
| moved | pin:wave8//V_cs/ | 0.9734231272 | 0.97349 | -0.42 | IN-BAR | 0.9734231272 | 0.975 | -0.26 | IN-BAR |
| moved | pin:wave8//V_ud/ | 0.9743242197 | 0.97435 | -0.16 | IN-BAR | 0.9743242197 | 0.97367 | +2.04 | BEYOND-SM |
| moved | pin:wave9//V_tb/ | 0.9991224498 | 0.999118 | +0.15 | IN-BAR | 0.9991224498 | 1.01 | -0.40 | IN-BAR |
| added | tau_mu strict MuLan (diagnostic) [tau_mu [vvP3 G_F]] |  |  |  |  | 2195041.001 | 2196980.3 | -881.50 | SM-PARITY |
| moved | validation_suite/Feigenbaum_alpha | 2.502967136 | 2.502907875 | — | OUTSIDE-ACCEPTED | 2.502908153 | 2.502907875 | — | OUTSIDE-ACCEPTED |
| moved | validation_suite/Feigenbaum_delta | 4.669210913 | 4.669201609 | — | OUTSIDE-ACCEPTED | 4.669197957 | 4.669201609 | — | OUTSIDE-ACCEPTED |
| removed | validation_suite/sin2_theta_W | 0.2312220291 | 0.23129 | -1.70 | SUPERSEDED-SEED |  |  |  | (unified/deduplicated) |
| removed | wave10/(g-2)/2_electron | 0.001159659965 | 0.00115965218 | +43246.77 | SUPERSEDED-SEED |  |  |  | (unified/deduplicated) |
| removed | wave10/m_mu/m_e | 206.7696386 | 206.7682827 | +294.76 | SUPERSEDED-SEED |  |  |  | (unified/deduplicated) |
| removed | wave1/T_CMB | 2.72471169 | 2.7255 | -1.31 | SUPERSEDED-SEED |  |  |  | (unified/deduplicated) |
| removed | wave1/alpha_s(M_Z) | 0.117099663 | 0.118 | -1.00 | SUPERSEDED-SEED |  |  |  | (unified/deduplicated) |
| removed | wave2/1/alpha_em | 137.0361976 | 137.0359992 | +9446.79 | SUPERSEDED-SEED |  |  |  | (unified/deduplicated) |
| removed | wave2/M_W/M_Z | 0.881202481 | 0.88136 | -1.05 | SUPERSEDED-SEED |  |  |  | (unified/deduplicated) |
| removed | wave2/m_pi/m_p | 0.1444186853 | 0.1487525757 | -22590.94 | SUPERSEDED-SEED |  |  |  | (unified/deduplicated) |
| removed | wave2/sin2_theta_W | 0.2311899746 | 0.23129 | -2.50 | SUPERSEDED-SEED |  |  |  | (unified/deduplicated) |
| removed | wave3/Deuteron_binding_MeV | 2.224564648 | 2.224566229 | -3.59 | SUPERSEDED-SEED |  |  |  | (unified/deduplicated) |
| moved | wave3/sin_theta_C | 0.2275911542 | 0.22501 | +3.80 | BEYOND-SM | 0.2244946092 | 0.22431 | +0.22 | IN-BAR |
| removed | wave4/Dm2_21/Dm2_32 | 0.02951701148 | 0.03067209776 | -1.42 | SUPERSEDED-SEED |  |  |  | (unified/deduplicated) |
| removed | wave4/m_c/m_b | 0.2948960718 | 0.304327038 | -7.78 | SUPERSEDED-SEED |  |  |  | (unified/deduplicated) |
| removed | wave4/mu_p_muN | 2.792852216 | 2.792847345 | +5941.02 | SUPERSEDED-SEED |  |  |  | (unified/deduplicated) |
| removed | wave4//V_ub/ | 0.003921256293 | 0.003732 | +2.10 | SUPERSEDED-SEED |  |  |  | (unified/deduplicated) |
| removed | wave5/Gamma_Z/M_Z | 0.02748978289 | 0.02736653946 | +4.88 | SUPERSEDED-SEED |  |  |  | (unified/deduplicated) |
| moved | wave7/Golden_angle_deg | 137.5060188 | 137.5077641 | — | OUTSIDE-ACCEPTED | 137.5077641 | 137.5077641 | — | IN-BAR |
| removed | wave7/m_tau/m_mu | 16.81691021 | 16.81769184 | -0.92 | IN-BAR |  |  |  | (unified/deduplicated) |
| removed | wave8/Deuteron_mu_muN | 0.8573914181 | 0.8574382335 | -21279.71 | SUPERSEDED-SEED |  |  |  | (unified/deduplicated) |
| moved | wave8/H2O_bond_angle | 104.4405426 | 104.51 | -1.39 | SM-PARITY | 104.5368015 | 104.51 | +0.54 | IN-BAR |
| removed | wave8/He4_binding_MeV | 28.30071694 | 28.29566238 | +5679.28 | SUPERSEDED-SEED |  |  |  | (unified/deduplicated) |
| removed | wave8/Triton_binding_MeV | 8.480800163 | 8.481796284 | -1131.96 | SUPERSEDED-SEED |  |  |  | (unified/deduplicated) |
| moved | wave8//V_cd/ | 0.2210078048 | 0.22487 | -5.68 | SUPERSEDED-SEED | 0.2210078048 | 0.221 | +0.00 | IN-BAR |
| moved | wave8//V_cs/ | 0.9749134853 | 0.97349 | +8.90 | SUPERSEDED-SEED | 0.9749134853 | 0.975 | -0.01 | IN-BAR |
| moved | wave8//V_ud/ | 0.9737066644 | 0.97435 | -4.02 | SUPERSEDED-SEED | 0.9737066644 | 0.97367 | +0.11 | IN-BAR |
| removed | wave9//V_tb/ | 0.9990765193 | 0.999118 | -1.43 | SUPERSEDED-SEED |  |  |  | (unified/deduplicated) |
| moved | τ_n closed form (wave3 pin) | 878.5928514 | 878.4 | +0.39 | IN-BAR | 878.5928514 | 878.3 | +0.73 | SUPERSEDED-SEED |
| moved | τ_n engine at G_F = G_μ | 878.6414717 | 877.82 | +2.86 | SM-PARITY | 878.6414717 | 878.3 | +0.85 | IN-BAR |
| moved | τ_n tip engine (vk P1, G_F,Z2) | 880.1412523 | 877.82 | +8.09 | SUPERSEDED-SEED | 880.1412523 | 878.3 | +4.60 | SUPERSEDED-SEED |
| removed | τ_n vt P2 (PASS-with-HOLD) | 877.8484108 | 877.82 | +0.10 | IN-BAR |  |  |  | (unified/deduplicated) |

## τ_μ diagnostic: C++ −881.50 vs the vv package's −883.24 (Δz 1.74, 3.8 ps). The vv form is the wrong one.
PDG 2024 eq.(10.8)–(10.10) defines G_μ = 1.1663788(6)e-5 through the Fermi-theory lifetime formula. Footnote 3, and
MuLan, put the W propagator 3m_μ²/(5M_W²) into Δr, not into τ_μ.

The new C++ `fold::vt::tau_mu_pdg_s` evaluates eq.(10.9) directly with the tip m_e, m_μ and α:
- At G_μ it gives MuLan −0.175 ppm (z −0.18, inside G_μ's printed rounding).
- On the carried vv P3 G_F it gives z −881.67, which agrees with the scaling diagnostic (−881.50).

The vv score.py vRS τ_μ differs in four places:

| term in vv score.py | Δτ_μ | Δz |
|---|---|---|
| multiplies by (1 + 3m_μ²/(5M_W²)), so the W propagator is double counted | −1.037 ppm | −1.04 |
| omits H2's −(5/4)π²√ρ (the term linear in m_e) | −0.329 ppm | −0.33 |
| omits H3 = −15.3 | −0.197 ppm | −0.20 |
| absolute evaluation against the rounded G_μ (the ratio scaling cancels this) | −0.175 ppm | −0.17 |
| **total** | **−1.747 ppm** | **−1.74** |

The radiative-factor H1, the phase space F(ρ), α̂(m_μ) and the input masses all agree between the two forms. The vv
ledger is read-only, so the fix is on the reporting side: the C++ keeps the scaling diagnostic, with the direct
eq.(10.9) as the independent check (`tests/test_vt_gf.cpp`). The vv τ_μ should drop the W factor and add H2 √ρ and H3
(Tracer).

**W-propagator term now carried in Δr (Tracer's check of 1f0192f).** Moving 3m_μ²/(5M_W²) out of the τ_μ formula
without adding it to Δr would have dropped it entirely. The carried chain now applies it:

- 1 − Δr → (1 − Δr)(1 − Δr_W), with Δr_W = 1 − (1 + 3m_μ²/(5M_W²))^(−1/2) = 5.1851e-7, using the engine's m_μ and M_W
  leaves (`Hooks::w_prop_dr`, on for vv P3 only).
- G_F: 1.16689392890418e-5 → **1.16689453394674e-5**, a +0.5185 ppm shift.
- Gate B margin: **442.17 ppm**, still ACCEPT.
- Consistent strict MuLan z: **−882.71** from PDG eq.(10.9) direct, −882.53 from the G_μ-ratio scaling.
- τ_n is unchanged. The term is m_μ-specific; for neutron decay q² ≈ (m_n − m_p)², which gives < 1e-10.
- The term is applied to the absolute G_F, not inside the ratio fixed point. Inside the fixed point the P0 baseline
  would cancel it; the x_t feedback of a 0.5 ppm G shift is < 1e-9 relative.
- The vt P2 / P1 alternates stay as Tracer filed them (no W term). The pre-W value is kept as `Solution::GF_noW` and is
  still checked against Tracer's package to 1e-25.
- Tests: Δr_W, the +0.5185 ppm shift, the 442.17 ppm margin, z −882.71, and that the W term does not leak into vt P2.

## sin θ_C target
The table row `wave3|sin_theta_C` is now scored against the PDG 2024 direct value |V_us| = 0.22431 ± 0.00085
(Eq. 12.8). The stale authority target 0.22759 is dropped, and its claimed-|z| tag is dropped with it. The result is
z = +0.217, which agrees with the scorecard's +0.22. The authority catalog (`closed_forms*.gen.inc`, generated from
fsot_compute.py and checked by regen-diff) still prints 0.22759 as its own target. That is upstream, and the engine
table no longer scores against it.

## r4 — stale targets, V_cd/V_cs, the m_c/m_b variant pin (Tracer REFINEMENT_LIST r4)

Values: Scout WAVE90 re-extract 43_5wf (PDG 2026 / CODATA 2022); full list in `reference/scoring_criteria_ironout2.tsv`.
Authority-generated catalog targets (`closed_forms*.gen.inc`) and the ledger route file (`golden/folded_routes.tsv`)
keep their filed targets; the single engine scores against the world average (`Retarget` in `derived_table.hpp`,
`WA-RETARGET` in `fsot_single_engine --folded`). No engine value moves except m_c/m_b 10φ and the two CKM rows below.

| row | old target | world average | engine value | z after |
|---|---|---|---|---|
| wave5 D_H_ratio | 2.547e-5 (0.09 %) | 2.508(29)e-5 PDG 2026 BBN Eq. 24.2 | 2.544683e-5 | **+1.26** (now out of bar; honest) |
| wave2 tau_reion | 0.0544 (no σ) | 0.0544(73) Planck 2018 / PDG 2026 | 0.0543966 | −0.0005 |
| wave8 gamma_2_Stieltjes | −0.00946 | −0.00969036319287232 (exact) | −0.00968635 | rel 0.041 % (no z) |
| wave4 r_p_fm / validation Proton_radius / 43.5rh | 0.8414 / 0.8413 / Grinin 0.8482(38) | 0.84075(64) CODATA 2022 | 0.8412485 | +0.78 |
| 43.5qk / 43.5ql Γ_Z | DELPHI 2487.6(41) / L3 2502.4(42) | 2495.5(23) MeV PDG 2026 | 2495.4157 | −0.04 |
| 43.5rn m_H | CMS 2020 125.38(14) | 125.13(11) GeV | 125.1581 | +0.26 |
| 43.5pp Δm²_21 | SK solar 6.10(95)e-5 | 7.60(17)e-5 eV² | 7.5247e-5 | −0.44 |
| 43.5qy m_K± | Cheng 493.657(20) | 493.677(15) MeV | 493.6802 | +0.21 |
| M_W (folded diagnostic, score only) | PDG 2024 80.3692(133) | 80.3625(77) GeV | host leaf | +0.81 |
| wave3 sin_theta_C | 0.22759 | 0.22431(85) (done earlier) | 0.224495 | +0.22 |

Left as filed and flagged **AMBIGUOUS**: m_π/m_p 0.14446 (charged vs neutral), m_c/m_b 0.291 (scheme/scale).

**V_cd / V_cs (reverses the CONFLICT above).** Against PDG 2026 direct |V_cd| 0.2247(22), |V_cs| 0.969(5): closed form
z −1.68 / +1.18, tip CKM leaf z +0.20 / +0.88. Keep-the-closest: the wave8 rows take the leaf (pin:wave8||V_cd|,
pin:wave8||V_cs|). No leaf moves, so no other row changes; both rows end in bar, no in-bar row leaves its bar.

**m_c/m_b 10φ column (bug).** The unify step wrote the frozen precision-audit pin string into every variant table
(canonical, 10φ, d5), so the 10φ column could not move. Fix: when a variant's pin equals a canonical leaf to 1e-12,
the variant takes pin × leaf_var/leaf_canon from the same seed variant's leaves. m_c/m_b 10φ: 0.304178 → **0.300333**;
the row's sensitivity flag becomes D-02 (variant-sensitive, as expected). C_cosm is unchanged. No other row moves.
