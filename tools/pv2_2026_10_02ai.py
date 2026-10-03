#!/usr/bin/env python3
"""Round-ai (FREEZE_2026-10-02ai, AI-1): two-subtraction Pauli-Villars observables at K 14, D 14 (fixed profile of the round-ag kmax-12 run), per kmax.
Each sea quantity is reported per spectrum (M, M_1, M_2, and vacuum) so the scorer forms sum_i c_i X(M_i) (and the single-PV comparison).
  python tools/pv2_2026_10_02ai.py --kmax 12 -> audit/pv2_2026-10-02ai_k12.json (numpy/scipy)"""
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
ap = argparse.ArgumentParser(); ap.add_argument("--kmax", type=float, default=12.0); ap.add_argument("--nosingle", action="store_true"); a = ap.parse_args()
RT = Path(__file__).resolve().parents[1]
m = json.loads((RT / "audit/murun_2026-10-02ag_K14_D14_k12.json").read_text()); inp = m["inputs"]; x = m["x_DPP"]
mpiM = inp["mpi_over_mp"] / inp["M_over_mp"]; Km = 14; Nc = 3; t0 = time.time()
MASS = {"m0": 1.0, "m1s": inp["Mpv_over_M"], "m1": 1.340129576, "m2": 6.959685111}   # m1s: single-PV mass (for the comparison)
if a.nosingle: del MASS["m1s"]   # kmax > 12: the single-PV comparison is only needed for the kmax-12 tolerance check
ang = C.Angular(Km); rad = C.Radial(14.0, a.kmax); C.RAD = rad; O = R.Ops(ang)
z = lambda r: 0 * r; th = lambda r: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
S = {k: C.spectrum(th, v, ang, rad, Km, True) for k, v in MASS.items()}; V = {k: C.spectrum(z, v, ang, rad, Km, True) for k, v in MASS.items()}
ev = C.valence(S["m0"]); print("spectra", round(time.time() - t0, 1), flush=True)
def diag_sum(sp, op, name, kind, rf):
    t = 0.0; val = None
    for (K, P), ent in sp.items():
        Mz = 0 if K == 0 else K
        d = np.real(np.diag(O.pair(ent, K, Mz, ent, K, Mz, op, name, kind))) if rf else C.op_diag(ent, ang, K, ang.st) / 3.0
        t += -0.5 * (2 * K + 1) * float(np.sum(np.sign(ent[0]) * d))
        if (K, P) == (0, 1): val = float(d[int(np.argmin(np.abs(ent[0] - ev)))])
    return t, val
def inertia_sea(sp):   # Nc/2 sum_{occ n, unocc m} |<m|tau_z|n>|^2/(e_m - e_n), no valence
    tot = 0.0
    for (K1, P1), aa in sp.items():
        for (K2, P2), bb in sp.items():
            if P1 != P2 or abs(K1 - K2) > 1: continue
            for M_ in range(-min(K1, K2), min(K1, K2) + 1):
                X = np.abs(C.tz_pair(aa, K1, bb, K2, ang, M_)) ** 2; ea, eb = aa[0], bb[0]
                msk = (ea < 0)[:, None] & (~(eb < 0))[None, :]; den = eb[None, :] - ea[:, None]
                tot += 0.5 * Nc * np.sum(X[msk] / den[msk])
    return float(tot)
OPS = {"A": ([(O.sxt[c], "sxt%d" % c, "const") for c in range(3)], [(O.tau[c], "tau%d" % c, "const") for c in range(3)], 6.0, 1),
       "Amu": ([(O.rxs_x_tau[c], "rxt%d" % c, "rfield") for c in range(3)], [(O.tau[c], "tau%d" % c, "const") for c in range(3)], 6.0, 1),
       "B": ([(O.tau[c], "tau%d" % c, "const") for c in range(3)], [(O.rxs[c], "rxs%d" % c, "rfield") for c in range(3)], 1.0, 0)}
out = {"generated_by": "tools/pv2_2026_10_02ai.py", "freeze": "FREEZE_2026-10-02ai", "K": Km, "D": 14.0, "kmax": a.kmax, "x_DPP": x, "masses": MASS, "eps_val": ev, "inputs": inp, "per": {}}
I_tot0 = C.inertia(S["m0"], S["m0"], 1e9, ang, Km, Nc, ev)   # valence + bare sea at M (PV weight ~ 0)
out["I_val_plus_sea0"] = float(I_tot0)
for k in MASS:
    for tag, sp in (("sol", S[k]), ("vac", V[k])):
        r = {"esum": float(C.esum(sp))}
        r["xat"], vx = diag_sum(sp, O.rxs_dot_tau, "rdt", "rfield", True); r["gA0"], vg = diag_sum(sp, None, None, None, False)
        if tag == "sol" and k == "m0": out["xat_val"] = vx; out["gA0_val_d"] = vg
        for nm, (X_, Y_, dv, ix) in OPS.items():
            c_ = complex(R.rot_sum(O, sp, None, X_, Y_) / dv); r[nm] = [c_.real, c_.imag]
        if tag == "sol" and k != "m0": r["I_sea"] = inertia_sea(sp)
        out["per"]["%s_%s" % (k, tag)] = r; print(k, tag, round(time.time() - t0, 1), flush=True)
for nm, (X_, Y_, dv, ix) in OPS.items():
    c_ = complex(R.rot_sum(O, S["m0"], ev, X_, Y_) / dv); out["%s_tot_m0" % nm] = [c_.real, c_.imag]
out["I_sea_m0"] = inertia_sea(S["m0"]); out["seconds"] = round(time.time() - t0, 1)
(RT / ("audit/pv2_2026-10-02ai_k%g.json" % a.kmax)).write_text(json.dumps(out, indent=1) + "\n"); print("written", out["seconds"], flush=True)
