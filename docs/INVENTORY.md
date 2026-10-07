# Inventory — FSOT 2.1 engine and trinary implementations (survey 2026-10-01)

## 1. Authority: `FSOT-2.1-Lean/vendor/fsot_compute.py`
- SHA-256 `AEB2ADAD…AAC170` = live pin **AEB2AD** (`vendor/fsot_compute_AUTHORITY_PIN.json`, `docs/PIN_LINEAGE.md`).
  Freeze pin D1D38A remains for Paper 03 / Ledger-A freeze files (not touched).
- 1300 lines, pure Python + **mpmath, `mp.dps = 50` (prec 169 bits)**. No I/O. Docstring/report banner still says "FSOT 2.0".
- Structure:
  | § | Content | C++ status |
  |---|---|---|
  | 1 | Seeds π, e, φ, γ (50-digit literal), Catalan G (50-digit literal) | ported |
  | 2 | Layer 1: ALPHA = ln π/(e φ¹³), PSI_CON, ETA_EFF, BETA, GAMMA_C, OMEGA, THETA_S, POOF | ported |
  | 3 | Layer 2: C_EFF (π⁻⁴), A_BLEED, P_VAR, B_IN, A_IN, SUCTION, CHAOS, P_BASE, P_NEW, C_FACTOR, K (1−π⁻⁴), C_COSM (1/(φπ²)) | ported |
  | 4 | `ScalarInput` (24 fields) + `compute_scalar`: S = K(T1+T2+T3) | ported |
  | 5 | Nest: 20 generations / 35 orifices, `derived_D_eff` = round(5·5^{g/19}), `_fold_look` (Atomic e/π, HEP 1−POOF/π), `_fold_hits` (HEP 1), `MEDIUM_ORIFICES` (12 unobserved), `_fold_C` (interpretation, not in S), `scalar_from_fold`, `domain_scalar`, cached S_COSM/S_QUANT/S_CHEM | ported |
  | 6–25 | Closed-form sections: wave1–wave10, validation_suite (28), lepton_ratios, dynamical_systems, neural_architecture, consciousness_model, homeostasis, soliton_stdp, cross_species, trinary (Max_Trits 27, Collapse_Threshold C_EFF·P_VAR), predictions | ported (generated) |
  | 26 | chemistry_ionization/electronegativity/bond_lengths/bond_energies/molecular/radii | ported (generated) |
  | — | full_report / CLI | `fsot_report` app |
- Totals: 26 sections, **368 closed-form rows, 343 with targets, 342 within 5 %** (C++ reproduces the same counts).
- Ledger B correction (outside the file, `scripts/fsot_api_predict_lib.py`): c = m(1+|S|·f), **f = ALPHA** for every domain (commit ba6a8288). Ported as `Engine::fsot_correct`.

### Other hub vendor modules (consumers of the authority)
| Module | Lines | Kind | Port tier |
|---|---|---|---|
| fsot_ckm_pmns.py | 28 | seed closed forms | 1 |
| fsot_path_sum.py | 189 | numeric | 2 |
| fsot_nse3d.py | 262 | numeric (3-D NSE; where C++ speed matters) | 2 |
| fsot_uniqueness_confinement.py | 417 | seed closed forms | 2 |
| fsot_matter_antimatter.py | 464 | seed closed forms (mpmath) | 2 |
| fsot_dynamics.py | 669 | dynamics (mpmath) | 2 |
| fsot_complex_interaction.py | 671 | seed closed forms (mpmath) | 2 |
| fsot_gr_sm.py | 992 | GR/SM derivations (mpmath) | 2 |
| fsot_seed_flavor.py | 1610 | 97 seed-closed flavor/EW functions | 2 |
| fsot_quantum_trinary_syntax.py | 412 | quantum depth rows + trinary string syntax (opcode registry JSON) | 1 |
| fsot_cepheid_pl.py, fsot_earth_fluid_forecast.py, fsot_reality_fiction_calibration.py | 734/900/612 | data panels | 3 |
| fsot_scale_interconnects.py | 5194 | 113 defs, JSON-heavy | 3 |
| fsot_millennium_accuracy.py / _track.py | 4990/191 | gauntlet, JSON-heavy | 3 |
| fsot_reality_os.py | 837 | status/atlas (sqlite) — keep Python | — |

### "Everything solved so far" as the hub defines it (README lock 2026-09-29, CURRENT_STATUS 2026-09-17)

