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
