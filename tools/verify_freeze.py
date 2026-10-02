#!/usr/bin/env python3
"""Independent (Python, stdlib only) check of a freezes/*.json written by apps/fsot_freeze_domain:
every row_sha256 is re-hashed from the row as stored, the selection hash from those rows, and the 35 core rows
from the hub's scripts/audit_parameter_count.py::_domain_table_sha scheme. Exit 0 iff all match. (The C++
`fsot_freeze_domain --verify` additionally checks the rows against the LIVE engine.)"""
import hashlib, json, sys


def h(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def row_json(r: dict) -> str:
    if r["kind"] in ("closed_form", "ledger_a"):
        return json.dumps(r["row"], sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    row = {k: v for k, v in r.items() if k not in ("row_sha256", "live_scalar") and not (k == "kind" and v == "core")}
    return json.dumps(row, sort_keys=True, separators=(",", ":"))


def main(path: str) -> int:
    d = json.load(open(path, encoding="utf-8"))
    bad = [r["domain"] for r in d["domains"] if h(row_json(r)) != r["row_sha256"]]
    rows = sorted(d["domains"], key=lambda r: r["domain"])
    sel = h("[" + ",".join(row_json(r) for r in rows) + "]")
    core = [{k: v for k, v in r.items() if k not in ("row_sha256", "live_scalar", "kind")} for r in rows if r["kind"] == "core"]
    core_sha = h(json.dumps(core, sort_keys=True, separators=(",", ":"))) if len(core) == 35 else None
    ok = not bad and sel == d["selection_sha256"] and core_sha == d.get("domain_table_sha256")
    print(f"{'OK' if ok else 'FAIL'} {path}: {len(rows)} rows, {len(bad)} bad row hashes, selection {sel[:16]}, core {str(core_sha)[:16]}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
