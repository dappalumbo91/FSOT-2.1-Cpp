# Rigor audit log

This file records anything discrepant, unreproducible or unusual found while porting. Entries are neutral
and each one gives its evidence (repo @ commit, file:line, value). It **reports only**. Nothing in any
other repo was edited, no frozen value or pin was changed, and theory-level choices are not judged.
A derivation is not called circular or tuned unless the evidence below shows it.

How to read an entry: **Observed** is a fact you can re-run. **Why it matters** says what a skeptical
reader would ask. **Suggested check** is optional work for the owner.

Pins used: authority `vendor/fsot_compute.py` SHA-256 `AEB2AD…` (hub commit d127c07e). Benchmark data
is at hub commit **6f9c2560** (2026-10-01; the authority file is unchanged there). Other repos are at the
commits listed in `docs/TRIT_SPEC.md` §4.

Re-run commands: `python tools/dump_ledger_b_golden.py --hub <hub@6f9c2560>` and
`build/fsot_ledger_b --hub <hub> --golden golden/ledger_b_6f9c2560.tsv` (the C++ port is bit-identical to
the Python, 13,841/13,841 lines).

---

## A. Benchmark gate and Ledger B (hub `scripts/benchmark_margin_lib.py`, `data/*_benchmark.json`)

### A-01 · Most of the gated "scalar" records are Ledger B corrections, where the error is fixed by construction
- **Observed.** There are 478 `*_benchmark.json` files: 477 active, 477 green, 1 excluded
  (`structure_calibration_benchmark.json`). Across them, 183,196 records enter the scalar error gate.
  Of those, 139,400 (76.1 %) have `eval_kind = "fsot_prediction"`, and they store
  `computed = round(m·(1+|S|·f), 6)` (`scripts/fsot_api_predict_lib.py:272,350`). For these records
  `error_pct = |S|·f·100` whatever the measured value is. The gate classifies only
  `eval_kind == "fsot_correction"` as structural (`benchmark_margin_lib.py:216-219`, with the comment
  "c = m(1+|S|ALPHA) is the Ledger B step. It is not a prediction"). The legacy label `fsot_prediction`
  for the same law is not listed, so it falls through to `"scalar"`. In 119 of the 414 files that have
  scalars, more than half of the gated scalars are these records.
- **The hub already discloses the principle.** `data/ledger_b_null_models.json` (hub @ ac1ef731, 2026-09-29)
  reports `beats_identity_cm = false` and `null_identity_cm_error_pct = 0.0`, with the note "B is
  engineering. Do not quote 477/477 as ToE accuracy."
- **Why it matters.** A reader of "477/477 green" will assume each file contains independent predictions.
  For files dominated by `fsot_prediction`, the pass is mostly a property of the c = m(1+|S|f) step.
- **Suggested check.** Treat `fsot_prediction` the same as `fsot_correction` in `classify_record`, then
  re-run `audit_all_benchmark_margins.py` and report how many files still have gated scalars and whether
  they remain green. This repo can compute that from the same code path. It is not changed here.

### A-02 · The stored Ledger B amplitudes are the older per-domain table, not f = ALPHA
- **Observed.** For the 139,400 gated `fsot_prediction` records, f was inferred as `(c/m − 1)/|S|` from the
  stored `computed`, `measured` and `fsot_scalar`. The most common values are
  0.0003 (43,429), 0.0002 (27,337), 0.00025 (25,589), 0.001 (6,577), 0.0005 (3,739), 0.0008 (2,738),
  0.0004 (1,678). The live law uses f = ALPHA = 8.0829374141404044e−4 for every domain.
- **Why it matters.** The stored records are not reproducible from the pinned authority. The per-domain f
  values are decimal choices, so they would need their own derivation or a documented history.

### A-03 · Only about 10 % of routed Ledger B records match the live AEB2AD law
- **Observed.** 140,088 Ledger B records (`fsot_prediction`/`fsot_correction`) are routed to one of the 35
  core domains. Another 7,168 have no routable `fsot_domain`. Re-scoring with c = m(1+|S|·ALPHA), with S
  from AEB2AD, gives: stored `computed` equal to `round(c,6|4)`: **14,634** (10.4 %); stored
  `fsot_scalar` equal to `round(S,6)`: **3,667**; stored `error_pct` equal: **4,223**. Per-file counts
  and the maximum relative deviation are in `golden/ledger_b_6f9c2560.tsv` (`lb_*` rows).
