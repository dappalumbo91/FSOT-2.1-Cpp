#!/usr/bin/env python3
"""Golden values for the C++ Ledger B re-scorer, produced by the hub's own Python.

Runs FSOT-2.1-Lean `scripts/benchmark_margin_lib.analyze_benchmark` (the code behind
data/benchmark_margin_audit.json and the 477/477 green gate) over every
data/*_benchmark.json at the pinned hub data commit, and re-scores every Ledger B
record (eval_kind fsot_prediction / fsot_correction routed to a 35-core domain) with
the hub's own law c = m(1+|S|f), f = ALPHA (scripts/fsot_api_predict_lib.fsot_correct),
using vendor/fsot_compute.py (pin-checked). Floats are written with repr() so the
C++ side can demand bit-identical doubles.

Usage: python tools/dump_ledger_b_golden.py --hub /path/to/FSOT-2.1-Lean [--out golden/ledger_b_<commit8>.tsv]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "records", "pooled_median_error_pct", "scalar_count", "scalar_median_error_pct",
    "max_scalar_error_pct", "effective_scalar_median_error_pct", "max_effective_scalar_error_pct",
    "worst_effective_scalar_error_pct", "rounding_ghost_scalar_count", "catalog_crosswalk_scalar_count",
    "strict_scalar_pass", "effective_scalar_pass", "max_gate_scalar_error_pct",
    "tier_scalar_median_error_pct", "tier_scalar_pass", "tier_scalar_max_pass", "scalar_median_pass",
    "classifier_count", "classifier_correct", "classifier_accuracy_pct", "classifier_pass",
    "official_pooled_median_error_pct", "green_gate_pass",
    "max_scalar_name", "max_scalar_property", "max_gate_scalar_name", "worst_effective_scalar_name",
]


def fmt(v) -> str:
    if v is None:
        return "None"
    if isinstance(v, bool):
        return "True" if v else "False"
    if isinstance(v, float):
        return repr(v)
    return str(v).replace("\t", " ").replace("\n", " ")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hub", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    hub = Path(a.hub).resolve()
    pin = json.loads((ROOT / "AUTHORITY_PIN.json").read_text())
    auth = hub / "vendor" / "fsot_compute.py"
    sha = hashlib.sha256(auth.read_bytes()).hexdigest().upper()
    if sha != pin["authority_sha256"]:
        sys.exit(f"PIN MISMATCH {sha[:6]}")
    try:
        commit = subprocess.run(["git", "-C", str(hub), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        commit = "unknown"
    want = pin.get("ledger_b_data_commit")
    if want and commit != want:
        sys.exit(f"hub data commit {commit[:8]} != pinned {want[:8]}")
    sys.path.insert(0, str(hub / "scripts"))
    sys.path.insert(0, str(hub / "vendor"))
    import fsot_compute as fc  # noqa: E402
    from benchmark_margin_lib import analyze_benchmark  # noqa: E402

    S = {n: float(fc.domain_scalar(n)) for n in fc.DOMAINS}
    alpha = float(fc.ALPHA)
    lines = [f"#hub_commit\t{commit}\t{sha[:6]}"]
    green = active = 0
    tot = {"lb": 0, "unrouted": 0, "c_match": 0, "s_match": 0, "e_match": 0}
    for path in sorted((hub / "data").glob("*_benchmark.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            lines.append(f"{path.name}\tload_error\tTrue")
            continue
        row = analyze_benchmark(doc, file_name=path.name)
        if row.get("excluded"):
            lines.append(f"{path.name}\texcluded\tTrue")
        else:
            active += 1
            green += bool(row["green_gate_pass"])
            for k in FIELDS:
                lines.append(f"{path.name}\t{k}\t{fmt(row.get(k))}")
        # Ledger B re-score with the live law
        lb = unrouted = c_match = s_match = e_match = 0
        max_dev = 0.0
        for r in (doc.get("material_records") or doc.get("records") or []):
            if not isinstance(r, dict) or r.get("eval_kind") not in ("fsot_prediction", "fsot_correction"):
                continue
            dom = r.get("fsot_domain")
            m = r.get("measured")
            if dom not in S or isinstance(m, bool) or not isinstance(m, (int, float)):
                unrouted += 1
                continue
            lb += 1
            m = float(m)
            c = m * (1.0 + abs(S[dom]) * alpha)
            cr = round(c, 6) if abs(c) < 1e6 else round(c, 4)
            err = abs(c - m) / abs(m) * 100.0 if m != 0 else abs(c - m) * 100.0
            stored_c = r.get("computed")
            if isinstance(stored_c, (int, float)) and not isinstance(stored_c, bool):
                if float(stored_c) == cr:
                    c_match += 1
                if cr != 0:
                    max_dev = max(max_dev, abs(float(stored_c) - cr) / abs(cr))
            if r.get("fsot_scalar") is not None and float(r["fsot_scalar"]) == round(S[dom], 6):
                s_match += 1
            if r.get("error_pct") is not None and float(r["error_pct"]) == round(err, 6):
                e_match += 1
        if lb or unrouted:
            for k, v in (("lb_records", lb), ("lb_unrouted", unrouted), ("lb_computed_match", c_match),
                         ("lb_scalar_match", s_match), ("lb_error_match", e_match), ("lb_max_rel_dev", max_dev)):
                lines.append(f"{path.name}\t{k}\t{fmt(v)}")
        tot["lb"] += lb; tot["unrouted"] += unrouted; tot["c_match"] += c_match; tot["s_match"] += s_match; tot["e_match"] += e_match
    lines.append(f"#summary\tactive\t{active}")
    lines.append(f"#summary\tgreen\t{green}")
    for k, v in tot.items():
        lines.append(f"#summary\t{k}\t{v}")
    out = Path(a.out) if a.out else ROOT / "golden" / f"ledger_b_{commit[:8]}.tsv"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}: active={active} green={green} ledgerB={tot}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
