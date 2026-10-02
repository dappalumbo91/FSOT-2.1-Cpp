#!/usr/bin/env python3
"""C++ (audit/precision_2026-10-02.tsv, mp169) vs Python/mpmath (audit/refinements_2026-10-02b.tsv) for the
2026-10-02b channel fixes and frozen-pending candidates. stdlib only; relative agreement 1e-12 required."""
import os, sys
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "audit")
cpp = {}
for l in open(os.path.join(A, "precision_2026-10-02.tsv"), encoding="utf-8"):
    if l.startswith("#"): continue
    f = l.rstrip("\n").split("\t")
    cpp[f[0]] = f
py = {}
for l in open(os.path.join(A, "refinements_2026-10-02b.tsv"), encoding="utf-8"):
    f = l.rstrip("\n").split("\t")
    if f[0] in ("fix", "candidate") and (f[0] == "fix" and f[5] in ("H0_CMB_BAO", "alpha_s_MZ") or f[10].startswith("chosen")):
        py[f[1]] = float(f[4])
pairs = {"F1": ("pin:wave1|H0", 3), "F2": ("alpha_s_MZ", 3), "C-MHW-1": ("pin:wave3|m_H/m_W", 19), "C-DM-1": ("pin:wave4|Dm2_21/Dm2_32", 19),
         "C-TCMB": ("pin:wave1|T_CMB", 19), "C-GZ": ("pin:wave5|Gamma_Z/M_Z", 19), "C-BD": ("pin:wave3|Deuteron_binding_MeV", 19),
         "C-MUD": ("pin:wave8|Deuteron_mu_muN", 19)}
bad = 0
for cid, (row, col) in pairs.items():
    c = float(cpp[row][col]); p = py[cid]
    ok = abs(c - p) <= 1e-12 * abs(p)
    bad += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {cid:8s} C++ {c:.15g}  Python {p:.15g}")
print(f"crosscheck 02b: {len(pairs)} values, failures {bad}")
sys.exit(1 if bad else 0)