- **Why it matters.** Most of the benchmark corpus predates the current pin (stale stored values).
  The gate reads the stored numbers (A-05), so the green status is that of the older law.

### A-04 · The gate trusts the stored `error_pct` and never recomputes it from `computed`/`measured`
- **Observed.** `scalar_metrics` reads `e = r.get("error_pct")` (`benchmark_margin_lib.py:341`) and gates on
  it. In **6,242** gated scalars spread over **40 files**, recomputing |c−m|/|m| from the stored fields gives
  more than 0.5 % while the stored `error_pct` is at most 0.5 %. The largest groups are
  `desi_edr_fits_residual_benchmark.json` (4,734) and `nasa_donki_solar_panel_benchmark.json` (1,425).
  Examples:
  - DONKI `goes_flux`: measured 8.450673703919165e−06, stored computed 8e−06 (−5.3 %), stored error_pct 0.020755.
  - DESI `redshift_z` (same mechanism; this example is −0.19 %, and 4,734 records in the file exceed 0.5 %):
    measured 8.516011942923869e−05, computed 8.5e−05, error_pct 0.010049.
  - `engineering_hardware_code_spine_benchmark.json` `bus_coherence`: computed 0.14590, measured 0.0088587,
    error_pct 0.0 (recomputed: 1,547 %).
  The first two follow from `round(computed, 6)` being an **absolute** 6-decimal rounding: values below
  about 1e−4 lose almost all their significant digits, while error_pct was taken before rounding. This
  also explains why 706 DONKI records "imply" f = −1.92728.
- **Why it matters.** The stored fields are internally inconsistent, and the gate cannot see it.
- **Suggested check.** Round to significant digits (e.g. `float(f"{c:.12g}")`). Add a gate assertion that
  `error_pct` is reproducible from the stored fields within the display precision, or record why not
  (σ-distance rows store a different unit; only 5 of the 6,242 have `sigma` set).

### A-05 · A benchmark file contains non-standard JSON tokens
- **Observed.** `data/frb_orifice_outgassing_benchmark.json` (hub @ 6f9c2560) contains 257 bare `NaN` tokens,
  for example line 785: `"puncture_energy": NaN`. Python's `json` accepts them. RFC 8259 parsers
  (nlohmann, JavaScript `JSON.parse`, Go, Rust serde) reject the whole file. The C++ port emulates
  Python here (`include/fsot/host/pyjson.hpp::loads`). Without that, this file silently drops from the audit
  (476 active instead of 477).
- **Suggested check.** Write `null` (or a string sentinel) with `allow_nan=False` in the writers.

## B. Authority `vendor/fsot_compute.py` (AEB2AD)

### B-01 · Rows counted in the "342/343 within 5 %" summary whose computed value is the target itself
- **Observed.** The following rows have a computed value that is a literal equal to the target:
  `Proton_radius` formula "exact", `mpf("0.8413")` vs `mpf("0.8413")` (line 418); `STDP_Tau_Plus_ms` and
  `STDP_Tau_Minus_ms` 20 vs 20 (924-925); `Metatron_Spheres` 13 vs 13 (881); `Metatron_Pathways` 27 vs 27 (882);
  `Max_Trits` 27 vs 27 (977). The rows `Potts3_beta` = 1/9 (754) and `Quark_condensate` = 1/4 vs 0.250 (757)
  are literal rationals. 1/9 is the known exact 2-D 3-state Potts exponent, so this is a correct identity
  rather than a seed-derived prediction. The golden summary counts 343 rows with targets, of which 342
  are within 5 %.
- **Why it matters.** A headline "N of M within 5 %" should list identity/definition rows separately
  from rows derived from the seeds.

### B-02 · A measured constant is used as an input inside the validation suite
- **Observed.** `a0 = mpf("0.529177")  # Bohr radius in Angstroms` (line 398) enters
  `v = 2*PI*a0*(1 + GAMMA/(PI**2 * E))` (line 412). CODATA 2022 gives a0 = 0.529177210544(82) Å, so the
  literal is truncated at 6 decimals.
