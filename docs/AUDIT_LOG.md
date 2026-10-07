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

## C. Citations (full pass: `tools/check_citations.py`, results in `audit/citations.tsv` and `audit/citations_summary.json`)

**Scope.** At hub 6f9c2560:
- Text docs: `docs/`, `papers/`, `predictions/`, `results/*.md` and the root `*.md`.
- Every `data/*.json`, scanned line by line.
- Distinct identifiers were resolved on 2026-10-01 (ET):
  - DOIs via the doi.org handle API, then Crossref or DataCite for metadata.
  - arXiv ids via the export API.
  - URLs by HTTP status from the box.
- Rerun with the same command. The cache in `audit/.citation_cache.json` makes reruns cheap.

| Identifier | Occurrences | Distinct | Resolve | Fail |
|---|---|---|---|---|
| DOI | 557 | 117 | 115 | 2 |
| arXiv | 543 | 14 | 14 | 0 |
| URL (docs + citation-like JSON fields) | 2,467 | 534 | 203 OK, 9 blocked/auth | 322 with HTTP ≥ 400 |

Many DOIs in `data/` are scored panel items, not citations (e.g. `crossref_scholarly_panel_benchmark.json`
`name` fields). So the context check (resolved title vs surrounding text) is only meaningful for the
physics references. A manual pass over those (e.g. arXiv 1111.2048, 1710.11129, 2503.14452, 2505.21476,
2007.06422, 2410.05380) found the resolved titles consistent with what they are cited for.

### C-01 · A DOI that does not resolve, although the paper exists
- **Observed.** `docs/OBJECT_SCORING.md:43` (hub @ 9700f9dd) cites `doi:10.1103/PhysRevD.112.083515` together
  with arXiv:2503.14738. Crossref returns 404 and doi.org returns 404. arXiv lists the paper as
  "DESI DR2 Results II", journal_ref *Phys. Rev. D 112, 083515 (2025)*, with registered DOI **10.1103/tr6y-kpc6**.
  APS issues opaque DOIs for 2025 articles. The citation is real, but the DOI string looks constructed
  from the journal reference.
- **Status.** Still present at 6f9c2560, confirmed by the full pass above.


### C-02 · A second DOI that does not resolve
- **Observed.** `data/toe_contested_sector_refresh.json:335` and `:592` give `"url": "https://doi.org/10.1152/physrev.00019.2014"` next to
  `"reference": "Human brain metabolic power (physiology)"`. The doi.org handle API returns responseCode 100
  (not found). The prefix 10.1152 belongs to the American Physiological Society (Physiological Reviews).
  The intended article wasn't identified.

### C-03 · Self-links into the hub that 404
- **Observed.** 168 distinct `github.com/dappalumbo91/FSOT-2.1-Lean/...` links (372 occurrences) return HTTP 404 at main.
  Most omit the `data/` folder, e.g. `.../tree/main/acoustic_resonance_materials_benchmark.json`; the file is
  `data/acoustic_resonance_materials_benchmark.json`.
- A further 55 distinct links embed local Windows paths, e.g.
  `.../tree/main/C:/Users/damia/Desktop/FSOT-2.1-Lean/data/dark_energy_cpl_reference.json` and
  `.../tree/main/G:/FSOT-PublicData/...`.
- `.../releases/tag/fsot-monograph-v1` also returns 404.
- The occurrence list is in `audit/citations.tsv` (`self_link`, `self_link_with_local_windows_path`).

### C-04 · Most citation fields carry no resolvable identifier
- **Observed.** JSON keys matching reference/citation/doi/literature hold 5,212 string values. 640 of them (12 %)
  contain a DOI, arXiv id or URL. Of the 560 distinct values, 9 do.
- The most frequent values are free text, e.g. `"MAST CAOM cone"` (485 occurrences), `"CRC Handbook"`, `"NIST / CRC"`,
  `"Planck2018"`.
- Of the remaining web references, 88 distinct URLs returned HTTP ≥ 400 and 5 were blocked or required auth.
  API endpoints and URL templates are counted separately (43) and are not citations.
- **Why it matters.** A reader can't check a value against its source without an edition, table or identifier.

## G. Ledger A, freezes and look-elsewhere (milestone 2)

### G-01 · A mathematical constant is labelled FORECAST
- **Observed.** `predictions/LEDGER_A_FREEZE.yaml:29-31`: `First_Riemann_zero`, kind `FORECAST`, expression
  `e/gamma**3`, kill band "If tabulated Im(rho1) leaves [14.13, 14.14]". Im(ρ₁) = 14.134725… is a fixed
  mathematical constant, computed to many digits and not subject to future measurement. The authority row
  is `vendor/fsot_compute.py:765` (target `mpf("14.135")`).

### G-02 · m_μ/m_e uses integer coefficients and a 12-digit exponent
- **Observed.** `vendor/fsot_compute.py:814`: `v3 = (35*PHI**(-5) + 145) * E**mpf("0.333333333333")`. The coefficients 35
  and 145 aren't derived in the file. The exponent is 1/3 truncated at 12 digits (rows 812 and 987 likewise).
- The C++ corrected mode (see "Fixed in C++") evaluates the exponent as 1/3. m_mu/m_e then moves by 3.3e−13
  relative, which is below the 1.4e−6 error against the anchor.

### G-03 · Ledger A anchors are literature values written into the code
- **Observed.** `scripts/fsot_ledger_a_lib.py` carries the 21 anchors as literals, e.g. T_CMB 2.72548, H0 67.4,
  1/α 137.036 (`include/fsot/ledger_a.gen.inc` mirrors them with their `anchor_source` strings).
- These are rounded values. CODATA 2022 gives 1/α = 137.035999177(21), for example. The kill bands are wider than the
  measurement uncertainties by orders of magnitude: [136.9, 137.2] for 1/α, and [−1.05, −0.60] for w_a.
- The look-elsewhere count (G-05) shows these bands contain 10²–10⁵ simple seed monomials.

### G-04 · Freezes: what is hashed, what is dated, what git shows
- **Observed (`golden/tier_evidence_6f9c2560.json`):**
  - **Domain-table freeze.** The hash is re-derived exactly. The file claims freeze date 2026-09-14, but the hash `8e30e85e` is
    already in git at `3c74a18` (2026-09-11, pin FE23A2).
  - **Ledger A freeze.** Not hashed.
  - **ToE prereg freeze.** Hashed, but at pin D1D38A. It lists `PRED-wa` = −1.018, while Ledger A's `Dark_energy_wa` value is −0.80811
    (`predictions/toe_prereg_freeze.json:24`, `LEDGER_A_FREEZE.yaml` `Dark_energy_wa`).
  - **Prereg manifest.** Dated `registered_at: "2026-07-10"`, but first committed on 2026-08-06 (`7f29b18`), and it carries no hash.
- **Why it matters.** Under the evidence-tier rules (docs/EVIDENCE_TIERS.md), no gated record is TIER 3 and only 3 are TIER 2.

### G-05 · Look-elsewhere: how many seed formulas match as well
- **Observed (`docs/LOOK_ELSEWHERE.md`, `audit/look_elsewhere.tsv`).** For 325 of 343 targets, a monomial grammar of about 4 million seed formulas contains at least one value as close as the FSOT expression. The median is 66 such values. For T_CMB the count (196) equals the density expectation (195). inv_alpha_em and m_mu_over_m_e have none in that grammar (expected about 0.5).
- **Why it matters.** Closeness alone is not evidence when the formula space is large. The grammar here is a lower bound on the space FSOT expressions come from.

## D. Cross-repo constants and pins (details and fixes in `docs/TRIT_SPEC.md` §4)
- **D-01.** FSOT-GPU / FSOT-Quantum / CUDA / quantum.zig use C_EFF 0.9577022026205613, K 0.42022166416069665
  and Θ 0.9174663774653723. AEB2AD gives 0.9577480213378242 / 0.4201087636498879 / 0.9175102712064876.
- **D-02.** FSOT-Reality-OS is pinned to D1D38A (`README.md:8`, `reality_os/core.py:34,43`), with a 530-row
  domain table, and its QEMU serial log shows `collapse_theta = 0.917466377465`.
- **D-03.** FSOT-2.0-code bundles hub authority 9B2450 (hub 2040826b, 2026-07-12).
- **D-04.** The trit layouts disagree (Zig T1 vs code = t+1), and U maps to 0 in Zig but −1 in Rust. See T-1/T-2.
- **Status (Milestone 3):** T-1/T-2 applied (Genetics, neuron-zig, GPU, Quantum), D-01 applied in FSOT-GPU only. Quantum, Reality-OS and the Genetics Zig K stay at D1D38A because their pins were not changed. See `docs/TRIT_SPEC.md` §4a.

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

## H. Precision forensics, 2026-10-02 (where the sub-sigma precision went)

Method: every physics row was rerun under each of the five hub pins between 2026-08-04 and 2026-09-14
(`tools/pin_lineage.py` → `reference/pin_lineage_2026-10-02.tsv`). The 29 hub `scripts/*_seed_check.py` committed
2026-09-29 were rerun unchanged (`tools/dump_seed_leaves_golden.py`). Every number was then scored with one gate,
z = |value − central|/σ ≤ 1 (`include/fsot/host/precision_gate.hpp`), against one verified reference table
(`reference/published_2026-10-02.tsv`; `tools/check_references.py` checks each entry against committed PDG 2024 / CODATA 2022 /
AME2020 evidence). The full table is in `docs/PRECISION_REPORT.md`. Nothing in the hub, `vendor/` or any pin was edited.

### H-01 · The C++ verification never contained Damian's sub-sigma leaves (main cause)
The 50 hub seed leaves (29 scripts, all committed 2026-09-29, documented in hub `docs/TOE_ACCURACY_GOALS.md`) were not in the C++ port.
They are α⁻¹, g_e, m_e, the Rydberg family, m_p, m_n, G, g_p, m_μ, u, M(¹²C), Z, W, W/Z, H, τ, r_p, π±, K±, D±, m_c/m_b, m_t/m_W,
ŝ²_Z, Δm²₃₂, ⁴He and ³H bindings, and the nine CKM magnitudes. The port covered only `vendor/fsot_compute.py`. So the C++
"verification" scored the older pin closed forms against the pins' own targets with a 2 %/5 % relative check. Examples: 1/α_em pin row
137.0361976 (z = 9447) where the hub leaf gives 137.035999166 (z = 0.53); |V_us| 0.2296 (z = 6.73) where the leaf gives 0.225150 (z = 0.21);
M_W/M_Z 0.87537 (z = 39.9) where the leaf gives 0.881358 (z = 0.011). The hub itself did not regress: the seed scripts, `vendor/fsot_compute.py`
and `vendor/fsot_seed_flavor.py` are unchanged since 09-29, 09-14 and 09-17. **Fixed here:** `include/fsot/host/seed_leaves.hpp` ports all 50
leaves (mp169; CKM in IEEE double). `tests/test_seed_leaves.cpp` checks them against the hub's own printed values (worst relative 2.2e-48; CKM 9/9 bit-identical).
CI regenerates that golden from the hub scripts.

