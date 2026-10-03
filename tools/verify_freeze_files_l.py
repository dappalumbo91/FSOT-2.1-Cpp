#!/usr/bin/env python3
"""Verify the FREEZE_2026-10-02l and FREEZE_2026-10-02lm sha256 files (stdlib only)."""
import hashlib, os, sys
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "audit"); bad = 0
for line in [l_ for f_ in ("FREEZE_2026-10-02l.sha256", "FREEZE_2026-10-02lm.sha256") for l_ in open(os.path.join(D, f_), encoding="utf-8")]:
    want, name = line.split()
    if hashlib.sha256(open(os.path.join(D, name), "rb").read()).hexdigest() != want: print("FAIL", name); bad += 1
print(f"freeze 02l: failures {bad}"); sys.exit(1 if bad else 0)
