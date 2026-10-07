# xval: broader FSOT 2.1 cross-validation harness (Linux / WSL2)

This is a secondary harness. The main reproduction guide is [`../docs/REPRODUCE.md`](../docs/REPRODUCE.md).
`cpp_check.sh` runs the complete FSOT-2.1-Cpp check: the four CI jobs, end to end.
The rest of this folder re-runs the hub (FSOT-2.1-Lean) and the sibling repos.

It is local-only. It never pushes, comments, or opens PRs. It never edits `vendor/fsot_compute.py`, pins or
freeze files. It only checks their hashes.

**Layout:** copy this folder to `~/fsot-xval`, or set `XV=/path` (every script reads `XV`, default `$HOME/fsot-xval`):
```bash
cp -r xval ~/fsot-xval && cd ~/fsot-xval && ./setup_toolchains.sh && ./RUN_ALL.sh --skip-xproof
```
Clones (`hub/`, `siblings/`), toolchains, venvs, `runs/` and `data/FSOT_SMILES_Lab_Dataset.json` are created
locally. None of them are committed. The SMILES dataset is copied from the hub's own `vendor/smiles/` and
checked against `data/SHA256SUMS`.

## C++ repo check
```bash
bash xval/cpp_check.sh            # from the FSOT-2.1-Cpp root; work dir ~/fsot-cpp-work (hub sparse clone + venv)
```
On the reference box (Debian 13, GCC 14.2, CMake 3.31, Boost 1.83, Python 3.13, QEMU 10.0) a fresh run took
169 s and ended with `ALL CPP CHECKS PASSED`.

## Files

| Path | What |
|------|------|
| `RUN_ALL.sh` | Runs every runnable layer one at a time and prints a PASS/FAIL/SKIP table. Results go to `runs/<stamp>/summary.tsv` plus one log per layer (`runs/latest` points at the newest run). |
| `setup_toolchains.sh` | Idempotent install of every toolchain (apt + elan + opam + release tarballs). |
| `toolchains/env.sh` | Puts the tools on `PATH`. `RUN_ALL.sh` sources it for you. |
| `tools/build_idris2.sh`, `tools/build_rocq.sh` | One-time Idris2 0.8.0 bootstrap and opam Rocq 9.0.1 switch, called by `setup_toolchains.sh`. |
| `tools/guarded.sh` | Wraps each layer with `setsid` + `nice`. If `MemAvailable` drops below `MIN_AVAIL_MB` (default 4000), it kills the whole process tree, waits for RAM to recover (above 6000 MB), and retries up to 3 times. There is no systemd here, so this watchdog stands in for a cgroup memory cap. |
| `tools/summarize_xproof.py` | Turns the hub's `data/cross_proof_verification_report.json` into per-framework rows. |
| `cpp_check.sh` | FSOT-2.1-Cpp: build, ctest (16 tests), regen-diff, hub-Python Ledger A/B goldens, C++ Ledger B re-score + corrected/genuine-miss reports, PRECISION_M3 classification, freeze verify, kernel + QEMU serial compare. |
| `tools/run_neural_language_verify.py` | Runs FSOT-2.1-Neural `run_language_loop.py --verify-only` with the SMILES dataset path added in-process, so the repo is not edited. |
| `data/SHA256SUMS` | sha256 of the SMILES Lab dataset. `RUN_ALL.sh` copies it from the hub's `vendor/smiles/FSOT_SMILES_Lab_Dataset.json` (Apache-2.0) into `data/`. |
| `hub/`, `siblings/` | Scratch clones. Each run does fetch + `reset --hard origin/HEAD` + `clean` (it keeps `.lake`/build caches). Hub generators rewrite tracked files in `hub/` on every run. That is expected and never committed. |

```bash
./RUN_ALL.sh                    # full run (hub CI + Lean + multiprover + siblings + twins)
./RUN_ALL.sh --skip-xproof      # skip the ~26 min multiprover run
./RUN_ALL.sh --only hub|siblings
./RUN_ALL.sh --with-runner      # also run hub scripts/fsot_verification_runner.py (slow, live downloads)
./RUN_ALL.sh --fresh            # re-clone everything
```

## Layers that run here

### Hub: dappalumbo91/FSOT-2.1-Lean

