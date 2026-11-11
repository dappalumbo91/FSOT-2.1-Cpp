# FSOT-2.1-Cpp as the single engine (branch `single-engine`, off PR #5 head 57ac6df — LOCAL ONLY, not pushed)

Steering: Damian t987u, 2026-11-11 12:24 PM EST. Every verdict below is produced by code in this repo
(`tests/test_derivations.cpp` → ctest `derivations`, double and mp169); nothing is chosen by preference.

## 1. Discrepancies D-01 … D-10 — what the derivation gives

| id | question | derivation (in-engine) | result |
|---|---|---|---|
| D-01 | pin AEB2AD vs 9EC3CF | `pin_canonical`: hash over CRLF-canonical bytes of vendor/fsot_compute.py | **AEB2AD** from both the raw and LF checkouts → resolved (9EC3CF is the LF-byte hash of the same file) |
| D-02 | C_cosm 1/(π²φ) vs 1/(10φ) | `rebuild_layer2(F, decade)`: AEB2AD's one decade map (10→π²) must rebuild C_EFF=π⁻⁴ and K=1−π⁻⁴ | decade π² rebuilds both **bit-identically**; decade 10 moves C_EFF −4.784e-5 and K +2.687e-4 → **1/(φπ²) derived**. Caveat: 13 closed forms are better under 10φ (Gluon_condensate 6.94 %→0.14 %, \|V_ub\| 2.65 %→0.009 %, …) — dial-in targets, see WORST_RESIDUALS.md §B |
| D-03 | Lean cache values vs engine | `lean_sync`: S_cosm, S_quant, H0, T_CMB, n_s, Ω_b h² recomputed live | equal to the engine (Ω_b h² Lean formula = engine exactly at QM rung 6) → caches derived, not stored |
| D-04 | QM rung 5 vs 6 | `nest_rung_continuous` = 5·5^{1/19} = 5.441992; `qm_rung_trials` (nearest, geometric, log5, floor, ceil) | every rule that leaves the other 19 rungs unchanged gives **5**; only ceil gives 6 and it moves 12 other rungs. **FLAGGED, both kept**: engine stays on the owner's rung 6 (decision 2026-10-23); `with_qm_rung(F,5)` is the one-call alternative; 7 rows all get worse under 5 (BEFORE_AFTER.md §3). Supporting 6: Lean \|S_cosm\|(1−S_quant) = authority (1−S_chem) only at D6. **Needs Damian's call.** |
| D-05 | ChemLink D_eff table / long-range gate | `chemlink_from_nest`, `long_range_gate_biochem` | 10,11,7,7,6,6,6; gate ceil(η_eff·10)=ceil(4.6694)=**5** → derived |
| D-06 | per-species D_eff | nest | species inherit Neuroscience rung **11** → derived |
| D-07, D-08, D-10 | build glob, stamp semantics, toolchains | — | process items, nothing to derive (documented in ../../DISCREPANCIES.md) |
| D-09 | trit encodings | `pack_t1`/`unpack_t1` | lossless 3/3 → resolved |

## 2. Literal → derived replacements (BEFORE_AFTER.md §1, 13 rows)
- `DNA_base_pair`: literal a0 → seed leaf a_0×1e10: 3.39645316 → 3.39645451
- `Proton_radius`: literal 0.8413 → G⁷ + P_new: 0.8412485
- 11 B-03 rows: decimal exponents → exact p/q (shifts ≈1e-15)
- Definition rows are tagged and never scored. No frozen value changed silently: all moves are in that table.

## 3. Folded into the engine
- `golden/folded_routes.tsv` (from tracer ledger sha256 2201ef2c…e1e): 85 PASS/INCLUDE rows (tk, tm, to, tg, ry, sd, sn, …); 42 tip predictions re-derived **live** by `fold::Live<R>` (worst rel 1.9e-11); 58 z re-scored; 46 in-bar, 12 out. sd/sn use recorded predictions (live port not done). sd uses g_A only as the F_A(0) input — g_A itself is not scored ((l)).
- **§43.5vt (G_F, τ_n) folded, flagged `SM_PARITY_REFINE_LATER`** (Damian t994u, 2026-11-11 1:00 PM EST; ruling
  RULING_t992u_SM_PARITY_GATE.md sha8 c65ff89d, verified as the sha256 of its body). Carried route P2 = C1+C2+C3+C5µ+C6
  (no C7): G_F = 1.16690544271959e-5, τ_n = 877.8484108 s; P1 (with C7) kept as the documented alternate.
  `include/fsot/fold/vt_gf.hpp` runs the fixed point live (x_t, Δρ, C5µ Δr^(2) + T_conv, C6 at every iteration) on the
  engine's own seed leaves (M_W, M_Z, α, s_W², m_t equal the vt package to 1e-50). Loop-invariant coefficients are banked in
  `golden/vt_package.tsv` (`tools/gen_vt_package.py`, 50 digits, stamped with the vt score.py / results.tsv / DONE.md sha256).
  Gates: τ_n Gate A PASS (z +0.099 UCNτ, +0.195 Pattie); G_F Gate A FAIL (strict MuLan τ_μ z −901.2), Gate B ACCEPT
  (+451.5 ppm vs G_μ ≤ 809.87). The rows that read G_F (Z-2 G_F, Γ_Z/M_Z A1 width) carry the same flag. Before/after: BEFORE_AFTER.md §4.
  Hooks: `fold::vt::Hooks` — `vv_rem_add` / `vv_route` (§43.5vv Δr), `tau_vk_override` (§43.5vw ΔR^V, §43.5vx g_A).
  Test: ctest `vt_gf`. Not ADOPT, no GO-MERGE. V_ud and g_A stay hosted inside τ_vk and are never scored.
- PRs #1–#4 cherry-picked with -x (c88aea4, 6937f2d, 29f3c64, fd00b48, 98ca744).
- Archive check [10]: the single-engine parity column equals all 368 archive obs entries; 13 moved rows all appear in BEFORE_AFTER; D-02/D-04 sensitivity flags agree with the archive.

## 4. Tests (Phase 3 run; see STATE.md for the latest) (zig 0.17 clang, Ninja; logs in ../../logs/phase3/)
- ctest: **108/109 pass**. The 1 failure is `golden`, long-double only (Chain_consistency_% cancellation row, rel 1.4e-12 vs tol 1e-15). It also fails on the untouched PR #5 baseline (ctest_baseline.log) — a toolchain artifact (N-3). double PASS; mp169 536/536 bit-identical to the golden.
- New tests: derivations, folded_routes, single_engine_table(_golden), single_engine_folded_golden, single_engine_before_after_committed, worst_residuals(_committed).
- Archive `tools/check.py`: PASS.

## 5. Next dial-in list
See WORST_RESIDUALS.md (15 scored rows with |z|>1; 24 unscored rows >0.5 %).

## Iron-out pass 1 (local branch ironout-1)
See [IRONOUT_1.md](IRONOUT_1.md) (before/after, verdicts, candidates not adopted, open decisions) and [SCORING_CRITERIA_IRONOUT_1.md](SCORING_CRITERIA_IRONOUT_1.md) (criteria-only changes).
