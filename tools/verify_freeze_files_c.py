#!/usr/bin/env python3
"""Verify the sha256 files of PROTOCOL_2026-10-02c and REFINEMENTS_2026-10-02c, and that the training output matches the freeze (stdlib only)."""
import hashlib, json, os, sys
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."); D = os.path.join(R, "docs", "freezes"); bad = 0
for s in ("PROTOCOL_2026-10-02c.sha256", "REFINEMENTS_2026-10-02c.sha256"):
    for line in open(os.path.join(D, s), encoding="utf-8"):
        want, name = line.split()
        if hashlib.sha256(open(os.path.join(D, name), "rb").read()).hexdigest() != want: print("FAIL", name); bad += 1
fr = json.load(open(os.path.join(D, "REFINEMENTS_2026-10-02c.json"), encoding="utf-8"))
if hashlib.sha256(open(os.path.join(R, "audit", "train_2026-10-02c.tsv"), "rb").read()).hexdigest() != fr["training_output_sha256"]: print("FAIL training output sha"); bad += 1
print(f"freeze 02c: accepted rules {fr['accepted_rules']}, patterns {fr['patterns_examined_total']}, failures {bad}"); sys.exit(1 if bad else 0)
