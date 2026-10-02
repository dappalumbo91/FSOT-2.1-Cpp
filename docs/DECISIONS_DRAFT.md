# Decisions draft (not applied)

Status: draft for review. No option below was applied. This file does not change
`AUTHORITY_PIN.json`, any pin (AEB2AD, D1D38A), `vendor/fsot_compute.py`,
`authority/fsot_compute.py`, `golden/`, `freezes/`, any frozen value, or any
gate tolerance.

Prepared from the local WSL reproduction of `FSOT-2.1-Cpp` @
`e845378ad4f201da25826b755cea99627c720344` (branch `reproduce-wsl-2026-10-02`).
Hub data @ `6f9c25605a52acabe662a42fc003afa5bf66b959`. Authority pin AEB2AD.
`bash xval/cpp_check.sh` ended `ALL CPP CHECKS PASSED`. Section 3 checks matched
the expected outputs. Counts below are from that run, from
`golden/ledger_b_corrected_6f9c2560.tsv`, from `audit/precision_m3_genuine_misses.tsv`,
and from the hub JSON at the pinned commit. Where a counterfactual was not
recomputed, it is marked not computed.

## Current corrected-mode counts (unchanged)

Source: `#summary` lines of `golden/ledger_b_corrected_6f9c2560.tsv`, byte-identical
to `./build/fsot_ledger_b --corrected-out`.

| Quantity | Value |
|---|---|
| Gated scalars | 183,196 |
| Over 0.5% stored -> recomputed | 0 -> 9 |
| Green files | 477 -> 471 of 477 |
| Genuine predictions | 43,796 |
| Genuine over 0.5% | 7 |
| Ledger B structural corrections (label `fsot_prediction` / `fsot_correction`) | 139,400 |
| Stored `error_pct` disagreeing with own fields | 50,436 |
| `stored_only` | 9,735 |
| of which zero-target / rounded-computed | 930 / 6,198 |
| Inequality / contraction rows | 17 / 1 |
| Ledger B records not reproducible from emitted `computed` | 47,994 of 140,088 in parity -> 0 in corrected |

The 6 files that go from green to not green are exactly:

- `anthropology_extension_benchmark.json`
- `creative_arts_math_spine_benchmark.json`
- `programming_language_laws_benchmark.json`
- `dark_sector_open_problems_benchmark.json`
- `cepheid_pl_interconnect_benchmark.json`
- `sh0es_full_sample_benchmark.json`

`cosmology_bubble_bleed_benchmark.json` stays green. Its two formula misses are
`frb_p34_periodicity`, which the C++ file gate treats as contested and scores
with the literature-aware effective error (0 when inside the band). They still
count in `genuine_over_0.5pct`.

## The 7 formula misses (observed)

All 7 have `within_literature = True` in `golden/ledger_b_genuine_misses_6f9c2560.tsv`.
Stored `error_pct` disagrees with the fields in every row.

| File | Name | Formula in the record | Computed | Measured | Recomputed error % | Reference uncertainty |
|---|---|---|---|---|---|---|
| `anthropology_extension_benchmark.json` | `Mean_dependency_length_EN` | `phi*(e/pi)+1` | 2.40001358369048 | 2.3 | 4.348416682194786 | 8.7% (`mean_dependency_length`, abs 0.2 words) |
| `creative_arts_math_spine_benchmark.json` | same row, relay | (empty formula field; same numbers) | same | 2.3 | same | 8.7% |
| `programming_language_laws_benchmark.json` | same row, relay | source `linguistics_formal_benchmark` | same | 2.3 | same | 8.7% |
| `cosmology_bubble_bleed_benchmark.json` | `FRB20121102A` | empty; computed 0.001 Hz | 0.001 | 1/1020 Hz | 2.0000000000000036 | 50% contested (`frb_p34_periodicity`) |
| same file | `FRB20200929C` | empty; computed 0.001 Hz | 0.001 | 1/980 Hz | 2.0000000000000067 | 50% contested |
| `dark_sector_open_problems_benchmark.json` | `tau_reion` | `phi*|Chaos| - ln(phi)` | 0.05439655350230806 | 0.0561 | 3.036446519949971 | 13.0% (Planck 2018, abs 0.0073) |
| same file | `D_H_ratio` | `1/(pi^4 * e^6)` | 2.5446825859417006e-05 | 2.527e-05 | 0.6997461789355196 | 1.2% (Cooke et al. 2018, abs 3e-07) |

