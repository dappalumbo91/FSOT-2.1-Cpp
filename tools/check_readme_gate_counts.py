#!/usr/bin/env python3
"""Claim-honesty check (IRONOUT PR, audit CLAIM_REQUIREMENTS A1): the pinned-only gate counts quoted in README.md
(and the current-gate sentence of docs/PRECISION_REPORT.md) must equal what the precision report prints.

The report line is audit/precision_2026-10-02.md: 'record set without the owner decisions OD-1/OD-2 (pinned rows
only ...): n=N  pass z<=1: A/N  pass |rel|<=2%: B/N'. The README must say 'Pinned rows only are A/N at z ≤ 1 and B/N at 2%'
and every '(X/N pinned only' in the README's current-gate paragraphs (the '**Current gate' and '**Gate at FREEZE_2026-10-02bg'
paragraphs) must be A/N. Exits non-zero on any mismatch."""
import re, sys, os
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
rep = open(os.path.join(root, "audit", "precision_2026-10-02.md"), encoding="utf-8").read()
m = re.search(r"pinned rows only[^\n]*?n=(\d+)\s+pass z<=1: (\d+)/(\d+)\s+pass \|rel\|<=2%: (\d+)/(\d+)", rep)
if not m:
    print("FAIL: pinned-only line not found in audit/precision_2026-10-02.md"); sys.exit(1)
n, z, n2, f = m.group(1), m.group(2), m.group(3), m.group(4)
want_z, want_f = f"{z}/{n}", f"{f}/{n}"
fails = []
readme = open(os.path.join(root, "README.md"), encoding="utf-8").read()
s = re.search(r"Pinned rows only are (\d+/\d+) at z(?: ≤ 1)? and (\d+/\d+) at 2", readme)
if not s: fails.append("README: 'Pinned rows only are ... at z and ... at 2%' sentence not found")
elif (s.group(1), s.group(2)) != (want_z, want_f): fails.append(f"README says {s.group(1)} at z / {s.group(2)} at 2%; report says {want_z} / {want_f}")
for para in re.findall(r"^\*\*(?:Current gate|Gate at FREEZE_2026-10-02bg)[^\n]*", readme, re.M):
    for q in re.findall(r"\((\d+/\d+) pinned only", para):
        if q != want_z: fails.append(f"README current-gate paragraph says {q} pinned only; report says {want_z}")
pr = open(os.path.join(root, "docs", "PRECISION_REPORT.md"), encoding="utf-8").read()
c = re.search(r"\*\*Current worktree gate[^\n]*?Pinned rows only are (\d+/\d+) at z and (\d+/\d+) at 2", pr)
if c and (c.group(1), c.group(2)) != (want_z, want_f): fails.append(f"PRECISION_REPORT current gate says {c.group(1)}/{c.group(2)}; report says {want_z}/{want_f}")
for x in fails: print("FAIL:", x)
print(f"readme_gate_counts: report pinned-only {want_z} at z, {want_f} at 2% -> " + ("OK" if not fails else f"{len(fails)} mismatch"))
sys.exit(1 if fails else 0)