- **Why it matters.** Where a "prediction" takes a measured quantity as input, the claim is relative to
  that input. That should be stated, and the truncation sets a precision floor of about 4e−7 relative.

### B-03 · Exponent literals typed as 15-digit decimals in a 50-digit engine
- **Observed.** `GAMMA**mpf("0.333333333333333")` (line 433), `PI**mpf("0.333333333333333")` (436),
  `PHI**mpf("0.333333333333333")` (439), `GAMMA**mpf("0.333333333333333")` (442). Each exponent differs from
  1/3 by 3.3e−16. Every other quantity is evaluated at mp.dps = 50.
- **Why it matters.** It is not stated whether these exponents mean 1/3 (a cube root). If they do, the rows
  carry a 1e−16-level deviation that the 50-digit golden faithfully preserves. The C++ port reproduces the
  literal as written.

### B-04 · The π-identity change to C_EFF and K is disclosed in the authority, but older copies are still in use
- **Observed.** Line 62: `C_EFF = … (1 + (1 / PI**4) * G_CAT / (PI * PHI))  # 3.1  0.01 → π⁻⁴`. Line 72:
  `K = … * (1 - 1 / PI**4)  # 3.11  0.99 → 1−π⁻⁴`. The older authority copy in FSOT-Reality-OS
  (`engine/fsot_compute.py:62`) still has `mpf("0.01")`. FSOT-Quantum `results/HARD_QUESTIONS.md:11` states
  K's closed form as "φ·(γ/e)·√2/ln(π)·99/100" = 0.4202216641606968, under pin D1D38A. The ratio
  K_live/K_old = 0.999731 equals (1−π⁻⁴)/0.99, as expected.
- **Why it matters.** Published reports in other repos quote constants from a different formula. When
  read side by side, they look like disagreement rather than versioning. Cross-repo drift is in TRIT_SPEC T-3/T-4.

### B-05 · Docstring version label
- **Observed.** Line 4: "FSOT 2.0 — Complete Computational Engine (Python / mpmath)". The hub and the
  pin are FSOT 2.1.

### B-06 · Seed literals (checked, consistent)
- `GAMMA` and `G_CAT` (lines 44-45) are typed as 50-digit decimals. Both equal mpmath's `euler` and
  `catalan` to all 50 digits. No discrepancy.

## C. Citations (sample; full pass is planned)

### C-01 · A DOI that does not resolve, although the paper exists
- **Observed.** `docs/OBJECT_SCORING.md:43` (hub @ 9700f9dd) cites `doi:10.1103/PhysRevD.112.083515` together
  with arXiv:2503.14738. Crossref returns 404 and doi.org returns 404. arXiv lists the paper as
  "DESI DR2 Results II", journal_ref *Phys. Rev. D 112, 083515 (2025)*, with registered DOI **10.1103/tr6y-kpc6**.
  APS issues opaque DOIs for 2025 articles. The citation is real, but the DOI string looks constructed
  from the journal reference.
- **Scope.** All 9 unique DOIs in the hub's top two directory levels of Markdown were resolved: 8 resolve.
  The 3 in `docs/THESIS_APPENDIX_XII.md` (lines 9219-9223, 11964) are metadata rows in a data table
  (encyclopedia entries such as "Loot Crates"), not supporting citations. The rest of the hub (deeper
  docs, JSON `reference` fields, paper drafts) is not yet checked. See the next milestone.

## D. Cross-repo constants and pins (details and fixes in `docs/TRIT_SPEC.md` §4)
- **D-01.** FSOT-GPU / FSOT-Quantum / CUDA / quantum.zig use C_EFF 0.9577022026205613, K 0.42022166416069665
  and Θ 0.9174663774653723. AEB2AD gives 0.9577480213378242 / 0.4201087636498879 / 0.9175102712064876.
- **D-02.** FSOT-Reality-OS is pinned to D1D38A (`README.md:8`, `reality_os/core.py:34,43`), with a 530-row
  domain table, and its QEMU serial log shows `collapse_theta = 0.917466377465`.
