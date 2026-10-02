# FSOT canonical trit wire format and codon mapping (proposal v1, 2026-10-01)

Status: **proposal**. This repo implements it. No other repo has been changed. Section 4 lists the
fixes each repo would need. They are up to the owner.

## 1. The trit
A trit is a balanced-ternary digit `t ∈ {−1, 0, +1}`. Arithmetic is balanced ternary: the value of
`t_{n−1} … t_1 t_0` is `Σ t_i·3^i`. Negation flips every trit. Rounding to fewer trits is truncation,
and truncation is round-to-nearest. Comparison is lexicographic from the most significant trit.
Semantic names (when a trit carries an FSOT state): `−1` = damp / SpinDown, `0` = null / Superposed,
`+1` = emerge / SpinUp. This matches the hub's `trit_from_S` and Reality-OS `sign_trit` (ε = 1e−12).

## 2. Canonical wire formats
There are two, one for storage and one for compute. Both are defined exactly here, and conversion
between them is lossless.

### 2a. Storage / interchange: **code = t + 1**, 2 bits per trit, little-endian lanes
| trit | code | bits |
|---|---|---|
| −1 | 0 | `00` |
| 0 | 1 | `01` |
| +1 | 2 | `10` |
| invalid | 3 | `11` (must be rejected on decode) |

- Trit `i` of a word occupies bits `2i+1 : 2i`. A `u64` carries 32 trits. Lane 0 holds the least significant trit.
- Rationale: this is already the format of FSOT-GPU / FSOT-Quantum `fsot_lib/trinary.py`
  (`pack_u64`, codes 0=SpinDown, 1=Superposed, 2=SpinUp), their CUDA kernels, the Lean/F*/Coq/Isabelle
  statements that use the 0/1/2 coding, and the positional codon pack in FSOT-Genetics `codon_core`
  (`trit + 1`, 0..728). Of the formats in use, it needs the fewest changes.
- Byte form (optional, for text-like streams): 5 trits per byte as the base-3 number `Σ code_i·3^i`
  (0..242). It packs denser than 2 bits per trit (8/5 = 1.6 bits per trit vs 2) and is used only for archives.

### 2b. Compute: **two bit-planes** (`P` = positions holding +1, `N` = positions holding −1)
- Trit `i` is `+1` iff bit `i` of `P` is set, `−1` iff bit `i` of `N` is set, and `0` otherwise. `P & N` must be 0.
- 64 trits per plane pair. All ternary logic is trit-parallel. Negation swaps `P` and `N`. The ternary
  full adder is a few AND/OR operations followed by a carry-propagation loop
  (`include/fsot/ternary.hpp::add_into`).
- Conversion to and from 2a is a fixed bit-deinterleave: `P = pext(w, 0xAAAA…)`, `N` = lanes whose code is 0.

### 2c. Legacy format (decode-only): Zig **T1** (`00`=0, `01`=+1, `11`=−1, `10` invalid)
Used by FSOT-Genetics `zig/src/trit.zig` (lines 49–50: `t1_pos = 0b01`, `t1_neg = 0b11`) and the same file
in fsot-neuron-zig. It is a sign/magnitude layout (bit0 = non-zero, bit1 = sign), which makes some
bit-sliced operations cheap (`pair_words_fast`, `neg_word` in `include/fsot/trit.hpp`). It is **not** the
canonical interchange format, because the same bit pattern means different trits in 2a and in T1:
`01` is 0 in 2a and +1 in T1. Readers must know which format they hold.

## 3. Canonical nucleotide → trit mapping
| base | primary trit (purine/pyrimidine axis) | secondary trit (A–T(U) axis) |
|---|---|---|
| A | +1 | +1 |
| G | +1 | 0 |
| C | −1 | 0 |
| T | −1 | −1 |
| **U** | **−1** | **−1** |
| N or anything else | 0 | 0 |

- **U is a pyrimidine and maps exactly like T.** This follows FSOT-Genetics `crates/codon_core/src/lib.rs`
  lines 40 and 50 (Rust). It is the biochemically consistent choice: in RNA, U takes T's place.
