# Plan for the rest of the C++ port

## Done in this prototype (golden-tested against AEB2AD)
- Whole of `vendor/fsot_compute.py`: seeds, layers 1–2, scalar law, nest/D_eff/look/hits/observed/C, 35 domain S, all 26 closed-form sections (368 rows), Ledger B `fsot_correct` (f = ALPHA), report CLI.
- Ternary core (`trit.hpp`) matching Zig/Rust/Python/CUDA semantics + bit-sliced fast paths; FSOTB VM core (`fsotb_vm.hpp`) running EVAL_PANEL on the live nest.
- **Milestone 1 (2026-10-01):** Ledger B / benchmark-margin re-scorer (`include/fsot/host/ledger_b.hpp`, `apps/fsot_ledger_b.cpp`): C++ port of the hub's `analyze_benchmark` + literature-aware error + live-law re-score; bit-identical to the hub Python on all 478 benchmark files at hub 6f9c2560 (13,841/13,841 golden lines). Balanced-ternary arithmetic core (`ternary.hpp`, docs/TERNARY.md), canonical trit spec (docs/TRIT_SPEC.md), audit log (docs/AUDIT_LOG.md).
- Codegen (`tools/gen_closed_forms.py`) refuses to run unless the authority SHA equals the pin; no number is typed by hand.

## Next (ordered by value / effort)
| # | Item | Source | Effort |
|---|---|---|---|
| 1 | ~~Ledger B panel re-scorer~~ **done (milestone 1)** | hub data/ (478 benchmark files at 6f9c2560) | — |
| 2 | Ledger A emit (`fsot_ledger_a_lib.py`) + `predict_closed_form` CLI | hub scripts | 0.5–1 d |
| 3 | Property routing (`fsot_api_predict_lib.py` route_property/formula_mass) | hub scripts | 0.5 d |
| 4 | Trinary syntax rows + opcode registry loader; Reality-OS 27-op wire FSOTB loader | hub vendor, Reality-OS fsotb.rs | 1–2 d |
| 5 | Extend AST codegen to pure-math modules: fsot_ckm_pmns, fsot_seed_flavor (97 fns), fsot_uniqueness_confinement, fsot_matter_antimatter, fsot_complex_interaction, fsot_gr_sm | hub vendor | 1–2 wk (codegen does most; hand-port loops) |
| 6 | Numeric kernels where C++ pays off: fsot_nse3d, fsot_path_sum, fsot_dynamics (double/f128, optional OpenMP) | hub vendor | 1 wk |
| 7 | Data panels / gauntlet (scale_interconnects, millennium_accuracy, cepheid, earth_fluid, fiction_calibration) | hub vendor | 3–4 wk; do last, keep Python as reference |
| 8 | Python binding (pybind11, optional `fsot[fast]`) + CUDA bridge for FSOT-GPU ternary attention using `trit.hpp` packing | — | 1 wk |
| 9 | C++ as an extra replay prover next to Rust f64 replay in the multiprover (emit obligation values from mp169) | hub verification | 1 d |

Rough total for full parity: 6–9 weeks. Items 1–4 (~1 week) cover the hub's headline ledgers.

## Milestones (long-running workstream)
1. **Done:** Ledger B re-scorer · balanced-ternary core · TRIT_SPEC · AUDIT_LOG v1.
2. Ledger A emit + property routing (items 2–3), `fsot_correct` CLI, citation pass over hub JSON `reference` fields and docs (AUDIT_LOG C), look-elsewhere enumeration tool (AUDIT_LOG E-1).
3. Freestanding header-only core (engine without std::vector/string/exceptions; `Engine<BTFloat>` usable bare-metal) + QEMU x86_64 demo printing the 35 domain scalars computed in balanced ternary over serial.
4. Pure-math vendor modules via the generator (item 5), numeric kernels (item 6).
5. Data panels / gauntlet (item 7).

## Precision policy
- `mp169` (Boost cpp_bin_float, header-only) = authority precision; used for golden and certificates.
- `__float128` gives 33 digits at ~20× Python speed; rounded to double it matches `float(mpmath)` bit-for-bit on all 536 real rows → recommended production type on GCC/Clang x86-64.
- `double` for hot loops (≈1e-14 rel; ~2500× Python). Note MSVC: `long double == double` and no `__float128`; use mp169 or MPFR (vcpkg) there.

## CI (`.github/workflows/ci.yml`)
1. `build-test`: CMake + Ninja build on ubuntu-latest, `ctest` (golden at every available type + trit tests).
2. `regen-diff`: fetch hub `vendor/fsot_compute.py` at the pinned commit, check SHA = `AUTHORITY_PIN.json`,
   run `gen_closed_forms.py` + `dump_golden.py`, fail if generated files differ from the committed ones.
3. `ledger-b`: sparse-clone the hub at `ledger_b_data_commit` (benchmark JSONs, anchor files, scripts, authority),
   regenerate `golden/ledger_b_6f9c2560.tsv` with the hub's own Python and diff it, then build `fsot_ledger_b`
   and require byte-identical output.