These are not the closed-form rows. Closed-form `tau_reion` (section `wave2`),
run here as `predict_closed_form --name tau_reion --digits 12`, is
`5.43965535023e-02` against target `5.44000000000e-02` (err% `6.335e-03`).
That target is 0.0544, not the Ledger B measured 0.0561.

A fourth FRB periodicity row exists and is not a formula miss:
`FRB20191221A`, measured 0.001 Hz, error 0. `FRB20201124A` is measured 1/995 Hz,
recomputed error `0.500000000000008`, category `float_noise_gate`, already kept
under the corrected-mode gate. So one 1000 s prediction is scored against four
FRB periods, three of which differ (1020 s, 980 s, 995 s).

The two extra gated rows above 0.5% are not formula misses. They are labelled
`fsot_prediction`:

| File | Name | Computed | Measured | Stored error % | Absolute uncertainty |
|---|---|---|---|---|---|
| `cepheid_pl_interconnect_benchmark.json` | `host_moduli_mean_vs_Li2024_TRGB` | 0.004391645567700664 | 0.01 | 0.017636334692765206 | 0.04 mag |
| `sh0es_full_sample_benchmark.json` | `full_sample_moduli_mean_vs_Li2024_TRGB` | same | 0.01 | same | 0.04 mag |

Relative error from those fields is `56.08354432299336%`. Absolute difference is
`0.005608354432299336`, which is inside 0.04. `c/m - 1 = -0.5608354432299336`,
so this is not the Ledger B step `c = m(1+|S|alpha)`.

## 1. Gate at the reference uncertainty instead of 0.5%?

All 7 formula misses are inside the bands above. The two Cepheid/SH0ES rows are
inside their absolute 0.04 mag band and outside 0.5% relative.

Options:

- A. Keep the 0.5% reproducibility gate. Report the band as a separate column
  (already present: `within_literature`). Counts unchanged: 9 gated rows, 7
  genuine misses, 471/477 green.
- B. Replace the gate with the resolved reference uncertainty wherever one
  exists, else 0.5%. For the 9 rows that currently fail, all would pass, so
  those files would return to green (471 -> 477) and genuine-over would go
  from 7 to 0, **if and only if** no currently green file newly fails. That
  second half was **not computed**. It is not safe to assume it is zero.
  Anchors tighter than 0.5% already exist: `neutrino_species` 0.033%,
  `higgs_mass` 0.136%. The resolver also has code defaults of 0.2% (biochem)
  and 0.15% (behavioral), both tighter than 0.5%.
- C. Dual report only: keep 0.5% as the gate that CTest checks, and add a
  second headline "inside reference band" that does not change green/genuine
  counts. Counts unchanged. This is a report change, not a data change.

Recommendation: C, not B. Widening the gate would hide disagreements that are
real against the stored measured value (4.35%, 3.04%, 2.00%). Do not change
the 0.5% constant to make the 7 rows pass.

## 2. FRB periodicity: one 1000 s prediction, several periods

Computed value is 0.001 Hz (1000 s) on every `frb_p34_periodicity` row in
`cosmology_bubble_bleed_benchmark.json`. Measured periods in that file:
1000 s (`FRB20191221A`, error 0), 995 s (`FRB20201124A`, float-noise 0.5%),
980 s and 1020 s (the two formula misses, 2%). The 50% anchor is labelled
contested and cites FRB 20200929C (Fonseca et al. 2022), then is applied to
the other names by the record-name alias and the shared property.

Options:

- A. Leave the four comparisons. Counts unchanged. The two 2% rows stay
  formula misses. The file stays green because the property is contested.
