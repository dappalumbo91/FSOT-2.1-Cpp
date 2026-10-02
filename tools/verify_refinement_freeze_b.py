#!/usr/bin/env python3
"""Verify docs/freezes/REFINEMENTS_2026-10-02b.{json,md} against their recorded sha256 values (stdlib only)."""
import hashlib, json, os, sys
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "freezes")
doc = json.load(open(os.path.join(D, "REFINEMENTS_2026-10-02b.json"), encoding="utf-8"))
bad = 0
for c in doc["candidates"]:
    if hashlib.sha256(c["statement"].encode()).hexdigest() != c["statement_sha256"] or c.get("tier") != "frozen-pending":
        print("FAIL", c["id"]); bad += 1
if hashlib.sha256(json.dumps(doc["candidates"], sort_keys=True, separators=(",", ":")).encode()).hexdigest() != doc["candidates_sha256"]:
    print("FAIL candidates_sha256"); bad += 1
if doc["candidate_count_total"] != sum(doc["candidate_count"].values()) or len(doc["family"]) != 104:
    print("FAIL candidate count"); bad += 1
for line in open(os.path.join(D, "REFINEMENTS_2026-10-02b.sha256"), encoding="utf-8"):
    want, name = line.split()
    if hashlib.sha256(open(os.path.join(D, name), "rb").read()).hexdigest() != want:
        print("FAIL file", name); bad += 1
print(f"refinement freeze 02b: {len(doc['candidates'])} candidates, N={doc['candidate_count_total']}, failures {bad}")
sys.exit(1 if bad else 0)