- **D-03.** FSOT-2.0-code bundles hub authority 9B2450 (hub 2040826b, 2026-07-12).
- **D-04.** The trit layouts disagree (Zig T1 vs code = t+1), and U maps to 0 in Zig but −1 in Rust. See T-1/T-2.

## E. Credibility gaps a skeptical physicist would raise (connective pieces, not errors)
1. **Look-elsewhere / formula multiplicity.** The closed forms combine about 12 seed-derived constants
   (π, e, φ, γ, G, ln π, √2, C_EFF, K, POOF, CHAOS, …) with small integer powers. No count is published of
   how many candidate expressions of comparable complexity were tried or exist per observable. Without that
   count, a 0.1–5 % agreement cannot be assigned a significance. Suggested: enumerate expressions up to the
   same complexity (e.g. ≤ 3 constants, powers −6..6) and report, per observable, the fraction that land
   within the claimed error. That fraction is a p-value proxy. This repo's C++ engine can do the
   enumeration fast.
2. **Uncertainty quantification.** Predictions carry no error bars. The gate compares to rounded targets
   (display precision, `scientific_measurement_lib.py`) or to literature bands. Seeds are exact, but the
   formula choice is a discrete uncertainty (item 1).
3. **Blind / out-of-sample tests.** The hub has preregistration scaffolding (`preregistered_falsifiable`,
   `wa_preregistered`; `docs/CASP_CAMEO_BLIND_PROTOCOL.md`). These rows are excluded from the scalar gate
   (`classify_record` returns structural for them), so the green count contains no held-out prediction.
   A dated, hashed list of predictions made before the measurement, scored separately, is the strongest
   missing piece.
4. **Dimensional analysis.** S is dimensionless. Dimensional observables enter through either the Ledger B
   multiplicative step (c = m·(1+|S|f), which needs m) or through formulas that take a measured constant as
   input (B-02). Which observables are predicted without a measured input of the same dimension is not
   documented.
5. **Baselines.** The hub's own null models (A-01) show Ledger B does not beat c = m. For the closed forms,
   no comparison is published against simple baselines (e.g. the best of N random seed combinations, or
   standard-model values where they exist).
6. **Held-out data and selection.** Benchmark panels are added over time, and the stored values were
   generated by several historical laws (A-02/A-03). Which panels were chosen after inspection, and what
   happens to failing panels, is not recorded in the data. The `AUDIT_EXCLUDED_BENCHMARKS` history is one
   example: one file is excluded, and two were re-included after changes (`fsot_precision_constants.py`
   comment).
7. **Reproducibility of stored numbers.** 90 % of routed Ledger B values do not match the pinned law (A-03),
   and 6,242 gated errors are not reproducible from their own fields (A-04). The pinned code is
   deterministic and this repo reproduces it bit-for-bit. The data files are not reproducible.

## Fixed in C++ (this repo only; the hub, `vendor/fsot_compute.py` and every pin are unchanged)

Each fix keeps a **parity mode**, which is byte-identical to the pinned Python and is what the golden tests
check, and adds a **corrected mode**. Frozen data is never rewritten; corrected results are reported
next to the parity ones.

| Finding | Parity mode (golden-tested) | Corrected mode | Where |
|---|---|---|---|
| A-04 gate trusts stored `error_pct` | `analyze_benchmark(doc, file, lit)` | `analyze_benchmark(..., recompute=true)`: gate error = \|c−m\|/\|m\| from the record's own fields. The stored value is kept only for rows whose error is not relative by design (simulation aggregates, σ-distance rows, adversarial-match rows) or whose fields aren't finite numbers (`stored_only`) | `include/fsot/host/ledger_b.hpp` |
| A-04 emitter `round(c, 6)` | `make_fsot_record(...)` → `round(c,6)` / `round(c,4)` | `make_fsot_record(..., corrected=true)` → `round_sig(c, 12)`, `round_sig(err, 12)` | `include/fsot/host/ledger_a.hpp`, `pyfloat.hpp::round_sig` |
| A-01 corrections counted as predictions | (not separated) | per file and in total: `ledger_b_structural_corrections` (eval_kind `fsot_prediction`/`fsot_correction`, c = m(1+\|S\|α)) vs `genuine_predictions` (all other gated scalars) | `fsot_ledger_b --corrected-out` |
| A-05 NaN tokens | read like Python | same values, plus each file's token counts and first line numbers in the report and on stderr | `pyjson.hpp::loads(text, NonFiniteLog*)` |
| B-01 / B-02 non-predictions | rows unchanged | `fsot_report` tags `[non-prediction: computed=target]` (exact equality at run time) and `[non-prediction: input:a0=0.529177]` (generator taint analysis: any row whose expression depends on a local bound to a decimal literal), and prints the headline with and without them | `apps/fsot_report.cpp`, `tools/gen_closed_forms.py` → `LITERAL_INPUT_ROWS` |
| B-03 truncated exponents | the literal as written | `Engine(Mode::corrected)`: every exponent literal that is a ≥12-digit truncation of p/q (q ≤ 12) is evaluated as p/q (generator emits `xexp(lit, p, q)`) | `include/fsot/engine.hpp`, `closed_forms.gen.inc` |

