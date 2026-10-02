# Evidence tiers

`fsot_ledger_b --tier-evidence golden/tier_evidence_6f9c2560.json --tiers-out tiers.tsv` puts every gated
record, every domain, every Ledger A row and every closed-form row with a target into one of three
tiers, or into a separate bucket. The output is pinned in `golden/evidence_tiers_6f9c2560.tsv`, and CTest
`evidence_tiers_report` diffs against it. The definitions match the spec word for word so the output can be
cross-checked against the hub's own implementation:

| Tier | Definition |
|---|---|
| **TIER 1 EXPLORATORY** | The mapping was set or changed while looking at the scored data. This is the default when dated evidence is missing. |
| **TIER 2 FROZEN-PENDING** | The mapping is hashed and dated in a freeze or prereg file, but not yet scored on data that postdates it. |
| **TIER 3 CONFIRMED HELD-OUT** | The freeze predates the data or its use. |
| **STRUCTURAL/IDENTITY** (separate bucket) | Ledger B corrections and target-equals-computed rows. |

## Operational rules (C++: `include/fsot/host/tiers.hpp`)

Nothing is promoted without dated evidence. Every rule errs toward the lower tier.

1. **Bucket first.**
   - A gated record goes in the bucket if its `eval_kind` is `fsot_prediction` or `fsot_correction` (Ledger B: c = m(1+|S|α)).
   - A record also goes in the bucket if its `computed` and `measured` are numbers and are exactly equal.
   - A closed-form row goes in the bucket if its computed value equals its target exactly.
2. **When a freeze counts.** All four conditions must hold:
   - (a) It carries an explicit hash.
   - (b) The hash covers the live mapping. For `data/domain_table_freeze.json`, the C++ re-derives the sha256 itself from its own 35-row DomainConfig table, using the hub's `json.dumps(sort_keys)` layout. The frozen pin must also equal the live pin.
   - (c) Git history shows the hash in the file (pickaxe search for the earliest commit).
   - (d) It has a date. **Freeze date** = the later of the claimed date and that first commit's date, at day granularity.
3. **Data use date** = the commit that first added the benchmark file (`git log --full-history --no-renames --diff-filter=A`).
   - Records added to an existing file later have a later true use date, so this date can only err toward *not* promoting.
   - Source/publication dates inside the data aren't needed. Under "or its use", a use date after the freeze is sufficient, and the use date can't be earlier than the data.
4. **Record tiers.**
   - A non-bucket record counts as scored with the frozen domain table only if it is attributed to a core domain (`fsot_domain`, else `domain`) and its stored `fsot_scalar` equals round(S_live, 6).
   - Such a record is TIER 3 if its use date is later than the freeze date, and TIER 2 otherwise.
   - Every other record is TIER 1, with the reason recorded.
5. **Domain tiers.**
   - A core domain is TIER 2 if the domain-table freeze counts, and TIER 3 only if at least one of its records is TIER 3.
   - Any other domain (extension or unattributed) is TIER 1.
6. **Ledger A and closed-form rows.** These are TIER 1 unless a counting freeze covers their expression.

## Result at hub 6f9c2560 / pin AEB2AD

| Freeze | Counts? | Reason |
|---|---|---|
| `data/domain_table_freeze.json` | yes | sha256 `8e30e85e…` re-derived in C++. Claimed date 2026-09-14; hash in git since 2026-09-11 (`3c74a18`, which was pin FE23A2; the table is unchanged since) |
| `predictions/LEDGER_A_FREEZE.yaml` | no | dated 2026-09-14 (first commit `f183c83`, same day), expressions verbatim, **no hash** |
| `predictions/toe_prereg_freeze.json` | no | `bundle_sha256` present, but frozen at pin D1D38A, not the live pin AEB2AD |
| `predictions/preregistered_predictions_manifest.yaml` | no | `registered_at` 2026-07-10, **no hash**. The file's first commit is 2026-08-06 (`7f29b18`) |

| Class | Gated records | Domains | Ledger A rows | Closed-form rows with target |
|---|---|---|---|---|
| TIER 1 EXPLORATORY | 17,406 | 33 | 21 | 323 |
| TIER 2 FROZEN-PENDING | 3 | 35 | 0 | 0 |
| TIER 3 CONFIRMED HELD-OUT | 0 | 0 | 0 | 0 |
| STRUCTURAL/IDENTITY | 165,787 (139,400 Ledger B, 26,387 target = computed) | — | 0 | 20 |

**Why nothing is TIER 3.** All 478 benchmark files were first committed between 2026-07 and 2026-09-11. The
only freeze that counts is dated 2026-09-14. So no scored data postdates a counting freeze.

**Why the domains are only TIER 2.** The 35-row table is frozen, but only Ledger B corrections (bucket)
and 3 TIER 2 records have been scored with it.

The 33 TIER 1 domains are the extension and other domain names that appear on records and are not in the
hashed table. The per-domain table with counts and reasons is in the `domain` lines of the golden TSV.

**What would change these tiers (not a recommendation, just the rule):**
- Ledger A would become TIER 2 if `LEDGER_A_FREEZE.yaml` carried a hash of its rows.
- Any record would become TIER 3 once scored on data first committed after its counting freeze.

Evidence is regenerated in CI from the hub's git history (`tools/gen_tier_evidence.py`) and diffed against
`golden/tier_evidence_6f9c2560.json`.
