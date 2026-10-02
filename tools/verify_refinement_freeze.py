#!/usr/bin/env python3
"""Verify docs/freezes/REFINEMENTS_2026-10-02.{json,md} against their recorded sha256 values (stdlib only)."""
import hashlib, json, os, sys
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "freezes")
J = os.path.join(D, "REFINEMENTS_2026-10-02.json")
bad = 0
doc = json.load(open(J, encoding="utf-8"))
for r in doc["refinements"]:
    h = hashlib.sha256(r["statement"].encode()).hexdigest()
    if h != r["statement_sha256"] or r.get("tier") != "frozen-pending":
        print("FAIL", r["id"], h); bad += 1
h = hashlib.sha256(json.dumps(doc["refinements"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
if h != doc["refinements_sha256"]:
    print("FAIL refinements_sha256", h); bad += 1
for line in open(os.path.join(D, "REFINEMENTS_2026-10-02.sha256"), encoding="utf-8"):
    want, name = line.split()
    got = hashlib.sha256(open(os.path.join(D, name), "rb").read()).hexdigest()
    if got != want:
        print("FAIL file", name, got); bad += 1
print(f"refinement freeze: {len(doc['refinements'])} refinements, tier {doc['tier']}, failures {bad}")
sys.exit(1 if bad else 0)
