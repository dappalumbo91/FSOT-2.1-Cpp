#!/usr/bin/env python3
"""Round-z soliton inertia trace (diagnostic, FREEZE_2026-10-02z Z-1): at the round-y proton-unit inputs (or a given M/m_p) and a
given DPP size x, split the cranking inertia I M into valence (valence -> unoccupied), Dirac-sea (bare) and Pauli-Villars parts, and
report the valence eigenvalue. M_PV/M from the PV condition with F/m_p = 1/(2 sqrt3 pi).
  python tools/itrace_2026_10_02z.py --hub HUB --cfg Mr,x,K [--cfg ...] --out audit/itrace_2026-10-02z.jsonl
"""
import argparse, json, math, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import fsot02d as X
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--cfg", action="append", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
X.setup(a.hub); L = X.leaves(); mp = float(X.kg_to_GeV(L["m_p_kg"]) * 1000); mpi = float(L["m_pi_pm_MeV"]); Nc = 3; Fr = 1 / (2 * math.sqrt(3) * math.pi)
def split(sp1, sp2, ang, ev, Mpv):
    out = {"val": 0.0, "sea": 0.0, "pv": 0.0}
    for wt, sp, withval in ((1.0, sp1, True), (-(1.0 / Mpv) ** 2, sp2, False)):
        for (K1, P1), aa in sp.items():
            for (K2, P2), b in sp.items():
                if P1 != P2 or abs(K1 - K2) > 1: continue
                for Mz in range(-min(K1, K2), min(K1, K2) + 1):
                    Xm = np.abs(C.tz_pair(aa, K1, b, K2, ang, Mz)) ** 2; ea, eb = aa[0], b[0]
                    va = np.zeros(len(ea), bool); vb = np.zeros(len(eb), bool)
                    if withval and (K1, P1) == (0, 1): va = np.abs(ea - ev) < 1e-12
                    if withval and (K2, P2) == (0, 1): vb = np.abs(eb - ev) < 1e-12
                    oa = (ea < 0) | va; ob = (eb < 0) | vb; den = eb[None, :] - ea[:, None]; m = oa[:, None] & (~ob[None, :]); mv = m & va[:, None]
                    t_v = 0.5 * Nc * np.sum(Xm[mv] / den[mv]); t_s = 0.5 * Nc * np.sum(Xm[m & ~mv] / den[m & ~mv])
                    if withval: out["val"] += wt * t_v; out["sea"] += wt * t_s
                    else: out["pv"] += wt * (t_v + t_s)
    return out
with open(a.out, "a") as fo:
    for cfg in a.cfg:
        Mr, x, K = cfg.split(","); Mr, x, K = float(Mr), float(x), int(K); t0 = time.time()
        M = Mr * mp; FM = Fr / Mr; Mpv = math.exp(0.5 * 4 * math.pi**2 * FM**2 / 3); mpiM = mpi / M
        ang = C.Angular(K); rad = C.Radial(float(K), float(K)); C.RAD = rad
        th = lambda r: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
        s1 = C.spectrum(th, 1.0, ang, rad, K, True); s2 = C.spectrum(th, Mpv, ang, rad, K, True); ev = C.valence(s1)
        sp = split(s1, s2, ang, ev, Mpv)
        rec = {"M_over_mp": Mr, "x": x, "K": K, "Mpv_over_M": Mpv, "eps_val": float(ev), "I_val_M": float(sp["val"]), "I_sea_M": float(sp["sea"]), "I_pv_M": float(sp["pv"]),
               "I_M": float(sp["val"] + sp["sea"] + sp["pv"]), "r0_over_inv_mp": x / Mr, "seconds": round(time.time() - t0, 1)}
        fo.write(json.dumps(rec) + "\n"); fo.flush(); print(cfg, rec, flush=True)
