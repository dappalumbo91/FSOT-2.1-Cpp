# FSOT 2.1 precision report: z ≤ 1 against published uncertainties (2026-10-02, updated 2026-10-02b)

Authority pin AEB2AD (unchanged). Hub data 6f9c2560 (unchanged). C++ values come from `apps/fsot_precision.cpp`: the hub seed leaves
(`include/fsot/host/seed_leaves.hpp`) and the pinned closed forms (Engine, parity mode). The references are in one file,
`reference/published_2026-10-02.tsv`. `tools/check_references.py` checks every entry against committed evidence:
the NIST CODATA 2022 allascii file, line extracts from the PDG 2024 PDFs, AME2020 lines, and quoted arXiv abstract/table text (`reference/evidence/arxiv_extracts.tsv`, 02b). CTest
`precision_report*` regenerates the table below byte for byte.

**Gate** (configured once in `include/fsot/host/precision_gate.hpp`): z = |value − central| / σ ≤ 1. σ is the current published
standard uncertainty on the side of the central value where the value lies. Sources are PDG 2024 (doi:10.1103/PhysRevD.110.030001),
CODATA 2022 (doi:10.1103/RevModPhys.97.025002) and AME2020 (doi:10.1088/1674-1137/abddaf). Cosmology uses Planck 2018
(doi:10.1051/0004-6361/201833910) through the PDG 2024 astrophysical-constants table; H0 is scored in the CMB+BAO channel (ACT DR6, arXiv:2503.14452; H-13). The legacy 2 % relative check and ppm are reported for every row.
No FSOT constant, `f`, domain parameter, tolerance, pin or frozen value was changed to get these numbers.

**Scored set (`rec = Y`).** For an observable that has a hub seed leaf committed by Damian (2026-09-29, hub `docs/TOE_ACCURACY_GOALS.md`), the leaf is scored.
Otherwise the AEB2AD closed form is scored (first occurrence in `full_report` order). Routes were never chosen by lowest z.
Rows marked `-` are superseded pin rows or alternates. They are still listed, with their own z.

## Summary

| | record set, confirmed | record set + passing frozen-pending (NOT confirmed) | all rows |
|---|---|---|---|
| rows | 91 | 91 | 123 |
| pass z ≤ 1 | **85 / 91** (was 83 before the 02b channel fixes H0, α_s) | 88 / 91 | 97 / 123 |
| pass legacy \|rel\| ≤ 2 % | 88 / 91 | 89 / 91 | 115 / 123 |
| median ppm | 93.0 | 93.0 | 178.6 |
| worst ppm | 37 659 (Δm²₂₁/Δm²₃₂, pin closed form) | 34 691 (δ_CP PMNS) | 62 397 (H0 vs SH0ES, alternate) |

Still open in the record set after 02b: Γ_Z/M_Z (z 4.89), deuteron binding (3.59), μ_d/μ_N (2.1e4). Frozen-pending, not confirmed: m_H/m_W, Δm²₂₁/Δm²₃₂, T_CMB.
The per-row table carries a separate **frozen-pending refined** column; the confirmed value column is unchanged by any refinement.

All 50 hub seed leaves pass z ≤ 1. The CODATA-class leaves are at sub-ppb to ppt relative error. For example, α⁻¹ is 137.035999166 at z = 0.53 (0.08 ppb).

## Where the precision went (per-prediction regression findings)

Historical best values: the hub seed scripts (all committed 2026-09-29 and unchanged since), and each physics row rerun under the five hub
pins D1D38A (08-04), 3090BC and FE23A2 (09-11), 3FBCE5 and AEB2AD (09-14) (`reference/pin_lineage_2026-10-02.tsv`). The
`historical best` column shows that value, rescored against the same 2024 reference. Details are in `docs/AUDIT_LOG.md` §H.

1. **Port scope: restored (H-01).** Sixteen observables had passed z ≤ 1 in Damian's hub but failed in the C++ verification, because the C++ only
   carried the older pin closed forms. The 17 superseded pin rows are: 1/α_em (z 9447), ŝ²_Z (wave2 2.50, validation 1.70), M_W/M_Z (39.9), m_π/m_p (2.3e4),
   |V_us| (6.73), |V_ub| (2.10), μ_p/μ_N (5941), m_c/m_b (7.78), |V_ud| (4.02), |V_cd| (5.68), |V_cs| (8.90), ⁴He (5679), ³H (1132), |V_tb| (1.22),
   m_μ/m_e (295) and (g−2)/2 (4.3e4). Another 28 of Damian's leaves were not verified at all in C++: m_e, the Rydberg family, m_p, μ_N, m_n, G, g_p, m_μ,
   u, M(¹²C), Z, W, H, τ, π±, K±, D± and Δm²₃₂. All 50 leaves are now ported and pass z ≤ 1.
2. **Stale or unsourced reference values: restored (H-02, H-06–H-08).** The C++ used the pin's own frozen targets as the measurement:
   sin²θ_W 0.23122, r_p 0.8414 (CODATA 2018), m_τ/m_e 3477.48 (own rounded value), m_c/m_b 0.291, rounded α⁻¹, m_n−m_p, μ_p, ⁴He and ³H, α_s 0.1179
   (PDG 2022), and the unsourced m_π/m_p 0.14446 and Γ_Z/M_Z 0.02749. These have been replaced by the cited 2024 table. Two hub bars are smaller than the
   printed PDG 2024 values: σ(m_c), σ(m_b) and σ(K±). Both leaves still pass with the printed bars.
3. **Alias bug (H-03).** In hub `fsot_seed_flavor.py`, `"V_cs": v_ud`. The C++ uses the second-row identity (z = 0.42). The fix is in the Grok Build prompt (Lean side).
4. **Re-pin regressions: deliberate pin changes, not reverted (H-04).** |V_us| 0.758 → 6.73, M_W/M_Z 1.05 → 39.9 and m_H/m_W 0.96 → 5.01 changed at
   3090BC → FE23A2 (hub 3c74a180, 2026-09-11, Quantum_Mechanics D 6 → 5). |V_ub| 0.974 → 2.10 changed at D1D38A → 3090BC (ba6a8288). The first, second and fourth
   are covered by leaves. **m_H/m_W is the one re-pin regression still in the scored set. It needs Damian's theory decision.**