- B. Score 1000 s only against the FRB whose measured period is 1000 s
  (`FRB20191221A`). Drop the other three from this prediction's gate.
  `genuine_over_0.5pct` 7 -> 5. Cosmology `genuine_over_0.5pct` 2 -> 0.
  Green files unchanged (already 471, cosmology already green). Formula-miss
  list loses 2 rows. This is a scoring-rule change, not a formula change.
- C. Declare a period window (980-1020 s) and mark all four structural.
  Same count effect as B on the current miss list, plus the float-noise row
  would no longer need the 1e-12 gate tolerance for this file. Not computed
  for any other file.

Recommendation: A until you choose which FRB the 1000 s expression is about.
Do not edit the 0.001 value. If the expression is only a claim about one
event, B is the honest scoring rule, and it should name that event in the
record rather than alias every FRB name to the same 50% band.

## 3. Target-derived rows labelled genuine

Verified rows, not a guess at every similar name:

- Seven `founding_*_panel_benchmark.json` files. Each has 19 `literature_anchor`
  gated scalars and 19 genuine predictions, 0 over 0.5%. That is 133 genuine
  predictions. M3 flags 5 of them as `computed_rounded` because
  `round(measured*(1+|S|*0.0005), 10)` collapsed (`founding_unmapped_laws_lib.py:46,52`).
  The construction is the measured value plus a 0.05% `|S|` step, not an
  independent measurement.
- `planetary_atmospheres_benchmark.json`: 21 genuine predictions, 2
  `stored_only`. Those two are `Europa:surface_pressure` and
  `Io:surface_pressure`. M3 evidence: `fsot_val` is built from the observation
  (`build_planetary_atmospheres_benchmark.py:129` and `:32-34`). The other 19
  rows in that file were **not** classified here as target-derived.
- `PRED-004` in `preregistered_predictions_benchmark.json`: 1 of 35 genuine
  predictions, `stored_only`. M3 evidence: measured = `fsot_predicted`
  (`tier_k_toe_gap_closure_lib.py:171,180`). Other `PRED-*` rows exist and
  were not included in this count.

Options:

- A. Leave the labels. Genuine predictions stay 43,796. None of these rows
  are in the 7 formula misses, so `genuine_over_0.5pct` stays 7.
- B. Reclassify the named set only: 133 founding anchors + Europa + Io +
  PRED-004 = 136 rows, from genuine to structural. Genuine predictions
  43,796 -> 43,660. Genuine-over unchanged. Green files unchanged.
  Evidence-tier STRUCTURAL would rise by 136 only if the tier rule is changed
  the same way. That tier total was not regenerated.
- C. Reclassify every row whose formula is `m` times a factor near 1, across
  the whole hub. **Not computed.** Do not use 136 as that number.

Other `Europa` / `Io` rows in `between_scale_interconnect_benchmark.json` are
`fsot_prediction` density folds. They are a different set and are not in the
136.

Recommendation: B, as a hub label change for you to accept. Do not change
`0.0005` or any seed. This repo should not edit the hub JSON.

## 4. Relay spines relabel Ledger B rows as `live_formula`

The cited site is `circuit_component_emergence_lib.py:432-436`. The M3 rows
are four `computed_rounded` records in `tier_96_circuit_spine_benchmark.json`:
`C_10nF_X7R`, `C_100nF_X7R`, `C_100pF_C0G`, `RC_22R_100nF`. That file has
37 genuine predictions, 35 `live_formula` rows, 7 `stored_only`, and 0 over
0.5%. It is already green.

A scan found 2,305 `live_formula` rows in 38 files. That is **not** the relay
count. Most of those rows were not checked against the circuit-spine copier.
Do not subtract 2,305 from genuine predictions.

Options:

- A. Leave them. Counts unchanged. The four rounded rows stay `stored_only`
  and do not fail the gate.
- B. Relabel the four M3 relay rows as structural copies of the source Ledger
  B rows. Genuine predictions 43,796 -> 43,792 if each is currently one
  genuine scalar (they are in a file whose gated scalars are the genuine
  set). Genuine-over and green unchanged.
