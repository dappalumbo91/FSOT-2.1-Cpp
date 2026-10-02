#!/usr/bin/env python3
"""Golden values for the C++ Ledger A emit and property routing, produced by the hub's own Python.

Rows (tab-separated, floats as repr):
  A      <id>  value  error_pct  pin                      fsot_ledger_a_lib.compare_anchor(id)
  MASS   <formula>  mass|None                             fsot_api_predict_lib.formula_mass
  ROUTE  <property>  routed_domain  factor                route_property(property, "<default>")
  REC    property  domain  formula  measured  ->  computed error_pct eval_kind fsot_domain fsot_scalar
                                                          make_fsot_record(...) on inputs taken from the
                                                          benchmark corpus (deterministic sample)
Usage: python tools/dump_ledger_a_routing_golden.py --hub /path/to/FSOT-2.1-Lean
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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
    ap.add_argument("--out", default=str(ROOT / "golden" / "ledger_a_routing.tsv"))
    ap.add_argument("--max-rec", type=int, default=8000)
    a = ap.parse_args()
    hub = Path(a.hub).resolve()
    pin = json.loads((ROOT / "AUTHORITY_PIN.json").read_text())
    if hashlib.sha256((hub / "vendor" / "fsot_compute.py").read_bytes()).hexdigest().upper() != pin["authority_sha256"]:
        sys.exit("authority PIN MISMATCH")
    commit = subprocess.run(["git", "-C", str(hub), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    if commit != pin["ledger_b_data_commit"]:
        sys.exit(f"hub commit {commit[:8]} != pinned")
    sys.path.insert(0, str(hub / "scripts"))
    sys.path.insert(0, str(hub / "vendor"))
    import fsot_ledger_a_lib as la  # noqa: E402
    import fsot_api_predict_lib as pl  # noqa: E402
    import fsot_compute as fc  # noqa: E402
    from fsot_canonical_adapter import _extension_folds  # noqa: E402

    known = set(fc.DOMAINS) | set(_extension_folds())
    lines = [f"#hub_commit\t{commit}"]
    for oid in la.LEDGER_A:
        c = la.compare_anchor(oid)
        lines.append("\t".join(["A", oid, fmt(c["value"]), fmt(c["error_pct"]), c["pin"]]))
    formulas, props, recs = set(), set(), []
    files = sorted(glob.glob(str(hub / "data" / "*_benchmark.json")))
    for p in files:
        try:
            d = json.loads(Path(p).read_text(encoding="utf-8"))
        except Exception:
            continue
        for r in d.get("material_records") or d.get("records") or []:
            if not isinstance(r, dict):
                continue
            f = r.get("formula")
            if isinstance(f, str) and f and "\t" not in f and "\n" not in f:
                formulas.add(f)
            pr = r.get("property")
            if isinstance(pr, str) and pr and "\t" not in pr:
                props.add(pr)
                m, dom = r.get("measured"), r.get("fsot_domain")
                if isinstance(m, (int, float)) and not isinstance(m, bool) and isinstance(dom, str) and dom in known:
                    recs.append((pr, dom, f if isinstance(f, str) and "\t" not in f else "", float(m)))
    for f in sorted(formulas) + ["", "H2O", "C6H12O6", "NaCl", "Xx2", "h2o", "(CH3)2CO", "C12H22O11", "Fe2O3"]:
        lines.append("\t".join(["MASS", f, fmt(pl.formula_mass(f))]))
    for pr in sorted(props | set(dict.keys(pl.PROPERTY_ROUTING))):
        d, fac = pl.route_property(pr, "<default>")
        lines.append("\t".join(["ROUTE", pr, d, fmt(fac)]))
    recs = sorted(set(recs))
    step = max(1, len(recs) // a.max_rec)
    nrec = 0
    for pr, dom, f, m in recs[::step]:
        rec = pl.make_fsot_record(lab="golden", property_name=pr, name="x", measured=m, domain=dom, formula=f or None)
        lines.append("\t".join(["REC", pr, dom, f, fmt(m), fmt(rec["computed"]), fmt(rec["error_pct"]), rec["eval_kind"],
                                rec["fsot_domain"], fmt(rec["fsot_scalar"])]))
        nrec += 1
    Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {a.out}: A={len(la.LEDGER_A)} MASS={len(formulas)+9} ROUTE={len(props | set(pl.PROPERTY_ROUTING))} REC={nrec} (of {len(recs)} distinct)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
