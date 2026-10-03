#!/usr/bin/env python3
"""Round-x energy-cutoff sea sum (FREEZE_2026-10-02x, X-1), derived from the round-w diagnostic: at the fixed DPP profile x (default 0.8) and the round-v inputs,
report per (D, k, K): valence eigenvalue, the mu_V^(0) sea sum (xat_sea) split by grand-spin sector, and the cranking
inertia split into valence (valence -> unoccupied) and sea parts. Writes JSON lines to --out.
  python tools/diag_2026_10_02w.py --hub HUB --cfg D,k,K [--cfg ...] --out audit/diag_2026-10-02w.jsonl
"""
import argparse, json, math, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
import fsot02d as X
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--cfg", action="append", required=True)
ap.add_argument("--x", type=float, default=0.8); ap.add_argument("--ecut", type=float, default=0.75); ap.add_argument("--out", required=True); a = ap.parse_args()
X.setup(a.hub); L = X.leaves(); mp = float(X.kg_to_GeV(L["m_p_kg"]) * 1000); mpi = float(L["m_pi_pm_MeV"]); M = mp / 3
Mpv = math.sqrt(math.e); mpiM = mpi / M; Nc = 3
def inertia_split(sp1, sp2, ang, ev):
    val = sea = 0.0
    for wt, sp, withval in ((1.0, sp1, True), (-(1.0 / Mpv) ** 2, sp2, False)):
        for (K1, P1), aa in sp.items():
            for (K2, P2), b in sp.items():
                if P1 != P2 or abs(K1 - K2) > 1: continue
                for Mz in range(-min(K1, K2), min(K1, K2) + 1):
                    Xm = np.abs(C.tz_pair(aa, K1, b, K2, ang, Mz)) ** 2; ea, eb = aa[0], b[0]
                    va = np.zeros(len(ea), bool); vb = np.zeros(len(eb), bool)
                    if withval and (K1, P1) == (0, 1): va = np.abs(ea - ev) < 1e-12
                    if withval and (K2, P2) == (0, 1): vb = np.abs(eb - ev) < 1e-12
                    oa = (ea < 0) | va; ob = (eb < 0) | vb; den = eb[None, :] - ea[:, None]
                    m = oa[:, None] & (~ob[None, :]); mv = m & va[:, None]
                    val += wt * 0.5 * Nc * np.sum(Xm[mv] / den[mv]); sea += wt * 0.5 * Nc * np.sum(Xm[m & ~mv] / den[m & ~mv])
    return float(val), float(sea)
with open(a.out, "a") as fo:
    for cfg in a.cfg:
        D, k, K = [float(s) for s in cfg.split(",")]; K = int(K); t0 = time.time()
        Ec = a.ecut * k; ang = C.Angular(K); rad = C.Radial(D, k); C.RAD = rad; O = R.Ops(ang); z = lambda r: 0 * r
        th = lambda r: -2 * np.arctan(a.x * a.x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
        v1 = C.spectrum(z, 1.0, ang, rad, K, True); v2 = C.spectrum(z, Mpv, ang, rad, K, True)
        s1 = C.spectrum(th, 1.0, ang, rad, K, True); s2 = C.spectrum(th, Mpv, ang, rad, K, True); ev = C.valence(s1)
        sec = {}
        for wt, sp in ((1.0, s1), (-(1.0 / Mpv) ** 2, s2), (-1.0, v1), ((1.0 / Mpv) ** 2, v2)):
            for key, ent in sp.items():
                Kk = key[0]; Mz = 0 if Kk == 0 else Kk
                d = np.real(np.diag(O.pair(ent, Kk, Mz, ent, Kk, Mz, O.rxs_dot_tau, "rdt", "rfield")))
                e = ent[0]; mask = np.abs(e) < Ec
                t = -0.5 * (2 * Kk + 1) * np.sum(np.sign(e[mask]) * d[mask])
                sec[str(key)] = sec.get(str(key), 0.0) + wt * t
        Iv, Is = inertia_split(s1, s2, ang, ev)
        nst = {str(kk): int(len(vv[0])) for kk, vv in s1.items()}
        rec = {"E_c_over_M": Ec, "D": D, "k": k, "K": K, "x": a.x, "eps_val": float(ev), "xat_sea": float(sum(sec.values())), "xat_sea_by_sector": sec,
               "I_val_M": Iv, "I_sea_M": Is, "I_M": Iv + Is, "n_states": nst, "seconds": round(time.time() - t0, 1)}
        fo.write(json.dumps(rec) + "\n"); fo.flush(); print(cfg, "eps", ev, "xat_sea", rec["xat_sea"], "I", Iv, Is, rec["seconds"], flush=True)