- C. Relabel all 35 `live_formula` rows in that file. Genuine would fall by
  at most 35. Exact overlap of the 35 with the 37 gated scalars was **not
  joined**, so 43,796 - 35 = 43,761 is an upper bound on the drop, not a
  measured new total.

Recommendation: B now, C only after a row-level join. Do not treat the relay
as a new prediction, and do not retune the source Ledger B formula.

## 5. Emitters store `computed` rounded to 6 or 10 decimals

Corrected mode already re-emits with `round_sig(c, 12)`. That is why
"not reproducible from emitted computed" is 47,994 -> 0 of 140,088. The
6,198 `computed_rounded_rows_kept_stored` are a different fact: the **stored
hub field** does not have enough digits, so the gate keeps the stored error.

Options:

- A. Leave hub emitters as they are. C++ keeps the stored error for 6,198
  rows. `stored_only` stays 9,735. Counts unchanged.
- B. Hub emitters store `round_sig(c, 12)` and a matching `error_pct`. Then
  those 6,198 rows become recomputable. `stored_only` would fall by 6,198,
  from 9,735 to 3,537, of which 930 are the zero-target rows and 2,607 are
  the other non-relative cases (9,735 - 6,198 - 930 = 2,607, matching the
  M2 `stored_only` figure of 2,607). How many of the 6,198 would then exceed
  0.5% **cannot be computed from the rounded stored `computed`**. That count
  is not invented here.
- C. Change the C++ fallback so a rounded row is failed instead of kept.
  That would move failures without new information. Not recommended.

Recommendation: B, in the hub, as a separate data commit you approve. Do not
do it in this repo, and do not change the 0.5% gate to compensate.

## 6. Stale stored `error_pct` (50,436 rows)

Includes all 7 formula misses. Examples from the genuine-miss file: dependency
length stored `0.0005659871035364658` vs recomputed `4.348416682194786`; both
FRBs stored `0.0` vs recomputed `2.0`; `tau_reion` stored `0.006335` vs
recomputed `3.036446519949971`; `D_H_ratio` stored `0.090986` vs recomputed
`0.6997461789355196`.

Corrected mode already gates recomputable rows on the recomputed error. So
rewriting stored `error_pct` to match the fields would **not** change the
corrected headlines (9 / 7 / 471) if no other field changes.

It **would** change parity mode. Parity trusts the stored error and is
477/477 green with 0 scalars over 0.5%. Writing the recomputed errors into
the hub would make parity fail the same 9 rows. That is a new ledger-data
commit, not a silent fix.

Options:

- A. Leave the hub fields. Corrected mode remains the audit view. Counts
  unchanged.
- B. Hub rewrite of `error_pct` from `computed` and `measured`, then a new
  `ledger_b_data_commit`. Parity green would drop. The new pin is your
  decision. Not done here.
- C. Teach parity mode to recompute. That would break the golden
  byte-identity this reproduction just checked. Rejected.

Recommendation: A in this repo. B only if you want the hub gate itself to
stop trusting stale `error_pct`. Do not edit `golden/ledger_b_6f9c2560.tsv`
to follow a rewrite.

## 7. Two Cepheid/SH0ES rows labelled `fsot_prediction`

Facts are in the table above. The label puts them in
`ledger_b_structural_corrections` (the counter increments on `eval_kind`
alone). The numbers are not `c = m(1+|S|alpha)`. They are the only reason
`cepheid_pl_interconnect_benchmark.json` (8 scalars, 8 labelled Ledger B,
0 genuine) and `sh0es_full_sample_benchmark.json` (5 scalars, 5 labelled
Ledger B, 0 genuine) are not green.

Options:

- A. Leave the label and the 0.5% gate. Counts unchanged: 9 gated rows,
  471/477 green, genuine-over stays 7.
- B. Relabel them off `fsot_prediction` and do not gate them (literature
  comparison, not a correction). Gated-over 9 -> 7. Green 471 -> 473.
  Label-based structural count 139,400 -> 139,398. Genuine predictions
  unchanged, because these files already contribute 0 genuine rows.
