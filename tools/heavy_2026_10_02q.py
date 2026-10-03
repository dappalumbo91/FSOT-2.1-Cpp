#!/usr/bin/env python3
"""Round-q heavy computations under FREEZE_2026-10-02q (run alone: ulimit -v 6000000; numpy/scipy). Writes audit/heavy_2026-10-02q.json after each case.

  python tools/heavy_2026_10_02q.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/heavy_2026-10-02q.json [--only TAG]
"""
import argparse, json, math, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
import fsot02d as X
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); ap.add_argument("--only", default=None); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves()
mp = float(X.kg_to_GeV(L["m_p_kg"]) * 1000); mpi = float(L["m_pi_pm_MeV"]); mpP = 938.27208943; Fpi = 130.2 / math.sqrt(2)
out = {"generated_by": "tools/heavy_2026_10_02q.py", "freeze": "FREEZE_2026-10-02q", "inputs": {"m_p": mp, "m_pi": mpi}}
xs = [0.6 + 0.1 * i for i in range(15)]
def log(*s): print(*s, flush=True)
def rnd(o):
    if isinstance(o, dict): return {k: rnd(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [rnd(v) for v in o]
    if isinstance(o, (float, np.floating)): return float("%.10g" % o)
    if isinstance(o, (np.bool_,)): return bool(o)
    return o
def save(): Path(a.out).write_text(json.dumps(rnd(out), indent=1) + "\n", encoding="utf-8")
def case(tag, M, Mpv, MN, mpiM, FM, D=10.0, km=10.0, Km=8):
    t0 = time.time(); ang = C.Angular(Km); rad = C.Radial(D, km); C.RAD = rad; O = R.Ops(ang)
    z = lambda r: 0 * r
    v1 = C.spectrum(z, 1.0, ang, rad, Km, True); v2 = C.spectrum(z, Mpv, ang, rad, Km, True); vac = (C.esum(v1), C.esum(v2))
    prof = lambda x: (lambda r: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r)))
    scan = []
    for x in xs:
        th = prof(x); s1 = C.spectrum(th, 1.0, ang, rad, Km); s2 = C.spectrum(th, Mpv, ang, rad, Km); ev = C.valence(s1)
        E = 3 * max(ev, 0.0) - 1.5 * ((C.esum(s1) - vac[0]) - (1.0 / Mpv) ** 2 * (C.esum(s2) - vac[1])) + R.mass_energy(th(rad.r), rad, mpiM, FM)
        scan.append([x, float(E), float(ev)])
    k = min(range(len(scan)), key=lambda i: scan[i][1]); edge = k in (0, len(scan) - 1)
    if not edge:
        (x0, y0), (x1, y1), (x2, y2) = [(scan[i][0], scan[i][1]) for i in (k - 1, k, k + 1)]
        den = (x0 - x1) * (x0 - x2) * (x1 - x2); A_ = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / den
        B_ = (x2 * x2 * (y0 - y1) + x1 * x1 * (y2 - y0) + x0 * x0 * (y1 - y2)) / den; xm = -B_ / (2 * A_)
    else: xm = scan[k][0]
    res = {"M_MeV": M, "Mpv_over_M": Mpv, "M_N_MeV": MN, "mpi_over_M": mpiM, "F_over_M": FM, "D": D, "kmax": km, "Kmax": Km, "scan": scan, "x_DPP": float(xm), "edge_minimum": edge}
    th = prof(xm); o = R.observables(th, Mpv, ang, rad, Km, 3, vac, v1, v2, O); o["E_m_over_M"] = R.mass_energy(th(rad.r), rad, mpiM, FM); o["E_sol_over_M"] += o["E_m_over_M"]
    res["DPP"] = o; log(tag, "DPP", o); out[tag] = res; save()
    thsc, conv, hist = R.self_consistent_m(th, Mpv, ang, rad, Km, 3, vac, mpiM, FM, log=lambda *s: log(tag, *s))
    res["SC_converged"] = conv; res["SC_history"] = hist; res["SC_profile"] = [[float(r), float(t)] for r, t in zip(rad.r[::50], thsc[::50])]
    if conv:
        f = R.profile_fn(rad, thsc); o = R.observables(f, Mpv, ang, rad, Km, 3, vac, v1, v2, O); o["E_m_over_M"] = R.mass_energy(thsc, rad, mpiM, FM); o["E_sol_over_M"] += o["E_m_over_M"]
        res["SC"] = o; log(tag, "SC", o)
    res["seconds"] = round(time.time() - t0, 1); save()
FF = math.sqrt(3) / (2 * math.pi)
cases = [("Q1_FSOT", mp / 3, math.sqrt(math.e), mp, mpi / (mp / 3), FF),
         ("Q1_sanity_M420_F93", 420.0, math.exp(0.5 * 4 * math.pi**2 * 93.0**2 / (3 * 420.0**2)), mpP, 140.0 / 420.0, 93.0 / 420.0),
         ("Q1_validation", mpP / 3, math.exp(0.5 * 4 * math.pi**2 * Fpi**2 / (3 * (mpP / 3)**2)), mpP, 139.57039 / (mpP / 3), Fpi / (mpP / 3))]
for tag, M, Mpv, MN, mpiM, FM in cases:
    if a.only and a.only != tag: continue
    case(tag, M, Mpv, MN, mpiM, FM)
log("written", a.out)