| Layer | Command | Typical time (warm) |
|-------|---------|---------------------|
| Pin | sha256 of `vendor/fsot_compute.py` must start with **AEB2AD** (see `docs/PIN_LINEAGE.md`) | 0 s |
| CI `margin-and-toe` | `audit_all_benchmark_margins.py` (green gate: 477/477 panels), tier-scalar soft report, `build_toe_gap_closure.py` (Label A/B, T1–T6) | ~20 s |
| CI `scientific-catalog-smt` | `run_smt2_catalog.py` with z3 4.13.3, `export_cross_proof_obligations.py` | ~5 s |
| CI `publication-smoke` | domain navigator, contested observables, parameter-count audit | ~10 s |
| Lean 4 | `lake exe cache get`, then `lake build` of **all 567 `FSOT.*` modules** + `FSOT2_0_Compute`, plus a grep for `sorry`/`axiom`. The default target only reaches 11 modules, so every module is named explicitly. | cold ~6 min (84 s cache + 334 s build); warm ~10 s |
| Multiprover (`run_cross_proof_verification.py`) | Lean connective → Python decimal → **SMT bulk (z3)** → **TLA+ (TLC)** → **Rocq 9.0** (49 chunks + coqchk) → **Isabelle2025-2** session `FSOT_CrossProof` (46 chunks) → **Rust f64 replay** (2130 obligations) → Rust↔Lean bridge → **F\*** → **QEMU** serial + disk boot → `hardware_bare_metal` (Rust processor/RAM kernels + QEMU chain) + GR/SM/CKM spine (Python/Rust/z3/Coq) | ~26 min |
| `fsot_verification_runner.py` (optional, `--with-runner`) | Full ingest/verify pipeline. It streams public data live (NOAA GHCND by-year files, other public APIs), so its runtime depends on the network. | 30+ min |

### Siblings and twins

| Repo | Layers |
|------|--------|
| FSOT-Chua-Circuit | Pin D1D38A. `verification/run_cross_proof.py`: algebra/pin, host observer, Chua sweep, obligations, SMT python + z3, Lean (v4.33.1), Coq, Rust, TLC. Isabelle is checked separately with `isabelle process_theories`. |
| FSOT-Genetics | Pin D1D38A. `verify_cross.py`, `run_cross_proof.py` (python, SMT, z3, Lean+Mathlib, Coq, Isabelle, F\*, Rust, TLC), `system_verify.py` (259 checks), `cargo check`, Haskell layer, Zig host self-test. |
| FSOT-2.1-Neural | `scripts/ci_smoke.py` (CPU torch), `run_language_loop.py --verify-only` (with the SMILES dataset), standalone Lean `formal/`. |
| fsot-neuron-zig | `zig build -Doptimize=ReleaseFast` + `fsot_mind suite` |
| fsot-neuron-haskell | `cabal build` + `cabal test` + `fsot-mind selftest / parity / phase-a` |
| fsot-neuron-idris | `idris2 --build` + `fsot-mind scalpel / phase-a` |

## Skipped and why

