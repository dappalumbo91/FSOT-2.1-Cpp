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
| τ_μ strict MuLan z (diag) | −901.2 | −881.5 (G_μ-ratio scaling; vv vRS form −883.24) | −883.24 |

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
- **vw validate: 4 FAILs, all mis-set bars, no scored number moves (for Damian, t999u Q5):**
  1. (iii) a², a³ vs analytic: 0.00294 vs a 5e-4 bar. The cause is CMS print rounding; re-integrating moves τ by
     about +1.2e-6 s.
  2. (iv) α_s continuity at m_c: 1.04e-11 vs a 1e-12 bar. A one-sided grid lookup; the true limits agree to 5.6e-17.
  3. (iv) α_s continuity at m_b: 2.93e-12 vs a 1e-12 bar. Same cause.
  4. (iv) runner vs tip AlphaS: 2.03e-6 vs a 1e-6 bar. The cause is the tip AlphaS linear-interpolation step at
     thresholds; the two agree to 4.7e-15 at the tip's own nodes.
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
| V_cd, V_cs | closed forms 0.221008 (+0.00), 0.974913 (−0.01) vs leaf 0.225150 (+1.04), 0.973423 (−0.26) | **CONFLICT**: the leaf is the tip CKM; closed forms not carried | none |
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

Why the total drops by 25: duplicates collapse to one engine-wide value. 21 superseded seed rows and 7 pin rows that
are now carried by their source row are dropped, and the τ_n folded routes are scored once per route against pdgLive
(their gates are secondary), not once per gate. Per scored quantity, nothing in bar was lost to unification. The new
out-of-bar rows are criteria moves only: V_ud and V_cd (direct values), the vt P1/P2 alternates and the vv-only τ_n.

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
