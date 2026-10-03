#!/usr/bin/env python3
"""Round-p heavy computations under FREEZE_2026-10-02p (run alone: ulimit -v 6000000). Needs numpy + scipy.
Writes audit/heavy_2026-10-02p.json, read by tools/score_2026_10_02p.py (CI does not rerun this job).

  python tools/heavy_2026_10_02p.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/heavy_2026-10-02p.json [--only TAG] [--small]
"""
import argparse, json, math, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
import fsot02d as X
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--only", default=None); ap.add_argument("--small", action="store_true"); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves()
mp = float(X.kg_to_GeV(L["m_p_kg"]) * 1000); mpP = 938.27208943; Fpi = 130.2 / math.sqrt(2)
out = {"generated_by": "tools/heavy_2026_10_02p.py", "freeze": "FREEZE_2026-10-02p", "inputs": {"m_p": mp}}
xs = [0.6 + 0.1 * i for i in range(15)]
def log(*s): print(*s, flush=True)
def case(tag, M, Mpv, MN, D=12.0, km=12.0, Km=12, sc=True):
    if a.small: D, km, Km = 10.0, 8.0, 6
    t0 = time.time(); ang = C.Angular(Km); rad = C.Radial(D, km); C.RAD = rad; O = R.Ops(ang)
    z = lambda r: 0 * r
    v1 = C.spectrum(z, 1.0, ang, rad, Km, True); v2 = C.spectrum(z, Mpv, ang, rad, Km, True); vac = (C.esum(v1), C.esum(v2))
    scan = [(x,) + C.energy(x, Mpv, ang, rad, Km, 3, vac) for x in xs]
    k = min(range(len(scan)), key=lambda i: scan[i][1]); edge = k in (0, len(scan) - 1)
    if not edge:
        (x0, y0), (x1, y1), (x2, y2) = [(scan[i][0], scan[i][1]) for i in (k - 1, k, k + 1)]
        den = (x0 - x1) * (x0 - x2) * (x1 - x2); A_ = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / den
        B_ = (x2 * x2 * (y0 - y1) + x1 * x1 * (y2 - y0) + x0 * x0 * (y1 - y2)) / den; xm = -B_ / (2 * A_)
    else:
        xm = scan[k][0]
    th = lambda r: -2 * np.arctan(xm * xm / (r * r))
    res = {"M_MeV": M, "Mpv_over_M": Mpv, "M_N_MeV": MN, "D": D, "kmax": km, "Kmax": Km, "scan": [[float(v) for v in s] for s in scan], "x_DPP": float(xm), "edge_minimum": edge}
    res["DPP"] = R.observables(th, Mpv, ang, rad, Km, 3, vac, v1, v2, O); log(tag, "DPP", res["DPP"])
    if sc:
        thsc, conv, hist = R.self_consistent(th, Mpv, ang, rad, Km, 3, vac, log=lambda *s: log(tag, *s))
        res["SC_converged"] = conv; res["SC_history"] = hist
        res["SC_profile"] = [[float(r), float(t)] for r, t in zip(rad.r[::50], thsc[::50])]
        if conv:
            res["SC"] = R.observables(R.profile_fn(rad, thsc), Mpv, ang, rad, Km, 3, vac, v1, v2, O); log(tag, "SC", res["SC"])
    res["seconds"] = round(time.time() - t0, 1); out[tag] = res
cases = [("P1_sanity_M420_F93", 420.0, math.exp(0.5 * 4 * math.pi**2 * 93.0**2 / (3 * 420.0**2)), mpP, {}),
         ("P1_FSOT", mp / 3, math.sqrt(math.e), mp, {}),
         ("P1_validation", mpP / 3, math.exp(0.5 * 4 * math.pi**2 * Fpi**2 / (3 * (mpP / 3)**2)), mpP, {}),
         ("P1_FSOT_conv", mp / 3, math.sqrt(math.e), mp, {"D": 14.0, "km": 14.0, "Km": 14, "sc": False})]   # convergence of the primary (DPP) pipeline
for tag, M, Mpv, MN, kw in cases:
    if a.only and a.only != tag: continue
    case(tag, M, Mpv, MN, **kw)
def rnd(o):
    if isinstance(o, dict): return {k: rnd(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [rnd(v) for v in o]
    if isinstance(o, (float, np.floating)): return float("%.10g" % o)
    if isinstance(o, (np.bool_,)): return bool(o)
    return o
Path(a.out).write_text(json.dumps(rnd(out), indent=1) + "\n", encoding="utf-8")
log("written", a.out)