The bullets under this heading are that 2026-09-29 survey, kept as the survey recorded them. The 2026-10-07 standing of this C++ tree is the current-standing section of the repository README: which comparisons lie inside a published standard uncertainty, which remain outside, and what the 2026-10-07 cross-proof gauntlet printed. The median-of-medians figure below is the survey figure. The z ≤ 1 score is the precision gate.
- **Engine**: 35-orifice nest, 5 seeds, zero free parameters (FORMULA_AUTHORITY_SYSTEM_CLOSED).
- **Ledger A** (predict, no measured input): closed forms via `scripts/fsot_ledger_a_lib.py` over the sections above; misses tracked in `results/MISSES.md`.
- **Ledger B** (correct): **477/477** green benchmark files (480 `data/*benchmark*.json` on disk), median-of-medians 0.005537779313588844 % over 414 prediction medians, 183,196 scalar records.
- **Ledger C / formal**: 5248/5248 Mathlib theorems; 2030 atomic obligations (2594 full) across Lean/Coq/Isabelle/F*/Rust, overall_ok; uniqueness spine 153/153 in 6 provers.
- **Gauntlet** (`results/GAUNTLET_STAMP.md`, AEB2AD): millenium_track, millenium_accuracy (comparable 70, beats 73, green 67), path_sum, market_process, sickness_two_system, process_time_smoke, weather_24h_retro — all PASS.

## 2. Trinary / ternary implementations
| Repo / file | Lang | Data type | What it does | FSOT mapping |
|---|---|---|---|---|
| FSOT-Genetics `zig/src/trit.zig` (byte-identical to fsot-neuron-zig `src/trit.zig`) | Zig | `Trit=i8` {−1,0,+1}; **T1 packing** 00=0, 01=+1, 11=−1; `TritWord` 32 trits/u64 | neg, pair (product), sumSat, consensus, fromS(lo,hi), base/codon primary, pairWords, selfTest | S → trit by thresholds; DNA A,G=+1 C,T=−1 |
| FSOT-Genetics `crates/codon_core` | Rust | `Trit=i8`; codon = primary+secondary axes; **base-3 pack** (trit+1) into u16 0..728 | nt_primary (U=−1), nt_secondary (A=+1,T/U=−1,G/C=0), encode/pack_codon | genetic code as 3³ space |
| FSOT-Genetics `scripts/trinary_syntax.py` | Python | amino-acid opcodes from trits | aromatic/branch/hetero trits, pair weights | protein syntax |
| FSOT-GPU `fsot_lib/trinary.py` (identical in FSOT-Quantum) + `trinary_torch.py` + CUDA `trinary_pack_main.cu` | Python/torch/CUDA | **code** {0=SpinDown,1=Superposed,2=SpinUp}, 2 bits/code, 32/u64 | collapse at ±C_EFF·P_VAR, trit_similarity (ternary consensus attention), pack/unpack | collapse threshold = authority `trinary()` row |
| FSOT-Quantum `zig/src/quantum.zig`, Lean `Trinary.lean`, `TrinaryQuantum.lean` | Zig/Lean | signed + code {0,1,2} | collapseCode, H-analog, CX-analog, Bell analog; Lean proves code round-trips | ternary spins |
| FSOT-Reality-OS `reality_os_trinary` (+ `reality_os_scalar`) | Rust no_std | i32 registers ×25, 27 opcodes, 27-trit word ABI | FSOTB/Metatron ISA VM, EVAL_PANEL = compute_s on a domain table, sign_trit (eps 1e-12) | 25 regs = D_eff ceiling, 27 ops = 3³ |
| Hub `vendor/fsot_quantum_trinary_syntax.py`, `vendor/trinary_os/isa/fsotb_opcode_registry.json` | Python/JSON | trit from sign(S) | "reality string" encoding of domains, opcode registry | same S |
| FSOT-2.1-Neural `fsot_bridge.py` | Python/torch | trit from S thresholds | gain 1+0.25·trit for features | neuron path |

**Shared core** (now `include/fsot/trit.hpp`): signed trit algebra, wire code ↔ signed, collapse, both packings,
consensus similarity, quantum analogs, codon encodings, FSOTB VM core (`fsotb_vm.hpp`).
**Domain-specific** (left for later): amino-acid opcode tables, torch/CUDA kernels, Neural feature gains.

### Things worth knowing (observed, nothing edited)
1. **Two 2-bit wire formats** for one trit: T1 (Zig: +1→01, −1→11, 0→00) vs code (GPU/Quantum/CUDA/codon pack: −1→00, 0→01, +1→10). Both supported in C++; not interchangeable on the wire.
2. **U (uracil)**: codon_core (Rust) maps U→−1; trit.zig maps U→0. C++ provides both (`nt_primary`, `base_primary`).
3. **Constants older than AEB2AD** in compiled code: FSOT-GPU/FSOT-Quantum `seeds.py`, `quantum.zig`, Reality-OS `reality_os_scalar` carry C_EFF 0.9577022026205613 and K 0.4202216641606967 (0.01/0.99 era) and collapse threshold 0.9174663774653723; live AEB2AD values are C_EFF 0.9577480213378242, K 0.4201087636498879, threshold **0.9175102712064876**. Reality-OS `AUTHORITY_PIN = "D1D38A"` and its 530-row domain table use the assigned D_eff/look/hits, not the nest. The C++ port takes these from the engine, so one regenerate keeps every layer on the pin.
4. The 10 panels FSOT-2.0-code bundles also exist in hub `data/` with the same stored pooled medians (generated July, before the f=ALPHA rebuild).
