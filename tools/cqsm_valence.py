#!/usr/bin/env python3
"""Valence-level chiral quark soliton (FREEZE_2026-10-02n N-2). Units M = 1. Pure Python (double precision), deterministic.

Profile theta(r) = 2 arctan(x^2/r^2) with x = r0 M. Grand-spin-0 valence level:
  u' = -sin(th) u + (E + cos th) v ;  v' = -(2/r) v + sin(th) v - (E - cos th) u
"""
import math
RMAX, NSTEP, R0 = 12.0, 3000, 1e-6

def _th(r, x):
    return 2.0 * math.atan(x * x / (r * r))

def _rhs(r, u, v, E, x):
    t = _th(r, x); s, c = math.sin(t), math.cos(t)
    return -s * u + (E + c) * v, -2.0 * v / r + s * v - (E - c) * u

def shoot(E, x, keep=False):
    h = (RMAX - R0) / NSTEP; r = R0; u = 1.0; v = -(E + math.cos(_th(r, x))) * r / 3.0
    path = [(r, u, v)] if keep else None
    nodes = 0
    for _ in range(NSTEP):
        k1 = _rhs(r, u, v, E, x); k2 = _rhs(r + h / 2, u + h / 2 * k1[0], v + h / 2 * k1[1], E, x)
        k3 = _rhs(r + h / 2, u + h / 2 * k2[0], v + h / 2 * k2[1], E, x); k4 = _rhs(r + h, u + h * k3[0], v + h * k3[1], E, x)
        un = u + h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); v = v + h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        if un * u < 0: nodes += 1
        u = un; r += h
        if abs(u) > 1e30 or abs(v) > 1e30:
            break
        if keep: path.append((r, u, v))
    return u, nodes, path

def level(x):
    """Valence level: the highest grand-spin-0 level in (-1, 1), i.e. the one descending from the upper continuum.
    Scan E downward from 0.999 in steps of 0.01 until (nodes, sign of u(RMAX)) changes, then bisect. None if no bound level."""
    top = shoot(0.999, x); key = lambda t: (t[1], t[0] > 0); kt = key(top)
    hi = 0.999; lo = None
    for k in range(1, 200):
        E = 0.999 - 0.01 * k
        if E <= -0.999: break
        if key(shoot(E, x)) != kt: lo = E; break
        hi = E
    if lo is None:
        return None
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if key(shoot(mid, x)) == kt: hi = mid
        else: lo = mid
    return 0.5 * (lo + hi)

def axial_ratio(E, x):
    """Int(u^2 - v^2/3) r^2 / Int(u^2 + v^2) r^2, truncated at the minimum of |u|+|v| beyond the peak (start of the growing numerical tail)."""
    _, _, p = shoot(E, x, keep=True)
    w = [abs(q[1]) + abs(q[2]) for q in p]
    im = max(range(len(w)), key=lambda i: w[i]) if w[-1] < w[0] * 1e3 else max(range(len(w) // 2), key=lambda i: w[i])
    cut = min(range(im, len(w)), key=lambda i: w[i])
    num = den = 0.0
    for i in range(cut):
        r, u, v = p[i]; dr = p[i + 1][0] - r
        num += (u * u - v * v / 3) * r * r * dr; den += (u * u + v * v) * r * r * dr
    return num / den

def sea_integral(x):
    """I1 with Int r^2 [theta'^2 + 2 sin^2 theta / r^2] dr = x * I1 (scale invariance r -> x s)."""
    n, smax = 200000, 400.0; h = smax / n; tot = 0.0
    for k in range(1, n + 1):
        s = (k - 0.5) * h; t = 2.0 * math.atan(1.0 / (s * s)); dt = -4.0 * s / (s ** 4 + 1.0)
        tot += (s * s * dt * dt + 2.0 * math.sin(t) ** 2) * h
    return tot

def soliton(M, F, Nc=3):
    """Minimize E(x) = Nc M E_val(x) + 2 pi F^2 I1 x / M over x = r0 M in [0.2, 4] (golden section after a coarse scan)."""
    I1 = sea_integral(1.0)
    def Etot(x):
        e = level(x)
        return (float("inf"), None) if e is None else (Nc * M * e + 2 * math.pi * F * F * I1 * x / M, e)
    grid = [0.2 + 0.1 * k for k in range(39)]; vals = [Etot(g)[0] for g in grid]
    k = min(range(len(grid)), key=lambda i: vals[i])
    if k in (0, len(grid) - 1) or vals[k] == float("inf"):
        return {"bound": False, "x": grid[k], "I1": I1}
    a, b = grid[k - 1], grid[k + 1]; g = (math.sqrt(5) - 1) / 2
    c, d = b - g * (b - a), a + g * (b - a); fc, fd = Etot(c)[0], Etot(d)[0]
    for _ in range(30):
        if fc < fd: b, d, fd = d, c, fc; c = b - g * (b - a); fc = Etot(c)[0]
        else: a, c, fc = c, d, fd; d = a + g * (b - a); fd = Etot(d)[0]
    x = 0.5 * (a + b); Et, e = Etot(x); ax = axial_ratio(e, x)
    return {"bound": True, "x": x, "E_val": e, "E_sol": Et, "I1": I1, "axial": ax, "g_A": (Nc + 2) / 3 * ax}

if __name__ == "__main__":
    print("I1", sea_integral(1.0))
    for x in (0.5, 1.0, 2.0): print(x, level(x))
