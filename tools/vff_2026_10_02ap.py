#!/usr/bin/env python3
"""Round-ap (FREEZE_2026-10-02ap, AP-1): isovector electric form factor of the round-ag soliton at O(1/I) (cranking):
G(q) = I[j0(q r)]/I[1], I[w] = sum_c sum_{n unocc, m occ} <n|tau_c|m><m|w(r) tau_c|n>/(e_n - e_m), valence occupied, PV-subtracted sea.
K 14, kmax 12, D 14 (sharp). -> audit/vff_2026-10-02ap.json"""
import json, math, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from scipy.special import spherical_jn
import cqsm_kr as C
import cqsm_rot as R
RT = Path(__file__).resolve().parents[1]; t0 = time.time(); rnd = lambda v: float("%.10g" % v); z = lambda r: 0 * r
def prof(x, mpiM): return lambda r: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
m = json.loads((RT / "audit/murun_2026-10-02ag_K14_D14_k12.json").read_text()); inp = m["inputs"]; Mpv = inp["Mpv_over_M"]; Mr = inp["M_over_mp"]
th = prof(m["x_DPP"], inp["mpi_over_mp"] / inp["M_over_mp"]); Km, kmax, D = 14, 12.0, 14.0
ang = C.Angular(Km); rad = C.Radial(D, kmax); C.RAD = rad; O = R.Ops(ang)
Q2 = [v / 0.88035 for v in (0.1, 0.25, 0.5, 0.75, 1.0)]; qM = [math.sqrt(x) / Mr for x in Q2]   # q in units of M
W = [("one", np.ones_like(rad.r)), ("r2", rad.r ** 2)] + [("j0_%d" % i, spherical_jn(0, q * rad.r)) for i, q in enumerate(qM)]
rc = {}
def radw(l, la, lb, iw):
    key = (l, la, lb, iw)
    if key not in rc:
        _, Fa, _ = rad.funcs(l, la); _, Fb, _ = rad.funcs(l, lb); rc[key] = np.einsum("p,pn,pm->nm", rad.w * W[iw][1], Fa, Fb)
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
def isum(sp, ev):
    tot = np.zeros(len(W), complex)
    for (K1, P1), a in sp.items():
        un = ~R.occ_mask(a[0], K1, P1, ev)
        for (K2, P2), b in sp.items():
            if P2 != P1 or abs(K2 - K1) > 1: continue
            oc = R.occ_mask(b[0], K2, P2, ev)
            if not un.any() or not oc.any(): continue
            den = a[0][un][:, None] - b[0][oc][None, :]
            for M2 in (-1, 0, 1):
                if abs(M2) > K2: continue
                for c in range(3):
                    Xm = O.pair(a, K1, 0, b, K2, M2, O.tau[c], "tau%d" % c, "const")[np.ix_(un, oc)]
                    for iw in range(len(W)):
                        Ym = pairw(b, K2, M2, a, K1, 0, O.tau[c], "tau%d" % c, iw)[np.ix_(oc, un)]
                        tot[iw] += (2 * K1 + 1) * np.sum(Xm * Ym.T / den)
    return tot
s1 = C.spectrum(th, 1.0, ang, rad, Km, True); ev = C.valence(s1); print("s1 %.1f" % (time.time() - t0), flush=True)
T1 = isum(s1, ev); print("sum s1 %.1f" % (time.time() - t0), flush=True)
s2 = C.spectrum(th, Mpv, ang, rad, Km, True); T2 = isum(s2, None); print("sum s2 %.1f" % (time.time() - t0), flush=True)
reg = T1 - (1.0 / Mpv) ** 2 * T2
out = {"generated_by": "tools/vff_2026_10_02ap.py", "freeze": "FREEZE_2026-10-02ap", "K": Km, "kmax": kmax, "D": D, "M_over_mp": Mr, "Mpv_over_M": Mpv,
       "Q2_over_mp2": [rnd(x) for x in Q2], "I": {W[i][0]: [rnd(reg[i].real), rnd(reg[i].imag)] for i in range(len(W))},
       "I_s1": {W[i][0]: rnd(T1[i].real) for i in range(len(W))}, "I_s2": {W[i][0]: rnd(T2[i].real) for i in range(len(W))}, "seconds": round(time.time() - t0, 1)}
(RT / "audit/vff_2026-10-02ap.json").write_text(json.dumps(out, indent=1) + "\n"); print("written", out["seconds"], flush=True)
