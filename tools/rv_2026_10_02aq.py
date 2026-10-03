#!/usr/bin/env python3
"""Round-aq (FREEZE_2026-10-02aq, AQ-1): shell-averaged isovector charge radius diagnostic.
I[w] = sum_c sum_{n unocc, m occ} <n|tau_c|m><m|w tau_c|n>/(e_n - e_m) for w = 1, r^2, split into valence (m = valence level), sea (other s1 occupied)
and PV (s2, no valence), on the 4 boxes D_j = 14 + j (pi/kmax)/4; --level A (kmax 12) | B (kmax 14, spectra from /home/box/fsot-am-cache).
-> audit/rv_2026-10-02aq_<L>_j<j>.json (resumable)"""
import argparse, json, math, pickle, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
ap = argparse.ArgumentParser(); ap.add_argument("--level", required=True); a = ap.parse_args()
RT = Path(__file__).resolve().parents[1]; rnd = lambda v: float("%.10g" % v)
def prof(x, mpiM): return lambda r: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
m = json.loads((RT / "audit/murun_2026-10-02ag_K14_D14_k12.json").read_text()); inp = m["inputs"]; Mpv = inp["Mpv_over_M"]
th = prof(m["x_DPP"], inp["mpi_over_mp"] / inp["M_over_mp"]); Km, D0 = 14, 14.0; kmax = {"A": 12.0, "B": 14.0}[a.level]
ang = C.Angular(Km); O = R.Ops(ang)
def sums(sp, ev, rad):
    W = [np.ones_like(rad.r), rad.r ** 2]; rc = {}
    def radw(l, la, lb, iw):
        key = (l, la, lb, iw)
        if key not in rc:
            _, Fa, _ = rad.funcs(l, la); _, Fb, _ = rad.funcs(l, lb); rc[key] = np.einsum("p,pn,pm->nm", rad.w * W[iw], Fa, Fb)
        return rc[key]
    def pairw(ent1, K1, M1, ent2, K2, M2, op, name, iw):
        e1, v1, b1, o1 = ent1; e2, v2, b2, o2 = ent2; A = np.zeros((o1[-1], o2[-1]), complex)
        for ia, (ta, ca, la) in enumerate(b1):
            for ib, (tb, cb, lb) in enumerate(b2):
                if ta != tb or ca[0] != cb[0]: continue
                key = (name, ca, cb, K1, M1, K2, M2)
                if key not in O.acache: O.acache[key] = ang.mat_const(ang.phi(ca[0], ca[1], K1, M1), ang.phi(cb[0], cb[1], K2, M2), op)
                c = O.acache[key]
                if abs(c) < 1e-12: continue
                A[o1[ia]:o1[ia + 1], o2[ib]:o2[ib + 1]] = c * radw(ca[0], la, lb, iw)
        return v1.conj().T @ A @ v2
    val, sea = np.zeros(2, complex), np.zeros(2, complex)
    for (K1, P1), a_ in sp.items():
        un = ~R.occ_mask(a_[0], K1, P1, ev)
        for (K2, P2), b in sp.items():
            if P2 != P1 or abs(K2 - K1) > 1: continue
            oc = R.occ_mask(b[0], K2, P2, ev)
            isv = np.zeros_like(oc)
            if ev is not None and (K2, P2) == (0, 1): isv = np.abs(b[0] - ev) < 1e-12
            if not un.any() or not oc.any(): continue
            den = a_[0][un][:, None] - b[0][oc][None, :]; vsel = isv[oc]
            for M2 in (-1, 0, 1):
                if abs(M2) > K2: continue
                for c in range(3):
                    Xm = R.Ops.pair(O, a_, K1, 0, b, K2, M2, O.tau[c], "tau%d" % c, "const")[np.ix_(un, oc)]
                    for iw in range(2):
                        Ym = pairw(b, K2, M2, a_, K1, 0, O.tau[c], "tau%d" % c, iw)[np.ix_(oc, un)]
                        T = (2 * K1 + 1) * (Xm * Ym.T / den)
                        val[iw] += np.sum(T[:, vsel]); sea[iw] += np.sum(T[:, ~vsel])
    return val, sea
for j in range(4):
    f_ = RT / ("audit/rv_2026-10-02aq_%s_j%d.json" % (a.level, j))
    if f_.exists(): print("j=%d done" % j, flush=True); continue
    t0 = time.time(); DD = D0 + j * (math.pi / kmax) / 4; rad = C.Radial(DD, kmax); C.RAD = rad; O.rcache = {}
    if a.level == "B":
        SP = pickle.loads((Path("/home/box/fsot-am-cache") / ("B_j%d.pkl" % j)).read_bytes()); s1, s2 = SP["s1"], SP["s2"]
    else:
        s1 = C.spectrum(th, 1.0, ang, rad, Km, True); s2 = C.spectrum(th, Mpv, ang, rad, Km, True)
    ev = C.valence(s1); v1, se1 = sums(s1, ev, rad); _, se2 = sums(s2, None, rad); q = (1.0 / Mpv) ** 2
    res = {"level": a.level, "kmax": kmax, "j": j, "D": rnd(DD), "I_val": [rnd(v1[0].real), rnd(v1[1].real)], "I_sea": [rnd(se1[0].real), rnd(se1[1].real)],
           "I_pv": [rnd(-q * se2[0].real), rnd(-q * se2[1].real)], "max_imag": rnd(max(abs(v1.imag).max(), abs(se1.imag).max(), abs(se2.imag).max())), "seconds": round(time.time() - t0, 1)}
    res["I1"] = rnd(res["I_val"][0] + res["I_sea"][0] + res["I_pv"][0]); res["Ir2"] = rnd(res["I_val"][1] + res["I_sea"][1] + res["I_pv"][1])
    tmp = f_.with_suffix(".tmp"); tmp.write_text(json.dumps(res, indent=1) + "\n"); tmp.replace(f_); print(res, flush=True)
print("done", flush=True)
