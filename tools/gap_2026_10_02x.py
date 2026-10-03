#!/usr/bin/env python3
"""Round-x: Diakonov-Petrov instanton-vacuum gap equation for the dynamical quark mass M(0) (FREEZE_2026-10-02x, X-2).
n = 4 N_c Int d^4p/(2pi)^4 M(p)^2/(p^2+M(p)^2), M(p) = M0 F(p rho)^2, F(k) = 2z[I0K1 - I1K0](z) - 2 I1K1(z), z = k/2, F(0) = 1.
Imported by the round-x scorer; numpy/scipy (exponentially scaled Bessel functions)."""
import math
from scipy.special import i0e, i1e, k0e, k1e
from scipy.integrate import quad
from scipy.optimize import brentq
def F(k):
    if k < 1e-8: return 1.0
    z = k / 2
    return 2 * z * (i0e(z) * k1e(z) - i1e(z) * k0e(z)) - 2 * i1e(z) * k1e(z)
def rhs(M0, rho, Nc=3):
    f = lambda p: p**3 * (M0 * F(p * rho)**2)**2 / (p**2 + (M0 * F(p * rho)**2)**2)
    tot = sum(quad(f, a, b, limit=400, epsabs=0, epsrel=1e-12)[0] for a, b in ((0, 1 / rho), (1 / rho, 5 / rho), (5 / rho, 200 / rho)))
    return 4 * Nc / (2 * math.pi)**4 * 2 * math.pi**2 * tot
def M0_of(n, rho, Nc=3):
    return brentq(lambda M: rhs(M, rho, Nc) - n, 10.0, 3000.0, xtol=1e-12, rtol=1e-14)
if __name__ == "__main__":
    print("F(1e-6)", F(1e-6), "F(1)", F(1.0), flush=True)
    print("DP validation M0", M0_of(200.0**4, 1 / 600.0), flush=True)
def write_json(path, n4):
    import json
    out = {"generated_by": "tools/gap_2026_10_02x.py", "freeze": "FREEZE_2026-10-02x",
           "validation_DP_M0_MeV": float("%.12g" % M0_of(200.0**4, 1 / 600.0)), "FSOT_n_quarter_MeV": n4,
           "FSOT_rho_inv_MeV": 3 * n4, "FSOT_M0_MeV": float("%.12g" % M0_of(n4**4, 1 / (3 * n4)))}
    open(path, "w").write(json.dumps(out, indent=1) + "\n")
