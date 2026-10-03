#!/usr/bin/env python3
"""Round-aa soliton (FREEZE_2026-10-02aa, AA-1): M/m_p from the gap equation with the condensate pin read in proton units (audit/gap_2026-10-02aa.json), F/m_p = 1/(2 sqrt3 pi) fixed, M_PV/M from the PV condition (massive DPP basis convergence; scan restricted to r0 M in [0.6, 1.0], identical to the full scan whenever the minimum is interior; timing logged) (run alone: ulimit -v 6000000; numpy/scipy). Writes audit/heavy_2026-10-02v.json after each case.

  python tools/heavy_2026_10_02v.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/heavy_2026-10-02v.json [--only TAG]
"""
import argparse, json, math, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
import fsot02d as X
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); ap.add_argument("--only", default=None); ap.add_argument("--sc-itmax", type=int, default=40); ap.add_argument("--K", type=int, default=12);  a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves()
mp = float(X.kg_to_GeV(L["m_p_kg"]) * 1000); mpi = float(L["m_pi_pm_MeV"]); mpP = 938.27208943; Fpi = 130.2 / math.sqrt(2)
out = {"generated_by": "tools/heavy_2026_10_02aa.py", "freeze": "FREEZE_2026-10-02aa", "inputs": {"m_p": mp, "m_pi": mpi}}
xs = [0.5 + 0.1 * i for i in range(7)]  # round v: interior-minimum scan window (the parabola uses only the 3 points around the minimum)
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
        scan.append([x, float(E), float(ev)]); log(tag, "scan", x, round(time.time() - t0, 1))
    k = min(range(len(scan)), key=lambda i: scan[i][1]); edge = k in (0, len(scan) - 1)
    if not edge:
        (x0, y0), (x1, y1), (x2, y2) = [(scan[i][0], scan[i][1]) for i in (k - 1, k, k + 1)]
        den = (x0 - x1) * (x0 - x2) * (x1 - x2); A_ = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / den
        B_ = (x2 * x2 * (y0 - y1) + x1 * x1 * (y2 - y0) + x0 * x0 * (y1 - y2)) / den; xm = -B_ / (2 * A_)
    else: xm = scan[k][0]
    res = {"M_MeV": M, "Mpv_over_M": Mpv, "M_N_MeV": MN, "mpi_over_M": mpiM, "F_over_M": FM, "D": D, "kmax": km, "Kmax": Km, "scan": scan, "x_DPP": float(xm), "edge_minimum": edge}
    th = prof(xm); o = R.observables(th, Mpv, ang, rad, Km, 3, vac, v1, v2, O); o["E_m_over_M"] = R.mass_energy(th(rad.r), rad, mpiM, FM); o["E_sol_over_M"] += o["E_m_over_M"]
    res["DPP"] = o; log(tag, "DPP", o); out[tag] = res; save()
    thsc, conv, hist = R.self_consistent_m(th, Mpv, ang, rad, Km, 3, vac, mpiM, FM, itmax=0, log=lambda *s: log(tag, *s))
    res["SC_converged"] = conv; res["SC_history"] = hist; res["SC_profile"] = [[float(r), float(t)] for r, t in zip(rad.r[::50], thsc[::50])]
    if conv:
        f = R.profile_fn(rad, thsc); o = R.observables(f, Mpv, ang, rad, Km, 3, vac, v1, v2, O); o["E_m_over_M"] = R.mass_energy(thsc, rad, mpiM, FM); o["E_sol_over_M"] += o["E_m_over_M"]
        res["SC"] = o; log(tag, "SC", o)
    res["seconds"] = round(time.time() - t0, 1); save()
FF = math.sqrt(3) / (2 * math.pi)
for Km in [a.K]:
    tag = "AA1_pu_massive_K%d" % Km
    G = json.loads((Path(__file__).resolve().parents[1] / "audit/gap_2026-10-02aa.json").read_text())
    Mr = G["M_over_mp"]                             # M/m_p, unit-free (AA-1)
    Fr = 1 / (2 * math.sqrt(3) * math.pi)            # F/m_p
    FMy = Fr / Mr; MpvM = math.exp(0.5 * 4 * math.pi**2 * FMy**2 / 3)
    out["inputs"].update({"M_over_mp": Mr, "F_over_mp": Fr, "F_over_M": FMy, "Mpv_over_M": MpvM, "mpi_over_mp": mpi / mp})
    t1 = time.time(); case(tag, Mr * mp, MpvM, mp, (mpi / mp) / Mr, FMy, D=float(Km), km=float(Km), Km=Km); log(tag, "total seconds", round(time.time() - t1, 1))
log("written", a.out)