| Layer | Reason |
|-------|--------|
| ESP32 hardware harness (eight-way) | Needs a physical ESP32 on a CP210x serial port. The hub runner already marks it optional and skips it. |
| FSOT-GPU / CUDA panels at runtime | Needs an NVIDIA GPU. The Lean priors for GPU/processor/RAM panels still build, and `hardware_bare_metal` uses recorded goldens. |
| FSOT-Qwen | Private LoRA/LLM training repo that needs a GPU. Its "cross-proof" rows (Coq 49/49, smt_catalog_bounds, tla_domain_routing, hardware_bare_metal) are copies of the hub's `cross_proof_verification_report.json`, which the hub multiprover layer re-checks here. |
| Windows-only scripts (`*.ps1`, `BOOT_*.cmd`, Windows TTS, `I:\`/`C:\` archive paths) | Not available on Linux. The Linux equivalents above are used instead. |
| Hub runner external corpora | Some ingest steps look for files on `I:\FSOT-Physical-Archive` / Desktop. The repo-bundled `vendor/` caches are used where present. |

## Toolchain notes

* Lean: elan, `leanprover/lean4:v4.31.0` (hub, Genetics, Neural). Chua pins `v4.33.1`, which elan fetches on demand.
* **Rocq 9.0.1** + rocq-stdlib + coq-interval come from an opam switch `rocq` (own OCaml 5.3.0) under `toolchains/opam`. The hub `.v` files use `From Stdlib`, which Debian's Coq 8.20 does not provide. A switch on the system OCaml failed because it picked up Debian OCaml libraries.
* Isabelle2025-2 (Linux bundle). The `HOL-Decision_Procs` heap is built once (~15 min at threads=2). `~/.isabelle/Isabelle2025-2/etc/settings` caps the ML heap at 3 GB.
* z3 4.13.3 (apt) is placed ahead of pip `z3-solver` on PATH. F\* 2026.07.05 also expects this version.
* cvc5 1.1.2, OpenJDK 21 + `tla2tools.jar` v1.8.0 (`toolchains/bin/tlc`), QEMU 10, GHC 9.6.6 / cabal 3.10, Zig 0.15.2, Idris2 0.8.0, Rust stable (`~/.cargo`).
* Python venvs: `venv` (hub requirements + scipy + z3-solver) and `venv-sib` (CPU torch for Neural).

## Last results (2026-10-02, ET, reference box: Debian 13, 8 cores, 16 GB, no GPU)

Full run `runs/20261002-000121` (hub 56fcbf31). The sibling re-run `runs/20261002-010811` was done after rebuilding Idris2.

* **Hub CI (3 jobs):** all PASS. Green gate 477/477, tier-scalar closed, Label A/B with T1–T6 6/6, z3 `sat`, navigator/contested/parameter audit OK.
* **Lean:** 567/567 modules + exe build. 0 errors, 0 `sorry`, 0 `axiom`.
* **Multiprover:** `overall_ok=True`, `seven_way_bare_metal=True`, `github_ready=True`. Coq 49/49, Isabelle 46/46, SMT 2205, Rust replay 2130, F\* / QEMU serial+disk / hardware_bare_metal / TLC all pass. ESP32 skipped. 1556 s.
* **Siblings + twins:** 23/23 PASS (3 min warm).
* **`fsot_verification_runner.py`:** FAIL. 32 summary items in 1370 s. Most come from missing Windows-only inputs (`C:/Users/damia/Desktop/...`, `D:\training data\cnc_data\Exp1.csv`, `vendor/neurolab/.../thalamic_gate_manifest.json`). Its final `lake build` then fails in 12 `*Priors.lean` files that the runner's own generators rewrote during the run. The committed versions of those files build cleanly. Treat it as not reproducible off Damian's machine, not as a proof failure.

Timing on the reference box: the full run with the runner took about 56 min, about 33 min without the runner (`--skip-xproof` brings it to about 7 min). One-time setup: apt ~3 min, Mathlib cache ~1.5 min per project, Isabelle heap ~15 min, Rocq opam ~13 min, Idris2 bootstrap ~10 min.

### Observations (neutral)

1. FSOT-Chua-Circuit: the optional Isabelle layer called `isabelle process -T`, which Isabelle2025-2 removed. **Fixed in `cecef94`**: it now tries `process_theories` first. 11/11 layers pass.
2. FSOT-Genetics: `scripts/system_verify.py` needs `scipy`, which was missing from `requirements.txt`. **Fixed in `f677663`**: 259/0 in a fresh venv.
3. fsot-neuron-zig: the README listed modes that were never implemented (`logic-probe`, `verify-stamp`, `mind-smoke`, …). **README corrected in `68e43ce`**. `suite` gives 67 PASS markers.
4. FSOT-2.1-Neural `fsot_nuron/chemical_codon.py` looks for the SMILES dataset only at two Windows paths, with no env override. `tools/run_neural_language_verify.py` injects the public hub copy in-process. The repo is not edited.
5. Inside the runner, the regenerated `Living_FSOT_Hardware` panel scores pooled 100% on the reference box (host-hardware audit). The regenerated `Math_Generator_Benchmark_Formula_Eval` scores 1.0049%. Both come from data rewritten by the runner. The committed data passes 477/477.

## Last results (2026-10-07, FSOTHUB)

C++ `main` `f9adc19`. Windows MSVC ctest 87/87. WSL `xval/cpp_check.sh` printed `ALL CPP CHECKS PASSED` in 404 s: ctest 88/88, including `neutral_mesons_pass`, goldens byte-identical, precision gate 91/91 at z ≤ 1 and 89/91 at the flat 2% check, QEMU serial byte-identical to `docs/bare_metal_serial_AEB2AD.txt`. Pin AEB2AD. The 88th Linux test is `freestanding_symbols`, which is GCC/Clang only.

Hub gauntlet `scripts/run_cross_proof_verification.py` on Lean `main` `b866a50` (the Rust-bridge link retry). The process exited 0 in 707 s. It printed `overall_ok: True`, `seven_way_bare_metal: True`, and `github_ready: True`.

| Layer | Result |
|---|---|
| Python decimal | PASS |
| Scientific catalog | 477 domains, 1908/1908 PASS |
| Lean connective | PASS |
| Coq / Rocq | 49/49 chunks passed |
| Lean ↔ Coq | PASS, 2030 lemmas indexed, 0 margin violations |
| Isabelle `FSOT_CrossProof` | 46/46 chunks passed |
| Lean ↔ Isabelle | PASS, 2030 lemmas indexed |
| F* | passed |
| Rust f64 replay | 2130 obligations passed |
| SMT (Z3) and TLA+ | passed |
| GR/SM/CKM | Python 288/288, Rust cargo passed, Z3 passed, Coq passed |
| QEMU | serial passed, disk passed |
| Rust↔Lean bridge | passed, boot scalar 0.09928895626861721 |
| Seven-way bare metal | True |
| ESP32 | skipped, no CP210x port, so eight-way is False |

The four neutral masses are locked by C++ `neutral_mesons_pass` (K⁰ z 0.0154, π⁰ z −0.00257, η z 0.394, η′ z 0.205). They are host evaluations on pin AEB2AD. They are not obligations of the Lean gauntlet, and they are not new rows on the 91.
