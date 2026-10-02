#!/usr/bin/env python3
"""Verify DERIVATIONS_2026-10-02d and REFINEMENTS_2026-10-02d sha256 files, and that the committed step-2 outputs match the freeze (stdlib only)."""
import hashlib, json, os, sys
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."); D = os.path.join(R, "docs", "freezes"); bad = 0
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
for s in ("DERIVATIONS_2026-10-02d.sha256", "REFINEMENTS_2026-10-02d.sha256"):
    for line in open(os.path.join(D, s), encoding="utf-8"):
        want, name = line.split()
        if sha(os.path.join(D, name)) != want: print("FAIL", name); bad += 1
fr = json.load(open(os.path.join(D, "REFINEMENTS_2026-10-02d.json"), encoding="utf-8"))
for k, p in (("training_output_sha256", "audit/train_2026-10-02d.tsv"), ("rows_output_sha256", "audit/rows_2026-10-02d.tsv")):
    if sha(os.path.join(R, p)) != fr[k]: print("FAIL", p); bad += 1
for n, h in fr["derivations_sha256"].items():
    if sha(os.path.join(D, n)) != h: print("FAIL derivations", n); bad += 1
print(f"freeze 02d: accepted rules {fr['accepted_rules']}, failures {bad}"); sys.exit(1 if bad else 0)
