#!/usr/bin/env python3
"""Verify the FREEZE_2026-10-02ag sha256 file (stdlib only)."""
import hashlib, os, sys
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "audit"); bad = 0
for line in open(os.path.join(D, "FREEZE_2026-10-02ag.sha256"), encoding="utf-8"):
    want, name = line.split()
    if hashlib.sha256(open(os.path.join(D, name), "rb").read()).hexdigest() != want: print("FAIL", name); bad += 1
print(f"freeze 02ag: failures {bad}"); sys.exit(1 if bad else 0)