- Codon pack (canonical): `primary = Σ_{k=0..2} (p_k+1)·3^k`, `secondary = Σ (s_k+1)·3^k`,
  `code = primary + 27·secondary` (0..728). Identical to `codon_core` and to `fsot::trit::pack_codon`.
- Case-insensitive. The position order is 5′→3′ = k = 0, 1, 2.

## 4. Mismatches found (evidence) and fixes
Original findings (left as written) and the proposed fixes. Status after Milestone 3 (2026-10-02) is in §4a.
| # | Where (repo @ commit, file:line) | What | Proposed fix |
|---|---|---|---|
| T-1 | FSOT-Genetics @ 8b4f80d `zig/src/trit.zig:37-39`; same file in fsot-neuron-zig @ 2a949f8 | `'U'` falls into `else => 0`, so RNA codons get a 0 (null) trit where `codon_core` (Rust) gives −1. The same RNA sequence therefore produces different primary trits in Zig and in Rust. | Add `'U','u'` to the −1 arm (one-line change). Add a cross-language test vector: `"AUG"` → primary `(+1,−1,+1)`. |
| T-2 | FSOT-Genetics/fsot-neuron-zig `trit.zig:49-50` vs FSOT-GPU @ 8b2c06e / FSOT-Quantum @ f308a6f `fsot_lib/trinary.py:50-57` | Two incompatible 2-bit layouts (T1 sign/magnitude vs code = t+1). | Keep T1 as an in-memory compute layout if wanted, but label it. Add `toCanonical/fromCanonical` (2a) at every file/wire boundary. Add a version tag to any stored trit blob, e.g. a 1-byte header `0xF1` = canonical v1. |
| T-3 | FSOT-GPU `fsot_lib/seeds.py:25,33`; FSOT-GPU & FSOT-Quantum `phase2_native_gpu/python/fsot_gpu_engine.py:51,54`; CUDA `fsot_attn_lib.cu:17`, `fsot_beat_cuda.cu:24`, `fsot_consensus_sparse.cu:11`; FSOT-Quantum `zig/src/quantum.zig:10` | Pre-π-identity constants: C_EFF = 0.9577022026205613, K = 0.42022166416069665, collapse threshold Θ = C_EFF·P_VAR = 0.9174663774653723. The live authority AEB2AD gives C_EFF = 0.9577480213378242, K = 0.4201087636498879, Θ = 0.9175102712064876. The old values are exactly what `0.01` in place of `π⁻⁴` produces (see A-04 in AUDIT_LOG). | Generate these constants from the pinned authority (as this repo does with `tools/gen_closed_forms.py`) instead of typing them in. Re-pin to AEB2AD. Θ moves by +4.39e−5, which can flip codes for inputs within 4.4e−5 of ±Θ. Re-run their verification reports afterwards. |
| T-4 | FSOT-Reality-OS @ 48b8515 `README.md:8`, `reality_os/core.py:34,43`, `engine/fsot_compute.py:62` | Pin D1D38A, an older authority copy (C_EFF uses `mpf("0.01")`), and the stale domain table. | Re-vendor `fsot_compute.py` at AEB2AD and regenerate the domain table. The QEMU serial log (`data/reality_os_qemu_serial.log:13`, `collapse_theta = 0.917466377465`) will change in the 5th decimal. |
| T-5 | FSOT-Reality-OS VM, `include/fsot/fsotb_vm.hpp` here | VM registers hold binary integers labelled as trits. The VM does not do balanced-ternary arithmetic. | Optional: back the 27-trit registers with `fsot::bt::Word27` (exact balanced-ternary add/sub/mul/div with wrap flag). This repo provides the type; the VM port can switch once the opcode semantics for overflow are decided. |