- C. Keep the label but gate on the absolute 0.04 mag band. They pass.
  Gated-over 9 -> 7. Green 471 -> 473. Structural count unchanged. This
  hides a 56% relative disagreement behind a wide absolute band.
- D. Relabel them as genuine predictions and keep the 0.5% gate. They become
  two more formula misses. Genuine-over 7 -> 9. Green stays 471 (same two
  files). Not recommended: the value is not an independent formula, and it
  is not the Ledger B correction either.

Recommendation: B. State in the record that the computed value is not a
Ledger B correction. Do not change 0.004391645567700664 to move it inside
0.5% of 0.01.

## What I would not do

- Do not edit AEB2AD, D1D38A, `AUTHORITY_PIN.json`, goldens, or freezes to
  close any item above.
- Do not change 0.5%, 5%, or any seed to make a row pass.
- Do not conflate closed-form `tau_reion` (0.006335% vs target 0.0544) with
  Ledger B `tau_reion` (3.036% vs measured 0.0561).

## 5c. Re-pin Quantum / Reality-OS, and the CUDA compile-check

Not applied. From `docs/TRIT_SPEC.md` section 4a, still true on this machine:

- T-3 in FSOT-Quantum is a README note only, because changing Theta / QM
  scalars would break the D1D38A gate. `authority_pin` reports 46F53B on
  Linux (LF). The CRLF bytes hash to D1D38A. That is a line-ending fact,
  not a reason to re-pin.
- T-4 / T-5 in FSOT-Reality-OS are documentation. Re-vendoring at AEB2AD
  was left undone by instruction. The QEMU serial `collapse_theta`
  0.917466377465 would move. AEB2AD Theta is 0.9175102712064876
  (shift +4.39e-5, as recorded in TRIT_SPEC).
- Desktop `C:\Users\damia\Desktop\FSOT-GPU` is missing. nvcc 13.3
  (`V13.3.73`) is installed. An older folder
  `C:\Users\damia\Desktop\gpu exparment for lean coq isabell andf star`
  exists (directory, mtime 2026-07-17). It was not built. A compile-check
  is only meaningful on the tree at `16e618b`, with no edits, plus the
  existing parity tests.

Options:

- A. Leave Quantum and Reality-OS on D1D38A. No count in this repo changes.
- B. Re-pin both to AEB2AD and regenerate their gates. Their D1D38A tests
  will fail until the gates are regenerated. Theta moves by +4.39e-5.
  This repo's goldens stay on AEB2AD either way. Not done.
- C. Compile-check FSOT-GPU `16e618b` locally, no edits. Does not re-pin
  Quantum. Not done, because that checkout is not at the Desktop path
  above.

Recommendation: A until you want B as its own task. C is safe later and
does not require B.

## Appendix: other button-up checks (no data changed)

### Citations (`tools/check_citations.py`)

Re-run against hub @ `6f9c256` with outputs in `/tmp` only. The committed
`audit/citations_summary.json` was not overwritten.

Identical: both failing DOIs still do not resolve
(`10.1103/physrevd.112.083515`, `10.1152/physrev.00019.2014`). JSON citation
fields still 5,212 values, 640 with an identifier, 560 distinct, 9 with an
identifier. arXiv still 14 distinct, all OK.

Not identical, and not a reason to edit the summary: the re-run is a
superset. `audit/citations.tsv` has 3,570 lines; the new TSV has 3,585.
`only_old` row count is 0. The extra rows are in `results/siblings/` and
one truncated `https://` token in
`results/literature/2026-09-01_prediction_status.md` (a command example,
HTTP error, not a new paper). Self-link HTTP 404 count stays 168. C-01 and
C-02 still stand.

### Look-elsewhere

`./build/fsot_look_elsewhere` printed:
`343 targets; 325 have at least one M-grammar value at least as close as the FSOT expression; median M_within 66`.
That matches the recorded G-05 line. No grammar limit was changed.

### Windows compilers (5e)

