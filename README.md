# FSOT-2.1-Cpp

[![CI](https://github.com/dappalumbo91/FSOT-2.1-Cpp/actions/workflows/ci.yml/badge.svg)](https://github.com/dappalumbo91/FSOT-2.1-Cpp/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

A C++20 port of the **FSOT 2.1** computational engine, plus a balanced-ternary (trinary) core.
The authority stays in the hub, **[FSOT-2.1-Lean](https://github.com/dappalumbo91/FSOT-2.1-Lean)**:
`vendor/fsot_compute.py` at pin **AEB2AD**. This repo reproduces that file's numbers in C++, golden-checks
every value against it, and runs it 2–2900× faster depending on the precision you pick.

The law is S = K(T1 + T2 + T3), built from five seeds (π, e, φ, γ, Catalan G) with zero free parameters:
D_eff comes from the 20-generation nest, look/hits/observed are named fold laws, and the Ledger B
amplitude is f = ALPHA.

## What is ported (v0.1)
- All of `fsot_compute.py`: seeds, layer-1/2 constants, the 24-input scalar law, nest → D_eff, the fold laws,
  the 35 domain scalars, all 26 closed-form sections (368 rows: waves 1–10, validation, leptons,
  dynamical systems, neural, consciousness, homeostasis, soliton/STDP, cross-species, trinary, predictions,
  chemistry), and the Ledger B correction c = m(1 + |S|·ALPHA).
- Trinary core (`include/fsot/trit.hpp`) with the same semantics as the trit code in
  [FSOT-Genetics](https://github.com/dappalumbo91/FSOT-Genetics) / [fsot-neuron-zig](https://github.com/dappalumbo91/fsot-neuron-zig) (Zig T1 packing, Rust codon packing),
  [FSOT-GPU](https://github.com/dappalumbo91/FSOT-GPU) / [FSOT-Quantum](https://github.com/dappalumbo91/FSOT-Quantum) (code {0,1,2}, collapse at C_EFF·P_VAR, consensus similarity, H/CX/Bell analogs).
  It adds bit-sliced 32-trit word ops and a 27-trit balanced-ternary integer.
- The FSOTB 27-opcode / 25-register VM core from [FSOT-Reality-OS](https://github.com/dappalumbo91/FSOT-Reality-OS) (`include/fsot/fsotb_vm.hpp`).
  Its EVAL_PANEL reads the live 35-domain nest.

- **Ledger B / benchmark-margin re-scorer** (`include/fsot/host/ledger_b.hpp`, `apps/fsot_ledger_b.cpp`): a C++ port of
  the hub's `benchmark_margin_lib.analyze_benchmark` (scalar/classifier/structural classification, literature-aware
  error, contested rows, gates) plus a re-score of every Ledger B record with the live law. Over all 478
  `data/*_benchmark.json` files at hub commit 6f9c2560, it is **bit-identical to the hub's Python**: 13,841 of 13,841 golden lines,
  477 active / 477 green, 140,088 routed Ledger B records. Runtime is 6.5 s, vs about 6 s for Python, and is dominated by JSON parsing.
- **Balanced-ternary arithmetic** (`include/fsot/ternary.hpp`, see [docs/TERNARY.md](docs/TERNARY.md)): trit/tryte words and a
  balanced-ternary floating-point type. Ternary operations do the actual math. `Engine<BTFloat<110>>` evaluates the whole
  FSOT core in ternary and matches the 50-digit golden to 9.5e-50. The header is freestanding: no heap, exceptions, iostream or libm.
- **Ledger A emit and property routing** (`include/fsot/host/ledger_a.hpp`): bit-identical to the hub Python.
- **Corrected modes** for the audit findings. Parity stays the default and is golden-tested.
  - `fsot_ledger_b --corrected-out` and `fsot_report --corrected`: see "Fixed in C++" in [docs/AUDIT_LOG.md](docs/AUDIT_LOG.md).
- **Evidence tiers** for every gated record and domain ([docs/EVIDENCE_TIERS.md](docs/EVIDENCE_TIERS.md)).
- **A look-elsewhere count** ([docs/LOOK_ELSEWHERE.md](docs/LOOK_ELSEWHERE.md)).
- **A full citation/DOI pass** (`tools/check_citations.py`).
- **Bare metal:** a freestanding `CoreEngine` (`include/fsot/core.hpp`) and an x86_64 kernel. It boots under QEMU and prints, over serial, the 35 domain S and all 368 closed-form rows (26 sections), computed in balanced ternary ([docs/BARE_METAL.md](docs/BARE_METAL.md)).
- **`predict_closed_form`:** CLI for any closed-form row in the freestanding ternary core (`--section`, `--name`, `--digits`, `--trits 40|72|110`, `--corrected`, `--tsv`, `--list-sections`).
- **Freezes:** `fsot_freeze_domain` writes and verifies dated SHA-256 freezes of the live mapping against AEB2AD. The tiers count them per row ([docs/FREEZES.md](docs/FREEZES.md)). New post-freeze public data is tracked in [docs/PROMOTION_WATCH.md](docs/PROMOTION_WATCH.md).
- **Precision pass:** the 188 genuine-prediction misses are split into data handling and formula, with the data-handling causes fixed in corrected mode ([docs/PRECISION_M3.md](docs/PRECISION_M3.md)).
- Specs and audit: [docs/TRIT_SPEC.md](docs/TRIT_SPEC.md) (canonical trit wire format + codon mapping, cross-repo
  mismatches, and the status of fixes T-1 to T-5 in the other repos) and [docs/AUDIT_LOG.md](docs/AUDIT_LOG.md) (neutral rigor log with evidence).

Header-only: `#include "fsot/engine.hpp"`, then `fsot::Engine<double> e; e.domain_scalar("Thermodynamics");`.

## Build (verified on Linux: Debian, GCC 14.2, CMake 4.4, Boost 1.83; CI on ubuntu-latest)
```bash
sudo apt-get install -y libboost-dev nlohmann-json3-dev ninja-build   # Boost: 169-bit type; nlohmann: Ledger B tool (both optional)
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build
ctest --test-dir build --output-on-failure           # golden, trit, ternary, freestanding tests
# Ledger B re-scorer against a hub checkout at AUTHORITY_PIN.json ledger_b_data_commit:
./build/fsot_ledger_b --hub /path/to/FSOT-2.1-Lean --golden golden/ledger_b_6f9c2560.tsv
./build/bench_ternary                                # ternary vs binary results + speed
./build/fsot_report                                  # full report at authority precision
./build/bench_cpp                                    # timings
```
Requirements: a C++20 compiler and CMake ≥ 3.20. Boost headers (Boost Software License) and GCC libquadmath are optional.
Nothing paid.

## How the golden tests tie to the authority
1. `AUTHORITY_PIN.json` records the hub commit `d127c07e`, the raw URL, and SHA-256 `AEB2ADAD…AAC170` of `vendor/fsot_compute.py`.
2. `tools/fetch_authority.py` downloads that exact file and refuses to continue if the SHA doesn't match.
3. `tools/gen_closed_forms.py` checks the SHA again, then translates the authority's closed-form sections from the Python AST
   into `include/fsot/closed_forms.gen.inc`. No number is typed by hand. The few Python-only loops are hand snippets
   bound to a hash of the exact source statement, so if the authority edits one of them, generation fails instead of drifting.
4. `tools/dump_golden.py` runs the authority with mpmath at mp.dps = 50 and writes `golden/golden_AEB2AD.tsv`:
   643 checks covering every constant, every domain's D_eff/hits/observed/look/C/S, Ledger B corrections, all 368 rows,
   and the 5 % pass counts.
5. `tests/test_golden.cpp` compares the C++ engine to the golden file at every available number type.
   CI's `regen-diff` job repeats steps 2–4 and fails if the generated files differ from what's committed.

When the hub moves its pin, update `AUTHORITY_PIN.json`, run `cmake --build build --target fsot_regen`
(configure with `-DFSOT_AUTHORITY=<path>`), and commit the regenerated files together.

## Precision (vs the 50-digit golden, 643 checks, all pass)
| Number type | Max relative deviation | Excluding the one cancellation row¹ | Rounded to double = `float(mpmath)` |
|---|---|---|---|
| `double` | 1.2e-12 | 1.1e-14 | 265/536 (others within a few ulp) |
| `long double` (x87 80-bit) | 5.6e-15 | 4.8e-18 | — |
| `__float128` | 2.4e-30 | 4.8e-33 | **536/536** |
| Boost `cpp_bin_float<169 bits>` (same precision as mpmath dps 50) | 1.9e-46 | 1.8e-49 | **536/536** |

¹ `Chain_consistency_%` subtracts two nearly equal ratios, so it magnifies rounding.
Example: S_thermo = 0.93638756406297475802… (169-bit), and 0.9363875640629747 when rounded to double, matching Python exactly.

## Precision against published uncertainties (z ≤ 1 gate, 2026-10-02)
`apps/fsot_precision` scores every physics prediction with z = |value − central|/σ ≤ 1. σ comes from PDG 2024, CODATA 2022 and AME2020
(`reference/published_2026-10-02.tsv`; every entry is checked against committed evidence by `tools/check_references.py`). The gate is configured
once, in `include/fsot/host/precision_gate.hpp`. The legacy 2 % check and ppm are reported next to it. Record set: **85/91 pass z ≤ 1** (88/91 with the passing frozen-pending refinements, not confirmed)
(88/91 under 2 %), median 93 ppm. All 50 hub seed leaves (`include/fsot/host/seed_leaves.hpp`, ported 2026-10-02) pass. Full table, regression
causes and the 6 remaining misses (3 with a frozen-pending candidate, 3 open: Γ_Z/M_Z, deuteron binding, μ_d) are in [docs/PRECISION_REPORT.md](docs/PRECISION_REPORT.md).
Post-hoc refinements are frozen as tier frozen-pending in [docs/freezes/REFINEMENTS_2026-10-02.md](docs/freezes/REFINEMENTS_2026-10-02.md) and
[docs/freezes/REFINEMENTS_2026-10-02b.md](docs/freezes/REFINEMENTS_2026-10-02b.md) (committed before scoring) and are never counted as confirmed.
A pre-registered train/test search for class-level dressing rules (docs/freezes/PROTOCOL_2026-10-02c.md, REFINEMENTS_2026-10-02c.md; 539 patterns, 5 classes) accepted **no** rule; see PRECISION_REPORT §2026-10-02c.
2026-10-02d re-derivations (docs/freezes/DERIVATIONS_2026-10-02d.md): Γ_Z built from partial widths, plus new rows Γ_W, τ_μ, τ_τ, μ_n, μ_t, μ_h and a two-nucleon μ_d, all frozen before scoring. None passes. The G_F-normalised rows fail because Damian's seed v = 58.24 GeV; see PRECISION_REPORT §2026-10-02d.
2026-10-02e (docs/freezes/DERIVATIONS_2026-10-02e.md): seed v fixed to its documented relation. On the primary on-shell scheme G_F is −3.6 % (tree level, no Δr), so Γ_Z/M_Z is still open. The new α_s(m_τ) and BR(τ→eνν̄) rows pass (frozen-pending).
2026-10-02f (docs/freezes/DERIVATIONS_2026-10-02f.md): Δr built from FSOT leaves (FSOT-only hadronic H1: 0.0296; with PDG Δα_had H2: 0.0332). G_F is −0.66 % (H1), Γ_Z/M_Z z 11.2, still open. The lost-route search across all repositories found no route for μ_n, μ_t, f_π, P_D, Δr or α(M_Z).
2026-10-02g (docs/freezes/DERIVATIONS_2026-10-02g.md): LEPTOP effective Z couplings in Γ_Z. The pre-declared PDG-input validation **failed** (Γ_Z 2.49592 vs SM 2.4940 ± 0.0009), so nothing is confirmed. FSOT H1: Γ_Z/M_Z z 8.0, still open; see PRECISION_REPORT §2026-10-02g.

2026-10-02h (audit/FREEZE_2026-10-02h.md): each miss was traced to its first break step, then diagnosed and branched. GZ-1 (complete Δr + Freitas Γ_Z) passes its PDG-input validations but fails with FSOT's own Δα_had (z 3.84). No FSOT-native Δα_had route exists yet. Counts are unchanged at 85/91 confirmed; see PRECISION_REPORT §2026-10-02h.

2026-10-02i (audit/OWNER_DECISIONS_2026-10-02i.md): owner decisions OD-1 (score the Δm² ratio against Δm²21/Δm²31) and OD-2 (Quantum_Mechanics D_eff = 6, the pre-2026-09-11 value), added as labelled owner-decision rows next to the pinned rows. The gate is **87/91 confirmed** (85/91 pinned only).

2026-10-02i (audit/FREEZE_2026-10-02i.md): two light-hadron routes (constituent-quark m_ρ, quark–hadron-duality Δα_had) fail their PDG-input validations, so no FSOT-native hadron sector exists yet. GZ-1 with the duality Δα_had gives Γ_Z/M_Z z 0.68 (frozen-pending, not confirmed).

2026-10-02j (audit/FREEZE_2026-10-02j.md): walk-down from FSOT's absolute scale to the strong sector. Λ^(5) from the FSOT α_s(M_Z) is 209.5 MeV vs FLAG 213(8) (z 0.43, validated method; not one of the 91 rows). No FSOT-native f_π, g_A or g_πNN: the NDA and quark-model routes fail their validations, and GMOR and Goldberger–Treiman validate but lack FSOT inputs. Hence the KSRF/Δα and deuteron chains were not run, and the gate stays at 87/91.

2026-10-02k (audit/FREEZE_2026-10-02k.md): θ_S = sin(ψ_con η_eff) has no known physical counterpart. The pion, kaon, D, W, Z, H and nuclear-binding leaves are pure numbers read in MeV and are not tied to the m_e anchor; the missing factor contains the SI-defined value of e. F_π (91.8 MeV) and g_πNN (12.92) come out only as hybrids with lattice ratios. m_ρ by lowest-meson dominance misses its 1 % gate, so the Δα and deuteron chains were not run. The gate stays at 87/91.

2026-10-02l (audit/FREEZE_2026-10-02l.md): the pion and kaon were treated as pseudo-Goldstone bosons (leading-order chiral perturbation theory plus Dashen's EM term), using FSOT's quark-mass ratios and its π± and K± leaves. The held-out K⁰ comes out at 497.597 MeV against 497.611(13) (−0.003 %). The π⁰ and η miss by about 3 %, the known limit of leading order. GMOR gives m_ud 3.60 MeV and m_s 99.7 MeV, but only as hybrids. A frozen D_eff → unit map (3 families, trained on π±, B(²H) and T_CMB) puts 0 of 10 held-out leaves within 2 %. The scale factor each leaf needs is set by the SI unit it is read in, not by its domain. The gate stays at 87/91.

2026-10-02m (audit/FREEZE_2026-10-02m.md): an FSOT-only pion decay constant, F = m_p/(2√3π) = 86.22 MeV, from the quark-level sigma model with N_c = 3. It is within 0.55 % of the chiral-limit value. The π⁰ from the electromagnetic sum rule comes out at 134.40 MeV (−0.43 %) and the K⁰ via Q at +0.13 %. The η and η′ fail. D_eff/S does not organize the m_e-multiple ratios. The gate stays at 87/91.

2026-10-02n (audit/FREEZE_2026-10-02n.md): an FSOT-only physical F_π of 90.51 MeV (−1.7 %), from the NLO step with l̄₄ = N_c in the quark-level sigma model. A valence chiral-quark-soliton g_A of 1.178 (−7.7 %) misses its 2 % gate, so the Δα → Γ_Z/M_Z chain stays gated off. The leading-order deuteron radius misses by 23 % (no effective range). D_eff maps on one reference leaf per domain fail. The gate stays at 87/91. The physical meaning, units path and status of every quantity are in docs/PHYSICAL_MAP.md.

2026-10-02o (audit/FREEZE_2026-10-02o.md): a full-Dirac-sea chiral quark soliton (Kahana–Ripka basis, Pauli–Villars) at M = m_p/3 is unbound (E = 3.41 M). Its leading-order g_A^(0) = 0.742 misses by 42 % without the 1/N_c rotational term, and Δ−N = 177 MeV misses by 40 %, so the Δα → Γ_Z/M_Z chain stays gated off. A one-pion-exchange deuteron with FSOT g_πNN gives r_d −4.1 %, Q_d −14 % and η −7.3 %. SU(6) μ_n (−2.7 %) and μ_d (+3.8 %) fail, and so does l̄₄ = 1 + ln(M_Q²/M_π²) (F_π −2.3 %). The gate stays at 87/91.

## Benchmarks (8-vCPU x86-64, GCC 14 -O3 -march=native; Python 3.13 + mpmath, dps 50)
| Workload | Python mpmath | double | long double | __float128 | 169-bit |
|---|---|---|---|---|---|
| Engine init (constants + nest + cached S) | 6.66 ms | 2.4 µs | 5.8 µs | 38 µs | 343 µs |
| 35 domain scalars | 4.93 ms | 2.0 µs (2460×) | 24.8 µs (199×) | 261 µs (19×) | 1.97 ms (2.5×) |
| All 26 sections (368 rows) | 5.05 ms | 39.6 µs (128×) | 55.4 µs (91×) | 217 µs (23×) | 1.61 ms (3.1×) |
| One S evaluation | 108 µs | 37 ns (2900×) | 510 ns | 7.4 µs (15×) | 54 µs (2.0×) |

| Ternary: consensus similarity, 4096 × 256 trits | Time |
|---|---|
| FSOT-GPU `trinary.py` (pure Python) | 58.1 ms |
| C++ lane loop | 4.94 ms (12×) |
| C++ bit-packed, 32 trits/u64 + popcount | 29 µs (~2000×) |

Details are in [docs/BENCHMARKS.md](docs/BENCHMARKS.md). `__float128` is the practical sweet spot: 33 digits, and it reproduces Python's doubles exactly.

## Windows / MSVC caveat
MSVC has no `__float128`, and its `long double` is the same as `double`. On MSVC the CMake script builds the
`double` and 169-bit Boost types only (get Boost headers from vcpkg: `boost-multiprecision boost-math`).
Use the 169-bit type when you need values that match Python exactly. MinGW-w64 GCC does support `__float128`. Damian reproduced the MSVC build on MSVC 19.44 (2026-10-02). The portability fixes are listed in docs/AUDIT_LOG.md H-33, and CI job `build-test-msvc` (windows-latest, blocking since 2026-10-02j, H-35) builds it and checks that the precision report is byte-identical. Windows steps are in docs/REPRODUCE.md §1.

Full reproduction guide (WSL2 recommended on Windows, with expected outputs for every check): [docs/REPRODUCE.md](docs/REPRODUCE.md).
One-shot Linux/WSL2 check of all four CI jobs: `bash xval/cpp_check.sh`.

## Roadmap (from [docs/PORT_PLAN.md](docs/PORT_PLAN.md))
1. ~~Ledger B panel re-scorer~~ (milestone 1) · ~~Ledger A emit + property routing~~ (milestone 2)
2. ~~Closed-form sections in the freestanding core; `predict_closed_form` CLI; freezes; trit fixes T-1 to T-5~~ (milestone 3)
3. Trinary syntax rows, opcode registry loader, wire-format FSOTB loader — 1–2 days
4. Extend the codegen to the hub's pure-math modules (seed_flavor, gr_sm, matter_antimatter, uniqueness_confinement, ckm_pmns, complex_interaction) — 1–2 weeks
5. Numeric kernels (nse3d, path_sum, dynamics) — about 1 week
6. Data panels and gauntlet modules — 3–4 weeks
7. Python binding (pybind11) and a CUDA bridge for ternary attention; a C++ replay alongside the hub's multiprover — about 1 week

A survey of the engine and of every trinary implementation is in [docs/INVENTORY.md](docs/INVENTORY.md).

## Layout
| Path | What |
|---|---|
| `include/fsot/engine.hpp` | engine, templated on the number type |
| `include/fsot/closed_forms.gen.inc` | generated sections (do not edit) |
| `include/fsot/real.hpp` | number-type shim (double / long double / __float128 / Boost 169-bit) |
| `include/fsot/trit.hpp`, `fsotb_vm.hpp` | trinary core, FSOTB VM |
| `include/fsot/ternary.hpp`, `core.hpp` | balanced-ternary arithmetic, freestanding core |
| `include/fsot/host/` | Ledger A/B, routing, tiers, Python-semantics helpers (host only) |
| `include/fsot/closed_forms_core.gen.inc` | generated freestanding closed-form sections (do not edit) |
| `kernel/` | x86_64 bare-metal QEMU demo |
| `freezes/` | dated SHA-256 freezes (`fsot_freeze_domain`) |
| `audit/` | citation pass, look-elsewhere, precision (M3) and promotion-watch outputs |
| `tools/` | pinned fetch, codegen, golden export |
| `golden/golden_AEB2AD.tsv` | golden values |
| `tests/`, `bench/`, `apps/` | tests, benchmarks, report CLI |

## License and citation
Apache License 2.0. Copyright 2026 Damian Arthur Palumbo. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
Citation metadata is in [CITATION.cff](CITATION.cff).