Trit-format fixes T-1 to T-5 stay as documented in `docs/TRIT_SPEC.md`.

**Results, hub data @ 6f9c2560, pin AEB2AD** (full per-file report: `golden/ledger_b_corrected_6f9c2560.tsv`,
regenerated and diffed in CI):

| Quantity | Parity | Corrected |
|---|---|---|
| Gated scalars above 0.5 % | 0 | 6,378 (in 46 files) |
| Green files (of 477 active) | 477 | 436 |
| Stored `error_pct` disagreeing with its own fields (tolerance 1e−6 + 1e−4·err) | — | 56,804 |
| Scalars gated on the stored value (`stored_only`) | — | 2,607 |
| Ledger B structural corrections among gated scalars | — | 139,400 |
| **Genuine predictions among gated scalars** | — | **43,796** (188 above 0.5 % after recompute) |
| Ledger B records whose error can't be reproduced from the emitted `computed` | 47,994 of 140,088 (`round(c,6)`) | 0 (`round_sig(c,12)`) |
| Non-standard JSON tokens | 257 NaN in 1 file, read silently | same, logged (first at line 785) |

The A-04 entry above gives 6,242 records / 40 files from an earlier one-off Python count. That count used
its own record selection (stored ≤ 0.5 % and recomputed > 0.5 %). The 6,378 / 46 here comes from the C++
rule in the table above, applied to every gated scalar. Both use the same stored fields.

Closed forms (`fsot_report`, mp169):
- 343 rows have targets and 342 are within 5 %.
- The run-time equality rule flags **20** rows whose computed value equals the target exactly: the six named in B-01 (`Proton_radius`, `STDP_Tau_Plus_ms`, `STDP_Tau_Minus_ms`, `Metatron_Spheres`, `Metatron_Pathways`, `Max_Trits`), plus `Richardson_D=25`, `Quark_condensate`, `Mandelbrot_boundary`, `N_Layers`, `N_Lobes`, `N_Columns`, `WM_Capacity`, `N_Attention_Heads`, `N_Drives`, `Binding_Window`, `Seq_Predict_Period`, `Replay_Passes`, `Cross_Opt_QO` and `pH_water`.
- Taint analysis flags **1** row with a measured input (`DNA_base_pair`, a0).
- Excluding these 21 rows: **321 of 322** are within 5 %.
- Some flagged rows are correct identities, not errors (e.g. (25/25)^0.2 = 1). The flag means only "not a prediction derived from the seeds".
- Corrected mode changes **11** rows. The largest relative shift is 5.9e−11 (`Chain_consistency_%`); the lepton mass ratios and `CMB_tau` shift by 1.8e−13 to 3.4e−13; the other seven by under 3e−16. No row crosses a 5 % boundary.

## F. This repo's own known limitations
- The Ledger B port emulates Python `str.lower()` only for ASCII and Greek Δ/Γ
  (`include/fsot/host/ledger_b.hpp::normalize_biochem_text`). The golden test passes at 6f9c2560. A future
  record with other non-ASCII uppercase letters in biochem name fields could diverge, and the CI golden
  diff would catch it.
- `BTFloat` division is faithfully rounded, not correctly rounded (±1 ulp). + − × are correctly rounded.
