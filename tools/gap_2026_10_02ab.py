#!/usr/bin/env python3
"""Round-ab (FREEZE_2026-10-02ab, AB-1): instanton size from the DP variational self-consistency n rho^4 = nu/(beta(rho) gamma^2),
then M/m_p from the unchanged gap equation with rho = rho_bar (n read in proton units as in AA-1). Writes audit/gap_2026-10-02ab.json (numpy/scipy)."""
import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scipy.optimize import brentq
import gap_2026_10_02x as G
Nc = 3; b = 11 * Nc / 3; nu = (b - 4) / 2; g2 = 27 * math.pi**2 * Nc / (4 * (Nc**2 - 1)); c = 0.65   # c = n^(1/4)/Lambda_PV (round-t FSOT Lambda^(0))
AA = json.loads((Path(__file__).resolve().parents[1] / "audit/gap_2026-10-02aa.json").read_text())
n4 = AA["n_quarter_over_mp"]
def eq1(x): return x**4 * b * math.log(c / x) * g2 - nu                         # one loop (frozen primary)
def eq2(x):
    L = math.log(c / x); return x**4 * (b * L + 102 / b * math.log(L)) * g2 - nu  # two loop (information)
x1 = brentq(eq1, 0.05, 0.5, xtol=1e-15)
xs = [0.05 + 0.001 * i for i in range(600) if 0.05 + 0.001 * (i + 1) < c - 1e-9]
try:
    x2 = next(brentq(eq2, u, u + 0.001, xtol=1e-15) for u in xs if eq2(u) * eq2(u + 0.001) < 0)
except StopIteration:
    x2 = None
k = G.M0_of(1000.0**4, x1 / 1000.0) / 1000.0                                     # M0/n^(1/4) at rho n^(1/4) = x1
out = {"generated_by": "tools/gap_2026_10_02ab.py", "freeze": "FREEZE_2026-10-02ab", "b": b, "nu": nu, "gamma2": g2, "n_quarter_over_Lambda_PV": c,
       "x_rho_n_quarter": float("%.12g" % x1), "R_over_rho": float("%.12g" % (1 / x1)), "beta_rho_bar": float("%.12g" % (b * math.log(c / x1))),
       "Lambda_PV_rho_bar": float("%.12g" % (x1 / c)), "packing_pi2_n_rho4": float("%.12g" % (math.pi**2 * x1**4)),
       "info_two_loop_x": (float("%.12g" % x2) if x2 else None), "n_quarter_over_mp": n4, "M0_over_n_quarter": float("%.12g" % k), "M_over_mp": float("%.12g" % (k * n4)),
       "aa_M_over_mp": AA["M_over_mp"]}
(Path(__file__).resolve().parents[1] / "audit/gap_2026-10-02ab.json").write_text(json.dumps(out, indent=1) + "\n"); print(out)