5. **fsot_scalar 0.886264 vs 0.887330 (H-05).** This is the High_Energy_Physics scalar under D1D38A vs AEB2AD, not a bug. No action.
6. **(Task-1 wording; see the 02b section for the outcome.) Genuine formula misses (outside σ under every pin). These need Damian's theory decision:** α_s(M_Z) z = 1.0004 (0.11710 vs 0.1180 ± 0.0009),
   H0 2.09, T_CMB 1.31, deuteron binding 3.59 (Damian's own seed check keeps the bare √e/e+φ; its √e+φ⁻⁴ candidate was not adopted and is not scored),
   Γ_Z/M_Z 4.89, Δm²₂₁/Δm²₃₂ 1.42 against PDG 2024, and the deuteron magnetic moment 2.1e4.
7. The seven Ledger B formula misses (02b diagnosis: all data handling, H-16) and the 181 data-handling fixes from milestone 3 are unchanged in the hub. They are a separate gate (0.5 % reproducibility,
   `docs/PRECISION_M3.md`). Options for that gate are in `docs/DECISIONS_DRAFT.md`.

## 2026-10-02b: dialing in the remaining misses (protocol: diagnose data first, then freeze, then score)

The freeze `docs/freezes/REFINEMENTS_2026-10-02b.{md,json,sha256}` (commit ce282e0, 2026-10-02 08:22 EDT) was written and committed **before** any candidate was
evaluated. It lists every candidate, the a-priori selection rules, the held-out checks and the total count N = 420. Scores: `audit/refinements_2026-10-02b.tsv`
(Python, hub engine unchanged) and the `refined_*` columns below (C++ mp169). The two agree to 15 digits (CTest `refinements_b_crosscheck`, re-scored and diffed in CI).

**Selection rules (fixed before scoring, never lowest z).**
- **S1** (route items): use the latest committed hub leaves, following Damian's leaf-quotient pattern (m_W/m_Z, m_π/m_p). Where no leaf exists, use the committed seed function.
- **S2** (single-formula items): for nuclear binding, take the nearest-A committed sibling dressing (triton: ×(1 + yy·γψ_con²)). Otherwise use Damian's documented cross-sector polish ×(1 + yy),
  yy = (POOF·SUCTION)². Signs come from the precedent, not from the data.
- **Family** (look-elsewhere only, nothing adopted): bare·(1 ± d·x), d ∈ {α, α², α³, yy}, x ∈ Damian's 13 named seeds. That is 104 forms per item.

| item | cause | fix / chosen candidate | value | z (before → after) | N tried | held-out | status |
|---|---|---|---|---|---|---|---|
| H0 | **bug (channel)**: scored against Planck CMB-only; Damian's 09-15 docstring names the CMB+BAO channel | reference → ACT DR6 P-ACT-LB + DESI DR2 68.43 ± 0.27 (arXiv:2503.14452) | 68.444996 | 2.09 → **0.056** | 0 | P-ACT-LB DR1 68.22(36): 0.62 pass; P-ACT 67.62(50): 1.65 fail | **confirmed (scored)** |
| α_s(M_Z) | **bug (object)**: pin 1/(eπ) is "a different object"; MS-bar α_s(M_Z) is `seed_alpha_s_MZ` (08-03) | route → 2(POOF/ψ_con)² | 0.1179088 | 1.0004 → **0.10** | 1 | no-lattice 0.1175(10): 0.41; FLAG 2021 0.1184(8): 0.61 (both correlated inputs) | **confirmed (scored)** |
| m_H/m_W | formula (re-pin regression FE23A2, no committed leaf quotient) | C-MHW-1 leaf m_H / leaf m_W (S1) | 1.5572980 | 5.01 → 0.37 | 2 | m_H/m_Z 0.37 pass; m_H/m_t 0.80 pass | frozen-pending |
| Δm²₂₁/Δm²₃₂ | formula; also a hub label conflict (target 0.0295 is the 21/31 convention, H-15) | C-DM-1 seed Δm²₂₁ / atmospheric leaf (S1) | 0.0307876 | 1.42 → 0.14 | 1 | Δm²₂₁ 0.03 pass; 21/31 convention 1.34 (different label) | frozen-pending |
| T_CMB | formula (units OK) | C-TCMB ×(1+yy) (S2) | 2.7260993 K | 1.31 → 0.999 | 104 | none independent | frozen-pending (weak: family chance rate 11.5 %) |
| Γ_Z/M_Z | formula (total width, consistent BW convention) | C-GZ ×(1+yy) (S2) | 0.0275038 | 4.89 → 5.44 | 104 | none | **open** |
| deuteron B | formula (not blind: Damian's windows were seen) | C-BD ×(1+yy·γψ_con²) (S2) | 2.2248259 MeV | 3.59 → 590 | 104 | none | **open** |
| μ_d/μ_N | formula (units OK: μ_N; 54.6 ppm vs 2.6 ppb) | C-MUD ×(1+yy) (S2) | 0.8578281 | 2.1e4 → 1.8e5 | 104 | none | **open** |

**Look-elsewhere.** Family hits at z ≤ 1: T_CMB 12/104 (11.5 %), Γ_Z/M_Z 3/104 (2.9 %), deuteron B 3/104 (2.9 %), μ_d 0/104, total 18/416 = **4.3 %**. A z ≤ 1 hit
from a form picked at random from the family therefore happens about 4 % of the time, and for T_CMB about 12 %. The single T_CMB pass at z 0.999 is weak evidence. The Γ_Z/M_Z hits
(×(1 − α·{γ, ψ_con, 1/φ})) and the deuteron hits (Damian's windows) were z-selected and are not adopted.

**Ledger B, 7 misses (H-16): all data handling, none formula.** For tau_reion, D/H and the 3 dependency-length rows, the stored `error_pct` was computed against a different
`measured` value than the one now in the row. Under the cited σ they pass z ≤ 1: tau 0.24 (Planck+BAO), D/H 0.59 (Cooke 2018), dependency length 0.50 (row's own band; unsourced).
The two FRB periodicity rows have no published periodicity behind them and cannot be gated (suspected unsupported data). The 0.5 % Ledger B gate and its data are unchanged,
and the hub items are in `/workspace/gb-recovery/GROK_BUILD_PROMPT_2026-10-02b.md`.

## Frozen-pending refinements (exploratory; not scored)

`docs/freezes/REFINEMENTS_2026-10-02.md` and `.json` record these with sha256 values. Rule: refine → freeze with a dated hash → test on unseen data.
R1 |V_us| = θ_S/φ + (1 − S_Chemistry) = 0.224494609175 (z 0.758 against the fit). R2 first-row deficit α_seed/(π√2) = 1.644994e-3 against measured
1.637752e-3 ± 7.31e-4 (z 0.0099). R3 |V_ud| channel_mismatch exemption (z_fit 0.161, z_direct 2.044, published separation 2.125). R4 route selection by lowest z
(picks seed λ, z 0.205). The numbers are recomputed by `apps/fsot_precision.cpp`, in the block at the end of the table.

## Per-prediction table

<!-- generated by apps/fsot_precision.cpp; do not edit by hand -->
Gate: z = |value - central| / sigma <= 1 (include/fsot/host/precision_gate.hpp); legacy check |rel| <= 2% reported alongside.

```
record set (scored): n=91  pass z<=1: 85/91  pass |rel|<=2%: 88/91  median ppm=93.03  worst ppm=37659.2 (pin:wave4|Dm2_21/Dm2_32)
all rows (incl. superseded/alternate): n=123  pass z<=1: 97/123  pass |rel|<=2%: 115/123  median ppm=178.6  worst ppm=62397.3 (pin:wave1|H0 vs SH0ES)
record set if the passing frozen-pending refinements were adopted (NOT confirmed): n=91  pass z<=1: 88/91  pass |rel|<=2%: 89/91  median ppm=93.03  worst ppm=34691.3 (pin:wave8|delta_CP_PMNS)
```

| id | route | rec | confirmed value | unit | central | sigma (-/+) | ppm | z | z<=1 | 2% | frozen-pending refined (id: value, z) | historical best | cause / note | source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| alpha_inv | leaf | Y | 137.035999165943 | 1 | 137.035999177 | 2.1e-08 | 8.069e-05 | 0.5265 | PASS | PASS |  | hub 1f151ed3 2026-09-29 printed z=0.53 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "inverse fine-structure constant" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| g_e | leaf | Y | 2.00231930436095 | 1 | 2.00231930436092 | 3.6e-13 | 1.268e-08 | 0.0705 | PASS | PASS |  | hub 69710678 2026-09-29 printed z=0.071 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "electron g factor" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| m_e_kg | leaf | Y | 9.1093837124488e-31 | kg | 9.1093837139e-31 | 2.8e-40 | 0.0001593 | 0.5183 | PASS | PASS |  | hub 6a2355a4 2026-09-29 printed z=0.518 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "electron mass" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| R_inf | leaf | Y | 10973731.5681557 | m^-1 | 10973731.568157 | 1.2e-05 | 1.191e-07 | 0.1089 | PASS | PASS |  | hub 6a2355a4 2026-09-29 printed z=0.108 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "Rydberg constant" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| a_0 | leaf | Y | 5.29177210586066e-11 | m | 5.29177210544e-11 | 8.2e-21 | 7.949e-05 | 0.5130 | PASS | PASS |  | hub 6a2355a4 2026-09-29 printed z=0.497 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "Bohr radius" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| lambda_C | leaf | Y | 2.42631023576685e-12 | m | 2.42631023538e-12 | 7.6e-22 | 0.0001594 | 0.5090 | PASS | PASS |  | hub 6a2355a4 2026-09-29 printed z=0.514 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "Compton wavelength" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| r_e | leaf | Y | 2.81794032113517e-15 | m | 2.8179403205e-15 | 1.3e-24 | 0.0002254 | 0.4886 | PASS | PASS |  | hub 6a2355a4 2026-09-29 printed z=0.480 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "classical electron radius" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| sigma_T | leaf | Y | 6.65245870823664e-29 | m^2 | 6.6524587051e-29 | 6.2e-38 | 0.0004715 | 0.5059 | PASS | PASS |  | hub 6a2355a4 2026-09-29 printed z=0.507 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "Thomson cross section" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| E_h | leaf | Y | 4.35974472220546e-18 | J | 4.359744722206e-18 | 4.8e-30 | 1.242e-07 | 0.1128 | PASS | PASS |  | hub 6a2355a4 2026-09-29 printed z=0.113 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "Hartree energy" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| mu_B | leaf | Y | 9.2740100672155e-24 | J T^-1 | 9.2740100657e-24 | 2.9e-33 | 0.0001634 | 0.5226 | PASS | PASS |  | hub 6a2355a4 2026-09-29 printed z=0.527 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "Bohr magneton" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| m_p_over_m_e | leaf | Y | 1836.15267340501 | 1 | 1836.152673426 | 3.2e-08 | 1.143e-05 | 0.6560 | PASS | PASS |  | hub 85f78c34 2026-09-29 printed z=0.656 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "proton-electron mass ratio" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| m_p_kg | leaf | Y | 1.67262192566849e-27 | kg | 1.67262192595e-27 | 5.2e-37 | 0.0001683 | 0.5414 | PASS | PASS |  | hub 85f78c34 2026-09-29 printed z=0.541 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "proton mass" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| mu_N | leaf | Y | 5.05078374012197e-27 | J T^-1 | 5.0507837393e-27 | 1.6e-36 | 0.0001627 | 0.5137 | PASS | PASS |  | hub 85f78c34 2026-09-29 printed z=0.514 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "nuclear magneton" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| m_n_over_m_p | leaf | Y | 1.00137841948711 | 1 | 1.00137841946 | 4e-10 | 2.708e-05 | 0.0678 | PASS | PASS |  | hub df369d55 2026-09-29 printed z=0.068 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "neutron-proton mass ratio" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| m_n_kg | leaf | Y | 1.6749275003254e-27 | kg | 1.67492750056e-27 | 8.5e-37 | 0.0001401 | 0.2760 | PASS | PASS |  | hub df369d55 2026-09-29 printed z=0.276 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "neutron mass" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| G_N | leaf | Y | 6.67430855062831e-11 | m^3 kg^-1 s^-2 | 6.6743e-11 | 1.5e-15 | 1.281 | 0.0570 | PASS | PASS |  | hub f9289f0b 2026-09-29 printed z=0.057 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "Newtonian constant of gravitation" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| g_p | leaf | Y | 5.5856946888715 | 1 | 5.5856946893 | 1.6e-09 | 7.671e-05 | 0.2678 | PASS | PASS |  | hub 221a3562 2026-09-29 printed z=0.268 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "proton g factor" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| m_mu_over_m_e | leaf | Y | 206.768281576289 | 1 | 206.7682827 | 4.6e-06 | 0.005435 | 0.2443 | PASS | PASS |  | hub 0f4882cc 2026-09-29 printed z=0.244 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "muon-electron mass ratio" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| m_mu_kg | leaf | Y | 1.88353161644208e-28 | kg | 1.883531627e-28 | 4.2e-36 | 0.005605 | 0.2514 | PASS | PASS |  | hub 0f4882cc 2026-09-29 printed z=0.251 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "muon mass" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| u_over_m_e | leaf | Y | 1822.88848625809 | 1 | 1822.88848627814 | 3.223e-08 | 1.1e-05 | 0.6220 | PASS | PASS |  | hub af598be7 2026-09-29 printed z=0.611 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | derived inv:A_r_e from [A_r_e: CODATA2022] |
| u_kg | leaf | Y | 1.66053906863299e-27 | kg | 1.66053906892e-27 | 5.2e-37 | 0.0001728 | 0.5519 | PASS | PASS |  | hub af598be7 2026-09-29 printed z=0.552 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "atomic mass constant" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| M_12C | leaf | Y | 0.0120000000105446 | kg mol^-1 | 0.0120000000126 | 3.7e-12 | 0.0001713 | 0.5555 | PASS | PASS |  | hub af598be7 2026-09-29 printed z=0.556 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "molar mass of carbon-12" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| m_Z_MeV | leaf | Y | 91.1873703594484 | GeV | 91.188 | 0.002 | 6.905 | 0.3148 | PASS | PASS |  | hub a4e2a07b 2026-09-29 printed z=0.315 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-gauge-higgs-bosons.pdf |
| m_tau_MeV | leaf | Y | 1777.00164018233 | MeV | 1776.93 | 0.09 | 40.32 | 0.7960 | PASS | PASS |  | hub 76adcf9b 2026-09-29 printed z=0.796 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-leptons.pdf |
| r_p_fm | leaf | Y | 0.841248540969768 | fm | 0.8409 | 0.0004 | 414.5 | 0.8714 | PASS | PASS |  | hub 24c5be5b 2026-09-29 printed z=0.871 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-baryons.pdf |
| m_pi_pm_MeV | leaf | Y | 139.570341070318 | MeV | 139.57039 | 0.00018 | 0.3506 | 0.2718 | PASS | PASS |  | hub 71fa2e3f 2026-09-29 printed z=0.272 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-mesons.pdf |
| m_D_pm_MeV | leaf | Y | 1869.66025880354 | MeV | 1869.66 | 0.05 | 0.1384 | 0.0052 | PASS | PASS |  | hub 1c4110ec 2026-09-29 printed z=0.005 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-mesons.pdf |
| m_K_pm_MeV | leaf | Y | 493.680211322105 | MeV | 493.677 | 0.015 | 6.505 | 0.2141 | PASS | PASS |  | hub 22fe031a 2026-09-29 printed z=0.247 (bar 0.013) | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-mesons.pdf |
| m_c_over_m_b | leaf | Y | 0.304178447628559 | 1 | 0.304327038010997 | 0.001212 | 488.3 | 0.1226 | PASS | PASS |  | hub 25820df0 2026-09-29 printed z=0.204 (bar 0.00073) | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | derived ratio:m_c_GeV/m_b_GeV from [m_c_GeV: PDG2024:sum-quarks] [m_b_GeV: PDG2024:sum-quarks] |
| m_W_MeV | leaf | Y | 80.3687519241648 | GeV | 80.3692 | 0.0133 | 5.575 | 0.0337 | PASS | PASS |  | hub 4afc9aad 2026-09-29 printed z=0.034 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-gauge-higgs-bosons.pdf |
| m_W_over_m_Z | leaf | Y | 0.881358368021383 | 1 | 0.88136 | 0.00015 | 1.852 | 0.0109 | PASS | PASS |  | hub 52ad2ee9 2026-09-29 printed z=0.008 (bar 0.000147) | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-gauge-higgs-bosons.pdf |
| m_pi_over_m_p | leaf | Y | 0.148752523565799 | 1 | 0.1487525756892 | 1.918e-07 | 0.3504 | 0.2717 | PASS | PASS |  | hub d049ffff 2026-09-29 printed z=0.272 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | derived ratio:m_pi_pm_MeV/m_p_MeV from [m_pi_pm_MeV: PDG2024:sum-mesons] [m_p_MeV: CODATA2022] |
| mu_p_over_mu_N | leaf | Y | 2.79284734443575 | 1 | 2.79284734463 | 8.2e-10 | 6.955e-05 | 0.2369 | PASS | PASS |  | hub daab5eb6 2026-09-29 printed z=0.237 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "proton mag. mom. to nuclear magneton ratio" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| m_n_minus_m_p_MeV | leaf | Y | 1.29333253206531 | MeV | 1.29333251 | 3.8e-07 | 0.01706 | 0.0581 | PASS | PASS |  | hub 9e418a66 2026-09-29 printed z=0.058 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | CODATA 2022 "neutron-proton mass difference energy equivalent in MeV" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| m_H_MeV | leaf | Y | 125.158097744339 | GeV | 125.2 | 0.11 | 334.7 | 0.3809 | PASS | PASS |  | hub 6b3ce06c 2026-09-29 printed z=0.381 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-gauge-higgs-bosons.pdf |
| m_t_over_m_W | leaf | Y | 2.14976592906816 | 1 | 2.14721560000597 | 0.003626 | 1188 | 0.7034 | PASS | PASS |  | hub 37c6bfc9 2026-09-29 printed z=0.703 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | derived ratio:m_t_GeV/m_W_GeV from [m_t_GeV: PDG2024:sum-quarks] [m_W_GeV: PDG2024:sum-gauge-higgs-bosons] |
| sin2_theta_W_MSbar | leaf | Y | 0.231275280502387 | 1 | 0.23129 | 4e-05 | 63.64 | 0.3680 | PASS | PASS |  | hub 684bb8b2 2026-09-29 printed z=0.368 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-standard-model.pdf |
| m_tau_over_m_e | leaf | Y | 3477.50545878783 | 1 | 3477.36526190635 | 0.1761 | 40.32 | 0.7960 | PASS | PASS |  | hub 87897c4f 2026-09-29 printed z=0.796 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | derived ratio:m_tau_MeV/m_e_MeV from [m_tau_MeV: PDG2024:sum-leptons] [m_e_MeV: CODATA2022] |
| dm2_32 | leaf | Y | 0.00244405957968814 | eV^2 | 0.002455 | 2.8e-05 | 4456 | 0.3907 | PASS | PASS |  | hub b1938b97 2026-09-29 printed z=0.289 (vs 2.438e-3 +- 2.1e-5) | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-leptons.pdf |
| B_He4_MeV | leaf | Y | 28.2956623785975 | MeV | 28.295662378 | 8.9e-07 | 2.112e-05 | 0.0007 | PASS | PASS |  | hub 3d0e7678 2026-09-29 printed z=0.027 (rounded total) | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | AME2020 mass excesses https://www-nds.iaea.org/amdc/ame2020/mass_1.mas20.txt |
| B_H3_MeV | leaf | Y | 8.48179631631388 | MeV | 8.481796284 | 8.8e-07 | 0.00381 | 0.0367 | PASS | PASS |  | hub 79cd6cf0 2026-09-29 printed z=0.037 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | AME2020 mass excesses https://www-nds.iaea.org/amdc/ame2020/mass_1.mas20.txt |
| CKM_V_ud | leaf | Y | 0.97432421968751 | 1 | 0.97435 | 0.00016 | 26.46 | 0.1611 | PASS | PASS |  | hub 4c270461 2026-09-29 printed z=0.161 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf |
| CKM_V_us | leaf | Y | 0.225149539040889 | 1 | 0.22501 | 0.00068 | 620.1 | 0.2052 | PASS | PASS |  | hub 4c270461 2026-09-29 printed z=0.205 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf |
| CKM_V_ub | leaf | Y | 0.00374199347253333 | 1 | 0.003732 | -8.5e-05/+9e-05 | 2678 | 0.1110 | PASS | PASS |  | hub 4c270461 2026-09-29 printed z=0.111 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf |
| CKM_V_cd | leaf | Y | 0.225149539040889 | 1 | 0.22487 | 0.00068 | 1243 | 0.4111 | PASS | PASS |  | hub 4c270461 2026-09-29 printed z=0.411 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf |
| CKM_V_cs | leaf | Y | 0.97342312722172 | 1 | 0.97349 | 0.00016 | 68.69 | 0.4180 | PASS | PASS |  | hub 4c270461 2026-09-29 printed z=0.418 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf |
| CKM_V_cb | leaf | Y | 0.0418939191239346 | 1 | 0.04183 | -0.00069/+0.00079 | 1528 | 0.0809 | PASS | PASS |  | hub 4c270461 2026-09-29 printed z=0.081 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf |
| CKM_V_td | leaf | Y | 0.0086013655784844 | 1 | 0.00858 | -0.00017/+0.00019 | 2490 | 0.1125 | PASS | PASS |  | hub 4c270461 2026-09-29 printed z=0.112 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf |
| CKM_V_ts | leaf | Y | 0.0411696875380703 | 1 | 0.04111 | -0.00068/+0.00077 | 1452 | 0.0775 | PASS | PASS |  | hub 4c270461 2026-09-29 printed z=0.078 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf |
| CKM_V_tb | leaf | Y | 0.999122449770219 | 1 | 0.999118 | -3.4e-05/+2.9e-05 | 4.454 | 0.1534 | PASS | PASS |  | hub 4c270461 2026-09-29 printed z=0.153 | restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01) | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf |
| alpha_s_MZ | seed | Y | 0.117908816617884 | 1 | 0.118 | 0.0009 | 772.7 | 0.1013 | PASS | PASS |  | channel fix F2 (REFINEMENTS_2026-10-02b): hub seed_alpha_s_MZ 8760d403 2026-08-03, the QCD-process coupling | channel fix: committed hub seed route (REFINEMENTS_2026-10-02b F2) | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-qcd.pdf |
| pin:wave1/alpha_s(M_Z) | pin | - | 0.117099663048638 | 1 | 0.118 | 0.0009 | 7630 | 1.0004 | **FAIL** | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.117099663 z=1.0004 | formula miss: outside sigma under every pin (best z=1.0004); alternate: Wave-1 geometric 1/(e pi), 'a different object' per the seed_alpha_s_MZ docstring (F2) | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-qcd.pdf |
| pin:wave1/H0 | pin | Y | 68.4449955638267 | km s^-1 Mpc^-1 | 68.43 | 0.27 | 219.1 | 0.0555 | PASS | PASS |  | D1D38A (012e5c64 2026-08-04) 68.44005683 z=0.0372 | pin target 67.4 is 3.81 sigma off the current reference; channel fix F1 (REFINEMENTS_2026-10-02b): global CMB+BAO H0 per hub seed_h0_global docstring 00ca7f1f; ref ACT DR6 P-ACT-LB + DESI DR2 | arXiv:2503.14452 https://arxiv.org/abs/2503.14452 (abstract) |
| pin:wave1/H0 vs Planck2018 | pin | - | 68.4449955638267 | km s^-1 Mpc^-1 | 67.4 | 0.5 | 1.55e+04 | 2.0900 | **FAIL** | PASS |  | D1D38A (012e5c64 2026-08-04) 68.44005683 z=2.0801 | formula miss; also worsened by re-pin: D1D38A->3090BC (ba6a8288 2026-09-11) z 2.0801->2.0900; alternate reference (Planck 2018 CMB-only); not the FSOT channel (F1) | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-astrophysical-constants.pdf |
| pin:wave1/H0 vs SH0ES | pin | - | 68.4449955638267 | km s^-1 Mpc^-1 | 73 | 1 | 6.24e+04 | 4.5550 | **FAIL** | FAIL |  | AEB2AD (d127c07e 2026-09-14) 68.44499556 z=4.5550 | formula miss: outside sigma under every pin (best z=4.5550); pin target 67.4 is 5.6 sigma off the current reference; alternate reference (distance ladder); not the FSOT channel (F1) | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-cosmological-parameters.pdf |
| pin:wave1/T_CMB | pin | Y | 2.72471169034307 | K | 2.7255 | 0.0006 | 289.2 | 1.3138 | **FAIL** | PASS | C-TCMB: 2.72609931538602, z=0.9989 (frozen-pending) | D1D38A (012e5c64 2026-08-04) 2.724728387 z=1.2860 | formula miss; also worsened by re-pin: D1D38A->3090BC (ba6a8288 2026-09-11) z 1.2860->1.3138 | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-astrophysical-constants.pdf |
| pin:wave1/n_s | pin | Y | 0.963333836595472 | 1 | 0.965 | 0.004 | 1727 | 0.4165 | PASS | PASS |  | D1D38A (012e5c64 2026-08-04) 0.9638062834 z=0.2984 |  | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-astrophysical-constants.pdf |
| pin:wave1/Omega_b_h2 | pin | Y | 0.0224616214186474 | 1 | 0.02237 | 0.00015 | 4096 | 0.6108 | PASS | PASS |  | D1D38A (012e5c64 2026-08-04) 0.02235612408 z=0.0925 |  | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-astrophysical-constants.pdf |
| pin:validation_suite/sin2_theta_W | pin | - | 0.231222029147931 | 1 | 0.23129 | 4e-05 | 293.9 | 1.6993 | **FAIL** | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.2312220291 z=1.6993 | formula miss: outside sigma under every pin (best z=1.6993); pin target 0.23122 is 1.75 sigma off the current reference; superseded by sin2_theta_W_MSbar | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-standard-model.pdf |
| pin:validation_suite/M_Z/M_W | pin | - | 1.1346009294087 | 1 | 1.13461014795316 | 0.0001931 | 8.125 | 0.0477 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 1.134600929 z=0.0477 | pin target 1.134 is 3.16 sigma off the current reference; superseded by m_W_over_m_Z | derived inv:W_over_Z from [W_over_Z: PDG2024:sum-gauge-higgs-bosons] |
| pin:wave2/1/alpha_em | pin | - | 137.036197559573 | 1 | 137.035999177 | 2.1e-08 | 1.448 | 9447 | **FAIL** | PASS |  | AEB2AD (d127c07e 2026-09-14) 137.0361976 z=9447 | formula miss: outside sigma under every pin (best z=9447); pin target 137.036 is 39.2 sigma off the current reference; superseded by alpha_inv | CODATA 2022 "inverse fine-structure constant" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| pin:wave2/sin2_theta_W | pin | - | 0.231189974599601 | 1 | 0.23129 | 4e-05 | 432.5 | 2.5006 | **FAIL** | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.2311899746 z=2.5006 | formula miss: outside sigma under every pin (best z=2.5006); pin target 0.23122 is 1.75 sigma off the current reference; superseded by sin2_theta_W_MSbar | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-standard-model.pdf |
| pin:wave2/M_W/M_Z | pin | - | 0.875373665319297 | 1 | 0.88136 | 0.00015 | 6792 | 39.9089 | **FAIL** | PASS |  | D1D38A (012e5c64 2026-08-04) 0.8814508416 z=0.6056 | re-pin regression (frozen pin; theory decision): D1D38A->3090BC (ba6a8288 2026-09-11) z 0.6056->1.0501; 3090BC->FE23A2 (3c74a180 2026-09-11) z 1.0501->39.9089; superseded by m_W_over_m_Z | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-gauge-higgs-bosons.pdf |
| pin:wave2/Omega_Lambda | pin | Y | 0.682736038135278 | 1 | 0.685 | 0.007 | 3305 | 0.3234 | PASS | PASS |  | D1D38A (012e5c64 2026-08-04) 0.6846890475 z=0.0444 |  | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-astrophysical-constants.pdf |
| pin:wave2/Omega_m | pin | Y | 0.315329188245007 | 1 | 0.315 | 0.007 | 1045 | 0.0470 | PASS | PASS |  | D1D38A (012e5c64 2026-08-04) 0.3152990182 z=0.0427 |  | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-astrophysical-constants.pdf |
| pin:wave2/Omega_DM_h2 | pin | Y | 0.120585820096538 | 1 | 0.12 | 0.0012 | 4882 | 0.4882 | PASS | PASS |  | D1D38A (012e5c64 2026-08-04) 0.1200006733 z=0.0006 |  | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-astrophysical-constants.pdf |
| pin:wave2/sigma_8 | pin | Y | 0.808381839410747 | 1 | 0.811 | 0.006 | 3228 | 0.4364 | PASS | PASS |  | 3090BC (ba6a8288 2026-09-11) 0.8109398794 z=0.0100 |  | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-astrophysical-constants.pdf |
| pin:wave2/tau_reion | pin | Y | 0.0543965535023081 | 1 | 0.054 | 0.007 | 7344 | 0.0567 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.0543965535 z=0.0567 |  | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-astrophysical-constants.pdf |
| pin:wave2/m_pi/m_p | pin | - | 0.144418685310253 | 1 | 0.1487525756892 | 1.918e-07 | 2.913e+04 | 2.259e+04 | **FAIL** | FAIL |  | D1D38A (012e5c64 2026-08-04) 0.1444574966 z=2.239e+04 | formula miss; also worsened by re-pin: D1D38A->3090BC (ba6a8288 2026-09-11) z 2.239e+04->2.259e+04; pin target 0.14446 is 2.24e+04 sigma off the current reference; superseded by m_pi_over_m_p | derived ratio:m_pi_pm_MeV/m_p_MeV from [m_pi_pm_MeV: PDG2024:sum-mesons] [m_p_MeV: CODATA2022] |
| pin:wave2/N_eff | pin | Y | 3.04571345428836 | 1 | 2.99 | 0.17 | 1.863e+04 | 0.3277 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 3.045713454 z=0.3277 |  | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-astrophysical-constants.pdf |
| pin:wave3//V_us/ | pin | - | 0.229586479099665 | 1 | 0.22501 | 0.00068 | 2.034e+04 | 6.7301 | **FAIL** | FAIL |  | 3090BC (ba6a8288 2026-09-11) 0.2244946092 z=0.7579 | re-pin regression (frozen pin; theory decision): 3090BC->FE23A2 (3c74a180 2026-09-11) z 0.7579->6.7301; pin target 0.2243 is 1.04 sigma off the current reference; superseded by CKM_V_us | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf |
| pin:wave3//V_cb/ | pin | - | 0.0419188788072566 | 1 | 0.04183 | -0.00069/+0.00079 | 2125 | 0.1125 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.04191887881 z=0.1125 | superseded by CKM_V_cb | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf |
| pin:wave3/Age_Gyr | pin | Y | 13.7871961192453 | Gyr | 13.797 | 0.023 | 710.6 | 0.4263 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 13.78719612 z=0.4263 |  | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-astrophysical-constants.pdf |
| pin:wave3/z_eq | pin | Y | 3393.81031040142 | 1 | 3402 | 26 | 2407 | 0.3150 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 3393.81031 z=0.3150 |  | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-astrophysical-constants.pdf |
| pin:wave3/r_star_Mpc | pin | Y | 144.399830031989 | Mpc | 144.43 | 0.26 | 208.9 | 0.1160 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 144.39983 z=0.1160 |  | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-astrophysical-constants.pdf |
| pin:wave3/Deuteron_binding_MeV | pin | Y | 2.22456464846253 | MeV | 2.224566229 | 4.4e-07 | 0.7105 | 3.5921 | **FAIL** | PASS | C-BD: 2.22482594553556, z=590.3 (fails; open) | AEB2AD (d127c07e 2026-09-14) 2.224564648 z=3.5921 | formula miss: outside sigma under every pin (best z=3.5921) | AME2020 mass excesses https://www-nds.iaea.org/amdc/ame2020/mass_1.mas20.txt |
| pin:wave3/Neutron_lifetime_s | pin | Y | 878.592851392283 | s | 878.4 | 0.5 | 219.5 | 0.3857 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 878.5928514 z=0.3857 |  | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-baryons.pdf |
| pin:wave3/m_t/m_W | pin | - | 2.14976592906816 | 1 | 2.14721560000597 | 0.003626 | 1188 | 0.7034 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 2.149765929 z=0.7034 | superseded by m_t_over_m_W | derived ratio:m_t_GeV/m_W_GeV from [m_t_GeV: PDG2024:sum-quarks] [m_W_GeV: PDG2024:sum-gauge-higgs-bosons] |
| pin:wave3/m_H/m_W | pin | Y | 1.55083682600647 | 1 | 1.55781070360287 | 0.001393 | 4477 | 5.0073 | **FAIL** | PASS | C-MHW-1: 1.55729801381558, z=0.3681 (frozen-pending) | 3090BC (ba6a8288 2026-09-11) 1.559147372 z=0.9597 | re-pin regression (frozen pin; theory decision): 3090BC->FE23A2 (3c74a180 2026-09-11) z 0.9597->5.0073; pin target 1.5595 is 1.21 sigma off the current reference | derived ratio:m_H_GeV/m_W_GeV from [m_H_GeV: PDG2024:sum-gauge-higgs-bosons] [m_W_GeV: PDG2024:sum-gauge-higgs-bosons] |
| pin:wave3/m_tau/m_e | pin | - | 3477.50545878783 | 1 | 3477.36526190635 | 0.1761 | 40.32 | 0.7960 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 3477.505459 z=0.7960 | superseded by m_tau_over_m_e | derived ratio:m_tau_MeV/m_e_MeV from [m_tau_MeV: PDG2024:sum-leptons] [m_e_MeV: CODATA2022] |
| pin:wave4/sin2_theta12 | pin | Y | 0.306964429788902 | 1 | 0.307 | 0.013 | 115.9 | 0.0027 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.3069644298 z=0.0027 |  | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-leptons.pdf |
| pin:wave4/sin2_theta23 | pin | Y | 0.545766610986025 | 1 | 0.558 | -0.021/+0.015 | 2.192e+04 | 0.5825 | PASS | FAIL |  | AEB2AD (d127c07e 2026-09-14) 0.545766611 z=0.5825 |  | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-leptons.pdf |
| pin:wave4/sin2_theta13 | pin | Y | 0.0220151582211441 | 1 | 0.0219 | 0.0007 | 5258 | 0.1645 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.02201515822 z=0.1645 |  | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-leptons.pdf |
| pin:wave4/Dm2_21/Dm2_32 | pin | Y | 0.0295170114802864 | 1 | 0.0306720977596741 | 0.0008124 | 3.766e+04 | 1.4219 | **FAIL** | FAIL | C-DM-1: 0.030787593346332, z=0.1422 (frozen-pending) | AEB2AD (d127c07e 2026-09-14) 0.02951701148 z=1.4219 | formula miss: outside sigma under every pin (best z=1.4219); pin target 0.0295 is 1.44 sigma off the current reference | derived ratio:dm2_21/dm2_32 from [dm2_21: PDG2024:sum-leptons] [dm2_32: PDG2024:sum-leptons] |
| pin:wave4//V_ub/ | pin | - | 0.00392125629338614 | 1 | 0.003732 | -8.5e-05/+9e-05 | 5.071e+04 | 2.1028 | **FAIL** | FAIL |  | D1D38A (012e5c64 2026-08-04) 0.003819660113 z=0.9740 | re-pin regression (frozen pin; theory decision): D1D38A->3090BC (ba6a8288 2026-09-11) z 0.9740->2.1028; superseded by CKM_V_ub | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf |
| pin:wave4//V_td/ | pin | - | 0.00857080098022107 | 1 | 0.00858 | -0.00017/+0.00019 | 1072 | 0.0541 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.00857080098 z=0.0541 | superseded by CKM_V_td | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf |
| pin:wave4//V_ts/ | pin | - | 0.0405033047150822 | 1 | 0.04111 | -0.00068/+0.00077 | 1.476e+04 | 0.8922 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.04050330472 z=0.8922 | superseded by CKM_V_ts | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf |
| pin:wave4/Jarlskog_J | pin | Y | 3.07277178666547e-05 | 1 | 3.12e-05 | -1.2e-06/+1.3e-06 | 1.514e+04 | 0.3936 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 3.072771787e-05 z=0.3936 |  | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf |
| pin:wave4/r_p_fm | pin | - | 0.841248540969768 | fm | 0.8409 | 0.0004 | 414.5 | 0.8714 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.841248541 z=0.8714 | pin target 0.8414 is 1.25 sigma off the current reference; superseded by r_p_fm | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-baryons.pdf |
| pin:wave4/m_n-m_p_MeV | pin | - | 1.2933328005542 | MeV | 1.29333251 | 3.8e-07 | 0.2247 | 0.7646 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 1.293332801 z=0.7646 | pin target 1.29333 is 6.61 sigma off the current reference; superseded by m_n_minus_m_p_MeV | CODATA 2022 "neutron-proton mass difference energy equivalent in MeV" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| pin:wave4/mu_p_muN | pin | - | 2.79285221626412 | 1 | 2.79284734463 | 8.2e-10 | 1.744 | 5941 | **FAIL** | PASS |  | AEB2AD (d127c07e 2026-09-14) 2.792852216 z=5941 | formula miss: outside sigma under every pin (best z=5941); pin target 2.79285 is 3.24e+03 sigma off the current reference; superseded by mu_p_over_mu_N | CODATA 2022 "proton mag. mom. to nuclear magneton ratio" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| pin:wave4/w0 | pin | Y | -1.02998129213726 | 1 | -1.028 | 0.031 | 1927 | 0.0639 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) -1.029981292 z=0.0639 |  | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-astrophysical-constants.pdf |
| pin:wave4/m_c/m_b | pin | - | 0.294896071776548 | 1 | 0.304327038010997 | 0.001212 | 3.099e+04 | 7.7820 | **FAIL** | FAIL |  | AEB2AD (d127c07e 2026-09-14) 0.2948960718 z=7.7820 | formula miss: outside sigma under every pin (best z=7.7820); pin target 0.291 is 11 sigma off the current reference; superseded by m_c_over_m_b | derived ratio:m_c_GeV/m_b_GeV from [m_c_GeV: PDG2024:sum-quarks] [m_b_GeV: PDG2024:sum-quarks] |
| pin:wave5/Gamma_Z/M_Z | pin | Y | 0.0274897828876688 | 1 | 0.0273665394569461 | 2.523e-05 | 4503 | 4.8848 | **FAIL** | PASS | C-GZ: 0.0275037827215945, z=5.4397 (fails; open) | AEB2AD (d127c07e 2026-09-14) 0.02748978289 z=4.8848 | formula miss: outside sigma under every pin (best z=4.8848); pin target 0.02749 is 4.89 sigma off the current reference | derived ratio:Gamma_Z_GeV/m_Z_GeV from [Gamma_Z_GeV: PDG2024:sum-gauge-higgs-bosons] [m_Z_GeV: PDG2024:sum-gauge-higgs-bosons] |
| pin:wave5/R_b | pin | Y | 0.216230145276809 | 1 | 0.21629 | 0.00066 | 276.7 | 0.0907 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.2162301453 z=0.0907 |  | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-standard-model.pdf |
| pin:wave5/R_c | pin | Y | 0.17210879887232 | 1 | 0.1721 | 0.003 | 51.13 | 0.0029 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.1721087989 z=0.0029 |  | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-standard-model.pdf |
| pin:wave5/A_FB_ell | pin | Y | 0.0171118919939693 | 1 | 0.0171 | 0.001 | 695.4 | 0.0119 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.01711189199 z=0.0119 |  | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-gauge-higgs-bosons.pdf |
| pin:wave5/A_ell_SLD | pin | Y | 0.151189108513105 | 1 | 0.1515 | 0.0019 | 2052 | 0.1636 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.1511891085 z=0.1636 |  | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-gauge-higgs-bosons.pdf |
| pin:wave5/m_H/m_t | pin | Y | 0.725706820162371 | 1 | 0.72550269455873 | 0.001376 | 281.4 | 0.1484 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.7257068202 z=0.1484 |  | derived ratio:m_H_GeV/m_t_GeV from [m_H_GeV: PDG2024:sum-gauge-higgs-bosons] [m_t_GeV: PDG2024:sum-quarks] |
| pin:wave5/Y_p_He4 | pin | Y | 0.244780998449757 | 1 | 0.2448 | 0.0033 | 77.62 | 0.0058 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.2447809984 z=0.0058 |  | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-astrophysical-constants.pdf |
| pin:wave5/D_H_ratio | pin | Y | 2.5446825859417e-05 | 1 | 2.547e-05 | 2.9e-07 | 909.9 | 0.0799 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 2.544682586e-05 z=0.0799 |  | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-bbang-nucleosynthesis.pdf |
| pin:wave7/m_u/m_d | pin | Y | 0.460031158054808 | 1 | 0.462 | 0.02 | 4262 | 0.0984 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.4600311581 z=0.0984 |  | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-quarks.pdf |
| pin:wave7/m_tau/m_mu | pin | Y | 16.8169102120244 | 1 | 16.8176918449783 | 0.0008518 | 46.48 | 0.9176 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 16.81691021 z=0.9176 |  | derived ratio:m_tau_MeV/m_mu_MeV from [m_tau_MeV: PDG2024:sum-leptons] [m_mu_MeV: CODATA2022] |
| pin:wave8//V_ud/ | pin | - | 0.973706664444628 | 1 | 0.97435 | 0.00016 | 660.3 | 4.0208 | **FAIL** | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.9737066644 z=4.0208 | formula miss: outside sigma under every pin (best z=4.0208); pin target 0.9737 is 4.06 sigma off the current reference; superseded by CKM_V_ud | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf |
| pin:wave8//V_cd/ | pin | - | 0.221007804791326 | 1 | 0.22487 | 0.00068 | 1.718e+04 | 5.6797 | **FAIL** | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.2210078048 z=5.6797 | formula miss: outside sigma under every pin (best z=5.6797); pin target 0.221 is 5.69 sigma off the current reference; superseded by CKM_V_cd | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf |
| pin:wave8//V_cs/ | pin | - | 0.974913485313156 | 1 | 0.97349 | 0.00016 | 1462 | 8.8968 | **FAIL** | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.9749134853 z=8.8968 | formula miss: outside sigma under every pin (best z=8.8968); superseded by CKM_V_cs | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf |
| pin:wave8/delta_CP_PMNS | pin | Y | 3.86818853632835 | rad | 3.73849525777185 | 0.6912 | 3.469e+04 | 0.1876 | PASS | FAIL |  | AEB2AD (d127c07e 2026-09-14) 3.868188536 z=0.1876 |  | derived pi:delta_CP_over_pi from [delta_CP_over_pi: PDG2024:sum-leptons] |
| pin:wave8/BR_Z_ee | pin | Y | 0.0336654326477979 | 1 | 0.033632 | 4.2e-05 | 994.1 | 0.7960 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.03366543265 z=0.7960 |  | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-gauge-higgs-bosons.pdf |
| pin:wave8/BR_Z_had | pin | Y | 0.699175038098444 | 1 | 0.69911 | 0.00056 | 93.03 | 0.1161 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.6991750381 z=0.1161 |  | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-gauge-higgs-bosons.pdf |
| pin:wave8/BR_Z_inv | pin | Y | 0.199977541121741 | 1 | 0.2 | 0.00055 | 112.3 | 0.0408 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.1999775411 z=0.0408 |  | PDG 2024 https://pdg.lbl.gov/2024/tables/rpp2024-sum-gauge-higgs-bosons.pdf |
| pin:wave8/He4_binding_MeV | pin | - | 28.3007169365692 | MeV | 28.295662378 | 8.9e-07 | 178.6 | 5679 | **FAIL** | PASS |  | AEB2AD (d127c07e 2026-09-14) 28.30071694 z=5679 | formula miss: outside sigma under every pin (best z=5679); pin target 28.3 is 4.87e+03 sigma off the current reference; superseded by B_He4_MeV | AME2020 mass excesses https://www-nds.iaea.org/amdc/ame2020/mass_1.mas20.txt |
| pin:wave8/Triton_binding_MeV | pin | - | 8.48080016263456 | MeV | 8.481796284 | 8.8e-07 | 117.4 | 1132 | **FAIL** | PASS |  | AEB2AD (d127c07e 2026-09-14) 8.480800163 z=1132 | formula miss: outside sigma under every pin (best z=1132); pin target 8.482 is 231 sigma off the current reference; superseded by B_H3_MeV | AME2020 mass excesses https://www-nds.iaea.org/amdc/ame2020/mass_1.mas20.txt |
| pin:wave8/Deuteron_mu_muN | pin | Y | 0.857391418128038 | 1 | 0.8574382335 | 2.2e-09 | 54.6 | 2.128e+04 | **FAIL** | PASS | C-MUD: 0.857828065354834, z=1.772e+05 (fails; open) | AEB2AD (d127c07e 2026-09-14) 0.8573914181 z=2.128e+04 | formula miss: outside sigma under every pin (best z=2.128e+04); pin target 0.8574 is 1.74e+04 sigma off the current reference | CODATA 2022 "deuteron mag. mom. to nuclear magneton ratio" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| pin:wave8/S_8 | pin | Y | 0.83201443471342 | 1 | 0.832 | 0.013 | 17.35 | 0.0011 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.8320144347 z=0.0011 |  | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-astrophysical-constants.pdf |
| pin:wave8/z_reion | pin | Y | 7.6719924223667 | 1 | 7.7 | 0.7 | 3637 | 0.0400 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 7.671992422 z=0.0400 |  | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-astrophysical-constants.pdf |
| pin:wave9//V_tb/ | pin | - | 0.999076519261229 | 1 | 0.999118 | -3.4e-05/+2.9e-05 | 41.52 | 1.2200 | **FAIL** | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.9990765193 z=1.2200 | formula miss: outside sigma under every pin (best z=1.2200); superseded by CKM_V_tb | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf |
| pin:wave10/m_mu/m_e | pin | - | 206.769638597122 | 1 | 206.7682827 | 4.6e-06 | 6.558 | 294.8 | **FAIL** | PASS |  | AEB2AD (d127c07e 2026-09-14) 206.7696386 z=294.8 | formula miss: outside sigma under every pin (best z=294.8); superseded by m_mu_over_m_e | CODATA 2022 "muon-electron mass ratio" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| pin:wave10/(g-2)/2_electron | pin | - | 0.00115965996487795 | 1 | 0.00115965218046 | 1.8e-13 | 6.713 | 4.325e+04 | **FAIL** | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.001159659965 z=4.325e+04 | formula miss: outside sigma under every pin (best z=4.325e+04); pin target 0.00115965 is 1.21e+04 sigma off the current reference; superseded by g_e (a_e = /g_e//2 - 1; the g_e leaf is the record route) | CODATA 2022 "electron mag. mom. anomaly" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| pin:wave10/eta_baryon_photon | pin | Y | 6.13974953542555e-10 | 1 | 6.04e-10 | 1.2e-11 | 1.651e+04 | 0.8312 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 6.139749535e-10 z=0.8312 |  | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-astrophysical-constants.pdf |
| pin:lepton_ratios/m_tau/m_e_lepton | pin | - | 3477.51317969453 | 1 | 3477.36526190635 | 0.1761 | 42.54 | 0.8398 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 3477.51318 z=0.8398 | superseded by m_tau_over_m_e | derived ratio:m_tau_MeV/m_e_MeV from [m_tau_MeV: PDG2024:sum-leptons] [m_e_MeV: CODATA2022] |
| pin:lepton_ratios/m_tau/m_mu_lepton | pin | - | 16.8172849931228 | 1 | 16.8176918449783 | 0.0008518 | 24.19 | 0.4776 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 16.81728499 z=0.4776 | superseded by wave7/m_tau/m_mu (first occurrence) | derived ratio:m_tau_MeV/m_mu_MeV from [m_tau_MeV: PDG2024:sum-leptons] [m_mu_MeV: CODATA2022] |
| pin:lepton_ratios/m_mu/m_e_lepton | pin | - | 206.768281922727 | 1 | 206.7682827 | 4.6e-06 | 0.003759 | 0.1690 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 206.7682819 z=0.1690 | pin target 206.768 is 61.5 sigma off the current reference; superseded by m_mu_over_m_e | CODATA 2022 "muon-electron mass ratio" https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| pin:predictions/CMB_tau | pin | - | 0.0539995112799474 | 1 | 0.054 | 0.007 | 9.05 | 0.0001 | PASS | PASS |  | AEB2AD (d127c07e 2026-09-14) 0.05399951128 z=0.0001 | superseded by wave2/tau_reion (first occurrence) | PDG 2024 https://pdg.lbl.gov/2024/reviews/rpp2024-rev-astrophysical-constants.pdf |

### EXPLORATORY (tier frozen-pending; not counted above; docs/freezes/REFINEMENTS_2026-10-02.md)

```
R1 |V_us| Chemistry route theta_S/phi+(1-S_Chemistry) = 0.224494609175  z_fit=0.7579  z_direct=0.2172
R2 first-row deficit alpha_seed/(pi*sqrt2) = 1.644994e-03  measured(direct Vud,Vus; seed Vub) = 1.637752e-03 +- 7.31e-04  z=0.0099
R3 V_ud exemption: seed V_ud=0.974324219688 z_fit=0.1611 z_direct=2.0444 published fit-vs-direct=2.1250 sigma_direct -> channel_mismatch (exempt under R3)
R4 branch pin_qm_floor             theta_S/phi + (1 - S_Quantum_Mechanics)    value=0.2295864791 z_fit=6.7301
R4 branch condensation_chemistry   theta_S/phi + (1 - S_Chemistry)            value=0.224494609175 z_fit=0.7579
R4 branch seed_lambda              POOF*(1+ETA_EFF)                           value=0.225149539041 z_fit=0.2052
R4 min-z route selection -> seed_lambda (z_fit=0.2052)
```

## Rerun on 2026-10-02 (logs in `xval/results/2026-10-02/`)

| step | result | log |
|---|---|---|
| C++ build (Release, Boost 1.83 mp169, -j1 under ulimit) | OK | `01_build.log` |
| full CTest | **22/22 pass** (golden at every type, trit, balanced ternary, core, Ledger A routing, seed leaves, precision report, references, refinement freeze, freestanding symbols, freezes, Ledger B ×4) | `02_ctest.log`, `02b_seed_leaves_verbose.log` |
| regen-diff vs the pinned Python engine (AEB2AD fetched by commit and checked by SHA-256, mpmath 1.4.1) | closed forms and `golden_AEB2AD.tsv` byte-identical | `03_regen_diff.log` |
| seed-leaf golden (hub scripts run unchanged), pin lineage, reference evidence, refinement freeze | all byte-identical / 0 failures | `04_leaves_lineage_refs.log` |
| Ledger B / Ledger A / tier evidence goldens from the hub's Python | byte-identical | `05_ledger_goldens.log` |
| C++ Ledger B re-score, corrected and genuine-miss reports, M3 classification, domain freeze, core sha | byte-identical; 13 842 lines, 0 mismatches | `06_ledger_b_cpp_freeze.log` |
| bare metal: freestanding x86_64 kernel under QEMU | exit 33; 35 S values, 368/368 closed forms; serial byte-identical | `07_bare_metal_qemu.log`, `serial.txt` |
| hub cross-checks (scratch clone @ 6f9c2560): margin audit, TOE gap, 31 seed scripts | 477/477 green; Label A/B true, 6/6; all scripts run | `08_hub_crosschecks.log` |

Not rerun today: the hub Lean build (567 modules, last result 0 errors) and the multiprover cross-proof run. Both are too heavy for this box's memory alongside the
C++ jobs. The Lean-side fixes are in a prompt for Damian's Grok Build agent, not in this repo.

## Rerun on 2026-10-02b (logs in `xval/results/2026-10-02b/`)

| step | result | log |
|---|---|---|
| C++ build (Release, Boost mp169, -j1 under ulimit -v 4.5 GB, nice) | OK | `00_configure.log`, `01_build.log` |
| full CTest | **24/24 pass** (adds `refinement_freeze_b`, `refinements_b_crosscheck`) | `02_ctest.log` |
| precision report regenerated | record 85/91 confirmed; 88/91 with passing frozen-pending | `03_precision.log` |
| seed-leaf golden, pin lineage, 02b re-score (CI-like venv, mpmath 1.4.1), references (115 rows incl. 6 arXiv), both freezes, C++↔Python crosscheck | byte-identical / 0 failures | `04_regen_refs_freezes.log` |

## 2026-10-02c: train/test search for class-level dressing rules (logs in `xval/results/2026-10-02c/`)

The protocol `docs/freezes/PROTOCOL_2026-10-02c` (commit 44adf76, 08:41:19 EDT) fixed the classes, the patterns and the acceptance criterion before any training number was computed.
The criterion: n ≥ 3, the same residual sign in every member, leave-one-out z ≤ 1 for at least 2/3 of members, and a full-training selection other than "none".
Training was then run and frozen in `docs/freezes/REFINEMENTS_2026-10-02c` (commit dd85c22, 08:42:21 EDT) before any target was scored (`tools/train_2026_10_02c.py`, `audit/train_2026-10-02c.tsv`).
Patterns examined: **539** (107 per class, 111 for B2). **No class met the criterion, so no rule was accepted and no target or held-out value changes.**

| class | n | sign agreement | α-power agreement | P3 LOO z ≤ 1 | P3 full selection | why no rule |
|---|---|---|---|---|---|---|
| W widths/lifetimes (τ_n, R_b, R_c, BR_Z ee/had/inv pins) | 6 | 4/6 | 5/6 | 6/6 | none | every member already passes bare, so there is nothing to learn |
| M moments/g (g_e, g_p leaves) | 2 | 1/2 | 0/2 (α³ vs α¹) | 0/2 | none | n < 3; opposite signs and orders |
| B1 binding leaves (He-4, H-3) | 2 | 1/2 | 2/2 (α²) | 0/2 | none | each leaf's dressing applied to the other gives z 9414 / 2853 |
| B2 Ledger B B/A vs AME2020 (13 nuclei) | 13 | 7/13 | 9/13 | 0/13 | none | P4 δ = c·v for v ∈ {1, A, A^-1/3, B/A}: LOO 0/13 for every v |
| T thermal (Ω_b h², N_eff, η_b) | 3 | 3/3 | 3/3 | 3/3 | none | the bare residuals −0.41 %, −1.8 %, −1.6 % are all within σ |

The thermal pins all run *high*, whereas bare T_CMB runs *low*: the class sign argues against the +yy T_CMB polish. This weakens the polish but does not kill it.

Scoring (`tools/score_2026_10_02c.py`, `audit/score_2026-10-02c.tsv`):
- **Targets, unchanged (no rule):** Γ_Z/M_Z z 4.88; deuteron B z 3.59; μ_d z 2.1e4; Ledger B H-2 B/A z 1773.
- **Held-out, bare:** R_ell z 0.33 (pass); Y_p z 0.006 (pass); Ledger B He-3 B/A z 5.3e4 (fail).
- **T_CMB checks:**
  - FSOT-internal T0 from the η_b and Ω_b h² pins via PDG BBN η10 = 274 Ω_b h²: 2.7277 ± 0.0017 K. The σ comes only from the rounding of 274 and was not pre-registered. Bare z 1.79, candidate z 0.95.
  - Noterdaeme 2011 T(z) normalisation 2.725 ± 0.002 K (arXiv:1012.3164; not independent of FIRAS): bare z 0.14, candidate z 0.55.
  - Discriminating power |cand − bare|/σ is 0.69 (Noterdaeme) and 0.84 (internal). Neither check can confirm or kill the polish, so it stays frozen-pending.

Pass counts are unchanged: **85/91 confirmed, 88/91 including frozen-pending**. The precision report was regenerated and is byte-identical. CTest passes 25/25 (adds `refinement_freeze_c`), and `xval/cpp_check.sh` passed.

## 2026-10-02d: re-derivations through Damian's building blocks (logs in `xval/results/2026-10-02d/`)

Order of work:
1. `docs/freezes/DERIVATIONS_2026-10-02d` (commit 73f89a5, 08:53:29 EDT) froze every construction, input and alternative count before any number was computed.
2. Part A and the part-B rows were scored, and the C1 training was run (`tools/train_2026_10_02d.py`, `audit/rows_2026-10-02d.tsv`, `audit/train_2026-10-02d.tsv`).
3. `REFINEMENTS_2026-10-02d` (commit 417b524, 08:54:34 EDT) froze the training before any C1 target was scored.
4. The targets were scored (`tools/score_2026_10_02d.py`, `audit/score_2026-10-02d.tsv`).

Look-elsewhere counts: A 4, B 15, C1 218, C2 2.

**A. Γ_Z structural route (A1).** Σ_f N_c G_F M_Z³/(6√2π)[(T3−2Qs²)²+T3²](1+3Q²α/4π)(1+α_s/π)_quarks, using Damian's seed G_F, the m_Z, sin²θ_W(MS-bar) and α leaves, and the α_s seed.
- **Result:** Γ_Z/M_Z = 0.4872, z 1.8e4. **FAIL**: the seed G_F is the cause.
- `seed_vev_GeV()` (hub `vendor/fsot_seed_flavor.py`; not scored in the hub suite) returns v = 58.24 GeV against v = 246.22 GeV. So seed G_F = 2.084e-4 GeV⁻², 17.9× the CODATA value 1.1663787(6)e-5, and every G_F-normalised width is high by that factor.
- **G_F-free held-outs:** σ_had⁰ = 41.472 nb vs 41.481(33), **z 0.29 (pass)**; R_ell = 20.799 vs 20.771(22), z 1.29.
- **G_F-normalised held-outs fail** by the same factor: Γ_inv z 5.6e3, Γ_ll z 1.6e4.

**B. New rows (frozen-pending; all fail z ≤ 1):**

| row | inputs | value | measured | z |
|---|---|---|---|---|
| G_F (diagnostic) | seed v | 2.0844e-4 GeV⁻² | 1.1663787(6)e-5 | 3.3e7 |
| Γ_W | seed G_F, m_W leaf, α_s seed | 37.44 GeV | 2.085(42) | 842 |
| τ_μ | seed G_F, m_μ, m_e, α leaves | 6.880e-9 s | 2.1969811(22)e-6 | 1.0e6 |
| τ_τ | τ_μ row, m_μ/m_τ leaves, BR(τ→eνν̄) **external** PDG | 9.11e-16 s | 290.3(5)e-15 | 579 |
| τ_π⁺ | not constructed: FSOT has no f_π | – | 26.033 ns | – |
| μ_n | −(2/3)μ_p leaf (SU(6)) | −1.861898 | −1.91304276(45) | 1.1e5 (−2.7 %) |
| μ_t | μ_p leaf (Schmidt, S state) | 2.792847 | 2.9789624650(59) | 3.2e7 (−6.2 %) |
| μ_h | Damian §67 #1037 P_VAR⁻⁷−C_FAC⁻¹ (stored value) | −2.126588 | −2.1276253498(17) | 6.1e5 (−488 ppm) |

**C1. Class search, enlarged classes, round-c criterion:** 0/2 accepted, so no rule is applied.
- W2 (9 members): sign 5/9, α-power 5/9, P3 LOO 6/9, full selection "none".
- M2 (13 members): sign 7/13, α-power 6/13, P3 LOO 0/13, P4 (v ∈ {1, A, A^-1/3, J}) LOO 0/12.
- Targets, bare: μ_d pin z 2.13e4 (−54.6 ppm); Damian's §67 #1036 μ_d route C_EFF⁻⁶/A_BLEED⁹ z 6.7e3 (−17.2 ppm); Γ_Z/M_Z pin z 4.88.
- Held-out: Mn-55 (§67) z 13.7; R_ell z 0.33.

**C2. Two-nucleon deuteron:** μ_d = μ_S − (3/2)(μ_S − ½)P_D, with μ_S = μ_p(leaf) + μ_n(row) and P_D = 5.76 % **external** (AV18).
- Result: 0.89372, z 1.6e7 (+4.2 %). The error comes from the μ_n row: with the CODATA μ_n the same formula gives 0.84699, which is the AV18 impulse value 0.847 (diagnostic only).
- A two-nucleon B_d is not constructible from FSOT leaves (it needs m_d or a_t, r_t).

**Pass counts unchanged:** 85/91 confirmed, 88/91 including frozen-pending. The precision report is byte-identical. CTest 26/26 (adds `refinement_freeze_d`); `xval/cpp_check.sh` passed.

## 2026-10-02e: v/G_F bug fix and missing pieces (logs in `xval/results/2026-10-02e/`)

`docs/freezes/DERIVATIONS_2026-10-02e` (commit b401c0d, 09:08:39 EDT) was committed before any downstream number.
- **Bug fix:** hub `seed_vev_GeV()` returns 58.24 GeV against its own docstring relation v = 2 m_W s_W/√(4πα). This repo implements the documented relation; the hub fix is left to Grok Build.
- **Scheme, decided a priori:** S1 (primary, FSOT-only) is on-shell s² = 1 − (m_W/m_Z)² from the leaves with α(0). S2 (secondary) is the MS-bar s² leaf with α̂(M_Z) = 1/127.930, an **external** PDG input.
- **Look-elsewhere:** scheme 4, α_s(m_τ) 3, BR/τ_τ 3. All rows are produced by `tools/score_2026_10_02e.py` into `audit/score_2026-10-02e.tsv`.

| row | S1 (primary) value / z | S2 (secondary) value / z |
|---|---|---|
| v | 250.775 GeV (+1.85 %) | 246.640 GeV (+0.17 %) |
| G_F | 1.12439e-5 (−3.60 %), z 7.0e4 | 1.16241e-5 (−0.34 %), z 6.6e3 |
| Γ_Z/M_Z (A1) | 0.026282, **z 43.0** | 0.027171, z 7.8 |
| Γ_inv | 479.73 MeV, z 13.0 | 495.95 MeV, z 2.2 |
| Γ_ll | 80.544 MeV, z 40.0 | 83.267 MeV, z 8.3 |
| σ_had⁰ (G_F-free) | 41.472 nb, z 0.29 | same |
| R_ell (G_F-free) | 20.799, z 1.29 | same |
| Γ_W | 2.0199 GeV, z 1.55 | 2.0882 GeV, **z 0.08** |
| τ_μ | 2.3641 μs, z 7.6e4 | 2.2120 μs, z 6.8e3 |
| τ_τ (external BR) | 313.08 fs, z 45.6 | 292.94 fs, z 5.3 |

S1 misses by about the size of the omitted on-shell Δr (PDG 0.03685): G_F is −3.6 %. Under the frozen rule Γ_Z/M_Z does **not** pass, so the record set is unchanged.

**Step 2 results:**
- **α_s(m_τ), nf = 3:** run with 4 loops from the seed α_s(M_Z) = 0.117909, with 3-loop decoupling at the FSOT thresholds m_b = 4.222 GeV and m_c = 1.284 GeV. Result 0.31339 vs PDG 0.314(14), **z 0.04**.
- **BR(τ→eνν̄)** from that α_s (fixed-order δ_P through a⁴, leading-log S_EW, FSOT V_ud and V_us; G_F-free): 0.17829 vs 17.82(4) %, **z 0.23**.
- **τ_τ with the FSOT BR:** S1 313.19 fs (z 45.8); S2 293.04 fs (z 5.5).
- **Not constructed:** μ_n, μ_t, f_π, τ_π⁺ and the two-nucleon μ_d. No FSOT route exists in the seeds, the §66/§67 database or the data, and none was invented.
- **§67 entries that don't reproduce** (recomputed − stored, stored values kept): #1036 −287 ppm, #1037 −78 ppm, #1038 −1074 ppm, #1039 +36948 ppm, #1041 +170 ppm, #1045 +10846 ppm. In every case the stored value is closer to the measurement.

**Pass counts:** 85/91 confirmed, 88/91 including frozen-pending (unchanged). The new frozen-pending rows that pass are α_s(m_τ) and BR(τ→eνν̄), plus Γ_W under the secondary scheme only. CTest 27/27; `xval/cpp_check.sh` passed.

## 2026-10-02f: Δr and α(M_Z) from FSOT leaves; lost-route search (logs in `xval/results/2026-10-02f/`)

`docs/freezes/DERIVATIONS_2026-10-02f` (commit 16de0bc, 16:21:08 EDT) was committed before any FSOT-input Δr, G_F or weak-row number was computed.
- **Decomposition:** Δr = Δα − (c²/s²)Δρ + Δr_rem. Sources: Hioki hep-ph/9511224 eqs. 2.1–2.4, PDG 2024 EW review eq. 10.23, and the one-loop constant as written in arXiv:1001.1759 eq. 12.
- **Hadronic part:** H1 (primary, FSOT-only) is a perturbative quark loop with constituent light quarks m_p/3 and the FSOT m_c and m_b. H2 (secondary) uses the external PDG 0.02783.
- **Disclosed:** a back-of-envelope H1 ≈ 0.024 was seen while designing it, and the choice was not changed. ρ^(2)(m_H/m_t) and the 3-loop leptonic term are omitted.
- **Look-elsewhere:** hadronic 2, light-quark choice 3, α_s scale 2, remainder constant 2, resummation 2.
- **Δr reference σ:** the freeze named σ 0.00021 (quadrature). The reference row uses the printed 0.00020 because the reference checker requires printed digits. z changes by less than 5 %.
- **Rows:** all produced by `tools/score_2026_10_02f.py` into `audit/score_2026-10-02f.tsv`, byte-identical in both venvs.

| piece | value |
|---|---|
| Δα_lep (1+2 loop) | 0.0314984 (2-loop 7.76e-5) |
| Δα_top | −5.75e-5 |
| Δα_had H1 / H2 | 0.024104 (PDG 0.02783(6): −13.4 %, z 62) / 0.02783 |
| Δρ (QCD factor 0.8927) | 0.008295 (H1) / 0.008326 (H2) |
| Δr_rem: top log / Higgs / constant | −0.005184 / +0.001510 / +0.006620 → 0.002946 |
| **Δr** | **H1 0.029623 (z 36 vs PDG SM 0.03685)** / H2 0.033240 (z 18) |
| 1/α(M_Z) on-shell (lep+had) | H1 129.416 / H2 128.906 |

| row | H1 (primary) value / z | H2 (secondary) value / z |
|---|---|---|
| G_F | 1.15871e-5 (−0.66 %), z 1.3e4 | 1.16305e-5 (−0.29 %), z 5.5e3 |
| Γ_Z/M_Z (A1) | 0.0270845, **z 11.2** | 0.0271859, z 7.2 |
| Γ_Z (A1) | 2.46977 GeV, z 11.2 | 2.47901 GeV, z 7.2 |
| Γ_inv | 494.37 MeV, z 3.2 | 496.22 MeV, z 2.0 |
| Γ_ll | 83.002 MeV, z 11.4 | 83.313 MeV, z 7.8 |
| σ_had⁰ / R_ell (G_F-free) | 41.472 nb z 0.29 / 20.799 z 1.29 | same |
| Γ_W | 2.0816 GeV, **z 0.08** | 2.0894 GeV, z 0.10 |
| τ_μ | 2.2262 μs, z 1.3e4 | 2.2096 μs, z 5.7e3 |
| τ_τ (external BR / FSOT BR) | 294.81 fs z 9.0 / 294.91 fs z 9.2 | 292.62 fs z 4.6 / 292.71 fs z 4.8 |

Δr closes most of the round-e gap (G_F goes from −3.60 % to −0.66 % under H1). The rest of the Δr shortfall is about 0.0037 in H1 from the hadronic part and about 0.0036 in both from the remainder/higher orders. Γ_Z/M_Z does **not** pass under H1 (z 11.2), so the record set is unchanged.

**Lost-route search** (40 dappalumbo91 repositories, every ref and the full history, read-only; 678 raw hits inspected):
- **No route found** for μ_n, the triton moment, f_π, P_D, Δr or α(M_Z). τ_π⁺ and the two-nucleon μ_d therefore can't be built.
- **Older parallel §67 versions** in the hub's `vendor/cosmology/database` copy (commit 5d0d5f31, 2026-07-10 00:52 EDT) were ported unchanged:
  - H-2 E/π = 0.865256 (+0.91 %, fail)
  - He-3 −(e−γ) = −2.141066 (+0.63 %, fail)
- **Deuteron binding:** only the known √e/e + φ (copied across repos) and Ledger B #72.

**Pass counts:** 85/91 confirmed, 88/91 including frozen-pending (unchanged). CTest 28/28; `xval/cpp_check.sh` passed.

## 2026-10-02g: effective Z couplings (LEPTOP) in Γ_Z; pre-declared validation FAILED (logs in `xval/results/2026-10-02g/`)

`docs/freezes/DERIVATIONS_2026-10-02g` (commit 0eba00a, 16:43:54 EDT) was committed before any round-g number (PDG- or FSOT-input) was computed.
- **Construction:** LEPTOP, Novikov–Okun–Rozanov–Vysotsky, hep-ph/9503308. Every Z → f f̄ channel uses one-loop effective couplings g_Af, g_Vf (V_i = t + T_i + H_i + C_i + δV_i) with LEPTOP's leading two-loop terms (α α_s, α α_s² t, α² t², α² h), the t-dependent Z→b b̄ vertex (φ + δφ), the QED/QCD radiators R_V, R_A, and two-loop running m̂_b, m̂_c at M_Z. This is the effective-coupling form of PDG 2024 EW review eqs. 10.53, 10.54, 10.76c and 10.77. Code: `tools/zwidth_g.py` (equation labels in comments). The Denner Δr code is not used; G_μ is round f's frozen G_F.
- **Transcription checks** against LEPTOP's printed numbers (m_t = 175) all agree to the printed digit, with one exception: δ_tα/α (eq. 308). The exact formula gives −0.00792; the printed −0.00768 is the leading 1/t term LEPTOP quotes.
- **Validation** (PDG/CODATA inputs only; criterion |Γ_Z − 2.4940| ≤ 0.0009): **Γ_Z = 2.49592 GeV, deviation +1.92 MeV: FAILED.** The partial widths are uniformly about 0.07 % above the PDG 2024 SM column (Γ_e 83.991 vs 83.955; Γ_inv 501.70 vs 501.435; Γ_u 300.18 vs 299.87; Γ_d 383.12 vs 382.75; Γ_b 375.92 vs 375.73). That is consistent with LEPTOP's 1995 truncation: the full two-loop fermionic terms are missing. Informational comparisons: R_e 20.745 (SM 20.736), R_b 0.21574 (0.21583), R_c 0.17223 (0.17221), σ_had⁰ 41.473 nb (41.481), sin²θ_eff 0.23150 (0.23161). Per the freeze the construction is **not validated**, so no round-g row is confirmed. The construction was not changed after the validation.
- **Look-elsewhere:** 72 configurations considered, 3 scored (H1, H2, H2c), 1 able to confirm (H1).

| row | H1 (primary) value / z | H2 (secondary) value / z | H2c (diagnostic, CODATA G_F) value / z |
|---|---|---|---|
| Γ_Z/M_Z | 0.0271650, **z 7.99** | 0.0272650, z 4.02 | 0.0273707, z 0.16 |
| Γ_Z | 2.47710 GeV, z 8.00 | 2.48622 GeV, z 4.03 | 2.49586 GeV, z 0.16 |
| Γ_inv | 498.39 MeV, z 0.54 | 500.27 MeV, z 0.71 | 501.71 MeV, z 1.67 |
| Γ_ll | 83.395 MeV, z 6.85 | 83.706 MeV, z 3.23 | 83.992 MeV, z 0.10 |
| R_ell | 20.729, z 1.91 | 20.728, z 1.99 | 20.744, z 1.22 |
| R_b | 0.215767, z 0.79 | 0.215760, z 0.80 | 0.215720, z 0.86 |
| R_c | 0.172177, z 0.03 | 0.172175, z 0.02 | 0.172231, z 0.04 |
| σ_had⁰ | 41.4774 nb, z 0.11 | 41.4779 nb, z 0.09 | 41.4737 nb, z 0.22 |
| sin²θ_eff^lept (held-out) | 0.232368, z 6.75 | 0.232442, z 7.32 | 0.231496, z 0.05 |

Γ_Z/M_Z does **not** pass under H1 (z 7.99), and the validation failed anyway, so nothing is confirmed. The H1 shortfall comes from G_μ(H1), which is 0.66 % low (round f). It enters Γ_Z directly and moves s² through eq. 303, which is why sin²θ_eff is high under H1 and H2. With the CODATA G_F (H2c, diagnostic only), the FSOT m_Z, m_t, m_H, α_s, m_b and m_c give Γ_Z within 0.16σ. Part of that agreement is the +1.9 MeV construction offset seen in validation.

**Pass counts:** 85/91 confirmed, 88/91 including frozen-pending (unchanged). The new round-g rows are frozen-pending and unconfirmable because validation failed. CTest 29/29; `xval/cpp_check.sh` passed.