## 4a. Status (Milestone 3, 2026-10-02). One direct push per repo to its default branch; no PRs, issues or comments. Pins and pinned authority files unchanged.
| # | Repo @ pushed commit | Applied | Not applied / why | Checks (before and after) |
|---|---|---|---|---|
| T-1 | FSOT-Genetics @ `2cd14ad`; fsot-neuron-zig @ `076a01e` | `trit.zig`: `'U','u'` → −1; `selfTest` vector AUG → (+1,−1,+1). Genetics `codon_core` gained the test `rna_u_matches_t_cross_language_vector` (AUG = ATG, `pack_codon` = 317). | — | Genetics: `verify_cross.py`, `cargo test -p codon_core` (6 → 7 pass), `zig build host`/`kernel`, `zig test src/trit.zig`. neuron-zig: `zig build host` (FSOT_TRIT PASS), `zig build`, `zig build kernel`. |
| T-2 | FSOT-Genetics `2cd14ad`, fsot-neuron-zig `076a01e` (Zig); FSOT-GPU `16e618b`, FSOT-Quantum `3c4375a` (`fsot_lib/trinary.py`) | T1 kept unchanged and labelled "legacy in-memory layout"; `toCanonical`/`fromCanonical`, `t1WordToCanonical`/`canonicalWordToT1`, tag `0xF1`. Python: canonical labelling, `unpack_u64_checked`, `t1_word_to_canonical`/`canonical_word_to_t1`, `CANONICAL_V1_TAG`. | — | GPU `tests/test_trit_layout_and_seeds.py` 4 pass; Quantum `tests/test_trit_layout.py` 3 pass. |
| T-3 | FSOT-GPU `16e618b` | `tools/gen_seeds_from_authority.py` (verifies the AEB2AD sha, rewrites the sites; `--check`); `fsot_lib/seeds.py`, `fsot_gpu_engine.py`, three CUDA `COLLAPSE_THRESHOLD` (0.9175102712064875 = the f64 product C_EFF·P_VAR; the mp value is …876), parity twins and `parity/golden.json` regenerated. | `results/`, `config/fsot_seeds.json`, F* boot literals and `industry_lm` corpus texts kept as history. No CUDA toolchain on the box: CUDA edit is literal-only, not compiled. | `run_parity.py` python/rust/formal OK. |
| T-3 | FSOT-Quantum `3c4375a` | README section only. | `fsot_quantum.verify` checks Θ and QM/QC scalars against its vendored D1D38A engine; changing them breaks its gate unless the pin changes (pins are not changed). Also documented: `authority_pin` reports 46F53B on Linux because of LF line endings (CRLF form hashes to D1D38A). | `verify`/`parity` identical before and after (only `authority_pin` fails, LF reason). `zig build run` PASS. |
| T-4 | FSOT-Reality-OS `6d3db14` | README "Historical pin and VM word format": D1D38A documented as a historical pin with its constants. | Re-vendoring at AEB2AD not done (pin unchanged by instruction). | pytest 6 pass. |
| T-5 | FSOT-Reality-OS `6d3db14` | Documented: `kernel/crates/reality_os_trinary/src/lib.rs` `Vm::regs: [i32;25]` with `wrapping_add/sub/mul`, `COLLAPSE` → `sign_trit`; points to `fsot::bt::Word27` in `include/fsot/ternary.hpp`. VM not rewritten. | — | as above |

Also outside T-1..T-5 and left unchanged: fsot-rna-codon-lab (old constants in a Kaggle script/notebook), fsot-neuron-zig `seeds.zig`/`seeds_fixed.zig` (old constants labelled "pin lineage D1D38A"), FSOT-Genetics Zig K (D1D38A parity values; repo pinned D1D38A).

## 5. Conformance vectors (checked by `tests/test_trit.cpp` / `tests/test_ternary.cpp`)
- 32 trits `(−1, 0, +1, 0, 0, …, 0)` packed per 2a: lane codes `0,1,2,1,1,…,1` → `0x5555555555555564`.
- 40-trit word: `from_int(2400000000) * from_int(−2399999999) = −5759999997600000000` exactly. Random 200,000-pair
  checks against int64 arithmetic, an exhaustive 5-trit table (59,049 pairs, all ops), and a 9-trit (tryte) table.
- Codon `AUG` → primary `(+1,−1,+1)`, secondary `(+1,−1,0)`, pack = `(2+0·3+2·9) + 27·(2+0·3+1·9)` = 20 + 27·11 = 317.