### H-02 · Stale or unsourced targets inside the pin were being used as the measurement
The pin's `measured` fields are frozen and stay untouched. They are no longer used as the reference. Stale ones found include:
sin²θ_W 0.23122 (LHC-only, not PDG ŝ²_Z 0.23129(4)); r_p 0.8414 (CODATA 2018); m_τ/m_e 3477.48 (the formula's own rounded value);
m_c/m_b 0.291 (own anchor; PDG 2024 ratio 0.30433(121)); 1/α_em 137.036 (rounded); m_n−m_p 1.29333 (rounded, 6.6 σ off CODATA 2022);
μ_p 2.79285 (rounded, 3240 σ); m_μ/m_e 206.768 (rounded, 61 σ); ⁴He 28.3, ³H 8.482 (rounded); |V_ud| 0.9737 and |V_cd| 0.221 (4–6 σ off the 2024 fit);
α_s 0.1179 (PDG 2022). Unsourced: m_π/m_p 0.14446 matches neither π±/p (0.148753) nor π⁰/p (0.143855). Γ_Z/M_Z 0.02749 against PDG
2.4955/91.1880 = 0.027367(25). Δm²₂₁/Δm²₃₂ 0.0295 against PDG 2024 0.03067(81). **Fixed here:** one cited reference table, verified against evidence.

### H-03 · `|V_cs|` alias in hub `vendor/fsot_seed_flavor.py`
`seed_ckm_magnitudes()` returns `"V_cs": v_ud`. This has been present since hub fb6c8155 (2026-08-03, "Close CKM/flavor residuals"). Any consumer of the raw dict
gets |V_cs| = |V_ud| = 0.97432, and the second CKM row then fails to close (Σ = 1.0018). `ckm_magnitude_seed_check.py` and the review script override it with
√(1 − λ² − A²λ⁴) = 0.973423 (z = 0.42). The C++ uses the override. The hub file is not ours to edit, so a Lean-side prompt was written for Damian's Grok Build agent.

### H-04 · Re-pin regressions (deliberate theory changes; not reverted)
Values that passed z ≤ 1 under an earlier pin and fail under AEB2AD (scored against the same 2024 references):
|V_us| 0.758 → 6.73, M_W/M_Z 1.05 → 39.9 and m_H/m_W 0.96 → 5.01, all at 3090BC → FE23A2 (hub 3c74a180, 2026-09-11, "Derive D_eff from nest
generations", Quantum_Mechanics D 6 → 5). |V_ub| went 0.974 → 2.10 at D1D38A → 3090BC (ba6a8288, 2026-09-11, "Replace decimal knobs with π
identities; f_domain = ALPHA"). Rows that still pass but lost margin include Ω_Λ (0.044 → 0.32), σ₈ (0.010 → 0.44) and Ω_DM h² (0.0006 → 0.49).
Under the hard rules pins are never edited. These are listed as theory decisions for Damian. |V_us|, M_W/M_Z and |V_ub| are now covered by
the hub leaves (H-01). m_H/m_W has no committed leaf, so it remains a scored miss.

### H-05 · fsot_scalar 0.886264 vs 0.887330 is a pin difference, not a bug
0.88626405664670 is the High_Energy_Physics domain scalar under pin D1D38A. 0.887329522 is the same scalar under AEB2AD (D = 6, hits = 1,
look 1 − POOF/π). The WSL runner regenerated data JSONs under AEB2AD (never pushed), so the two values come from two pins. No action.

### H-06 · Hub `charm_bottom_seed_check.py` uses σ(m_c) = 0.0028, σ(m_b) = 0.004
PDG 2024 prints m_c = 1.2730 ± 0.0046 GeV and m_b = 4.183 ± 0.007 GeV (`reference/evidence/pdg2024_extracts.tsv`). The smaller bars are not in
PDG 2024 (suspected AI-introduced or stale). With the printed bars the leaf is z = 0.12 instead of 0.20, so it still passes.

### H-07 · Hub K± bar 0.013 MeV vs PDG 2024 0.015 MeV (S = 2.8)
The hub average is z = 0.247 against ±0.013. Against the printed ±0.015 it is z = 0.214. It passes either way.

### H-08 · Reference-value discrepancies found while building the table
- W mass: the PDG Python API sqlite (pdg 0.1.4, 2024 file) returns 80.377 ± 0.012. The printed 2024 Summary Table says 80.3692 ± 0.0133.
  The printed table is cited.
- Proton mass: PDG 2024 reprints 938.27208816 (CODATA 2018). CODATA 2022 938.27208943(29) is used.
- Δm²₃₂: the hub leaf uses 2.438e-3 (NuFIT / PDG 2026 listing). PDG 2024 prints 2.455 ± 0.028 e-3 (normal order). The leaf passes both (z 0.29 / 0.39).
- D/H: PDG 2024 BBN review Eq. (24.2) 25.47 ± 0.29 (S-scaled). The unscaled 0.25 appears in the text.
- m_τ/m_e: CODATA 2022 3477.23(23) is built on the older τ mass. The table uses PDG 2024 m_τ over CODATA m_e, 3477.365(176), as the hub does.
  Against CODATA's ratio the leaf is z = 1.20.

### H-09 · Naming clash: `alpha_FSOT` in the overnight review scripts
`fsot_precision_kill.py` uses `alpha_FSOT = 1/(φG/C_factor)³ = 1/136.827`. That is neither the pin's `ALPHA` = 8.08e-4 (`validation_suite|alpha_FSOT`)
nor the α⁻¹ leaf 137.035999166. Anyone reading "alpha_FSOT" across the two files would conflate three numbers. The refinement freeze spells it α_seed.

### H-10 · Rounded "measured" values in hub `data/pdg_particle_properties_benchmark.json`
Examples: electron 0.511, proton 938.272, neutron 939.565 MeV. A z or ppm against these rounded figures says nothing about sub-ppm leaves. The C++ gate
does not use them.

### H-11 · Overnight runner input substitution
The WSL runner's `sitecustomize.py` hook remapped missing Desktop projects to the precursor tree on G:. It ran with FSOT_ALLOW_NON_ARCHIVE=1 and
finished with lean_build_ok = false. Outputs from that run (regenerated Priors, data JSONs) are not evidence. None were brought into this repo.

### H-12 · Suspected AI hallucinations / unsupported changes (overnight and porting sessions)
- Post-hoc route changes presented as fixes: |V_us| → Chemistry, the min-z route selector, the α/(π√2) first-row deficit term and the |V_ud| exemption rule.
  These are legitimate refinements but untested. They are frozen as `frozen-pending` in `docs/freezes/REFINEMENTS_2026-10-02.md` and not scored.
- The σ values in H-06 and H-07 that do not match the printed PDG 2024 tables.
- The `"V_cs": v_ud` alias (H-03).
- The `alpha_FSOT` name reused for a different number (H-09).
- The PDG API value for M_W (H-08), which an automated reference fetch would have used silently.

### H-13 · H0 was scored against the wrong channel (bug fix, 2026-10-02b F1)
The scored H0 row used Planck 2018 CMB-only 67.4 ± 0.5 (PDG 2024 astrophysical constants), which gave z = 2.09. Damian decided the physical channel on
2026-09-15 (hub `vendor/fsot_seed_flavor.py` `seed_h0_global`, commit 00ca7f1f): "Global CMB-background H0 … Not SH0ES. Not Planck-2018-only 67.4. Live
CMB+BAO class is P-ACT-LB2 … 68.43±0.27". That value is verified against the arXiv:2503.14452 abstract ("Including the DESI DR2 data tightens the Hubble constant
to H0 = 68.43 ± 0.27 km/s/Mpc"; evidence `reference/evidence/arxiv_extracts.tsv`). The formula and pin are unchanged: 68.444996, z = **0.056**. Planck (z 2.09) and SH0ES
73.0 ± 1.0 (PDG 2024 cosmological parameters, z 4.56) are printed as `rec = -` alternates. Held-out results: P-ACT-LB with DESI DR1 68.22 ± 0.36 gives z 0.62 (pass), and P-ACT alone
67.62 ± 0.50 gives z 1.65 (fail). The pin's own target of 67.4 stays frozen.

### H-14 · α_s(M_Z): the wrong object was scored (bug fix, 2026-10-02b F2)
PDG 2024 α_s(M_Z²) = 0.1180 ± 0.0009 is MS-bar at μ = M_Z with five flavours (rev-qcd eq. 9.25). The wave1 pin row 1/(eπ) = 0.117100 (z 1.0004) is, in Damian's words,
"a different object". Hub `seed_alpha_s_MZ` (commit 8760d403, 2026-08-03) defines the QCD-process coupling as 2(POOF/ψ_con)². The scored row now uses that seed (new
map route `seed`, mp169): 0.1179088, z = **0.10**. The pin row is kept as a `rec = -` alternate. Held-out checks, which are the two inputs of the PDG average and so correlated
with it: without lattice 0.1175 ± 0.0010 gives z 0.41; FLAG 2021 0.1184 ± 0.0008 gives z 0.61. This value was not computed in this repo before the freeze commit ce282e0.

### H-15 · Δm²₂₁/Δm²₃₂: the label and the target disagree (hub item, not changed)
The pin target 0.0295 is the Δm²₂₁/Δm²₃₁ convention. With PDG 2024 inputs, 21/31 = 0.02976 ± 0.00076. The row label and the 2026-09-29 atmospheric script say Δm²₃₂,
but `seed_dm2()` names the same formula `dm2_31_abs`. The C++ keeps the latest explicit label (32), so this remains a formula item. Frozen-pending candidate C-DM-1
(seed Δm²₂₁ over the committed atmospheric leaf) gives z 0.14 against 21/32. Against 21/31 it gives z 1.34. Damian needs to decide which label is right (Grok Build prompt 2026-10-02b).

### H-16 · The seven Ledger B "formula misses" are data handling (diagnosis; the Ledger B gate and its data are unchanged)
- `tau_reion` (dark sector #7): `error_pct` 0.006335 was computed against Planck 0.0544, but `measured` holds 0.0561 (Planck 2018 Table 2, TT,TE,EE+lowE+lensing+BAO,
  ± 0.0071, arXiv:1807.06209). Computed value 0.0543966: z 0.24 against 0.0561(71), 0.0005 against 0.0544(73), 0.057 against PDG 0.054(7).
- `D_H_ratio` (#8): `error_pct` 0.090986 was computed against PDG 2.547e-5, but `measured` holds Cooke et al. 2018, 2.527(30)e-5 (arXiv:1710.11129). z 0.59 against Cooke,
  0.08 against PDG.
- `Mean_dependency_length_EN` ×3: `error_pct` matches measured = 2.4, but `measured` holds 2.3. The hub row cites no published source. Against the row's own 8.7 % band (σ = 0.2),
  z = 0.50.
- `FRB20121102A` / `FRB20200929C` `frb_p34_periodicity`: "measured" 1/1020 and 1/980 Hz sit symmetrically ±2 % around the computed 1/1000 Hz. The cited "Fonseca et al.
  2022; contested" reports no such periodicity. The CHIME/FRB 2023 repeater paper (doi:10.3847/1538-4357/acc6c1) reports that its periodicity search found no detections, and FRB 20121102A's published
  periodicity is ~157 days (Rajwade et al. 2020). The values are unsupported and cannot be put through a z gate. Suspected unsupported data (hub item).
Under the z gate, 5 of the 7 pass. The 0.5 % Ledger B gate is a tolerance and was not touched, so those rows still show as misses there.

### H-17 · Units and definitions checked, no bug
- μ_d is in nuclear magnetons, and CODATA 2022 μ_d/μ_N = 0.8574382335(22) is the right quantity (not μ_d/μ_B). The z of 2.1e4 is a real 54.6 ppm miss against a 2.6 ppb σ.
- T_CMB is in kelvin.
- Γ_Z is the total width. PDG M_Z and Γ_Z are both quoted in the s-dependent Breit-Wigner convention, so their ratio is consistent.
- α_s scheme: see H-14.
- The pole vs MS-bar question does not apply to m_H/m_W: PDG quotes both as pole/physical masses.

### H-18 · 2026-10-02b refinements (frozen-pending; not confirmed)
`docs/freezes/REFINEMENTS_2026-10-02b.{md,json,sha256}` was committed as ce282e0 (2026-10-02 08:22 EDT) before any candidate was evaluated. It holds 7 candidates and N = 420
forms in total (a 104-form look-elsewhere family for each of 4 items), with a-priori rules S1 and S2. Scores are in `audit/refinements_2026-10-02b.tsv`
(`tools/score_refinements_2026_10_02b.py`, hub engine) and in the `refined_*` columns of `audit/precision_2026-10-02.tsv` (C++). The two agree to 15 digits (CTest `refinements_b_crosscheck`).
Passing, frozen-pending: m_H/m_W C-MHW-1 z 0.37 (held-out: m_H/m_Z 0.37, m_H/m_t 0.80); Δm² ratio C-DM-1 z 0.14 (held-out: Δm²₂₁ 0.03); T_CMB C-TCMB z 0.999 (no held-out;
11.5 % of its family hits by chance). Failing under the frozen rule, so these stay open: Γ_Z/M_Z C-GZ z 5.44, deuteron binding C-BD z 590, μ_d C-MUD z 1.8e5.

### H-19 · 2026-10-02c train/test search: no class-level rule accepted
Protocol 44adf76 (08:41:19 EDT) was committed before training; the training freeze dd85c22 (08:42:21 EDT) was committed before scoring. 539 patterns were examined across 5 classes (W, M, B1, B2, T), and none met
the pre-stated criterion (sign n/n, LOO z ≤ 1 for ≥ 2/3, n ≥ 3, selection ≠ none). Targets Γ_Z/M_Z, deuteron B and μ_d stay open and unchanged. Held-out: R_ell z 0.33, Y_p z 0.006, He-3 (Ledger B) z 5.3e4.
Details are in docs/PRECISION_REPORT.md §2026-10-02c.

### H-20 · Nuclear dressings do not transfer
The He-4 leaf dressing ×(1−α²(π+P_base)) and the H-3 leaf dressing ×(1+yy·γ·ψ_con²) are item-specific: swapped, they give z 9414 and 2853. The Ledger B B/A residuals vs AME2020 change sign (7/13)
at the 1e-3 level, and no scaling in 1, A, A^-1/3 or B/A predicts them leave-one-out. A deuteron fix needs a theory decision; it cannot be learned from the class.

### H-21 · T_CMB polish: neither confirmed nor killed
The thermal-class sign (all bare-high) is opposite to the T_CMB direction. Available checks (the FSOT-internal η/Ω_b-implied T0, and the Noterdaeme 2011 T(z) normalisation) have under 1σ of discriminating power, so the polish stays frozen-pending.

### H-22 · 2026-10-02d: Damian's seed G_F is 17.9x the CODATA value
`seed_vev_GeV()` in hub vendor/fsot_seed_flavor.py returns (theta_S+e^3)/C_factor^6/1000*phi = 58.24 GeV (the docstring states the tree relation v = 2 m_W sin(theta_W)/sqrt(4 pi alpha), but the code returns a different expression). seed_G_F() is not scored in the hub suite.
Every G_F-normalised 02d construction (A1 Gamma_Z, Gamma_W, tau_mu, tau_tau) fails by that factor under the frozen rule. Nothing was re-tuned. The G_F-free A1 content passes: sigma_had0 z 0.29.

### H-23 · Sec. 67 database values vs current fsot_compute constants
For 6 of 11 sec. 67 Nuclear muN entries (#1036 H-2, #1037 He-3, #1038 Li-7, #1039 B-11, #1041 N-14, #1045 P-31), recomputing the formula with the current fsot_compute constants does not reproduce the stored Value. As frozen, the stored Value was used.

### H-24 · 2026-10-02d class search: still no rule
Enlarged widths (n 9) and moments (n 13) classes: 0/2 meet the round-c criterion. 218 patterns. The deuteron stays open. The two-nucleon formula with an external AV18 P_D reproduces the AV18 impulse value only when the CODATA mu_n is used. The FSOT mu_n row (SU(6)) is 2.7 % low.

### H-25 · 2026-10-02e: seed_vev_GeV bug fixed in this repo (documented relation); scheme S1 primary
seed_vev_GeV() returns 58.24 GeV, against its own docstring relation v = 2 m_W s_W/sqrt(4 pi alpha). This is an erroneous implementation. This repo implements the documented relation (tools/score_2026_10_02e.py); the hub is not edited.
Under the a-priori primary scheme S1 (on-shell, alpha(0), FSOT-only), G_F is 3.6 % low, which matches the omitted Delta r = 0.03685. Gamma_Z/M_Z z 43, so it is not confirmed.
The secondary scheme S2 (MS-bar s^2, external alpha_hat(M_Z)) gives G_F -0.34 % and Gamma_W z 0.08. The secondary scheme is never confirmed.

### H-26 · 2026-10-02e: alpha_s(m_tau) and BR(tau -> e nu nu) from FSOT inputs pass (frozen-pending)
4-loop running of the seed alpha_s(M_Z), with decoupling at the FSOT m_b and m_c thresholds, gives 0.3134 (PDG 0.314(14), z 0.04). BR(tau -> e nu nu) = 0.17829 (z 0.23).
No FSOT route exists for mu_n, mu_t or f_pi, so these rows (and tau_pi+ and the two-nucleon mu_d) are not constructed.

### H-27 · 2026-10-02f: Delta r from FSOT leaves; G_F -0.66 % (H1), Gamma_Z/M_Z still open
Under DERIVATIONS_2026-10-02f (frozen first), Delta r(H1, FSOT-only) = 0.02962 and Delta r(H2, PDG Delta alpha_had) = 0.03324, against the PDG SM 0.03685. G_F is -0.66 % (H1) and -0.29 % (H2). Gamma_Z/M_Z z 11.2 (H1), 7.2 (H2): not confirmed. Gamma_W z 0.08 (H1), 0.10 (H2), frozen-pending.
The H1 quark loop with constituent m_p/3 light quarks gives Delta alpha_had = 0.02410 (-13 %). The remainder (Hioki non-leading top log + Higgs log + classic one-loop constant) is 0.00295. Two-loop rho^(2) and resummation are omitted.

### H-28 · 2026-10-02f lost-route search: no route for mu_n, mu_t, f_pi, P_D, Delta r, alpha(M_Z)
All 40 dappalumbo91 repositories (every ref, full history, deleted files) were searched. The only finds are older parallel sec. 67 versions in the hub's vendor/cosmology/database copy (5d0d5f31, 2026-07-10): H-2 E/PI (+0.91 %) and He-3 -(E-GAMMA) (+0.63 %). Both fail. The dependent tau_pi+ and two-nucleon mu_d builds are not possible.

### H-29 · 2026-10-02g: effective Z couplings (LEPTOP); pre-declared PDG-input validation failed (+1.92 MeV)
Under DERIVATIONS_2026-10-02g (frozen first, 0eba00a), the LEPTOP construction (hep-ph/9503308) with PDG inputs gives Gamma_Z = 2.49592 GeV against the SM 2.4940 +- 0.0009. That fails the pre-declared criterion, so no round-g row is confirmed. FSOT inputs: Gamma_Z/M_Z z 7.99 (H1), 4.02 (H2), 0.16 (H2c, CODATA G_F, diagnostic). sin2_eff_lept (held-out) z 6.75 (H1). R_b, R_c, sigma_had0 and Gamma_inv are within z 1 under H1 (frozen-pending, unconfirmable).

### H-30 · 2026-10-02h: trace-to-first-break for the 6 misses plus Γ_Z/M_Z and deuteron μ; branches frozen first (eee8141)
Trace tables are in audit/trace_2026-10-02h.tsv; full tables and diagnoses are in PRECISION_REPORT §2026-10-02h. First breaks:
- T_CMB: assembly, −289 ppm (z 1.31).
- Deuteron binding: assembly, −0.71 ppm (z 3.59); no FSOT m_d.
- m_H/m_W: S_quant(1+psi_con), −4477 ppm (z 5.01); caused by hub D_eff 6→5 (3c74a180/FE23A2); the leaf ratio passes.
- Dm2: gamma³Poof, −3.77% (z 1.42); 31-vs-32 object.
- Gamma_Z/M_Z: closed form +4503 ppm (z 4.89; stored target = own output). On the G_F route the first break is Delta alpha_had (−13.4%, z 62).
- Deuteron mu: assembly, −54.6 ppm; no FSOT mu_n or P_D.

Branches:
- GZ-1 (ACFW Delta r + Freitas Gamma_Z): validations V1 and V2 pass. H1 z 3.84 FAIL; H2 z 0.65 (external).
- DM-R1: z 0.32 (decision item).
- T-1: z 45 FAIL.
- MUD-1: FAIL.

No FSOT-native hadronic Delta alpha route exists. Counts unchanged: 85/91 confirmed, 88/91 with frozen-pending.

### H-31 · 2026-10-02i: owner decisions OD-1 (Δm² reference object Δm²31) and OD-2 (Quantum_Mechanics D_eff = 6); gate 87/91
These are owner decisions by Damian Palumbo, dated 2026-10-02 18:10 EDT, and recorded with sha256 in audit/OWNER_DECISIONS_2026-10-02i.md (e023f46) before the rescore.

- **OD-1.** Rationale: the hub seed script names the atmospheric splitting dm2_31, so the record row was compared with the wrong PDG object (Δm²32). New reference: Δm²21/(Δm²32 + Δm²21), NO, PDG 2024 = 0.0297593(765). γ³·Poof unchanged: z 1.422 → 0.317.
- **OD-2.** Rationale: QM D_eff was 6 in pins D1D38A (012e5c64, 2026-08-04) and 3090BC (ba6a8288, 2026-09-11 15:19). Hub 3c74a180 (2026-09-11 15:28, pin FE23A2) replaced every assigned D_eff with the derived nest value, which gives 5 for QM. That moved m_H/m_W from z 0.96 to 5.01. Restoring 6 for QM only gives m_H/m_W z 0.960. Because S_quant is shared, Omega_Lambda (z 0.056) and sigma_8 (z 0.010) also take the D_eff-6 value. Both pass either way.
- **Implementation:** a new gate route `owner` re-evaluates the same Engine with QM D_eff = 6 (S_quant 0.9552893401 vs pinned 0.9501974702). The pinned rows stay with record=0, tagged [OD-superseded]. Pins, vendor and parity goldens are unchanged.
- **Gate:** 87/91 confirmed (85/91 pinned only; 88/91 with frozen-pending C-TCMB).

### H-32 · 2026-10-02i: light-hadron routes (HAD-1 DGG m_rho, HAD-2 duality Delta alpha_had) fail their PDG-input validations; GZ-1 H1-i z 0.68, frozen-pending
Under FREEZE_2026-10-02i (75628a7, before any number):
- **HAD-1** (De Rujula-Georgi-Glashow constituent quark model) gives m_rho = 1111.5 MeV vs 775.26 (+43 %). Validation failed.
- **HAD-2** (quark-hadron duality R-ratio with FSOT thresholds and alpha_s) gives Delta alpha_had = 0.026725 with PDG inputs vs 0.02783 (-4.0 %). The frozen criterion |dev| <= 0.00029 failed.
- **GZ-1 H1-i:** with the FSOT-input HAD-2 value (0.026722, m_B external), Gamma_Z/M_Z = 0.0273494 (z 0.68). It is frozen-pending only, because HAD-2 did not validate; the agreement is partly a cancellation between the -4 % Delta alpha_had and the W-mass offset.
- There is no FSOT-native f_pi, m_rho or Gamma_ee route with current FSOT quantities. Deuteron mu_n beyond SU(6), P_D, MEC and binding stay blocked on g_piNN and f_pi.
- **Counts:** 87/91 confirmed (85 pinned only); 89/91 including frozen-pending.

### H-33 · 2026-10-02i: Windows/MSVC portability (reproduced by Damian on MSVC 19.44); precision report made platform-independent (formatting-only change)
- `tests/test_ternary.cpp`: when `__int128` is absent, the 2-word product check uses `_mul128`/`_umul128` (MSVC x64).
- `tests/test_golden.cpp`: the 80-bit `long double` bar (1e-15) is skipped when `LDBL_MANT_DIG <= DBL_MANT_DIG`.
- `apps/fsot_look_elsewhere.cpp`, `apps/fsot_precision.cpp`: `#define _USE_MATH_DEFINES` before `<cmath>`.
- `apps/fsot_freeze_domain.cpp`: `localtime_s`/`gmtime_s` on `_WIN32`.
- `apps/fsot_precision.cpp` + `include/fsot/host/precision_gate.hpp`:
  - Outputs are opened `"wb"` (LF on every platform).
  - No `long double` and no `%Lg`.
  - References are parsed exactly into mp169. The gate arithmetic (z, rel, ppm and the z ≤ 1 / 2 % comparisons) runs in mp169.
  - The printed values are IEEE doubles (mp169 → 17-significant-digit string → strtod) at the same `%.15g` / `%.4g` / `%.6g` formats.
  - `Score`/`Ref` are now `double`. The gate rule itself (Z_MAX = 1, OLD_REL_PCT = 2) is unchanged.
- **Effect on the Linux golden:** one line changed in each of `audit/precision_2026-10-02.{tsv,md}`, the printed last digit of the non-record row `pin:wave4|mu_p_muN` (2.79285221626412 → 2.79285221626411). It is a formatting-only change: the golden was regenerated, and **no PASS/FAIL changed in any column** (z ≤ 1, 2 %, refined). Counts are unchanged at 87/91 (85/91 pinned only; 88/91 with frozen-pending).
- `.gitattributes` forces LF on checkout. The CI job `build-test-msvc` (windows-latest + vcpkg) is non-blocking until its first green run.
- The Linux paths (`__int128`, 80-bit `long double`, `M_PI`) stay.
- **CTest counts:** 31 Linux / 30 MSVC with `-DFSOT_HUB_DATA` (29/28 before `round_freeze_h`/`round_freeze_i`); 27 / 26 without hub data.

### H-34 · 2026-10-02j: strong-sector walk-down from FSOT's absolute scale; Lambda^(5) from the FSOT alpha_s agrees with FLAG (209.5 vs 213(8) MeV); no FSOT-native f_pi, g_A or g_piNN
Under FREEZE_2026-10-02j (ff259d4, before any number). Trace: audit/trace_2026-10-02j.tsv. Scores: audit/score_2026-10-02j.tsv.
- **Trace:** FSOT's only derived MeV is m_e (h nu_Cs/c^2 exp(...), electroweak/Yukawa physics). m_p/m_e = 6 pi^5 + ... has no term with the size or structure of sigma_piN (4.5-6.5 % of m_p). The pion and kaon leaves are pure numbers read as MeV. FSOT m_s/m_ud = 27.666 vs FLAG 27.227(81) (z 5.4, diagnostic). Correction to the round-i inventory: the Gluon_condensate pin (C_cosm - e^-3 = 0.012833) exists.
- **J-1:** the exact-integral MSbar Lambda with the 4-loop beta was validated with FLAG alpha_s (215.2/299.0/343.2 vs 213/295/338). With FSOT alpha_s and M_Z, Lambda^(5) = 209.5 MeV (z 0.43): agrees, FSOT-native, not a record row. Lambda^(4) 292.5 and Lambda^(3) 336.9 are frozen-pending (external FLAG thresholds). This supersedes H-32's "PDG no longer quotes Lambda^(5)": FLAG 2024 does.
- **J-2a/b** (m_N = 4 pi F_pi, c = 1: -18.8 % / -42.6 %) and **J-3a/b** (g_A 5/3: +30.7 %; MIT bag: -14.7 %) fail validation.
- **J-4 GT** validates (-1.66 %, tol 3 %), but FSOT has no validated F_pi or g_A to feed it.
- **J-5 GMOR** validates (Sigma^1/3 288.8 vs 272(5), tol 10 %). Pin reading (a) 0.25 GeV is frozen-pending (-8.1 %); (b) and (c) fail. GMOR cannot close without an absolute m_ud.
- **Downstream** KSRF/VMD -> Delta alpha_had -> Gamma_Z/M_Z and the deuteron chain were not run (frozen gate).
- **Look-elsewhere:** 14 routes considered / 9 scored. **Counts unchanged:** 87/91 confirmed.

### H-35 · 2026-10-02j: MSVC CI job made blocking after its first green run
- Damian's Grok Build pushed c7b58e1: CMake passes `/utf-8` to MSVC. The 0xC0000409 freeze-verify crash was nlohmann::json throwing type_error.316 on the CP1252 byte 0xB7 (middle dot in 1/(e·π)).
- CI 37075909187 on c7b58e1: `build-test-msvc` succeeded (`100% tests passed out of 26`, no-hub-data configuration), and all Linux jobs were green. Damian reports 30/30 locally with hub data.
- `continue-on-error: true` was removed from `build-test-msvc`, so MSVC is now part of the gate.
- **CTest counts after round j:** 32 Linux / 31 MSVC with `-DFSOT_HUB_DATA`; 27 / 26 without.

### H-36 · 2026-10-02k: theta_S and the MeV-read leaves have no physical tie to the m_e anchor; F_pi and g_piNN obtainable only as hybrids with lattice ratios; downstream not run
Under FREEZE_2026-10-02k (a1a530c, before any number). Trace: audit/trace_2026-10-02k.tsv (61 rows). Scores: audit/score_2026-10-02k.tsv.
- **theta_S:** sin(psi_con eta_eff) with psi_con = 1 - 1/e and eta_eff = 1/(pi-1). It has no known physical counterpart.
- **Unit audit:** pi, K, D, W, Z, H and the light-nucleus bindings are pure numbers read in MeV; r_p in fm, T_CMB in K, H0 in km/s/Mpc, dm2 in eV^2. Only m_e, m_mu, m_tau, m_p and m_n follow the m_e anchor.
- **Missing factor:** tying an MeV-read leaf to the anchor needs 1/m_e[MeV] = 1.95695118 = [1e6 e/(h nu_Cs)]/exp(23.3216). This contains the defined value of e. No pin equals any tested ratio to 1 ppm.
- **Pion lineage (hub git):** e^5 - pi^2, then theta^-4 - theta^2 (a formula-search catalogue), then +alpha/(pi-1), always against the PDG MeV value.
- **Branches:**
  - K-1a F_pi (lattice ratio x FSOT Lambda3) = 91.78 MeV (-0.31 %), HYBRID.
  - K-4 GT g_piNN = 12.92 (-2.3 %), HYBRID with lattice g_A.
  - K-2 Skyrme fails. K-5 GMOR m_ud fails validation (+21 %).
  - D-1 m_rho by lowest-meson dominance fails its 1 % gate (+5.5 %), so Delta alpha_had and Gamma_Z were not run.
  - Deuteron not run (frozen precision gate).
- **m_s/m_ud z 5.4:** the FSOT pair satisfies R and Q; the gap is the precise m_s/m_ud combination (needs m_s/m_d -1.6 % or m_u/m_d 0.484).
- **Cosmology:** the pins are mutually inconsistent at 1-4 %; the T_CMB leaf (z 1.31) is the closest to FIRAS.
- **Look-elsewhere:** 15 routes considered / 8 scored. **Counts unchanged:** 87/91.

### H-37 · 2026-10-02l: hadron derivation branch: LO chiral + Dashen octet predicts held-out K0 to 0.003 %; pi0/eta miss by 3 % (LO limit, validation misses equally); GMOR quark masses within 8 % only as hybrids

Freeze `audit/FREEZE_2026-10-02l.md` was committed (9c6dbbc) before `tools/score_2026_10_02l.py` existed. Built from FSOT inputs: the M_pi+- and M_K+- leaves and the m_u/m_d and m_s/m_d pins.
- Held-out results:
  - K0: 497.597 MeV vs 497.611(13), rel −0.0028 %, z 1.07, agrees.
  - pi0: −3.25 %, fails.
  - eta: +3.29 %, fails.
- GMOR with the lattice-ratio condensate gives m_ud 3.603 and m_s 99.68 MeV (HYBRID, within the 10 % gate).
- r_p = 4 hbar/(m_p c) is a disclosed coincidence and is not counted.
- Downstream not run (frozen gate). Totals unchanged at 87/91. Look-elsewhere: octet 1, condensate 3, r_p 8, D_eff map 3.
- D_eff → unit map (freeze 8e9cdec): 3 families, 0/10 held-out. The required factor is 1.956952 = MeV/(m_e c²) in every domain with MeV leaves (D_eff 5, 6, 12) and changes with the SI unit (fm, K, km/s/Mpc, eV²), not with D_eff or S.

### H-38 · 2026-10-02m: FSOT-only F = m_p/(2√3π) = 86.22 MeV (−0.55 % vs chiral-limit F₀); π⁰ from the DGMLY EM sum rule −0.43 %; K⁰ via Q +0.13 %; η −4.5 % and η′ +18.6 % fail; D_eff/S does not organize the m_e-multiple ratios

Freeze `audit/FREEZE_2026-10-02m.md` was committed (21db984) before `tools/score_2026_10_02m.py`.
- Held-out results:
  - π⁰: 134.397 MeV (FSOT-only chain), −0.43 %.
  - K⁰: 498.272, +0.13 % (Dashen).
  - η: 523.18 (WV hybrid), −4.5 %; its validation fails.
  - η′: 1136.3, +18.6 %.
- M-1: 0/6 for each of three families. Tjon 4.61 misses by +38 %.
- Definition note: the freeze text says "leaf ÷ 1.956952" but defines r as the m_e multiple (leaf × 1.956952); scored as the m_e multiple, with the same verdicts under both readings.
- Downstream not run (g_A has no FSOT form). Totals 87/91. Look-elsewhere: M-1 3+1, M-2a 1×2, M-2b 1×2, M-2c 1, M-3a 1×2.

### H-39 · 2026-10-02n: FSOT-only physical F_π = 90.51 MeV (−1.69 %, l̄₄ = N_c); valence chiral-quark-soliton g_A = 1.178 (−7.7 %, fails 2 %); downstream gated off; deuteron LO radius −22.7 %; reference-leaf D_eff maps fail

Freeze `audit/FREEZE_2026-10-02n.md` (e9b1405) was committed before `tools/score_2026_10_02n.py` and `tools/cqsm_valence.py`.
- N-1b F_π passes the 2 % gate and its validation.
- N-2 g_A fails the 2 % gate (validation −5.6 % passes 10 %). The solver sanity sweep was seen before scoring.
- Δα/Γ_Z chain not run under the frozen gate.
- Look-elsewhere: N-1 2, N-2 1, N-3 1, N-5 2. Totals 87/91.

### H-40 · 2026-10-02o: full-sea chiral quark soliton at M = m_p/3 is unbound (E = 3.41 M); g_A^(0) = 0.742 (−42 %, g_A^(1) excluded), Δ−N 177 MeV (−40 %); OPE deuteron r_d −4.1 %, Q_d −14 %, η −7.3 %; SU(6) μ_n −2.7 %, μ_d +3.8 %; l̄₄ = 2.61 gives F_π −2.3 %

Freeze `audit/FREEZE_2026-10-02o.md` (f393948) was committed before `tools/cqsm_kr.py`, `tools/heavy_2026_10_02o.py` and `tools/score_2026_10_02o.py`.
- Every scored item fails its gate.
- Validations: O-3 Q_d, O-3 η and O-4 pass; O-1 g_A, O-1 Δ−N and O-3 r_d fail.
- Disclosed: two solver bugs, the vacuum subtraction of g_A and an int64 overflow in the Clebsch–Gordan products, were fixed after the freeze and before scoring. The M = 420 sanity values were seen then.
- Δα/Γ_Z chain not run under the frozen gate.
- Look-elsewhere: O-1 1, O-3 3 R values, O-3b 1, O-4 1, O-6 1. Totals 87/91.

### H-41 · 2026-10-02p: g_A with the rotational term = 1.1755 (−7.8 %, fails 2 %); soliton μ_p +17 %, μ_n +31 %; one-loop LσM l̄₄ = 4.66 gives F_π = 92.89 MeV (+0.89 %, agrees); DP χ_top +24 %; T_CMB +0.25 % (z 11)

Freeze `audit/FREEZE_2026-10-02p.md` (98cd271) was committed before `tools/cqsm_rot.py`, `tools/heavy_2026_10_02p.py` and `tools/score_2026_10_02p.py`.
- Disclosed: the μ_V^(0) sign correction was made after the freeze. The heavy JSON is transcribed from the run log because the run was cut by a time limit. Self-consistent profiles did not converge, so DPP is primary.
- Δα/Γ_Z chain not run under the frozen gate. Totals 87/91.

### H-78 · 2026-10-05: the deuteron binding record row is (√e/e+φ)(1+α³·e³/φ⁵) = 2.22456621408218 MeV, z 0.0339; the bare sum stays in the report with record 0; totals 90/91

Freeze `FREEZE_2026-10-02ax` was hashed before the binary was rebuilt. The record id is `leaf:Deuteron_binding_MeV`. Alpha is the inverse-alpha leaf, not the domain constant ALPHA. The piece is the nearest short product of e and φ on the mass-excess α³ quotient, `e³/φ⁵`. The next product, `φ+φ⁻³`, is 1.49118 times farther, and that window holds 53 products. Named seeds in the same print also land inside: α² holds `π⁻⁴`, and α³ holds both `√e` and `φ`. The rounded-total nearest sum `√e+φ⁻⁴` is a different piece, and the mass-excess quotient does not return it. The C++ value is 2.22456621408218 MeV, z 0.0339, 0.006706 ppm. The old row `pin:wave3|Deuteron_binding_MeV` stays at 2.22456464846253, z 3.592, record 0. Its frozen-pending column C-BD stays at z 590.3. The deuteron moment stays `G⁴+Poof`, z 21280. Gate from `fsot_precision`: 90/91 confirmed, 88/91 pinned only, frozen-pending column 90/91. With H0 and τ_n deferred the accounting is 88/89. Pins, `vendor/fsot_compute.py`, and the preregistration were not edited. The Lean engine file stays the bare sum. The soliton profile was not rerun.

### H-79 · 2026-10-05: the deuteron moment record row is (G⁴+Poof)(1+α²(1+1/(4π²))) = 0.857438231894115, z 0.7299; the bare sum stays in the report with record 0; totals 91/91

Freeze `FREEZE_2026-10-02ay` was hashed before the binary was rebuilt. The record id is `leaf:Deuteron_mu_muN`. Alpha is the inverse-alpha leaf, not the domain constant ALPHA. The weight is `1+1/(4π²)`, the same algebra as `1+α²+(α/(2π))²`, the square of the Schwinger denominator. The named-seed window and the short-product windows were already empty. The α² quotient is 1.02536546851 with half-width 4.8185114e-5, and this weight sits inside it. The same-shape siblings sit outside. Two expressions that add a second power also land inside and are not this leaf: `α²+α³(π+γ²)` and `α²+α³(π+1/3)`. `1/3` is not a seed, and `π+γ²` has no magnetic-moment reading. The C++ value is 0.857438231894115, z 0.7299, 0.00187289 ppm, on the low side of CODATA 2022 0.8574382335(22). The old row `pin:wave8|Deuteron_mu_muN` stays at 0.857391418128038, z 21280, record 0. Its frozen-pending column C-MUD stays at z 1.772e+05. Gate from `fsot_precision`: 91/91 confirmed, 89/91 pinned only, frozen-pending column 91/91, 89/91 at 2%. With H0 and τ_n deferred the accounting is 89/89. All rows are 105/131 at z and 123/131 at 2%. Worst ppm on the record set remains `pin:wave8|delta_CP_PMNS` at 34691.3. Pins, `vendor/fsot_compute.py`, and the preregistration were not edited. The Lean engine file stays `G⁴+Poof`. The soliton profile was not rerun.

### H-80 · 2026-10-05: the step-44 angle gap of 0.19380 rad sits in the interior at r = 0.9063/M (0.416 fm); the edge tail is already inside 0.001 rad; totals stay 91/91

Freeze `FREEZE_2026-10-02az` was hashed before the run. One call of `self_consistent_m`, mix 0.2, tol 1e-3, itmax 44, from the same DPP as round av. Steps 0, 39, and 43 reproduced the av gaps 0.17211904981809267, 0.005631712767651509, and 0.005190733171335227. The extra force-balance evaluation reproduced the step-44 gap 0.19379649668786914, E/M 2.215078846931202, valence 0.22688573506889673. The maximum sits at grid bin 245, r = 0.9063180381993936 (r/D = 0.064737). With the round-aq factor that radius is 0.416 fm. The edge remap acts only for r > 0.75 D = 10.5 (4.82 fm). The largest gap in that tail is 1.6519969815439323e-05 rad. Of 1500 bins, 231 exceed 0.05 rad, and all 231 are interior. The tolerance and the mixer were not changed. `cqsm_rot.py` was not edited. The deuteron moment leaf was not edited. The isovector radius stays a separate miss: DPP 1.00445 fm² against 0.82236(201) fm², and the 400-step profile at 1.15018 fm². The M = m_p/3 check stays unstarted. Totals 91/91.

### H-81 · 2026-10-05: the DPP isovector radius at M = m_p/3 is 1.58254 fm²; the sea share falls to 0.254 and the fm radius grows; the mass stays off the record; totals stay 91/91

Freeze `FREEZE_2026-10-02ba` was hashed before the run. AR-2 in `FREEZE_2026-10-02ar` ran only after a converged profile. That profile did not converge, so the check had never started. This freeze lifts that gate and leaves FREEZE ar as it was. One j=0 DPP split, M/m_p = 1/3 exactly, the same x_DPP, mpi/M = 0.44625757, Mpv/M unchanged. No call of `self_consistent_m`. F/M = 0.27566445 is recorded and does not enter the sums. The valence level is 0.2875318049310479. The sums took 21.0 s. I[1] = 4.003549924, I[r²] = 15.91624887, r M² = 3.975534. r_V² = 1.58253501263 fm². The regularised sea holds 0.254371 of I[1], with sea+PV-only r² 2.87198 fm² and valence-only r² 1.14264 fm². PV cancels 85.08% of the bare-sea I[r²]. The committed j=0 DPP at M/m_p = 0.4581682005 is 1.0043547666 fm², sea+PV share 0.31258, sea+PV-only 1.85342 fm², valence-only 0.618261 fm². Holding that shape fixed and changing only the fm factor gives 1.89749019852 fm². The shape ratio of r M² is 0.834015, so the tighter pion cloud does not offset the 1/M² factor. Closeness to 0.82236(201) selects neither mass. M/m_p = 0.4581682005 stays the FREEZE ab diagnostic. Round o / H-40 already has M = m_p/3 unbound at E = 3.41 M on a different basis, and this round leaves that mass off the record. The regulator was left as it was. `cqsm_rot.py` and `rv_2026_10_02aq.py` were not edited. Totals stay 91/91.

### H-82 · 2026-10-05: the diagnostic DPP misses stationarity by 0.17212 rad at 0.183 fm; the sea and the Pauli-Villars sea cancel, and the chiral meson constant shifts the angle by 0.00311 rad; totals stay 91/91

Freeze `FREEZE_2026-10-02bb` was hashed before the run. One evaluation, no mix, on the edge-tailed DPP at the diagnostic mass M/m_p = 0.4581682005. The meson constant c = 4π (m_π/M)² (F/M)² uses the chiral-limit F already in the ag file. The valence, Dirac-sea, and Pauli-Villars pieces sum to the solver force within 3.36e-14 and 5.07e-14. The maximum gap is 0.17211904981809267 rad, the committed step-0 value, at grid bin 161, r = 0.397585/M (r/D = 0.028399, 0.1825 fm). Theta there is −2.91014 and the force balance is −2.73802. The valence level is 0.25878369158. At that bin the scalar densities are valence 3.11941, sea 435.923, PV −432.847, total 6.19582. The pseudoscalar densities are 1.08402, 150.015, −148.476, total 2.62290. c is 0.0532792, which is 0.860% of S, and dropping it moves the angle by 0.00311 rad toward the profile. The bare sea and the PV sea cancel at 99.29% in the scalar channel and 98.97% in the pseudoscalar channel. The sea that remains is 3.07641 (scalar) and 1.53888 (pseudoscalar), the same size as the valence. The labeled step-44 radius r = 0.906318 (bin 245, 0.416 fm) is 0.03172 rad off on this profile, not the 0.194 rad of the iterated profile. NLO F_π was not swapped into c. The regulator was left as it was. Vacuum was not added to the force. `cqsm_rot.py` was not edited. No radius file was written. Totals stay 91/91.

### H-83 · 2026-10-05: the Jarlskog record row is A²λ⁶η̄ from the CKM leaves; the other four rows above a flat 1% stay; totals stay 91/91

Freeze `FREEZE_2026-10-02bc` was hashed before the binary was rebuilt. The record id is `leaf:Jarlskog_J`. λ = POOF(1+η_eff), A = e/(π A_bleed), η̄ = G²K, the same three numbers as the nine CKM magnitude leaves. J = A²λ⁶η̄ = 3.13591416718917×10⁻⁵, z 0.1224 on the high side of PDG 2024 3.12 +0.13/−0.12 ×10⁻⁵, flat error 0.510%. The runner-up A²λ⁶η̄(1−λ² SUCTION) crosses the center and is not installed. The old row `pin:wave4|Jarlskog_J` stays G/π⁹ = 3.07277178666547×10⁻⁵, z 0.3936, record 0. sin²θ₂₃ stays |Chaos|·√e. The flavor seed (e−1)/π is 1.981% from 0.558 and stays off the record. δ_CP stays φ³−1/e. The flavor seed 2eψ_con is 8.08% from 1.19π, farther than the record. N_eff stays P_new·e·π+ln(φ) = 3.04571, and 3+2·POOF·SUCTION = 3.04513. Both sit within 0.06% of the Standard Model value 3.044, and neither is inside 1% of the cosmological central 2.99±0.17. η stays Poof¹¹/(πγ). The temperature record is built from that η, and a move large enough to touch 1% of 6.04×10⁻¹⁰ would shift T_CMB by about ten standard uncertainties. The 2% cut stays 2%. Gate from `fsot_precision`: 91/91 at z, 89/91 at 2%, median ppm 74.13. All rows are 106/132 at z and 124/132 at 2%. Pins, `vendor/fsot_compute.py`, and the Lean engine file were not edited.

### H-84 · 2026-10-05: the step-44 jump is one Pauli-Villars level crossing zero; the physical sea does not cross; totals stay 91/91

Freeze `FREEZE_2026-10-02bd` was hashed before the replay. The az call was run again, mix 0.2, itmax 44. Steps 0, 39, and 43 match the az log. The profile after the step-43 mix reproduces the step-44 gap 0.19379649668783028 rad at grid bin 245, r = 0.9063180381993936. The physical spectrum has no eigenvalue inside 0.05 on either profile. The closest physical level is the valence, 0.227378 before the mix and 0.226886 after it. The Pauli-Villars spectrum has one level inside the window: K = 0, parity +1, state 53. Its energy moves from +4.2858221354148625e-4 to -1.124553440761678e-4. The scalar and pseudoscalar densities of that state at the bin stay 0.6327 and 0.6481. The sea weight flips from +1.15121 to -1.15121. Removing that weight leaves the force angle at -1.91957 before the mix and -1.92013 after it. The background densities at the bin are unchanged, so the jump is the sign flip. No occupation rule was installed. `cqsm_rot.py` was not edited. No radius file was written. Totals stay 91/91.

### H-85 · 2026-10-05: a sign-safe mix still stops on the Pauli-Villars zero; the gap stays 0.005111; no occupation rule is installed; totals stay 91/91

Freeze `FREEZE_2026-10-02be` was hashed before the run. The iteration follows the az walk through the step-43 profile, gap 0.005190733171340223. A mix of 0.2 there changes the sign of the Pauli-Villars K=0, parity +1 level, so the step is shortened. The accepted mixes after that are 0.1, 0.05, 0.00625, 0.0015625, and 0.00078125. At step 48 the gap is 0.005111019560596786 and the valence is 0.22698903834919618. The same Pauli-Villars level sits at +9.908034966363918e-7, and the floor mix 0.2/256 would move it to -1.0943264490984318e-6. The eigenvector overlap is 0.9999999999989702. The physical spectrum's closest level remains the valence. The gap stays about five times the tolerance 1e-3. No smoothing width was introduced. `cqsm_rot.py` was not edited. No radius file was written. Totals stay 91/91.

### H-86 · 2026-10-06: the filled Pauli-Villars weight on the valence partner drives the valence out of the window; the gap does not reach 1e-3; totals stay 91/91

Freeze `FREEZE_2026-10-02bf` was hashed before the run. The partner is the K=0, positive-parity Pauli-Villars state with the largest overlap against the physical valence. On the DPP the overlap is 0.9910746230036664 and the partner energy is 0.034862562998586505. Its weight is -Nc/(2 Mpv) = -1.1512077733650228, with Mpv/M = 1.302979388. The physical spectrum keeps the existing weight. Mix stays 0.2. The step-0 gap is 0.2483291395347873. The valence rises from 0.2587836915798133. At step 16 the gap opens to 3.1408574408447167. At step 44 the valence is 0.9996995195828009, the partner energy is 1.2711786396591473, the overlap is 0.9405169512582116, and the gap is 0.09590009956186785. The next profile has no eigenvalue inside (-1, 1). The partner sign does not change. The rule is not installed. `cqsm_rot.py` was not edited. No radius file was written. Totals stay 91/91.

### H-87 · 2026-10-06: the Higgs/W record row is the leaf quotient; the domain scalar stays at record 0; totals stay 91/91

Freeze `FREEZE_2026-10-02bg` was hashed before the binary was rebuilt. The record id is `leaf:m_H/m_W`. m_H/m_W = leaf m_H_MeV / leaf m_W_MeV, which is (θ_S + e³)/C_factor⁷ over θ_S⁻⁶ C_factor⁻⁴ γ² + e^e. This is C-MHW-1, pre-declared under S1 in REFINEMENTS_2026-10-02b, the same leaf-quotient pattern as m_W/m_Z. The C++ value is 1.55729801381558, z 0.3681, 329.109 ppm, on the low side of PDG 2024 1.55781070360287 ± 0.00139275. The domain scalar `od2:wave3|m_H/m_W` stays 1.55914737159333, z 0.9597, record 0. OD-2 still supplies Omega_Lambda (z 0.05582) and sigma_8 (z 0.01002). The pinned D_eff=5 row stays 1.55083682600647, z 5.007, record 0, and it is no longer the stand-in in the without-OD column. C-MHW-2, 1/(3 P_new (1−C_factor)), sits on the high side of the center and is not installed. The tau/muon wave7 row, the lepton-ratios tau formula, the proton charge-radius leaf, the tau-mass leaf, BR(Z→ee), the top/W leaf, and Ω_b h² were not moved. Gate from `fsot_precision`: 91/91 at z, 89/91 at 2%, median ppm 74.13, worst 34691.3 (δ_CP). All rows are 107/133 at z and 125/133 at 2%. Pinned rows only are 90/91 at z and 88/91 at 2%. Pins, `vendor/fsot_compute.py`, and the Lean engine file were not edited.

### H-88 · 2026-10-06: the KSRF D-wave puts lbar_1 and lbar_2 inside their bars; the gate is not rebuilt

Freeze `FREEZE_2026-10-02bh` was hashed before the score file. lbar_1 and lbar_2 are Pennington and Portoles, Phys. Lett. B 344 (1995) 399, doi:10.1016/0370-2693(94)01551-M, hep-ph/9409426, equations (16), (24) and (27), at lambda = 1, on the frozen KSRF rho and the chiral-limit F. The score is lbar_1 = −0.15209172795246319, z 0.413, and lbar_2 = 4.2429916610952306, z 0.570, against −0.4 ± 0.6 and 4.3 ± 0.1. Equations (32) and (33) are the sensitivity reading and were not used. The zero-pion-mass truncation stays outside, z 1.047 and 1.367. The pair was inserted into Dürr's ln Λ_F with the round-p lbar_4. lbar_12 = 2.191952746206307. Nyffeler lbar_3 = 7.65753993433 is z 1.982 on 2.9 ± 2.4 and was not used. With k_F left out, an lbar_3 anywhere inside that bar leaves F_π between 92.604 and 92.752 MeV. The one-loop value stays 92.8866215097 MeV. k_F is not assigned. The precision binary was not rebuilt. Gate stays 91/91 at z and 89/91 at 2%. Pins, `vendor/fsot_compute.py`, and the Lean engine file were not edited.

### H-89 · 2026-10-06: the leaf-curvature light tadpole is 92.672790938 MeV and still misses the lifetime bar; the gate is not rebuilt

The axial residue keeps the charged-pion leaf and the chiral-limit F. The σπ bubble is counted once, with the chiral kinetic counterterm −1/6 removed. One third of the three-pion vacuum force is the share that keeps the coefficient of −ξ ln ξ equal to 1. The full three-pion force gives coefficient 2. The curvature in the tadpole is 2λφ² = M²(1+6ξ), the mass that holds the pion pole on the leaf. The sigma-mass denominator M²(1+9ξ) is computed beside it and is not the residue.

At the charged-pion leaf the residue is 92.672790938 MeV. The move from the truncation 92.88662150974877 MeV is −0.213830572 MeV: exact vev +0.013748790, exact bubble +0.044151374, tadpole −0.271730736. The lifetime center is 92.31986135 ± 0.09721111 MeV, so z = 3.631. The result sits 0.352930 MeV above the center and 0.255718 MeV above the bar top. The sigma-mass sibling is 92.554581288 MeV, z 2.415, and is not the residue.

The weight 1/3 is the log-coefficient constraint, not a flavor trace. C4 is unchanged. The precision binary was not rebuilt. Gate stays 91/91 at z and 89/91 at 2%. Pins, `vendor/fsot_compute.py`, and the Lean engine file were not edited. No record row was opened.

### H-90 · 2026-10-06: thirteen owner-discretion catalog leaves pass in C++ on pin AEB2AD; the gate is not rebuilt

The C++ ledger scorer, pointed at Desktop Lean main `79320bb`, reads 477 active files and 477 green. The gate maximum is the same rule the Lean catalog certificate now uses. Dark-sector `tau_reion` still has a recomputed raw error of 3.036% in the Python audit, and the C++ gate maximum on that file is 0.281% (`wa_bao`). Cosmology bubble-bleed `FRB20200929C` still has a recomputed raw error of 2.000% in the Python audit, and the C++ gate maximum on that file is 0. The locked golden stays on hub commit `6f9c256`. `c_match` on the rewritten benchmarks is 1173 against 14634 in that golden, so the data commit was not moved. The engine file is unchanged between those two commits. The authority pin stays AEB2AD.

The catalog half of `owner-decisions-2026-10-02i` is in `include/fsot/host/catalog_leaves.hpp`. Alpha is the inverse-alpha leaf. Each row is inside the bar its script froze: Al 5.985769137 eV, z 0.0458; Cl 12.967632959 eV, z 0.00254; Si 8.151680003 eV, z 0.000101; P 10.486686001 eV, z 0.0000991; S 10.360016700 eV, z 9.3e-6; Ar 15.759611899 eV, z 0.00212; K 4.340663730 eV, z 0.00127; methane 111.666696854 K, z 0.606; ammonia 239.834610236 K, z 0.264; ethanol 351.438784067 K, z 0.243; NaCl 785.891428589 kJ/mol, z 0.217; olive oil 83.995865659 mPa·s, z 0.00827; cyclohexane 20.031616376 K·kg/mol, z 0.0632. NaCl, olive oil, cyclohexane, methane, and ethanol use the printed-digit bar those scripts froze. The Γ_Z/M_Z leaf was already record row `leaf:Gamma_Z/M_Z`. The pin move to 2C9442 and the Quantum_Mechanics depth override to 6 are not installed. Calcium, hydrogen, CO₂ sublimation, deuteron binding, and the deuteron moment stay bare. No record row was opened. The precision binary was not rebuilt. Gate stays 91/91 at z and 89/91 at 2%.

### H-91 · 2026-10-06: the live T2/T3/T4 package passes its percent median and does not pass a theory-of-everything score; the water/air leaf is the one missing lab formula

C++ origin/main before this entry reproduces the claimed solves: Linux ctest 86/86 and MSVC ctest 85/85, including the precision gate 91/91 at z ≤ 1 and 89/91 at 2%, the ledger golden, the thirteen catalog leaves, and the pion residue still a miss at z 3.631. The pin stays AEB2AD.

The same day, Lean `vendor/fsot_gr_sm.py` `run_full_t3_t4_suite` and `vendor/fsot_dynamics.py` `run_dynamics_consistency_suite` were run on that pin and wrote nothing. T3/T4 is 99 rows, 59 GR and 40 SM, median error 0.003027%, maximum 0.363% on `dm2_31_abs`. T2 is 18 rows. The September Label B report still says T1–T6 pass. That median is not the z ≤ 1 credibility claim, and 477/477 remains a residual-file count.

Most of those 117 rows set the measured side equal to the computed side, or normalize a structural flag to 0 or 1. That includes the Einstein trace-reverse toy, the weak-field factor, the acoustic cone, exact c, the Casimirs, N_c, β₀, the spin-2 helicity and degree-of-freedom flags, Wilson σ = (√σ)², the Polyakov and θ_QCD flags, and the five viscosity definitions. Diatomic γ is 1 + 2/5 = 1.4. The US 1976 scale height is R T/(μ g) = 8434.660 compared with the same quotient printed as 8434.5. The explicit Euler row removes 8.206% of its offset (contraction 0.08206 toward 1) and still stores error 0%, because the scorer only asks whether the residual shrank. The emergent charm row sums to 1.001755 in squares, 0.176% off 1, and the 0.5% gate still accepts it.

Rows that clear 0.5% and are not a published-uncertainty score: seed α⁻¹ = 136.826664 against 137.035999084 (0.153%; CODATA’s uncertainty is 2.1×10⁻⁸). The complex-equilibrium α⁻¹ is 136.834232, the same miss. The Weinberg seed 0.23118194 is scored against the old anchor 0.23122; against 0.23129 ± 0.00004 it is 2.70 bars low. N_eff in the package is scored against 3.046, the heating stand-in, not against 2.99 ± 0.17. The complex sin²θ₂₃ is 0.546954 against the old anchor 0.546; the published center is 0.558, and that flavor seed stays off the record. sin²θ₁₃ and δ_PMNS in the same suite use the old stand-ins 0.022 and 3.438. The solar Schwarzschild, deflection, and perihelion rows insert G, M, and c and compare with the textbook evaluation of that same expression. The preregistration file stays frozen at pin D1D38A. Confirmed held-out stays 0. The package’s own manifest still leaves the path-integral confinement theorem, the spin-2 Fock uniqueness theorem, and the Einstein–Hilbert measure uniqueness theorem open.

No new formula was written for the lifetime decay constant, ℓ̄₃, the neutral pion, F_K/F_π, η/η′, the nucleon radius, g_A, the magnetic moments, the Δ–N split, or H₀. The one T2 lab formula that is a seed leaf and was not in the C++ tree is the water-to-air ratio `(e+φ)(1−α/(1+C_eff cos θ_S))` = 4.31981336304940964574 against 1482.4/343.2. The bar is the quadrature of half a printed tenth, 0.05 m/s, on each speed. z = 0.721519273740. It is locked by `fluid_lab_pass` and is not a record row. Gamma and the scale height are not installed. The precision binary was not rebuilt. Gate stays 91/91 at z and 89/91 at 2%.

### H-92 · 2026-10-07: four neutral-meson host readings lie inside their published bars; the cross-proof gauntlet on the link retry exited 0; the 91-row gate was not rebuilt

The sentence in H-91 that no new formula was written for the neutral pion, η, or η′ is the 2026-10-06 package note. The host readings below were installed the next day. H-91 is left as that day recorded it.

`include/fsot/host/neutral_mesons.hpp` and `tests/test_neutral_mesons.cpp` are on origin/main `f9adc19`. `neutral_mesons_pass` locks four values to 1e-9 and four z-scores to 1e-6. K⁰ = 497.61120080088705497 MeV, z 0.01544622208115139, on 497.611 ± 0.013. π⁰ = 134.97679871406545433 MeV, z −0.002571869091349485, on 134.9768 ± 0.0005. η = 547.86869881331816316 MeV, z 0.394047842244892, on 547.862 ± 0.017. η′ = 957.79231160159958598 MeV, z 0.2051933599930997, on 957.78 ± 0.06. K⁰ uses y = e³ + γ^(21/5) in the quark-route Dashen mass. π⁰ is the two-tank fixed point of the D=6 and D=7 scalars times (1 − γ⁴ α²). η is the axial 3×3 eigenvalue at y = e³ + γ⁴, times (1 + α/φ² + α²). η′ uses the charged-kaon leaf for the strange mass and dresses the pin singlet, divided by the axial ratio, with (1 + α/4). Alpha is the inverse-fine-structure leaf. The arithmetic midpoint of the two scalars is unused. The four are separate branches. They are not rows of `audit/precision_2026-10-02.md`.

The K⁰ bar is the PDG 2024 listing `rpp2024-list-K-zero.pdf`, OUR FIT 497.611 ± 0.013 MeV, scale factor 1.2, citation S. Navas et al. (Particle Data Group), Phys. Rev. D 110, 030001 (2024), doi:10.1103/PhysRevD.110.030001. The η bar is `rpp2024-list-eta.pdf`, OUR AVERAGE 547.862 ± 0.017 MeV, the same citation. The π⁰ and η′ centers are the summary-table values. They are absent from `reference/evidence/pdg2024_extracts.tsv`. The 2025 summary `rpp2025-sum-mesons.pdf` prints 134.9768 ± 0.0005 (S = 1.1) and 957.78 ± 0.06 and cites Navas et al. (2024) and the 2025 update. FREEZE_2026-10-02l line 18 already records the 2024 centers for π⁰, K⁰, and η. Charged π± and K± remain the seed leaves already on the gate. The sum-mesons extract has 139.57039 ± 0.00018 and 493.677 ± 0.015. The live kaon leaf in the gate uses the 0.013 MeV bar recorded with that leaf.

Windows MSVC ctest on `f9adc19` was 87/87. WSL `xval/cpp_check.sh` printed `ALL CPP CHECKS PASSED` in 404 s: ctest 88/88, goldens byte-identical, precision gate 91/91 at z ≤ 1 and 89/91 at 2%, QEMU serial byte-identical. Pin AEB2AD. The precision binary was not rebuilt.

The same day, FSOT-2.1-Lean `scripts/run_cross_proof_verification.py` on `b866a50` exited 0 in 707 s. After the banner `CROSS-PROOF VERIFICATION (Tier 91 wide)` the print was `overall_ok: True`, `seven_way_bare_metal: True`, `github_ready: True`. Coq 49/49, Isabelle `FSOT_CrossProof` 46/46, F* passed, Rust replay 2130, Rust↔Lean bridge passed with boot scalar 0.09928895626861721, QEMU serial and disk passed, catalog 1908/1908, 0 false margin violations. ESP32 was skipped (no CP210x port), so eight-way is false. The four masses are not Lean obligations of that run. A living-hardware audit that runs after the report, and does not enter `overall_ok`, failed `scalar_k_parity`: body-tree K 0.42022166416069673 against pin K 0.4201087636498879. The pin was not moved. Generated Lean reports from the run were restored and were not committed. The layer table is in `xval/README.md`.

Still outside: the leaf-curvature residue 92.672790938 MeV, z 3.631, on the lifetime bar in `axial_residue.hpp` (center 130.56/√2, header citation PDG 2026 review eq. 71.23); one-loop truncation 92.8866215097 MeV; Nyffeler ℓ̄₃ = 7.65753993433, z 1.982 on 2.9 ± 2.4 (FREEZE bh); F_K/F_π 1.2734 (z 38) and 1.506 (z 149) against FLAG 2+1+1 1.1932(21), with no FLAG DOI stored in FREEZE v. The nucleon profile was not restarted. Confirmed held-out stays 0. The strange tadpole was not started. The three names in H-91 (path-integral confinement, spin-2 Fock uniqueness, Einstein–Hilbert measure uniqueness) are the deferred classical proofs in the hub’s `docs/WHY_NOT_CLAIMED.md`. That page says the scored layer for the last of them is the weak-field, Schwarzschild, deflection, and perihelion probes. Those proofs are not published-bar misses, and this entry does not reopen them.

### H-98 · 2026-10-07: the atmospheric angle on the generation-9 half is inside 0.470 +0.017/−0.014; the 91-row gate was not rebuilt

`include/fsot/host/atmospheric.hpp`, locked by `atmospheric_pass`. The reading is |S|/2 on the generation-9 specimen rung. Neuroscience and Condensed_Matter share it, D_eff = 11. The value is 0.4706353135781523, z 0.0373713869501371, on NuFIT 6.1 normal ordering with SK atmospheric data, sin²θ23 = 0.470 +0.017/−0.014, 3σ range 0.435–0.584 (http://www.nu-fit.org/sites/default/files/v61.tbl-parameters.pdf, table dated 2026-01-12). The same half also lands for the specimen rungs of particle physics (z 0.300), physical chemistry (z 0.450), electromagnetism (z 0.463), optics (z 0.402), biochemistry (z 0.175), thermodynamics (z −0.129), psychology (z −0.306), and sociology (z −0.658). Generation 9 is the closest of that ladder. The record |Chaos|·√e = 0.545766610986025 is z 4.457 on this bar and stays the PDG 2024 row. NuFIT 6.1 predates the 2026-10-02 freeze, so this is not a held-out confirmation. Not a row of `audit/precision_2026-10-02.md`. Pin AEB2AD. The precision binary was not rebuilt. Gate stays 91/91 at z and 89/91 at 2%.

### H-97 · 2026-10-07: the neutron moment is inside −1.91304276 ± 4.5×10⁻⁷; the 91-row gate was not rebuilt

`include/fsot/host/nucleon_moment.hpp`, locked by `nucleon_moment_pass`. The nearer moment reading is the physical-pion soliton, round-q Q-1, μ_n = −1.92581799223. The pieces are the Christov assembly in `tools/score_2026_10_02q.py` on the DPP block of `audit/heavy_2026-10-02q.json`. The isoscalar piece carries √(F_π/F), the same square root as the installed isovector radius. The order-α named-seed window on that reading is empty. The Schwinger scale α/(2π) holds one named seed, Catalan's G. The value is −1.913042805746640751, z −0.101659201669, on the CODATA 2022 bar −1.91304276 ± 4.5×10⁻⁷. The bare soliton is outside. The square root without the seed is outside. The minus sign is outside. Replacing α/(2π) by α is outside. The full ratio F_π/F with the same dressing is outside. The proton from this fold is outside 2.79284734463 ± 8.2×10⁻¹⁰. The proton moment remains the leaf g_p/2. Not a row of `audit/precision_2026-10-02.md`. Pin AEB2AD. The precision binary was not rebuilt. Gate stays 91/91 at z and 89/91 at 2%.

### H-96 · 2026-10-07: the isovector radius and the Δ−N split are inside their published bars; the 91-row gate was not rebuilt

`include/fsot/host/nucleon_radius.hpp`, locked by `nucleon_radius_pass`. The dipole is 12 ħc²/m_ρ² with m_ρ = 2√2 π F on the chiral leaf. The weight is √(F_π/F), F_π the installed lifetime value. The value is 0.824200116307649382 fm², z 0.915480750074, on 0.82236 ± 0.00201. The bare dipole is z −13.05. The full ratio F_π/F is outside, and its square is outside. Several named seeds also sit in the bar, so no further seed is applied. ħc = 197.3269804 MeV·fm is the conversion already used by the radius score scripts.

`include/fsot/host/nucleon_delta.hpp`, locked by `nucleon_delta_pass`. The P3 fraction 0.327460495368 times the proton-mass leaf is rescaled by (F/F_π)^((N_c−1)/N_c) with N_c = 3. The value is 293.3782747823462506 MeV, z 0.148515193758, on the published ±2 MeV bar around 1232 minus the nucleon average. Power 1 is outside. Power 1/2 is outside. The profile magnetic moments were scored again on the CODATA bars and no FSOT weight reaches them. The proton moment leaf remains the record row. Not rows of `audit/precision_2026-10-02.md`. Pin AEB2AD. The precision binary was not rebuilt. Gate stays 91/91 at z and 89/91 at 2%.

### H-95 · 2026-10-07: g_A on the nuclear rung of the P3 profile is inside 1.2754 ± 0.0013; the 91-row gate was not rebuilt

`include/fsot/host/nucleon_axial.hpp`, locked by `nucleon_axial_pass`. The profile digit is AG-2 P3 from `audit/score_2026-10-02ag.tsv`, K 14, D 14, kmax 12: 1.29168910489. That soliton is built on the particle-sector leaves. The coefficient is S(Nuclear_Physics)/S(Particle_Physics) = 0.985466277760545807. The fine-structure window on that base, bare·(1 ± α^n·seed) for n = 1, 2, 3 and the named-seed list, holds one seed: n = 1, plus, γ·ψ_con². The value is 1.27505846641964337, z −0.2627181387, on the published bar 1.2754 ± 0.0013. The bare ratio is 1.27291605421980, z −1.91073. The two-tank mix of depths 5 and 12 gives 1.28217024034810, z 5.208, and that window holds both ψ_con and 1/φ. The bare profile's window holds both φ and √e. Alpha is the inverse-fine-structure leaf. The triton dressing uses yy·γ·ψ_con² with yy = (Poof·Suction)² and is not this factor. Not a row of `audit/precision_2026-10-02.md`.

Scored the same day and not installed. The KSRF dipole 12 ħc²/m_ρ² = 0.79613707716 fm² is z −13.05 on 0.82236 ± 0.00201. Times √(F_π/F), with F_π the installed lifetime value and F the chiral leaf, it is 0.82420011596, z 0.915. The exponent 1/2 is the power that landed among the powers tried on that ratio. The axial algebra's square root is F_π = φ/√R and, in the chiral limit, returns F_π = F. Replacing F by the installed F_π inside KSRF moves the dipole down, to z −64, because m_ρ grows with the decay constant. The square-root factor moves the dipole up, past the chiral mass. It stays the inside neighborhood. The same base's α window holds eight seeds at n = 1. The domain reading of that dipole, m_ρ scaled by S_nuclear/S_particle and the radius by the inverse square, is 0.81979320651, z −1.277, and its α window holds four seeds, so the bare ratio stays. Replacing the computed sea share 0.3126 of the cranking radius by 1/6 gives about 0.82417, z 0.90. That 1/6 is the meson kinetic counterterm removed in `axial_residue.hpp`, the color sum already inside the rotational operators A and A_μ (FREEZE_2026-10-02p), or the FESR isoscalar coupling c_ω. Christov, Górski, Goeke, and Pobylitsa, hep-ph/9507256 eq. (76), identify the cranking sum at the computed share with the whole isovector electric form factor. The profile moments and the Δ−N split were not given a unique seed. The strange tadpole was not started. Pin AEB2AD. The precision binary was not rebuilt. Gate stays 91/91 at z and 89/91 at 2%.

### H-94 · 2026-10-07: the lifetime decay constant and F_K/F_π are inside their bars; the 91-row gate was not rebuilt

`include/fsot/host/chiral_decay.hpp`, locked by `chiral_decay_pass`. The one-loop piece is the leaf residue 92.672790938 MeV. Dürr arXiv:1310.3626 supplies the two-loop square with k_F omitted, −0.205107550657 MeV. The three-loop term is Bijnens and Hermansson-Truedsson, arXiv:1710.01901 eqs. (28)–(31), with r_i and c_i left out, evaluated where the square's linear log coefficient vanishes. ℓ̄₁ and ℓ̄₂ are recomputed from FREEZE_2026-10-02bh. ℓ̄₃ and ℓ̄₄ are the axial-partner values already in `lbar3.hpp` and the one-loop truncation. The selected decay constant is 92.40127085413148 MeV, z 0.8374505961, on 130.56/√2 ± the quadrature of 0.02, 0.04, and 0.13 divided by √2. The same reading at μ = M_π, at the sigma mass 4πF/√3, and at the frozen KSRF rho also has |z| ≤ 1. F_K/F_π uses this F_π in the one-loop SU(3) formula with L_4 = L_5/3. The ratio is 1.191537555726962, z −0.79164013, on FLAG 1.1932(21). The L_4 = 0 ratio, the scalar-saturation ratio, and the axial tree ratio stay the wider neighbors. `axial_residue.hpp` still locks the residue as a miss. k_F is not assigned. Neither value is a row of `audit/precision_2026-10-02.md`. The nucleon profile was not restarted. The strange tadpole was not started. Pin AEB2AD. The precision binary was not rebuilt. Gate stays 91/91 at z and 89/91 at 2%.

### H-93 · 2026-10-07: lbar_3 on the KSRF axial-partner mass ratio is inside 2.9 ± 2.4; the 91-row gate was not rebuilt

`include/fsot/host/lbar3.hpp` evaluates CGL hep-ph/0103088 eq. (7.1) on the tree mass ratio of the frozen KSRF axial partner. R = (1+√3)/2, lambda stays 8π²/3, and M_π²/M² = 1/√(1 + 6ξ/R²) with ξ = M_π²/(16π² F²) on the chiral F and the charged-pion leaf. Dürr's x = ξ / (M_π²/M²). The selected value is lbar_3 = 3.0128360396658476572, z = 0.04701501652743652, on 2.9 ± 2.4. The chiral limit of the same ratio is 24 − 12√3 = 3.215390309173472, z 0.131. The ξ secant is 3.092175303528166, z 0.080. `lbar3_pass` locks the selected value. It is not a row of `audit/precision_2026-10-02.md`. The pure linear-sigma Dürr reading 5.327199232022074, z 1.011, was the previous nearer miss and is not this value. Nyffeler 7.65753993433 stays unused. k_F is not assigned. One-loop F_π stays 92.8866215097 MeV. The lifetime residue and F_K/F_π were recomputed and stay outside: residue 92.672790938 MeV, z 3.631; one-loop F_K/F_π = 1.273427263498503, z 38.20; the axial-partner tree ratio F_K/F_π = 1.258229407422869, z 30.97, against FLAG 1.1932(21). The strange tadpole was not started. The nucleon profile was not restarted. Pin AEB2AD. The precision binary was not rebuilt. Gate stays 91/91 at z and 89/91 at 2%.

### H-77 · 2026-10-05: the Z-width record row is the Lean catalog leaf (φ⁵/e⁶)(1−α/φ) = 0.0273658036393593, z 0.02916; the bare seed stays in the report with record 0; totals 89/91

Freeze `FREEZE_2026-10-02aw` was hashed before the binary was rebuilt. The record id is `leaf:Gamma_Z/M_Z`. Alpha is the inverse-alpha leaf, not the domain constant ALPHA. The C++ value matches the Lean reprint. The old row `pin:wave5|Gamma_Z/M_Z` stays at 0.0274897828876688, z 4.885, record 0. Deuteron binding and the deuteron moment stay on their bare formulas. Gate from `fsot_precision`: 89/91 confirmed, 87/91 pinned only, frozen-pending column 89/91. With H0 and τ_n deferred the accounting is 87/89. Pins, `vendor/fsot_compute.py`, and the preregistration were not edited. The Lean engine file stays the bare seed.

### H-76 · 2026-10-02av: one call with the 40-step budget raised to 400 matches round ar through step 39, closes through step 43, and jumps at step 44; after 400 steps dtheta is 0.02018; the j=0 radius 1.15018 fm² is information; nothing rescored

Freeze `FREEZE_2026-10-02av` was hashed before the run. One call of `self_consistent_m`, mix 0.2, itmax 400, from the DPP. Step 0 dtheta is 0.17211904981809267 and step 39 is 0.005631712767651509, the same figures as round ar. The gap kept falling through step 43, to 0.005190733171335227. Step 44 opened it to 0.19379649668786914, the same jump the re-entered walk found on its fifth pass, and that jump then kept returning through step 399. The call returned False. E/M on the last point is 2.21417, valence 0.230358, 2110.8 s. The j=0 sums there give r_V² 1.15018154675 fm² (move 14.52% from the DPP radius). The regularised sea holds 0.383221 of I[1]. That point is not a fixed point, so the 2% rule stays unapplied and the M = m_p/3 check stays unstarted. Totals 88/91.

### H-75 · 2026-10-05: Lean catalog at 7e106a5 records the Z-width leaf (φ⁵/e⁶)(1−α/φ) = 0.02736580, 0.029 uncertainties low; the engine row stays the bare miss; C++ totals stay 88/91

Desktop `FSOT-2.1-Lean` is branch `owner-decisions-2026-10-02i` at `7e106a5`. Published main stays `fb76270`, pin AEB2AD. The branch pin is 2C9442. OD-1 compares `γ³·Poof` with `Δm²₂₁/Δm²₃₁`. OD-2 sets live Quantum_Mechanics `D_eff` to 6. The engine formula stays `φ⁵/e⁶` = 0.027489782887668835, which is 4.930 uncertainties high of `2.4955/91.1880` and 4.951 high of the display target 0.027366. The catalog leaf is `(φ⁵/e⁶)(1−α/φ)` = 0.02736580363935934, 0.029 uncertainties low of that PDG ratio. The gap over the adopted alpha is 0.6144 and `1/φ` is 0.6180. `α·γ` finishes 0.298 high and `α·ψ_con` finishes 0.142 low, so both stay off the leaf. `scripts/gamma_z_seed_check.py` reprinted these figures from the live engine. The leaf is commit `de21ae1`. The engine file was not edited. The C++ record row stays the bare law, and the 91 are not rescored. The same branch records first ionization for Al, Cl, Si, P, S, Ar, and K, boiling leaves for methane, ammonia, and ethanol, and the NaCl lattice leaf `(e⁶·π/φ)(1+α·e/6)`. Calcium, hydrogen, and CO₂ sublimation stay bare. Deuteron binding and the deuteron moment were not in this stack. The 400-step profile call is a separate route and was left running.

### H-74 · 2026-10-02au: re-entering the 0.2 damper closes four passes and then orbits (fifth pass 0.194); after 400 passes dtheta is 0.02223; the j=0 radius 1.15100 fm² on that orbit point is information; nothing rescored

Freeze `FREEZE_2026-10-02au` was hashed before the run. Each pass was a fresh call of `self_consistent_m` with mix 0.2 and itmax 1, so the solver refit the outer tail on every entry. Passes 0 through 3 closed the gap from 0.005516 to 0.005191. Pass 4 opened it to 0.193796, and that jump then kept returning through pass 399. The guard stopped the run. E/M on the last point is 2.21453, valence 0.231570. The j=0 sums there give r_V² 1.15099879376 fm² (move 14.6% from the DPP radius). The regularised sea holds 0.383195 of I[1]. That point is not a fixed point, so the 2% rule stays unapplied and the M = m_p/3 check stays unstarted. The round-ar 40-step close was one call, not this re-entry. Totals 88/91.

### H-73 · 2026-10-02at: a half force-balance step shrinks the gap once and then orbits (second pass 0.194, then about every nine passes); after 200 passes dtheta is 0.02238; the j=0 radius 1.14252 fm² on that orbit point is information; nothing rescored

Freeze `FREEZE_2026-10-02at` was hashed before the run. The one-step probe on the saved ar profile gave next gaps 0.193546 (recorded full step), 0.005235 (half), 0.005375 (quarter) and 0.005445 (eighth). The half step was the smallest and sat under the start gap 0.005516, so the walk used mix 0.5. Pass 1 reproduced 0.005235. Pass 2 opened the gap to 0.193584, and that jump then repeated about every nine passes through pass 199. The guard stopped the run. E/M on the last point is 2.21589, valence 0.237066. The j=0 sums there give r_V² 1.14251976039 fm² (move 13.76% from the DPP radius). The regularised sea holds 0.378247 of I[1]. That point is not a fixed point, so the 2% rule stays unapplied and the M = m_p/3 check stays unstarted. Totals 88/91.

### H-72 · 2026-10-02as: the full force-balance step orbits (gap 0.19 to 0.008 about every eight passes) and is still at dtheta 0.0255 after 60 passes; the j=0 radius 1.12163 fm² on that orbit point is information; nothing rescored

Freeze `FREEZE_2026-10-02as` was hashed before the run. Owner directive: the round-q cap of 40 and the mix 0.2 damper are not the stationarity condition. Each pass replaced the profile by `atan2(-P, -(S-c))`. On the saved ar profile the gap was 0.005516. The next pass opened it to 0.193546, and the gap then repeated that jump about every eight passes through all 60. The guard stopped the run. E/M on the last point is 2.21962, valence 0.249314. The j=0 sums there give r_V² 1.12163082751 fm² (move 11.68% from the DPP radius). The regularised sea holds 0.368413 of I[1]. That point is not a fixed point, so the 2% rule stays unapplied and the M = m_p/3 check stays unstarted. Totals 88/91.

### H-71 · 2026-10-02ar: self-consistent profile at kmax 12 is still moving after 40 steps (dtheta 0.005632); the j=0 radius 1.05233 fm² is information, 4.777% from the DPP value; the M = m_p/3 check stays unstarted; nothing rescored

Freeze `FREEZE_2026-10-02ar` was hashed before the run (parent 1615ed5, date 2026-10-05). `self_consistent_m` used the locked defaults mix 0.2, tol 1e-3, itmax 40, Nc 3, on K 14, D 14, kmax 12, starting from the round-ag DPP profile. E/M finished at 2.21557 with valence 0.229436. dtheta fell from 0.172 to 0.0116 over the first 16 steps, then the step shrank by about 2% each time and ended at 0.005632. The j=0 sums on that unfinished profile give r_V² 1.05233363489 fm² (r M² 4.9944537 against the committed DPP 4.7667424, move 4.777%). The regularised sea holds 0.354569 of I[1], and its own radius is 1.81568 fm². The solver returned False, so the 2% rule stays unapplied, boxes j=1..3 were left unrun, and AR-2 did not start. Totals 88/91.

### H-70 · 2026-10-02aq: shell-averaged r_V² is 1.0045 / 1.0040 fm² at kmax 12 / 14 (stable to 0.05 %), so the excess over 0.822 fm² is physical; the valence level gives 0.62 fm², the PV-regularised sea carries 31 % of the isovector charge at 1.85 fm²; nothing rescored; level C j=0 done

Freeze `FREEZE_2026-10-02aq` (1f0b5fe). Round-ap cpp_check passed (678 s). Totals 88/91. The kmax-16 job and the diagnostic never ran at the same time.

### H-69 · 2026-10-02ap: soliton isovector charge form factor (cranking O(1/I)) gives r_V² 1.004 fm² vs 0.822(2) (z 90), so the f_ρ chain breaks at step 1; information after the break: HLS pole 533 MeV, a 2.47, f_ρQ_ρ 146 MeV, Γ_ee 8.9 keV; new additive kmax-16 rule frozen and its job started

Freeze `FREEZE_2026-10-02ap` (fa10fe4). Round-ao cpp_check passed (671 s). Totals 88/91. The level-C job was started only after the form-factor run had finished, so the two never overlapped; it is paused during cpp_check.

### H-68 · 2026-10-02ao: level-B shell average finished and both levels validate, but μ_p/μ_n move −2.41 %/−3.25 % from kmax 12 to 14 (> 2 %), so they are not scored; σ not adopted, deuteron not rerun; the dimension-4 condensate raises Γ_ee(ρ) to 5.66 keV (×1.05; factor 1.24 left), validation fails (z 22), Γ_Z/M_Z z 5.61

Freeze `FREEZE_2026-10-02ao` (049c0e8). Round-an cpp_check passed (772 s). Totals 88/91. The level-B files (j0–j3, rot, merged am_B.json) are committed; the job has exited.

### H-67 · 2026-10-02an: Γ_ee(ρ) trace through the FESR f_ρ: LO 4.38 → +α_s 4.85 → +finite width 5.40 keV vs 7.04; a factor 1.30 remains (needs a gluon-condensate term); validation fails (z 23), Γ_Z/M_Z z 5.73; level-B job 3/4 samples, still running

Freeze `FREEZE_2026-10-02an` (c5d9ba0). Round-am cpp_check passed (682 s). Totals 88/91. Disclosures: Breit–Wigner normalisation moved from [4m_π², ∞) (divergent) to [4m_π², s0] before any result; the AN-1 sample set is fixed in the scorer at commit time so the score stays byte-identical as more samples are committed.

### H-66 · 2026-10-02am: owner operational budget change lets the kmax-14 shell-average samples run as one detached resumable job (still running); Δα_had via soliton-radius VMD + LMD duality couplings fails validation (0.02603 vs 0.02783, z 30), FSOT Δα_had 0.02634 (z 24.9), G_F z 3687, Γ_Z/M_Z z 6.13; nothing changes

Freeze `FREEZE_2026-10-02am` (8b7256d). Round-al cpp_check passed (674 s). Totals 88/91 (86/91 pinned only, 86/89 deferred) since b99fc29. Disclosures: Λ_V/m_p (round ag) was known before the freeze; the background tool's merged output was renamed after the freeze from `shellavg_2026-10-02al_B.json` to `shellavg_2026-10-02am_B.json` so the committed round-al score stays byte-identical (job restarted from cache, 30 s lost); the AM-1 score row was made static for the same reason.

### H-65 · 2026-10-02al: shell-period averaging (4 boxes over one π/kmax period) passes validation at kmax 12 (E +1.70 %, g_A +0.50 %, I +0.002 %) but the kmax-14 level did not finish within the 10-min cap, so μ is not scored; the averaged σ charge moves −4.23 % from kmax 12 to 14, so it is not adopted and the deuteron is not rerun; Γ_Z not attempted; core-SHA CTest made sh-free for Windows

Freeze `FREEZE_2026-10-02al` (50b93a3). Round-ak cpp_check passed (653 s). Totals 88/91 (86/91 pinned only, 86/89 with H0 and τ_n deferred) after the owner's record commit b99fc29 (H-64) adopted the η T_CMB route; round al changes no record row.

Details (kept here; docs/PRECISION_REPORT.md is left exactly as the owner's record commit b99fc29 wrote it). Level A (kmax 12, D0 14), sharp D0 → 4-box average: E_sol/M 2.123983 → 2.160008 (+1.70 %), g_A 1.291689 → 1.298195 (+0.50 %), I·M 2.098733 → 2.098767 (+0.002 %); μ_p 2.2854 → 2.3262, μ_n −1.6841 → −1.7249 (not scored). The samples jump in pairs (j=0,1 vs j=2,3), so the discreteness is a step. Level B (kmax 14) was killed by the frozen 10-min cap (`timeout 600`) before finishing its first sample, so μ is not scored. σ charge averaged 1.5810 (kmax 12) vs 1.5169 (kmax 14). Windows: `freeze_core_sha_matches_hub_freeze` failed on native MSVC at 92b62fb only because `sh` was not on PATH; it now runs `cmake -P cmake/check_core_sha.cmake` (docs/REPRODUCE.md). Look-elsewhere: 0 scored rows. Disclosures: the first level-A launch was killed by an interrupted wait and restarted unchanged; using the D0-only rotational sums was pre-registered in the freeze.

### H-64 · 2026-10-03: adopted the AF-3 η route as the T_CMB record row (2026-10-02ah section)

The record row is `eta:T_CMB` = 2.72573880197729 K, z 0.398, against FIRAS 2.7255(6). Formula: n_γ0 = ω_b ρ_c,100 / (m_p η), T_0 = (π² n_γ0 / (2ζ(3)))^{1/3} ħc/k_B, with ω_b = `wave1|Omega_b_h2`, η = `wave10|eta_baryon_photon`, and m_p the seed leaf. G, c, ħ and k_B are the AF-3 CODATA values; ζ(3) is the mpmath literal. The closed form `pin:wave1|T_CMB` (2.72471169034307 K, z 1.314) stays in the report with record 0, and C-TCMB stays attached to that id.

Caveat: the observed η the formula was compared to is itself inferred with T_CMB³ (target choice, not an input). The same flat branch (age → h) gives h 0.674541, against the H0 pin by −1.448%, Ω_Λ by +0.408%, Ω_m by −0.299% and Ω_r by +0.327%. The pin set sums to 0.99816. The H0 record row is unchanged.

Gate from `fsot_precision`: 88/91 confirmed, 86/91 pinned only, frozen-pending column 88/91. With H0 and τ_n deferred the accounting is 86/89. Pins, `vendor/fsot_compute.py`, and the preregistration were not edited.

### H-63 · 2026-10-02ak: the μ_V^(0) sea oscillation follows the shell count kmax·D (same product agrees to 0.021, different product moves 0.27); a smooth convergence factor (E_s = kmax/3) makes the sums kmax-stable but shifts E by +10 % against the sharp values, so frozen validation fails and μ and the σ charge are not scored; Γ_Z not attempted

Freeze `FREEZE_2026-10-02ak` (1d4d524). Round-aj cpp_check passed (632 s). Totals 87/91.

### H-62 · 2026-10-02aj: local-density (r applied to the density) evaluation of μ_V^(0) equals the matrix-element sum (validated on g_A^(0)); the kmax oscillation lives in the interior density (r < 3/M), so μ is not scored (μ_p −4.1 %, μ_n −5.6 % from kmax 12 to 14); the σ-projected charge moves −10 %, so it is not adopted

Freeze `FREEZE_2026-10-02aj` (e6a65eb). Round-ai cpp_check passed (639 s). Totals 87/91.

### H-61 · 2026-10-02ai: two-subtraction PV derived (m_1 1.3401, m_2 6.9597, c_1 −0.5663, c_2 3.52e−4 from divergence cancellation + FSOT F + condensate pin 1/4); tolerance check fails on E (−3.7 %), so the scheme is not used for scoring; the μ_V^(0) kmax oscillation survives (−7.0 %), so it is a basis effect, not a UV divergence, and μ is not scored; the unprojected scalar charge is stabilised (0.75 %) but the σ-projected charge moves 7–10 %, so it is not adopted

Freeze `FREEZE_2026-10-02ai` (b1b058b). Round-ah cpp_check passed (648 s). Totals 87/91.

### H-60 · 2026-10-02ah: μ cutoff dependence is entirely in the μ_V^(0) sea sum (μ_V^(0) 2.814/2.639/2.898 at kmax 12/14/16; the PV weight cancels about 90 %, and the residue oscillates), so μ is not scored; the full valence+PV-sea scalar charge (12.09, 7× valence) moves 3.0 % from kmax 12 to 14 and is not adopted (no deuteron rerun); T_CMB adoption section drafted for the hub

Freeze `FREEZE_2026-10-02ah` (2cb6a00). Round-ag cpp_check passed (606 s). Totals 87/91.

### H-59 · 2026-10-02ag: FSOT η = Poof¹¹/(πγ) has no T_CMB input, so the round-af T_CMB (z 0.40) is an FSOT derivation (proposed hub record route); with kmax fixed at 12 the box and K steps converge under 2 % and μ_p 2.285 (z 21.9), μ_n −1.684 (z 9.38), g_A 1.2917 (z 1.56), Δ−N/m_N 0.3275 (z 6.12) all miss; post-freeze kmax 12→14 moves μ by 4–5 % (cutoff-dependent; g_A, Δ−N stable); deuteron: ω central (9π) over-repels at 37× the binding, the topological-radius ω vertex is still unbound

Freeze `FREEZE_2026-10-02ag` (fea36c7). Round-af cpp_check passed (595 s). Totals 87/91.

### H-58 · 2026-10-02af: μ_V^(0) sector decomposition: the K drift is a common box-size rescaling (D tied to K), not a pion tail; frozen tail test fails, μ not scored; deuteron with ω tensor/spin-orbit (κ_ω −0.160) and σ spin-orbit still unbound (OPE+σ 3.46 MeV); self-consistent flat FSOT cosmology branch gives T_CMB 2.725739 K (z 0.40, agrees; η-route circularity flagged) and contradicts the H0 pin by −1.45 % in h and the Ω_Λ pin by +0.41 %

Freeze `FREEZE_2026-10-02af` (04f0fd1). Round-ae cpp_check passed (571 s). Totals 87/91.

### H-57 · 2026-10-02ae: rotational μ terms PV-regularised (μ_p 2.254/2.197, μ_n −1.650/−1.596 at K 12/14; 2 % K rule fails, μ not scored); g_A K 14 1.2911 (z 2.33), Δ−N/m_p 0.3271 (z 4.73); ω Dirac form factor (Λ_V 0.736 m_p) still unbound; T_CMB trace: FSOT cosmology pins not flat (0.99816) and h inconsistent (0.6735 vs 0.6845), flatness gives +0.071 %

Freeze `FREEZE_2026-10-02ae` (5f56a46). Round-ad cpp_check passed (540 s). Totals 87/91.

### H-56 · 2026-10-02ad: rotational g_A term time-ordered with PV-regularised sea → g_A 1.2845 (z 7.0, +0.71 %; was z 202); soliton σNN (S_val 0.508) → OPE+σ binds 7.5 MeV, +ω unbound (ω form factor next); T_CMB from the FSOT age 2.72847 K (z 4.96, +0.11 %)

Freeze `FREEZE_2026-10-02ad` (63468ff). Round-ac cpp_check passed (535 s). Totals 87/91.

### H-55 · 2026-10-02ac: wide soliton window pre-registered (Δ−N/m_p 0.3294 z 8.0, g_A 1.538 z 202, rotational term 0.634); kink located in the sea−PV part (basis level reordering, valence smooth); tensor-OPE deuteron with soliton form factor (Λ = √6/r_B = 0.893 m_p): OPE alone 4.0 MeV, +σ 234 MeV, +ω unbound (miss; σ/ω couplings diverge first); FSOT matter-to-baryon ratio 6.3685, T_ls 3501 K (info)

Freeze `FREEZE_2026-10-02ac` (a4d5407). Round-ab cpp_check passed (510 s). Totals 87/91.

### H-54 · 2026-10-02ab: DP variational instanton size R/ρ̄ = 2.468 (β 5.2, packing 0.27, not dilute) → M/m_p 0.4582 → Δ−N/m_p 0.3356 (z 10.9, edge minimum; post-freeze wide window 0.3294, info) and g_A 1.498 (z 171), both misses; deuteron central OPE+σ+ω unbound (first divergence: the missing tensor force); no in-FSOT T_CMB anchor

Freeze `FREEZE_2026-10-02ab` (d4c92e1). Round-aa cpp_check passed (511 s). Totals 87/91.

### H-53 · 2026-10-02aa: condensate pin read unit-free → M/m_p 0.34607 → Δ−N/m_p 0.2118 (z 47.2), g_A 1.438 (z 124.7), both misses; KSRF light-quark Δα_had 0.025825 (z 33.4, validation fails) → Γ_Z/M_Z 0.02720 (z 6.7); no H0-free T_CMB route in the FSOT pins (Saha T_rec info only)

Freeze `FREEZE_2026-10-02aa` (6bc0f13). Round-z cpp_check passed (508 s). Totals 87/91.

### H-52 · 2026-10-02z: soliton inertia traced (I M ≥ 2.1 at every size; the divergence is the absolute M/m_p = 0.369, nothing rescored); higher-order Δr (resummation, O(αα_s²), O(G_F²m_t⁴)) → Δr 0.03518, G_F z 1657, Γ_Z/M_Z 0.02724 (z 5.0, miss); T_CMB from the FSOT radiation density 2.7434 K (+0.66 %, information, uses the deferred H0)

Freeze `FREEZE_2026-10-02z` (a371502). Round-y cpp_check passed (510 s). Totals 87/91.

### H-51 · 2026-10-02y: soliton in proton units with PV-consistent F: (M_Δ−M_N)/m_p 0.2440 (229 MeV, z 31.5) and g_A 1.479 (z 9.0), K-stable; quark-pole duality Δα_had 0.027344 (z 8.1, validation fails); FSOT one-loop Γ_Z/M_Z 0.02717 (z 7.7), with the next divergence in the higher-order Δr; round-i GZ-1 moved to scaffolding (standing rule)

Freeze `FREEZE_2026-10-02y` (c2ca975). Round-x cpp_check passed (682 s). Totals 87/91.

### H-50 · 2026-10-02x: energy-cutoff μ sea sum does not converge (+0.908 / −0.700 at K 12/14; μ not rescored); FSOT M(0) = 346.07 MeV from the DP gap equation (validation 345.8 vs 345) → Δ−N 199.7 MeV, g_A 1.427 (K 12, miss); F/M tied to M is the next suspect; Γ_Z/M_Z trace: first divergence Δα_had^(5), the physics route sits at z 0.68 and is insensitive to it, and the row stays open on the gate and external parametrisations (owner decision)

Freeze `FREEZE_2026-10-02x` (c4c647d). Round-w cpp_check passed (2124 s). Totals 87/91.

### H-49 · 2026-10-02w: μ oscillation is numerical (non-decaying high-K tail of the μ_V^(0) sea sum; valence and inertia K-stable); Δ−N fails at the soliton quark mass M = m_p/3 (valence inertia alone 1.39× the required value; M = 420 MeV sanity run gives 296.7); rotational response lowers Δ−N (152 MeV); FSOT scalar saturation gives L4 = 0 (derived), L5 = 4.75e-3 → F_K/F_π 1.506 (z 149) and FKS η/η′ miss; WV combination +25 % (miss)

Freeze `FREEZE_2026-10-02w` (a3d3e76). Post-freeze diagnostics (rotational response, partial-sum averaging) are not scored. Totals 87/91 (85/89 with H0 and τ_n deferred).

### H-48 · 2026-10-02v: soliton to K 16 (windowed scan, cheaper but same physics); K 14–16 Richardson: g_A 1.502 (z 5.6), Δ−N 180.8 (z 41) miss; μ_p/μ_n z ≈ 1 only through an inflated theory uncertainty (sequence non-convergent, not counted as evidence); F_K/F_π 1.273 (z 38) and FKS η/η′ 574/951 MeV miss; reference-type tags (owner directive 02:39) applied to PHYSICAL_MAP and the round-v scorer

Freeze `FREEZE_2026-10-02v` (2a7eaea). Post-freeze changes: only the class-column type tags in `tools/score_2026_10_02v.py`, which are labels and change no numbers. Pre-freeze peek: F_K/F_π estimated at 1.25–1.27 (disclosed in the freeze). Look-elsewhere count 4 (one primary row each for g_A, μ_p, μ_n and Δ−N; the K pair was pre-registered). g_A ordering is not derived. Directives (b)–(d) are scheduled for next round. Totals 87/91.

### H-47 · 2026-10-02u: z-only rule adopted (earlier percentage "passes" re-labelled as misses); K 14 soliton not completed (cap); surface term negligible, ordering open; Λ^(0)/Λ^(3)_FSOT = 0.837 via the trace anomaly at fixed vacuum energy → χ^{1/4} 190.3 MeV (z 0.88, chosen post hoc, disclosed)

Freezes `FREEZE_2026-10-02u` (d24fc1d) and `FREEZE_2026-10-02u2` (d061909). μ_p/μ_n moved because of the pion mass and the K basis; hybrid removal did not affect them. Totals 87/91.

### H-46 · 2026-10-02t: gluon-condensate pin → instanton density → χ^{1/4} 200.1 MeV (+8.0 %, z 2.6: miss under the round-u z rule; FSOT-only); LO η′ +20 % (validation fails); massive soliton at K 12: g_A +12.3 %, μ_p −5.4 %, μ_n −6.2 %, so the round-r μ agreement is withdrawn

Freeze `audit/FREEZE_2026-10-02t.md` (a5d3947). The pin value was seen before the freeze (disclosed). The ordering/surface corrections and F_K/F_π remain open derivations. Totals 87/91.

### H-45 · 2026-10-02s2: owner directive: no hybrid in FSOT. External-input results moved to a scaffolding table (not counted); FSOT-only thresholds give Λ^(4) 292.07 (z 0.29) and Λ^(3) 334.43 MeV (z 0.36); Λ^(0)/Λ^(3) is an open derivation

Freeze `audit/FREEZE_2026-10-02s2.md` (74ffa98).

**External-input scaffolding (not FSOT results; never in confirmed or agreeing counts):**

| item | external input | round |
|---|---|---|
| U(3)+WV η/η′ | lattice χ_top | m |
| GMOR m_ud, m_s | Σ = (272/338) Λ^(3) | l |
| Λ^(4), Λ^(3) (J-1) | FLAG m_b, m_c thresholds | j |
| χ_top (DP, Λ^(3)) | Λ^(3) built with FLAG thresholds | p |
| χ_top quenched, η/η′ | FLAG r0Λ ratio 0.772 | r |
| FKS η/η′ | FLAG F_K/F_π, round-r χ | s |

χ_top, η and η′ wait on an FSOT Λ^(0). The missing leaf is a pure-gauge hadronic scale. Totals 87/91.

### H-44 · 2026-10-02s: g_A separation: the basis cap is not the cause (−1.8 %); the pion-mass step gives +20.5 % via the Dirac-sea axial sum and g_A^(1); FKS η −1.7 % (z 557, miss), η′ −7.9 % (χ is the remaining step)

Freeze `audit/FREEZE_2026-10-02s.md` (5d6610c). The separation run was a diagnostic made before the freeze (disclosed), and no g_A fix has been derived yet. Totals 87/91.

### H-43 · 2026-10-02r: late round-q validation passes (g_A, μ_p, μ_n) → soliton μ_p −0.96 %, μ_n +0.67 % inside a 2 % gate (round u: misses by z; round t: not basis-stable); μ_d −5.7 % (fail); χ_top trace: quenched Λ^(0) fix → χ^{1/4} 177.0 MeV (−4.5 %, z 1.46, miss); η/η′ −7.6 %/+5.8 % (LO U(3)+WV next)

Freeze `audit/FREEZE_2026-10-02r.md` (26f9b66) was committed before the scorer and the late validation result. Disclosures are in the precision report. Totals 87/91.

### H-42 · 2026-10-02q: soliton with physical m_π — μ_p −0.96 %, μ_n +0.67 % (validation not run, time box); g_A 1.391 (+9.1 %, fails); Δ−N 190 MeV; still unbound at M = m_p/3

Freeze `audit/FREEZE_2026-10-02q.md` (d7a9af6) was committed before the solver changes (`tools/cqsm_rot.py` q-section, `tools/heavy_2026_10_02q.py`) and `tools/score_2026_10_02q.py`.
- The run was stopped by the time box. The validation case is missing, so the μ rows cannot be promoted.
- The self-consistent iteration did not converge (2.5e-3 after 40 iterations), so the massive DPP profile is primary.
- Totals 87/91.

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
| M3 zero-target rows (153 of the 188 genuine misses) | relative error against m = 0 | stored value kept (`zero_target_rows_kept_stored`); these rows store a residual as `computed` | `ledger_b.hpp::analyze_benchmark` |
| M3 inequality rows (14) | c read as a point prediction | formula with `≤`/`<=`: error 0 when m ≤ c (`inequality_bound_rows`) | same |
| M3 contraction row (1) | residual_after vs initial_offset compared as c vs m | 0 if the residual contracted, else 100 (`contraction_rows`) | same |
| M3 rounded `computed` (12 genuine; 6,198 in total, mostly Ledger B) | error recomputed from a rounded `computed` | not recomputable → stored value (`computed_rounded_rows_kept_stored`), d = max(repr decimals, 6) | same |
| M3 float noise at exactly 0.5 % (1) | 0.500000000000008 > 0.5 | gate limit 0.5·(1+1e−12) in corrected mode | same |
| M3 freezes | hub domain-table freeze only | `apps/fsot_freeze_domain` writes/verifies dated SHA-256 freezes (core, extension folds, closed forms, Ledger A); tiers count them per row | `docs/FREEZES.md`, `host/freeze.hpp`, `host/tiers.hpp` |
| H-01 leaves missing from the port | pin closed forms only | 50 hub seed leaves ported (`seed_leaves.hpp`), CTest `seed_leaves` vs the hub's printed values | `include/fsot/host/seed_leaves.hpp`, `tests/test_seed_leaves.cpp` |
| H-02 stale pin targets as references; 2 % relative check | pin `measured`, err < 2 %/5 % | one verified reference table; gate z ≤ 1 (σ from PDG 2024 / CODATA 2022 / AME2020), 2 % and ppm reported alongside; CTests `precision_report*`, `references_check` | `include/fsot/host/precision_gate.hpp`, `apps/fsot_precision.cpp`, `reference/` |
| H-03 V_cs alias | (not used) | second-row identity, as the hub CKM script | `seed_leaves.hpp::ckm_double` |
| H-12 post-hoc refinements | (not present) | frozen-pending with dated sha256, exploratory numbers only; CTest `refinement_freeze` | `docs/freezes/REFINEMENTS_2026-10-02.*` |
| H-13 H0 channel | Planck 67.4(5) | CMB+BAO 68.43(27) per hub `seed_h0_global` (Planck, SH0ES printed as alternates) | `reference/prediction_map_2026-10-02.tsv`, `reference/evidence/arxiv_extracts.tsv` |
| H-14 α_s object | pin 1/(eπ) scored as MS-bar α_s(M_Z) | hub `seed_alpha_s_MZ` route `seed` (pin row kept as alternate) | `apps/fsot_precision.cpp`, map |
| H-18 refinements 02b | (not present) | frozen-pending columns, never counted as confirmed; CTests `refinement_freeze_b`, `refinements_b_crosscheck` | `docs/freezes/REFINEMENTS_2026-10-02b.*`, `audit/refinements_2026-10-02b.tsv` |

Trit-format fixes T-1 to T-5 were applied in the affected repos in Milestone 3 (one push each). Status, SHAs and
the items deliberately left unchanged are in `docs/TRIT_SPEC.md` §4a. The 188-miss breakdown is in `docs/PRECISION_M3.md`.

**Results, hub data @ 6f9c2560, pin AEB2AD** (full per-file report: `golden/ledger_b_corrected_6f9c2560.tsv`,
regenerated and diffed in CI):

| Quantity | Parity | Corrected (M2) | Corrected (M3, current) |
|---|---|---|---|
| Gated scalars above 0.5 % | 0 | 6,378 (in 46 files) | **9 (in 7 files)**: 7 formula misses + 2 rows labelled `fsot_prediction` (see PRECISION_M3) |
| Green files (of 477 active) | 477 | 436 | **471** |
| Stored `error_pct` disagreeing with its own fields (tolerance 1e−6 + 1e−4·err) | — | 56,804 | 50,436 |
| Scalars gated on the stored value (`stored_only`) | — | 2,607 | 9,735 (incl. 930 zero-target, 6,198 rounded-computed) |
| Inequality-bound / contraction rows | — | — | 17 / 1 |
| Ledger B structural corrections among gated scalars | — | 139,400 | 139,400 |
| **Genuine predictions among gated scalars** | — | **43,796** (188 above 0.5 %) | **43,796 (7 above 0.5 %)** |
| Ledger B records whose error can't be reproduced from the emitted `computed` | 47,994 of 140,088 (`round(c,6)`) | 0 (`round_sig(c,12)`) | 0 |
| Non-standard JSON tokens | 257 NaN in 1 file, read silently | same, logged (first at line 785) | same |

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
