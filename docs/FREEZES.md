# Dated SHA-256 freezes (`apps/fsot_freeze_domain`)

A freeze records, on a date, a hash of the mapping that will be used to score future data. The evidence-tier report
(`docs/EVIDENCE_TIERS.md`) only counts a freeze toward TIER 2/3 if three things hold:
1. It carries an explicit hash.
2. That hash is re-derived from the live mapping by C++.
3. Git shows the hash in the file on that date.

The freeze date is the later of the claimed date and the first commit carrying the hash.

## Write
```
fsot_freeze_domain --authority <hub>/vendor/fsot_compute.py --out freezes/domain_freeze_<YYYY-MM-DD>_AEB2AD.json
    [--scope all|core|extension|closed_form|ledger_a] [--domains Name,cf:<section>/<row>,la:<id>,...] [--note TEXT]
```
- **Authority check:** the authority file is hashed and must equal `AUTHORITY_SHA256` (AEB2AD), or the tool refuses. The K line (hub `K_LINE_NEEDLE`) is checked as in the hub's `data/domain_table_freeze.json`.
- **Date:** `--date` defaults to the later of today's local and UTC dates. Earlier dates are rejected.
- **Rows:** taken from the C++ engine; nothing is chosen by hand. Each row carries `row_sha256`, plus `live_scalar` or the value (informative only, not hashed).

| Row kind | JSON hashed (sorted keys, compact) | Key |
|---|---|---|
| core (35) | `{"C","D_eff","delta_psi","delta_theta","domain","hits","observed"}`, the hub's `_domain_table_sha` row | domain name |
| extension_fold (372 reachable of 375; 3 are shadowed by a core name or an earlier fold, as in `ledger_a::domain_scalar`) | `{"D_eff","delta_psi","domain","hits","kind":"extension_fold","observed"}` | fold name |
| closed_form (368) | `{"computed","formula","kind","name","section"}` (computed = Python repr string) | `cf:<section>/<name>` |
| ledger_a (21) | `{"expression","expression_id","id","kind","units","value"}` | `la:<id>` |

Hashes written to the freeze file:
- `selection_sha256`: sha256 of `"[" + row JSONs sorted by key, joined with "," + "]"`.
- `domain_table_sha256`: written when all 35 core rows are present. It equalled the hub's freeze hash `8e30e85e72091462c4d66df2d498afb36ccbc2d40eb5df01b4e083947c79dad3` up to the 2026-10-02 freeze; since the rung-6 QM decision (2026-10-23) CTest `freeze_core_sha_matches_hub_freeze` checks the current freeze `8cde2e8b…`.

## Verify
- `fsot_freeze_domain --verify freezes/X.json` checks every row against the live engine (CTest `freeze_verify_*`).
- `python3 tools/verify_freeze.py freezes/X.json` is an independent stdlib-only re-hash of the stored rows (CTest `freeze_verify_py_*`).

## How a new freeze counts
1. Commit the file under `freezes/`.
2. `tools/gen_tier_evidence.py` lists it under `cpp_freezes`, with the first commit of this repo whose version of the file carries `selection_sha256`. CI runs this with `fetch-depth: 0`.
3. `include/fsot/host/tiers.hpp` accepts it only at the live pin, and only if every frozen `row_sha256` and the `selection_sha256` equal the live rows.

Each covered domain, closed-form row and Ledger A row then gets the earliest usable freeze date.
- **TIER 2:** a covered row is scored on data first used on or before that date.
- **TIER 3:** a non-structural record is scored with the frozen row on data first used strictly after it.

A changed mapping makes the old freeze stop covering the changed rows. It does not silently move the date.

## Freezes in this repo
| File | Date | Rows | selection_sha256 |
|---|---|---|---|
| `freezes/domain_freeze_2026-10-02_AEB2AD.json` (history; QM rung 5) | 2026-10-02 | 35 core + 372 extension + 368 closed-form + 21 Ledger A = 796 | `580eb6e72ca75e2995b4331828b7a9f513978ce5c5aa3d7a798c2b83de4182dd` |
| `freezes/domain_freeze_2026-10-23_AEB2AD.json` (current; QM rung 6, owner decision 2026-10-23) | 2026-10-23 | 796 (same split); core domain_table_sha256 `8cde2e8bfafa2576eb4f5c6199f1f5b647b573d3d759ebf5556924a3364a42d1` | `18c80999b0aa6c631585354f495535dd7c7175dfa2ecdf9ccb89e976ddad98cc` |

Effect on the tier report (`golden/evidence_tiers_6f9c2560.tsv`):
- **Domains:** TIER1 33 → 12 and TIER2 35 → 56. The extension domains that appear in hub records are now frozen.
- **Ledger A:** 21 rows TIER1 → TIER2.
- **Closed-form rows with targets:** 323 TIER2, 20 STRUCTURAL.
- **Records:** unchanged (T2 = 3, T3 = 0). Every hub record attributed to an extension domain is STRUCTURAL.

Nothing is TIER 3 yet, because no data first used after a freeze has been scored. `docs/PROMOTION_WATCH.md` lists candidate data.

Effect of `freezes/domain_freeze_2026-10-23_AEB2AD.json` (rung 6 QM, 2026-10-23):
- The hub `data/domain_table_freeze.json` (8e30e85e…) and the 2026-10-02 C++ freeze are both NOT-USABLE at the live mapping. The 2026-10-02 freeze fails on the Quantum_Mechanics row.
- **Domains:** TIER1 12, TIER2 56 (unchanged).
- **Ledger A:** 21 rows at TIER2 (unchanged).
- **Closed-form rows:** 323 at TIER2 (unchanged).
- **Records:** T2 3 → 2. The Quantum_Mechanics hub record was scored with the rung-5 scalar, so it no longer matches any usable frozen row and drops to TIER1.
- `freeze_verify_domain_freeze_2026-10-02_AEB2AD` fails by design, because the history file no longer equals the live mapping. `freeze_verify_py_…` (stored-row re-hash) still passes.
