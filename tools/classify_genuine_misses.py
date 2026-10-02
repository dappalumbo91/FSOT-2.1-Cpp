#!/usr/bin/env python3
"""Classify the genuine (non-Ledger-B) scalar records that the M2 corrected mode put over the 0.5 % gate.

Input : a TSV written by `fsot_ledger_b --corrected-out X --genuine-misses-out misses.tsv` (columns file, index, ...)
        and the hub data directory at ledger_b_data_commit (6f9c256).
Output: audit/precision_m3_genuine_misses.tsv, one row per record: category, cause (data_handling | formula),
        and the evidence read from the record itself. Hub emitter lines cited are at hub commit 6f9c256.

Categories (same rules as include/fsot/host/ledger_b.hpp corrected mode, M3):
  zero_target       measured == 0, the row stores a residual as `computed` (error_pct == computed)  -> data_handling
  inequality_bound  formula is an inequality (<=); computed is the bound and measured <= computed     -> data_handling
  contraction       residual_after < initial_offset (contract check), not an equality                  -> data_handling
  computed_rounded  computed stored as round(x, d), d >= 6, |c - m| <= 0.5e-d (or c == 0, |m| < 5e-7)   -> data_handling
  float_noise_gate  relative error is 0.5 % in exact arithmetic, > 0.5 only by float rounding          -> data_handling
  formula_miss      fields are consistent; computed and measured differ by more than 0.5 %            -> formula
Usage: python tools/classify_genuine_misses.py --misses misses.tsv --hub-data DIR --out audit/precision_m3_genuine_misses.tsv
"""
from __future__ import annotations

import argparse
import csv
import json
from fractions import Fraction
from pathlib import Path

EMITTERS = {
    "domain_pooled_residual": "scripts/build_formula_corpus_closure_benchmark.py:33-43 writes computed=pooled median, measured=0.0, error_pct=pooled median",
    "source_pooled_residual": "scripts/circuit_component_emergence_lib.py:440-460 (and the other *_spine libs) write computed=pool, measured=0.0, error_pct=pool",
    "kepler_mean_motion_vs_a": "scripts/build_mpcorb_fsot_benchmark.py:347-351 writes computed=round(k_med,10), measured=0.0",
    "kepler_p95": "scripts/build_mpcorb_fsot_benchmark.py (diagnostic twin of kepler_mean_motion_vs_a), measured=0.0",
}
ROUNDING_SRC = {
    "founding_": "scripts/founding_unmapped_laws_lib.py:46,52 computed=round(measured*(1+|S|*0.0005),10) (tier_gap_fill_lib.py:106-109)",
    "planetary_atmospheres": "scripts/build_planetary_atmospheres_benchmark.py:129 computed=round(fsot_val,6); fsot_val=observed*(1+|S|*0.177) for observed<0.1 (:32-34)",
    "preregistered_predictions": "scripts/tier_k_toe_gap_closure_lib.py:171,180-181 computed=round(fsot*(1+|S|*0.0004),6), measured=fsot_predicted",
    "tier_96_circuit_spine": "scripts/circuit_component_emergence_lib.py:432-436 relays the source panel's computed and relabels eval_kind fsot_prediction->live_formula; the source computed was rounded by make_fsot_record (fsot_api_predict_lib.py:350, round(x,6))",
}


def repr_decimals(x: float) -> int:
    if x == 0:
        return 0
    r = repr(x)
    mant, _, exp = r.partition("e")
    e = int(exp) if exp else 0
    frac = mant.split(".")[1].rstrip("0") if "." in mant else ""
    return max(0, len(frac) - e)


def rel(c: float, m: float) -> float:
    if m == 0:
        return 0.0 if c == 0 else 100.0
    return abs(c - m) / abs(m) * 100.0


