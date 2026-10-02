#!/usr/bin/env python3
"""Print per-framework status lines (TSV: key<TAB>status<TAB>detail) from the hub's
data/cross_proof_verification_report.json, then an OVERALL line."""
import json, os, sys
from pathlib import Path
root = Path(sys.argv[1] if len(sys.argv) > 1 else str(Path(os.environ.get("XV", Path.home() / "fsot-xval")) / "hub"))
r = json.loads((root / "data/cross_proof_verification_report.json").read_text(encoding="utf-8"))
def cnt(v):
    out = []
    for k in ("chunk_count", "obligation_count", "passed_count", "failed_count"):
        if k in v: out.append(f"{k}={v[k]}")
    ch = v.get("chunks") or v.get("chunk_results")
    if isinstance(ch, list) and ch:
        ok = sum(1 for c in ch if isinstance(c, dict) and c.get("status") in ("passed", "ok", True) or (isinstance(c, dict) and c.get("passed") is True))
        out.append(f"chunks_ok={ok}/{len(ch)}")
        bad = [c.get("file") or c.get("theory") or c.get("name") for c in ch if isinstance(c, dict) and not (c.get("status") in ("passed", "ok") or c.get("passed") is True)]
        if bad: out.append("not_ok=" + ",".join(map(str, bad[:12])))
    if v.get("reason"): out.append("reason=" + str(v["reason"])[:120])
    if v.get("engine"): out.append("engine=" + str(v["engine"]))
    return " ".join(out)
for k, v in (r.get("frameworks") or {}).items():
    if not isinstance(v, dict): continue
    st = str(v.get("status", v.get("overall_ok", "?")))
    st = {"passed": "PASS", "failed": "FAIL", "skipped": "SKIP", "True": "PASS", "False": "FAIL"}.get(st, st.upper())
    print(f"{k}\t{st}\t{cnt(v)}")
for k in ("connective_spine", "full_formal_spine", "scientific_catalog_spine", "transcendental_bounds", "gr_sm_ckm_spine"):
    v = r.get(k) or {}
    if isinstance(v, dict):
        bits = [f"{x}={v[x]}" for x in ("obligation_count", "provable_count", "margin_violation_count", "domain_count", "status") if x in v]
        print(f"spine.{k}\tINFO\t{' '.join(bits)}")
flags = {k: r.get(k) for k in ("overall_ok", "seven_way_bare_metal", "eight_way_hardware", "github_ready", "esp32_skipped")}
print("OVERALL " + " ".join(f"{k}={v}" for k, v in flags.items()))
