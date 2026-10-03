#!/usr/bin/env python3
"""Round-ag (FREEZE_2026-10-02ag, AG-2; code of round ae with box size D and momentum cutoff kmax decoupled from K): soliton at M/m_p 0.458168 (round ab) with the pre-registered window 0.5-1.6, at a given K;
at the DPP minimum: R.observables plus the sea/PV/vacuum splits of the rotational sums A, Amu, B (for the PV-regularised g_A and mu).
  python tools/murun_2026_10_02ag.py --K 12 --D 14 --kmax 12 -> audit/murun_2026-10-02ag_K12_D14_k12.json (numpy/scipy)"""
import argparse, json, math, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
ap = argparse.ArgumentParser(); ap.add_argument("--K", type=int, default=12); ap.add_argument("--D", type=float, default=14.0); ap.add_argument("--kmax", type=float, default=12.0); a = ap.parse_args(); Km = a.K
RT = Path(__file__).resolve().parents[1]
inp = json.loads((RT / "audit/heavy_2026-10-02ab_wide_K12.json").read_text())["inputs"]
Mpv = inp["Mpv_over_M"]; mpiM = inp["mpi_over_mp"] / inp["M_over_mp"]; FM = inp["F_over_M"]; t0 = time.time()
ang = C.Angular(Km); rad = C.Radial(a.D, a.kmax); C.RAD = rad; O = R.Ops(ang)
z = lambda r: 0 * r
v1 = C.spectrum(z, 1.0, ang, rad, Km, True); v2 = C.spectrum(z, Mpv, ang, rad, Km, True); vac = (C.esum(v1), C.esum(v2))
prof = lambda x: (lambda r: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r)))
xs = [0.5 + 0.1 * i for i in range(12)]
def scan(xs):
    out = []
    for x in xs:
        th = prof(x); s1 = C.spectrum(th, 1.0, ang, rad, Km); s2 = C.spectrum(th, Mpv, ang, rad, Km); ev = C.valence(s1)
        E = 3 * max(ev, 0.0) - 1.5 * ((C.esum(s1) - vac[0]) - (1.0 / Mpv) ** 2 * (C.esum(s2) - vac[1])) + R.mass_energy(th(rad.r), rad, mpiM, FM)
        out.append([x, float(E), float(ev)]); print("scan", x, round(time.time() - t0, 1), flush=True)
    return out
sc = scan(xs)
k = min(range(len(sc)), key=lambda i: sc[i][1])
if k == len(sc) - 1:
    sc += scan([xs[-1] + 0.1 * i for i in range(1, 6)]); k = min(range(len(sc)), key=lambda i: sc[i][1])
edge = k in (0, len(sc) - 1)
if not edge:
    (x0, y0), (x1, y1), (x2, y2) = [(sc[i][0], sc[i][1]) for i in (k - 1, k, k + 1)]
    den = (x0 - x1) * (x0 - x2) * (x1 - x2); A_ = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / den
    B_ = (x2 * x2 * (y0 - y1) + x1 * x1 * (y2 - y0) + x0 * x0 * (y1 - y2)) / den; xm = -B_ / (2 * A_)
else: xm = sc[k][0]
th = prof(xm); o = R.observables(th, Mpv, ang, rad, Km, 3, vac, v1, v2, O)
s1 = C.spectrum(th, 1.0, ang, rad, Km, True); s2 = C.spectrum(th, Mpv, ang, rad, Km, True); ev = C.valence(s1)
OPS = {"A": ([(O.sxt[c], "sxt%d" % c, "const") for c in range(3)], [(O.tau[c], "tau%d" % c, "const") for c in range(3)], 6.0),
       "Amu": ([(O.rxs_x_tau[c], "rxt%d" % c, "rfield") for c in range(3)], [(O.tau[c], "tau%d" % c, "const") for c in range(3)], 6.0),
       "B": ([(O.tau[c], "tau%d" % c, "const") for c in range(3)], [(O.rxs[c], "rxs%d" % c, "rfield") for c in range(3)], 1.0)}
split = {}
for nm, (X, Y, dv) in OPS.items():
    f = lambda sp, e: complex(R.rot_sum(O, sp, e, X, Y) / dv)
    tot, sea, pv, va, vb = f(s1, ev), f(s1, None), f(s2, None), f(v1, None), f(v2, None)
    split[nm] = {"tot": [tot.real, tot.imag], "sea": [sea.real, sea.imag], "pv": [pv.real, pv.imag], "vac": [va.real, va.imag], "vacpv": [vb.real, vb.imag]}
    print(nm, split[nm], round(time.time() - t0, 1), flush=True)
rnd = lambda v: float("%.10g" % v)
out = {"generated_by": "tools/murun_2026_10_02ag.py", "freeze": "FREEZE_2026-10-02ag", "K": Km, "D": a.D, "kmax": a.kmax, "inputs": inp, "scan": sc, "x_DPP": rnd(xm), "edge_minimum": edge,
       "DPP": {k_: rnd(v) for k_, v in o.items()}, "split": {n: {k_: [rnd(u) for u in v] for k_, v in d.items()} for n, d in split.items()}, "seconds": round(time.time() - t0, 1)}
(RT / ("audit/murun_2026-10-02ag_K%d_D%g_k%g.json" % (Km, a.D, a.kmax))).write_text(json.dumps(out, indent=1) + "\n"); print("written", flush=True)
