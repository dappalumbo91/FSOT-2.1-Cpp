# Reproduce FSOT-2.1-Cpp on a Windows PC: copy-paste prompt for a local coding agent

Everything below the line is one prompt. Paste it into Grok Build (or any local agent) on the Windows PC.
Every expected number comes from this repo's docs and goldens. Each one was re-checked on 2026-10-02
(ET) on a Debian 13 box with GCC 14.2.0, CMake 3.31.6, Boost 1.83, nlohmann_json 3.11.3, Python 3.13.5,
mpmath 1.4.1 and QEMU 10.0.13. `bash xval/cpp_check.sh` ran all of it from a fresh copy in 169 s.

---

## Prompt

You are reproducing **FSOT-2.1-Cpp** (https://github.com/dappalumbo91/FSOT-2.1-Cpp) on my Windows PC.
The C++ port of the FSOT 2.1 engine must match the pinned Python authority bit for bit. Build it, run every
check below, compare each result with the expected value, and give me a pass/fail table. Then work on the
"button-up" list at the end, within the hard rules.

### Hard rules (do not break these, even if a check fails)
1. Do **not** edit, regenerate-and-commit, or "fix" any of these:
   - `AUTHORITY_PIN.json`, or any pin (AEB2AD, D1D38A);
   - the hub's `vendor/fsot_compute.py`, or `authority/fsot_compute.py` (this one is fetched and sha-checked);
   - anything in `golden/` or `freezes/`;
   - `audit/precision_m3_genuine_misses.tsv` or `docs/bare_metal_serial_AEB2AD.txt`;
   - any frozen value, or any `*.gen.inc` file by hand.
2. Do **not** tune constants, exponents, tolerances or gate limits to make a check pass. A mismatch is a
   finding. Report it with the exact output.
3. Do not push, open PRs or issues, or comment on GitHub unless I explicitly ask. Work in a local branch.
4. Use only free tools and public data. Do not invent data or numbers. If an input is missing, say which one
   and where it is expected.
5. Run heavy jobs one at a time. Keep at least 4 GB RAM free.

### 0. What is pinned
| Item | Value |
|---|---|
| Repo | `https://github.com/dappalumbo91/FSOT-2.1-Cpp` (branch `main`; the checks below were verified at `56bac54` and at the commit that added this file) |
| Python authority | hub `dappalumbo91/FSOT-2.1-Lean` @ `d127c07e518ae349f500d68d9e32b6236349c8f9`, `vendor/fsot_compute.py` sha256 `AEB2ADAD6E80F487772C5DF90A2E3DDA71624AB831A6A83B94AB471AC9AAC170` |
| Ledger A/B data | hub @ `6f9c25605a52acabe662a42fc003afa5bf66b959` (`ledger_b_data_commit` in `AUTHORITY_PIN.json`) |
| Core domain table | `domain_table_sha256` = `8e30e85e72091462c4d66df2d498afb36ccbc2d40eb5df01b4e083947c79dad3` |
| Dated freeze | `freezes/domain_freeze_2026-10-02_AEB2AD.json`, 796 rows, selection_sha256 `580eb6e72ca75e2995b4331828b7a9f513978ce5c5aa3d7a798c2b83de4182dd` |

### 1. Toolchain (all free). Use WSL2 for the byte-identical checks
Recommended: **WSL2 + Ubuntu 24.04** for everything. All four CI jobs run on Linux. Three things only
work there:
- QEMU bare-metal boot of an ELF kernel built with the host `g++`/`ld`;
- byte-identical diffs of Python-written goldens. On native Windows, Python `Path.write_text` writes CRLF,
  so `git diff` / `diff -q` fail on line endings alone;
- the `sh -c` CTest commands.

Setup (PowerShell as admin, once): `wsl --install -d Ubuntu-24.04`. Then inside Ubuntu:
```bash
sudo apt-get update && sudo apt-get install -y git build-essential cmake ninja-build libboost-dev \
  nlohmann-json3-dev python3 python3-venv qemu-system-x86 binutils
g++ --version; cmake --version; qemu-system-x86_64 --version; python3 --version
```
Clone inside the WSL filesystem (`~/`), not under `/mnt/c`, because `/mnt/c` is slow and changes line
endings:
```bash
git clone -c core.autocrlf=false https://github.com/dappalumbo91/FSOT-2.1-Cpp ~/FSOT-2.1-Cpp
cd ~/FSOT-2.1-Cpp && git log -1 --format='%h %ci'
```
Requirements: CMake ≥ 3.20 (`cmake_minimum_required`), C++20, Boost ≥ 1.75 headers (`find_package(Boost 1.75)`),
nlohmann_json ≥ 3.2. Reference versions: GCC 14.2.0 / CMake 3.31.6 / Boost 1.83 (README says CMake 4.4 also
verified). Ubuntu 24.04 ships GCC 13, CMake 3.28, Boost 1.83 and Python 3.12. Those satisfy the minimums, but
report the versions you used.

Optional native Windows builds, as an extra data point only:
- **MinGW-w64 (MSYS2 UCRT64, free):** `pacman -S mingw-w64-ucrt-x86_64-{gcc,cmake,ninja,boost,nlohmann-json,python}`.
  GCC there supports `__float128`, so all four precision types are tested. MSYS2 provides `sh` and `nm` for the
  two shell-based tests.
- **MSVC (VS 2022 Build Tools, free) + vcpkg: native Windows, supported since 2026-10-02i.** Damian reproduced the build on
  MSVC 19.44, and CI runs it as job `build-test-msvc` on `windows-latest` (blocking since
  its first green run, CI 37075909187; AUDIT_LOG H-35). The portability changes:
  - `test_ternary` uses `_mul128`/`_umul128` when `__int128` is absent.
  - `test_golden` skips the 80-bit `long double` bar when `LDBL_MANT_DIG <= DBL_MANT_DIG`.
  - `_USE_MATH_DEFINES` is set for `M_PI`.
  - `fsot_freeze_domain` uses `localtime_s`/`gmtime_s`.
  - CMake passes `/utf-8` for MSVC. Formula text and names (`BP_H₂O`, middle dot, Greek) are UTF-8 in the sources. Without that flag MSVC uses code page 1252: goldens fail on the names, and `nlohmann::json::dump` throws `type_error.316` (byte `0xB7`) so `fsot_freeze_domain` exits `0xC0000409` before it prints the core-table hash.
  - The precision report does its gate arithmetic in mp169 and prints IEEE doubles (no `%Lg`). It is written in binary mode (LF), so it is byte-identical to the Linux golden.

  The Linux paths (`__int128`, 80-bit `long double`, `M_PI`) are unchanged. Steps (Developer PowerShell for VS 2022):
  ```powershell
  git clone -c core.autocrlf=false https://github.com/dappalumbo91/FSOT-2.1-Cpp; cd FSOT-2.1-Cpp
  git clone https://github.com/microsoft/vcpkg $HOME\vcpkg; & $HOME\vcpkg\bootstrap-vcpkg.bat
  & $HOME\vcpkg\vcpkg.exe install boost-multiprecision boost-math nlohmann-json --triplet x64-windows
  cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE="$HOME\vcpkg\scripts\buildsystems\vcpkg.cmake" -DVCPKG_TARGET_TRIPLET=x64-windows
  cmake --build build --config Release
  ctest --test-dir build -C Release --output-on-failure
  ```
  MSVC has no `__float128`, and `long double == double`, so `test_golden` checks `double` and mp169 only. `freestanding_symbols` is
  not registered (GNU/Clang only). `freeze_core_sha_matches_hub_freeze` needs `sh` on PATH (Git for Windows ships one). Python 3 must
  be on PATH for the freeze/reference tests. `.gitattributes` forces LF on checkout.
  **Expected CTest counts** with `-DFSOT_HUB_DATA`: **50 on Linux** and **49 on MSVC** (the difference is `freestanding_symbols`). Without hub data the counts are 27 and 26, the CI `build-test` configuration. Before rounds h–n added `round_freeze_h` … `round_freeze_z`, the counts were 29 and 28.
- Native Windows: clone with `-c core.autocrlf=false`. Run the Python byte-identical diffs (step 3) in WSL2 only.

**Current precision gate** (`audit/precision_2026-10-02.md`): **87/91 confirmed** at z ≤ 1, including the owner decisions OD-1/OD-2 (audit/OWNER_DECISIONS_2026-10-02i.md). Without them (pinned rows only) it is 85/91; with the frozen-pending refinements it is 88/91.

### 2. Fastest path: one script
From the repo root in WSL2:
```bash
bash xval/cpp_check.sh                     # work dir defaults to ~/fsot-cpp-work (hub sparse clone + venv)
```
It mirrors `.github/workflows/ci.yml` (jobs `build-test`, `regen-diff`, `ledger-b`, `bare-metal`). It stops at
the first mismatch and must end with `ALL CPP CHECKS PASSED`. The reference run took 169 s (≈120 s of that was
the build at `-j3`). The sections below give each command and its expected output, so you can run them one by
one and report each.

### 3. Checks, commands and expected output

**3.1 Build + CTest (CI `build-test`, plus the `ledger_b` tests when hub data is given)**
```bash
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DFSOT_HUB_DATA=$HOME/fsot-cpp-work/hub
cmake --build build -j3
ctest --test-dir build --output-on-failure
```
Expected (2026-10-02z): `100% tests passed` with **50 tests** when `-DFSOT_HUB_DATA` is given, or **27** without it (Linux; 49 / 26 on MSVC). The original 16 are listed below. Since then the precision-gate, reference and freeze-verification tests (`seed_leaves`, `precision_report*`, `references_check`, `refinement_freeze*`, `refinements_b_crosscheck`, `derivations_freeze_e/f/g`, `round_freeze_h/i/j/k/l/m/n/o/p/q/r/s/s2/t/u/u2/v/w/x/y/z`) were added. The original 16 are:
- `golden`, `trit`, `ternary`, `core_vs_engine`, `core_closed_forms_vs_golden`, `predict_closed_form_smoke`;
- `ledger_a_routing`, `look_elsewhere_smoke`, `freestanding_symbols`;
- `freeze_core_sha_matches_hub_freeze`, `freeze_verify_domain_freeze_2026-10-02_AEB2AD`,
  `freeze_verify_py_domain_freeze_2026-10-02_AEB2AD`;
- `ledger_b`, `evidence_tiers_report`, `ledger_b_corrected_report`, `ledger_b_genuine_misses`.

Without `-DFSOT_HUB_DATA` the last four are not registered. Boost's `cpp_int.hpp` prints
`-Wstringop-overread` warnings with GCC 14. They are harmless and the build still succeeds.

**3.2 Parity vs the pinned Python engine (bit-for-bit S values): `./build/test_golden`**
Expected lines:
```
double               checked= 643 failed=0  max_rel=1.198e-12 [sec.lepton_ratios.3(Chain_consistency_%)] ... PASS
long double          checked= 643 failed=0  max_rel=5.587e-15 ... PASS
  __float128: 536/536 values bit-identical to golden after rounding to this type ...
__float128           checked= 643 failed=0  max_rel=2.431e-30 ... PASS
  cpp_bin_float<169>: 536/536 values bit-identical to golden after rounding to this type ...
cpp_bin_float<169>   checked= 643 failed=0  max_rel=1.887e-46 ... PASS
S_thermo(mp169 -> double) = 0.93638756406297474 bit-identical to float(mpmath)
GOLDEN: ALL PASS
```
The `double` line also says `S_thermo(double) = 0.93638756406297519 ... differs by a few ulp`. That is
expected: a plain-double evaluation is not bit-exact. The 169-bit and `__float128` types round to Python's
`float(mpmath)` exactly. On MSVC the `long double`/`__float128` lines are absent.

**3.3 Regenerate from the pinned Python and diff (CI `regen-diff`, WSL2)**
```bash
python3 -m venv ~/fsot-cpp-work/venv && ~/fsot-cpp-work/venv/bin/pip install mpmath==1.4.1
P=~/fsot-cpp-work/venv/bin/python
$P tools/fetch_authority.py --out authority/fsot_compute.py      # -> "authority AEB2AD @ d127c07e -> authority/fsot_compute.py"
$P tools/gen_closed_forms.py --authority authority/fsot_compute.py
$P tools/dump_golden.py --authority authority/fsot_compute.py      # -> "644 lines, pin AEB2AD, 343 targets, 342 within 5%"
git diff --exit-code -- include/fsot/closed_forms.gen.inc include/fsot/closed_forms_core.gen.inc golden/golden_AEB2AD.tsv
```
Expected: `fetch_authority.py` prints `PIN MISMATCH` if the sha256 is wrong. `gen_closed_forms` reports 26
sections. `git diff` exits 0.

**3.4 Ledger B re-score: byte-identical with the hub's Python (CI `ledger-b`)**
Sparse-clone the hub data at the pinned commit (exact CI paths):
```bash
H=~/fsot-cpp-work/hub
git clone -q --filter=blob:none --no-checkout https://github.com/dappalumbo91/FSOT-2.1-Lean $H
git -C $H sparse-checkout set --no-cone '/data/*_benchmark.json' '/data/literature_uncertainty_anchors.json' \
  '/data/stumped_observables_reference.json' '/data/extension_folds_derived.json' '/data/domain_table_freeze.json' \
  '/predictions/' '/scripts/' '/vendor/fsot_compute.py'
git -C $H checkout -q 6f9c25605a52acabe662a42fc003afa5bf66b959
$P tools/dump_ledger_b_golden.py --hub $H --out /tmp/ledger_b.tsv && diff -q /tmp/ledger_b.tsv golden/ledger_b_6f9c2560.tsv
./build/fsot_ledger_b --hub $H --golden golden/ledger_b_6f9c2560.tsv
```
Expected Python: `active=477 green=477 ledgerB={'lb': 140088, 'unrouted': 7168, 'c_match': 14634, 's_match': 3667, 'e_match': 4223}`,
then no diff output.

Expected C++:
```
note: frb_orifice_outgassing_benchmark.json: read 257 non-standard JSON tokens (NaN/Infinity) tolerantly, first at line 785
fsot_ledger_b: 478 files, active=477 green=477 ledgerB=140088 unrouted=7168 c_match=14634 s_match=3667 e_match=4223 (≈6.5–10 s)
golden compare: 13842 lines, 0 mismatches
```
13842 lines = 1 header + 13,841 golden lines, matching the README's "13,841 of 13,841".

**3.5 Ledger A + property routing + tier evidence (CI `ledger-b`, continued)**
```bash
$P tools/gen_ledger_a_routing.py --hub $H        # "ledger A: 21 rows (6 translated emitters); routing: 161 properties, 30 elements"
$P tools/dump_ledger_a_routing_golden.py --hub $H --out /tmp/ledger_a_routing.tsv   # "A=21 MASS=1268 ROUTE=3339 REC=8496 (of 127438 distinct)"
git diff --exit-code -- include/fsot/ledger_a.gen.inc include/fsot/routing.gen.inc
diff -q /tmp/ledger_a_routing.tsv golden/ledger_a_routing.tsv
$P tools/gen_tier_evidence.py --hub $H           # "4 hub freezes, 1 cpp freezes, 478 benchmark files dated, 0 undated"
git diff --exit-code -- golden/tier_evidence_6f9c2560.json
```
Expected: every diff is empty.

**3.6 Corrected mode (audit fixes A-01/A-04/A-05/B-01..B-03 and M3; parity mode stays golden)**
```bash
./build/fsot_ledger_b --hub $H --corrected-out /tmp/c.tsv --genuine-misses-out /tmp/g.tsv
cmp /tmp/c.tsv golden/ledger_b_corrected_6f9c2560.tsv && cmp /tmp/g.tsv golden/ledger_b_genuine_misses_6f9c2560.tsv
./build/fsot_report --corrected | tail -6
```
Expected: both `cmp` succeed. `/tmp/g.tsv` has 7 data rows: the 7 formula misses in 3.9. `fsot_report --corrected` ends with:
```
Total constants with targets: 343
Within 5% of target: 342
Flagged non-predictions (computed=target or measured input): 21 (21 within 5%)
Genuine predictions with targets: 322
Genuine predictions within 5%: 321
Rows changed by corrected mode: 11
```
Corrected-mode totals from `docs/AUDIT_LOG.md` (they live in `golden/ledger_b_corrected_6f9c2560.tsv`):

| Quantity | Value |
|---|---|
| Gated scalars > 0.5 % | **9 in 7 files** (7 formula misses + 2 `fsot_prediction` rows) |
| Green files | 471/477 |
| Genuine predictions | 43,796 (7 > 0.5 %) |
| Stored `error_pct` disagreeing with own fields | 50,436 |
| `stored_only` | 9,735 (930 zero-target, 6,198 rounded-computed) |
| Inequality / contraction rows | 17 / 1 |
| Ledger B structural corrections | 139,400 |
| Ledger B records not reproducible from emitted `computed` | 47,994 of 140,088 in parity → 0 in corrected |
| NaN tokens | 257 in 1 file (first at line 785) |

Closed-form corrected mode: largest shift 5.9e-11 (`Chain_consistency_%`), and no row crosses a 5 % boundary.

**3.7 Closed-form predictions (`predict_closed_form`)**
```bash
./build/predict_closed_form --name H0 --digits 12
./build/predict_closed_form --name H0 --digits 12 --trits 40
./build/predict_closed_form --list-sections | head -3
```
Expected (P=110 and P=40 give the same 12 digits):
```
predict_closed_form: 2 rows (BTFloat<110>, parity mode, pin AEB2AD)
wave1                        H0                                 = 6.84449955638e+01  target 6.74000000000e+01  err% 1.550e+00
validation_suite             V25_H0                             = 6.84449955638e+01  target 6.74000000000e+01  err% 1.550e+00
```
`--list-sections` starts with `wave1`, `validation_suite`, `wave2`. Other flags: `--section`, `--corrected`, `--tsv`,
`--trits 40|72|110`. Note: the closed-form `tau_reion` (section wave2) gives 5.43965535023e-02 vs target 0.0544 (6.3e-3 %).
The Ledger B formula miss `tau_reion` (3.04 %) is a different record: `dark_sector_open_problems_benchmark.json`,
measured 0.0561.

**3.8 Freeze / hash check (`fsot_freeze_domain`, `tools/verify_freeze.py`)**
```bash
./build/fsot_freeze_domain --verify freezes/domain_freeze_2026-10-02_AEB2AD.json
python3 tools/verify_freeze.py freezes/domain_freeze_2026-10-02_AEB2AD.json
./build/fsot_freeze_domain --print-core-sha
```
Expected:
```
OK freezes/domain_freeze_2026-10-02_AEB2AD.json: 796 rows, freeze_date 2026-10-02, selection_sha256 580eb6e72ca75e2995b4331828b7a9f513978ce5c5aa3d7a798c2b83de4182dd
OK freezes/domain_freeze_2026-10-02_AEB2AD.json: 796 rows, 0 bad row hashes, selection 580eb6e72ca75e29, core 8e30e85e72091462
8e30e85e72091462c4d66df2d498afb36ccbc2d40eb5df01b4e083947c79dad3
```
Do **not** write a new freeze into `freezes/`. If you try `--authority ... --out`, write to `/tmp`.

**3.9 Precision M3: 188 genuine misses = 181 data handling + 7 formula (`docs/PRECISION_M3.md`)**
```bash
$P tools/classify_genuine_misses.py --misses audit/m2_genuine_misses_input.tsv --hub-data $H/data --out /tmp/pm3.tsv
cmp /tmp/pm3.tsv audit/precision_m3_genuine_misses.tsv
cut -f1,3,9 /tmp/g.tsv
```
Expected breakdown:

| Count | Category | Kind |
|---|---|---|
| 153 | `zero_target` | data_handling |
| 14 | `inequality_bound` | data_handling |
| 12 | `computed_rounded` | data_handling |
| 7 | `formula_miss` | formula |
| 1 | `float_noise_gate` | data_handling |
| 1 | `contraction` | data_handling |
| 188 | total | |

`cmp` must be silent. The 7 formula misses (recomputed error %):
- `Mean_dependency_length_EN`, 4.348416682194786, in each of `anthropology_extension_benchmark.json`,
  `creative_arts_math_spine_benchmark.json` and `programming_language_laws_benchmark.json`;
- `FRB20121102A`, 2.0000000000000036 (`cosmology_bubble_bleed_benchmark.json`);
- `FRB20200929C`, 2.0000000000000067 (same file);
- `tau_reion`, 3.036446519949971 (`dark_sector_open_problems_benchmark.json`);
- `D_H_ratio`, 0.6997461789355196 (same file).

The 2 extra gated rows above 0.5 % are the Cepheid/SH0ES `fsot_prediction` rows
`host_moduli_mean_vs_Li2024_TRGB` and `full_sample_moduli_mean_vs_Li2024_TRGB`.

**3.10 Ternary core (balanced-ternary arithmetic, `docs/TERNARY.md`)**
```bash
./build/test_ternary | tail -3; ./build/test_core | tail -3; ./build/test_core_closed_forms | tail -1; ./build/test_trit | tail -1
```
Expected:
```
Engine<BTFloat<72>> (~114 bits): 168 golden values, max rel err 1.188e-32 [const.BETA], tol 1e-31  PASS
Engine<BTFloat<110>> (~174 bits): 168 golden values, max rel err 9.495e-50 [const.BETA], tol 1e-48  PASS
TERNARY: ALL PASS (0 failures)
BTFloat<72>: 35 domains, 0 mismatches
  P=110 Particle_Physics S=9.50197470167014204069298236913e-01 (host 9.50197470167014204069298236912e-1)
BTFloat<110>: 35 domains, 0 mismatches
core closed forms: 368 rows, worst rel 1.02e-46 (Chain_consistency_%), 0 mismatches
TRIT: ALL PASS (0 failures)
```
The CTest `freestanding_symbols` also checks that the ternary core references no malloc/new/throw/printf/libm symbols.

**3.11 QEMU bare-metal demo (CI `bare-metal`, WSL2)**
```bash
./kernel/build.sh build-kernel
qemu-system-x86_64 -m 64 -kernel build-kernel/fsot_kernel.elf -serial file:serial.txt -display none \
  -no-reboot -monitor none -device isa-debug-exit,iobase=0xf4,iosize=0x04; echo "exit=$?"
python3 tools/check_kernel_serial.py serial.txt
cmp serial.txt docs/bare_metal_serial_AEB2AD.txt && echo SERIAL_IDENTICAL
```
Expected:
- `exit=33`, which is success through isa-debug-exit;
- `kernel serial: 35 domain S values, worst relative error 7.57e-41; 368/368 closed forms, worst 4.70e-40 vs 50-digit golden -> PASS`;
- the last serial line is `DONE CF 368`, and the serial log is byte-identical to the committed reference;
- about 1.6 s under QEMU TCG (`docs/BARE_METAL.md`);
- `ld` may warn `LOAD segment with RWX permissions`, which is harmless.

**3.12 Evidence tiers (`docs/EVIDENCE_TIERS.md`)**
CTest `evidence_tiers_report` diffs `build/evidence_tiers.tsv` with `golden/evidence_tiers_6f9c2560.tsv`. Documented result:

| Class | Gated records | Domains | Ledger A rows | Closed-form rows with target |
|---|---|---|---|---|
| TIER 1 EXPLORATORY | 17,406 | 12 | 0 | 0 |
| TIER 2 FROZEN-PENDING | 3 | 56 | 21 | 323 |
| TIER 3 CONFIRMED HELD-OUT | 0 | 0 | 0 | 0 |
| STRUCTURAL/IDENTITY | 165,787 (139,400 Ledger B, 26,387 target = computed) | — | 0 | 20 |

Nothing is TIER 3 yet (`docs/PROMOTION_WATCH.md`).

**3.13 Precision gate (z ≤ 1, `docs/PRECISION_REPORT.md`)**
```
python3 tools/check_references.py          # references: 105 rows ...; failures: 0
python3 tools/verify_refinement_freeze.py  # refinement freeze: 4 refinements, tier frozen-pending, failures 0
./build/test_seed_leaves                   # 50 leaves vs the hub scripts' printed values
./build/fsot_precision --refs reference/published_2026-10-02.tsv --map reference/prediction_map_2026-10-02.tsv \
  --lineage reference/pin_lineage_2026-10-02.tsv --tsv-out p.tsv --md-out p.md
cmp p.tsv audit/precision_2026-10-02.tsv && cmp p.md audit/precision_2026-10-02.md
```
Expected: `record set (scored): n=91  pass z<=1: 83/91  pass |rel|<=2%: 88/91  median ppm=93.03`. The CI ledger-b job also regenerates
`golden/seed_leaves_6f9c2560.tsv` (it runs the hub's `scripts/*_seed_check.py` unchanged) and `reference/pin_lineage_2026-10-02.tsv`, then diffs both.

### 4. Report format
Give one table with these columns: check, command, expected, observed, PASS/FAIL. Also give:
- the tool versions (compiler, CMake, Boost, nlohmann_json, Python, mpmath, QEMU, OS/WSL build);
- the repo commit;
- total wall time.

For any FAIL, paste the first 30 lines of output and stop there. Don't "fix" goldens or pins.

### 5. Button-up list (what is still open). Work only within the hard rules
These are open items recorded in the repo. Several are **theory or data decisions for me (Damian)**. For those,
prepare an analysis and a recommendation, but do not change data, pins or constants to close them.

**5a. The 7 formula misses and related decisions (`docs/PRECISION_M3.md`, "Needs a theory or data decision")**
1. Should rows with a reference uncertainty be gated at that uncertainty instead of 0.5 %? All 7 formula misses lie inside their bands.
2. FRB periodicity: one prediction (1000 s) is scored against 3 FRBs with different periods.
3. Target-derived rows labelled genuine: `literature_anchor` founding panels (c = m(1+|S|·0.0005)), planetary Europa/Io, and PRED-004. Should they be STRUCTURAL?
4. Relay spines (`circuit_component_emergence_lib.py:432-436`) relabel Ledger B rows as `live_formula`.
5. Emitters store `computed` rounded (6 or 10 decimals). Storing `round_sig(c, 12)` would make every row recomputable. Until then C++ falls back to the stored error for 6,198 rows.
6. Stale stored `error_pct` values in hub data: 50,436 rows disagree with their own fields, including all 7 formula misses.
7. The two Cepheid/SH0ES `host_mu_vs_trgb_mean` rows are labelled `fsot_prediction`, but their computed value is not a Ledger B correction.

For each item, write up the options and what each would change in the corrected-mode counts. Put the
write-up in a new file, e.g. `docs/DECISIONS_DRAFT.md`, for my review. Don't apply any option.

**5b. Open audit findings (`docs/AUDIT_LOG.md`)**
Fixes for A-01, A-04, A-05, B-01..B-03 and the M3 categories exist in C++ **corrected mode only** ("Fixed in C++"
table). The rest stay open:
- A-02 (stored Ledger B amplitudes use the old per-domain table) and A-03 (~10 % of routed Ledger B records match the live AEB2AD law);
- B-04 (older copies of C_EFF/K still in use) and B-05 (docstring version label);
- C-01/C-02 (two DOIs don't resolve), C-03 (hub self-links that 404) and C-04 (most citation fields have no resolvable identifier). Re-run `tools/check_citations.py` and compare with `audit/citations_summary.json`;
- G-01..G-05 (Ledger A labels/anchors, freeze dating, look-elsewhere multiplicity). `./build/fsot_look_elsewhere` prints the summary: `343 targets; 325 have at least one M-grammar value at least as close as the FSOT expression; median M_within 66`;
- D-01..D-04 (cross-repo constants and pins; see 5c);
- E-1..E-7 (credibility gaps: look-elsewhere significance, uncertainty quantification, blind tests, dimensional analysis, baselines, panel selection, reproducibility of stored numbers);
- F (this repo's limits): the Ledger B lower-casing emulation covers ASCII + Greek Δ/Γ only, and `BTFloat` division is faithfully rounded, not correctly rounded.

Allowed work: documentation and analysis, new tests that only read pinned data, and C++ corrected-mode
additions that keep parity mode golden-identical. Anything that changes hub data or a pin goes to me as a
proposal.

**5c. TRIT_SPEC T-1..T-5 status (`docs/TRIT_SPEC.md` §4a)**
- T-1 applied: FSOT-Genetics `2cd14ad`, fsot-neuron-zig `076a01e`.
- T-2 applied: Genetics, neuron-zig, FSOT-GPU `16e618b`, FSOT-Quantum `3c4375a`.
- T-3 applied in FSOT-GPU only (CUDA edit is literal-only and was **not compiled**, because there was no CUDA
  toolchain). FSOT-Quantum got a README note only, because changing Θ/QM scalars would break its D1D38A
  gate. Quantum's `authority_pin` reports 46F53B on Linux because of LF endings (the CRLF form hashes to D1D38A).
- T-4 / T-5 documentation only (FSOT-Reality-OS `6d3db14`). Re-vendoring at AEB2AD is **not done**, by
  instruction, and the VM is not rewritten.
- Deliberately unchanged: fsot-rna-codon-lab, fsot-neuron-zig `seeds.zig`/`seeds_fixed.zig` (D1D38A lineage)
  and the Genetics Zig K.

Open decisions for me: whether to re-pin Quantum/Reality-OS to AEB2AD, and whether to compile-check the
FSOT-GPU CUDA edit on my NVIDIA machine (if I have one). That is safe to do locally: build plus the existing
parity tests, with no edits.

**5d. Roadmap (`docs/PORT_PLAN.md`)**
Items 4–9 are open:
- trinary syntax rows + opcode registry / Reality-OS FSOTB loader;
- AST codegen for pure-math vendor modules;
- numeric kernels;
- data panels / gauntlet;
- pybind11 binding + CUDA bridge;
- C++ as an extra replay prover.

These are optional and only after everything above passes. Each new port must be golden-tested against the
AEB2AD Python and must leave the pins alone.

**5e. Windows-specific items to report**
- Does the MSVC build work?
- Does the MinGW build pass `golden` with `__float128`?
- Do the `sh -c` tests run?

Report the results. Don't change CMake behaviour for Linux.

### 6. Secondary: the broader cross-validation harness (`xval/`)
The C++ checks above are the main task. `xval/` also re-runs the hub (FSOT-2.1-Lean) and its siblings on
Linux/WSL2. It is optional and much heavier: a full run takes ~56 min with the runner, ~33 min without it and
~7 min with `--skip-xproof`. One-time setup: Isabelle heap ~15 min, Rocq opam ~13 min, Idris2 ~10 min.

```bash
cp -r xval ~/fsot-xval && cd ~/fsot-xval
./setup_toolchains.sh        # apt + elan (Lean v4.31.0) + TLA+ 1.8.0 + F* v2026.07.05 + Isabelle2025-2 + Zig 0.15.2 + Idris2 0.8.0 + Rocq 9.0.1 (opam) + Rust
./RUN_ALL.sh --skip-xproof   # then ./RUN_ALL.sh for the full multiprover; --with-runner adds the hub runner
cat runs/latest/summary.tsv
```

Memory: `tools/guarded.sh` kills a layer if `MemAvailable` < 4000 MB and retries. WSL2 gets 50 % of host RAM by
default, so set `memory=` in `%UserProfile%\.wslconfig` if needed. Never run Isabelle and the hub runner at the
same time.

Expected, measured 2026-10-02 (ET) at hub `56fcbf31` and siblings Chua `cecef94`, Genetics `f677663`, Neural
`e12a4bc`, neuron-zig `68e43ce`, neuron-haskell `5c12baa`, neuron-idris `2ee5060`:

| Layer | Expected |
|---|---|
| Hub pin | `vendor/fsot_compute.py` sha256 starts `AEB2AD` |
| Hub CI | margin audit green 477/477 fail=0; tier_scalar closed, fails 0; TOE Label A/B True, criteria 6/6; z3 4.13.3 → sat; 24 obligations exported; navigator 375 panels / 19 routes; contested pooled 0.007871 %; parameter audit freeze_ok, domain_table_sha256 8e30e85e… |
| Lean 4 v4.31.0 | all 567 `FSOT.*` modules + `FSOT2_0_Compute`, 0 errors, 0 `sorry`, 0 `axiom` |
| Multiprover | `overall_ok`, `seven_way_bare_metal` and `github_ready` all True; Coq 49/49 (Rocq 9.0.1), Isabelle 46/46, SMT 2205, TLC pass, Rust replay 2130, Rust↔Lean bridge (boot_scalar 0.09928895626861721), F* pass, QEMU serial+disk pass, hardware_bare_metal pass, GR/SM/CKM 288/288; ESP32 skipped (needs the board) |
| Siblings + twins | 23/23 PASS: Chua cross_proof 11/11 (10 required + Isabelle); Genetics verify_cross 21 OK, cross_proof 10/10, system_verify n=259 fail=0, cargo, Haskell, Zig host; Neural smoke + language gates (SMILES hit_rate 99.4 %, median 0.058 %) + formal Lean; zig `suite` 67 PASS markers; Haskell test/selftest/parity/phase-a; Idris build/scalpel/phase-a |
| `fsot_verification_runner.py` (`--with-runner`) | **FAIL on Linux, 32 summary items** (see below) |

SMILES dataset: FSOT-2.1-Neural `fsot_nuron/chemical_codon.py` looks only at `I:\FSOT-Physical-Archive\01_SR-ITE-USB-Original\6_unified_oracle\smiles_lab\FSOT_SMILES_Lab_Dataset.json`
and `C:\Users\damia\Desktop\FSOT SMILES Lab\FSOT_SMILES_Lab_Dataset.json`, with no env override. The public copy is
https://github.com/dappalumbo91/FSOT-2.1-Lean/blob/main/vendor/smiles/FSOT_SMILES_Lab_Dataset.json (Apache-2.0),
sha256 `10b4c7e1abe3532d7b94ad0007694672ca7687609d83a1aca63e2e75c114d091` (at hub 56fcbf31). The harness
injects it in-process via `tools/run_neural_language_verify.py`.

**Runner task (on my PC):** on Linux the hub runner failed for two reasons:
- missing Windows-only inputs: `C:/Users/damia/Desktop/...` (Fuel Lab, weather, Soul Sibling, Unified DB, Knowledge
  base, Lean_Proofs, Photonic, VibraFSOT, magnetic strings, Trinary Fluid, NeuroLab .jl, BlackHole thesis,
  autonomous MC), `D:\training data\cnc_data\Exp1.csv`,
  `vendor/neurolab/DataAnalysisExpert/export/thalamus/thalamic_gate_manifest.json` and the Trinary Codon build script;
- its final `lake build` failed in 12 `*Priors.lean` files that the runner itself regenerated: BiologicalCudaPhysarum,
  BiologyStrictEmpirical, BubbleBleed, CosmologyHigherWaves, Cryosphere, GbifSpeciesOccurrence, HiggsBranching,
  IGEMLiveFasta, IGEMSyntheticBiology, ParticlePhysics, SyntheticBiology, UniprotProteinAnnotations. The committed
  versions build cleanly.

On my Windows PC, do this:
1. List which of those input paths actually exist on this machine (path, size, mtime).
2. Run the runner once natively. Report its 32 summary items as PASS/FAIL, each with its cause.
3. For each missing input, propose either a fallback to a bundled `vendor/` copy (if one exists in the hub) or
   documented public download steps.

Do not fabricate data. Do not commit regenerated hub data. Do not touch hub pins.

---
*Prepared 2026-10-02 (ET). Source docs: README.md, docs/AUDIT_LOG.md, docs/PRECISION_M3.md, docs/TRIT_SPEC.md,
docs/EVIDENCE_TIERS.md, docs/FREEZES.md, docs/BARE_METAL.md, docs/PORT_PLAN.md, docs/PROMOTION_WATCH.md,
.github/workflows/ci.yml.*
