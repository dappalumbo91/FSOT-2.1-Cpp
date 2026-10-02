# Refinements freeze — 2026-10-02 (tier: frozen-pending)

These are refinements to how the FSOT math folds into domains. They were made on 2026-09-30 to 10-02
(Grok Build overnight session; review copies in `gb-recovery/review/`). They are frozen here with dated hashes.
The rule is: **refine → freeze with a dated hash → test on unseen data**. None of them is scored as a
confirmed prediction in `docs/PRECISION_REPORT.md`. Their numbers are listed below and in the
"EXPLORATORY" block of `audit/precision_2026-10-02.md`, labelled exploratory. The C++ evaluator is
`apps/fsot_precision.cpp`.

Machine-readable copy: `REFINEMENTS_2026-10-02.json`. The statement hashes are sha256 of the exact UTF-8
`statement` string. `refinements_sha256` = sha256 of the compact sorted JSON of the `refinements`
array. `REFINEMENTS_2026-10-02.sha256` holds the file hashes. `tools/verify_refinement_freeze.py` checks all three
(CTest `refinement_freeze`).

Pin AEB2AD and hub data 6f9c2560 are unchanged. No FSOT constant, `f`, domain parameter or tolerance was changed.

| id | refinement (exact statement in the JSON) | statement sha256 | exploratory numbers (PDG 2024) |
|---|---|---|---|
| R1 | \|V_us\| = θ_S/φ + (1 − S_Chemistry), in place of the pin's θ_S/φ + (1 − S_Quantum_Mechanics) | `a6305088e58187feef46dcfe80491da4aec905fefd507d91a2c9b7a606691269` | 0.224494609175; z = 0.758 vs fit 0.22501(68); z = 0.217 vs direct 0.22431(85) |
| R2 | First-row deficit 1 − Σ\|V_ui\|²(direct) = α_seed/(π√2), with α_seed = 1/(φG/C_factor)³ | `7e116ea7e41854997101bbc62ccd62bf1e9fd35e010aba1d9d75c51c93416c40` | predicted 1.644994e-3; measured 1.637752e-3 ± 7.31e-4; z = 0.0099 |
| R3 | \|V_ud\| channel_mismatch exemption: fit passes, direct fails, and the published fit-vs-direct separation ≥ the seed's direct z | `c9632ca8e60adf7b67e807f4326a46108ad530140b12147f968d7d2837153167` | seed 0.974324219688: z_fit = 0.161, z_direct = 2.044, separation = 2.125 → channel_mismatch |
| R4 | Route selection: among passing routes, take the lowest z | `7c5a3b27b305d7570f9002532532b1aeca2ebe0ec044da690b1011df5846ec60` | selects seed λ = POOF(1+η_eff) = 0.225149539041, z = 0.205 (others 0.758 and 6.730) |

`refinements_sha256 = 26df93d8a796b7aa01e8f3f486e1df220e4418a7ffeff5aa263a0bbea547bf6b`

Notes:

- R1 gives the same value as the closed form under pin 3090BC, before FE23A2 moved Quantum_Mechanics from D=6 to D=5
  (hub 3c74a180, 2026-09-11). Re-routing a single observable is a domain-fold choice. It is frozen here and was not
  applied to the pin.
- R2's α_seed (1/136.827) is a different number from the pin constant `ALPHA` (8.08×10⁻⁴) and from the α⁻¹ leaf
  (137.035999166). The review script calls it `alpha_FSOT`. See AUDIT_LOG H-09.
- R4 is a selection rule. The scored set uses the committed CKM seed leaf (hub `scripts/ckm_magnitude_seed_check.py`,
  4c270461, 2026-09-29). That leaf existed before this freeze and is not chosen by z. In this case it is also the route R4 picks.
- Unseen-data tests: the next PDG/CKMfitter/UTfit |V_us| and global fit (R1, R4), and a new superallowed |V_ud| with new
  K-decay |V_us| (R2). R3's verdict must be recorded before the seed z is looked at.

Source-script sha256 (review copies, not committed here): fsot_precision_kill.py `6b41915f…1b45db8`,
fsot_routing_refiner.py `fe48687f…ca8ec84db`, fsot_routing_refinement.json `a51a3b65…7e279ccb`,
fsot_locked_routes.json `cc97c7dc…480f9f418`. The full hashes are in the JSON.