- WSL `sh -c` tests passed (`freestanding_symbols`,
  `freeze_core_sha_matches_hub_freeze`).
- MSVC: VS 2022 Build Tools 17.14.30, `cl` 19.44.35225 for x64, invoked
  through `vcvars64.bat`. `cl` is not on the default PATH. vcpkg was not
  found, so the MSVC project build was not run. No CMake change was made.
- `sh` is not on PATH. Git for Windows has
  `C:\Program Files\Git\bin\sh.exe`. It was not added to PATH.
- MinGW / MSYS2 UCRT64 is not installed (`C:\msys64` missing). The
  `__float128` MinGW golden was not run.

### Runner inputs on this PC (section 6, inventory only)

The native hub runner was **not** started. It regenerates Lean priors. Those
files were not written and will not be committed. Paths below are the
literals in hub @ `6f9c256` manifests, not guessed folders.

| Path | State |
|---|---|
| `C:\Users\damia\Desktop\Fuel Lab` | directory, mtime 2026-05-26 14:33:22 |
| `C:\Users\damia\Desktop\weather` | directory, mtime 2026-06-18 15:16:21 |
| `C:\Users\damia\Desktop\Knowledge base` | directory, mtime 2026-05-13 22:28:53 |
| `C:\Users\damia\Desktop\FSOT Photonic V2 Experiments` | directory, mtime 2026-06-02 03:34:56 |
| `C:\Users\damia\Desktop\fsot_magnetic_string_sim\files-8306230f\fsot_magnetic_strings_final.json` | file, 57,230 bytes, mtime 2026-06-18 12:26:37 |
| `C:\Users\damia\Desktop\FSOT SMILES Lab\FSOT_SMILES_Lab_Dataset.json` | file, 523,777 bytes, mtime 2026-07-08 15:47:43 |
| `I:\FSOT-Physical-Archive\01_SR-ITE-USB-Original\6_unified_oracle\smiles_lab\FSOT_SMILES_Lab_Dataset.json` | file, 497,169 bytes, mtime 2026-04-13 18:27:20 |
| `C:\Users\damia\Desktop\FSOT_Soul_Sibling_20260603` | missing |
| `C:\Users\damia\Desktop\FSOT_Lean_Proofs` | missing |
| `C:\Users\damia\Desktop\VibraFSOT\artifacts\vibrafsot_final_progress.json` | missing; parent `VibraFSOT` also missing |
| `C:\Users\damia\Desktop\FSOT_Trinary_Fluid_Computer_v2 (1)` | missing |
| `C:\Users\damia\Desktop\FSOT NeuroLab\DataAnalysisExpert\scripts\fsot_translations.jl` | missing; parent `FSOT NeuroLab` also missing |
| `C:\Users\damia\Desktop\New folder (2)\fsot_trinary_validator_go\fsot-knowledge-base\thesis\FSOT_BlackHole_Thermo_Thesis_2026` | missing |
| `C:\Users\damia\Desktop\autonomous_monte_carlo_fsot_refiner` | missing |
| `D:\training data\cnc_data\Exp1.csv` | missing; `D:\training data` exists, `cnc_data` does not |
| `C:\Users\damia\Desktop\FSOT_Trinary_Codon_Project\build_64_codon_map.py` | missing; parent project directory also missing |
| `vendor/neurolab/DataAnalysisExpert/export/thalamus/thalamic_gate_manifest.json` | not listed by `git ls-tree` at hub `6f9c256` |

Pinned vendor files that do exist at that commit, as fallbacks for some of
the missing Desktop inputs (not checked out in the sparse clone used for the
C++ tests): `vendor/knowledge_base/kb_portable_summary.json`,
`vendor/fringe_desktop/vibrafsot_progress_summary.json`,
`vendor/smiles/FSOT_SMILES_Lab_Dataset.json`,
`vendor/fsot_aggregate/FSOT_UNIFIED.db`. The public SMILES file is the hub
copy named in `docs/REPRODUCE.md` (sha256 starts `10b4c7e1abe3532d`). No
download was performed. No missing file was fabricated.