def classify(file: str, rec: dict) -> tuple[str, str, str]:
    c = float(rec["computed"])
    m = float(rec["measured"])
    stored = rec.get("error_pct")
    prop = str(rec.get("property") or "")
    formula = str(rec.get("formula") or "")
    if m == 0:
        src = EMITTERS.get(prop, "")
        return ("zero_target", "data_handling",
                f"measured=0, computed={c!r}, stored error_pct={stored!r} (== computed: {stored == c}); "
                f"|c-m|/|m| undefined (100 by convention). {src}".strip())
    if "\u2264" in formula or "<=" in formula:
        return ("inequality_bound", "data_handling",
                f"formula '{formula}'; computed={c!r} is the bound, measured={m!r} <= bound: {m <= c}; stored error_pct={stored!r}")
    if rec.get("residual_after") is not None and rec.get("initial_offset") is not None:
        ra, io = float(rec["residual_after"]), float(rec["initial_offset"])
        return ("contraction", "data_handling",
                f"contract check: residual_after={ra!r} < initial_offset={io!r}: {abs(ra) < abs(io)}; measured={m!r}, "
                f"computed={c!r} = 1-residual_after/initial_offset; stored error_pct={stored!r}")
    d = repr_decimals(c)
    if (c == 0 and abs(m) < 0.5e-6) or (c != 0 and d >= 6 and abs(c - m) <= 0.5 * 10.0 ** (-d) * (1 + 1e-9)):
        src = next((v for k, v in ROUNDING_SRC.items() if file.startswith(k)), "")
        return ("computed_rounded", "data_handling",
                f"computed={c!r} ({d} decimals), measured={m!r}, |c-m|={abs(c - m):.3g} <= 0.5e-{max(d, 6)}: the stored computed "
                f"cannot resolve the error; stored error_pct={stored!r}. {src}".strip())
    e = rel(c, m)
    if e > 0.5:
        exact = abs(Fraction(c) - Fraction(m)) / abs(Fraction(m)) * 100
        # exact rational error of the decimal inputs (period-based rows: 1/1000 vs 1/995)
        if "period_s" in rec:
            exact = abs(Fraction(1, 1000) - Fraction(1) / Fraction(str(rec["period_s"]))) / (Fraction(1) / Fraction(str(rec["period_s"]))) * 100
        if exact <= Fraction(1, 2) and float(c) == 0.001:
            return ("float_noise_gate", "data_handling",
                    f"computed={c!r} = 1/1000 Hz, measured=1/{rec.get('period_s')} Hz; exact error {float(exact)!r} % = 0.5 %, float gives {e!r}")
    sm = rec.get("scientific_measurement") or {}
    band = sm.get("reference_uncertainty_pct")
    return ("formula_miss", "formula",
            f"computed={c!r} (formula '{formula or rec.get('source') or ''}'), measured={m!r}, error {e:.4g} %; "
            f"stored error_pct={stored!r} disagrees with the fields; reference uncertainty {band} %"
            + (f" (within band)" if band is not None and e <= float(band) else ""))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--misses", required=True, type=Path)
    ap.add_argument("--hub-data", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    cache: dict[str, list] = {}
    out = [["file", "index", "name", "property", "computed", "measured", "stored_error_pct", "m2_recomputed_error_pct",
            "category", "cause", "evidence"]]
    for r in csv.DictReader(a.misses.open(encoding="utf-8"), delimiter="\t"):
        f = r["file"]
        if f not in cache:
            txt = (a.hub_data / f).read_text(encoding="utf-8")
            d = json.loads(txt.replace("-Infinity", "null").replace("Infinity", "null").replace("NaN", "null"))
            cache[f] = d.get("material_records") or d.get("records") or []
        rec = cache[f][int(r["index"])]
        cat, cause, ev = classify(f, rec)
        out.append([f, r["index"], r["name"], r["property"], r["computed"], r["measured"], r["stored_error_pct"],
                    r["recomputed_error_pct"], cat, cause, ev])
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("w", encoding="utf-8", newline="") as fh:
        csv.writer(fh, delimiter="\t", lineterminator="\n").writerows(out)
    from collections import Counter
    cnt = Counter((row[8], row[9]) for row in out[1:])
    for (cat, cause), n in sorted(cnt.items(), key=lambda kv: -kv[1]):
        print(f"{n:4d}  {cat:18s} {cause}")
    print(f"{len(out) - 1:4d}  total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
