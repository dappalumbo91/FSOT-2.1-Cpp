#!/usr/bin/env python3
"""Round-ba (FREEZE_2026-10-02ba, hashed before this run): j=0 DPP isovector split at M/m_p = 1/3.
  python -u tools/rv_2026_10_02ba.py
Does not edit cqsm_rot.py, rv_2026_10_02aq.py, or the 91. Does not call self_consistent_m."""
import hashlib, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
RT = Path(__file__).resolve().parents[1]
OUT = RT / "audit/rv_2026-10-02ba_j0.json"
K, D0, KMAX, NQ = 14, 14.0, 12.0, 1500

def freeze_ok():
    D = RT / "audit"; bad = 0
    for line in open(D / "FREEZE_2026-10-02ba.sha256", encoding="utf-8"):
        want, name = line.split()
        if hashlib.sha256((D / name).read_bytes()).hexdigest() != want: bad += 1
    return bad == 0

def sums(sp, ev, rad, O, ang):
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

def main():
    if not freeze_ok():
        print("ROUND_BA_FAILED freeze hash", flush=True); sys.exit(1)
    if OUT.exists():
        print("ROUND_BA_EXISTS", flush=True); return
    ag = json.loads((RT / "audit/murun_2026-10-02ag_K14_D14_k12.json").read_text(encoding="utf-8"))
    inp = ag["inputs"]; M = 1.0 / 3.0; x = float(ag["x_DPP"]); Mpv = float(inp["Mpv_over_M"])
    mpiM = float(inp["mpi_over_mp"]) / M; F = float(inp["F_over_mp"]) / M
    th = lambda r: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
    ang = C.Angular(K); rad = C.Radial(D0, KMAX, NQ); C.RAD = rad; O = R.Ops(ang)
    print("BA-1 M/m_p", M, "mpi/M", mpiM, "F/M", F, "Mpv/M", Mpv, "x_DPP", x, flush=True)
    t0 = time.time()
    s1 = C.spectrum(th, 1.0, ang, rad, K, True); s2 = C.spectrum(th, Mpv, ang, rad, K, True)
    ev = C.valence(s1)
    if ev is None:
        print("ROUND_BA_VALENCE_LOST", flush=True); return
    v1, se1 = sums(s1, ev, rad, O, ang); _, se2 = sums(s2, None, rad, O, ang); q = (1.0 / Mpv) ** 2
    rnd = lambda v: float("%.10g" % v)
    res = {"freeze": "FREEZE_2026-10-02ba", "level": "A", "kmax": KMAX, "j": 0, "D": D0, "nq": NQ, "K": K,
           "M_over_mp": M, "F_over_M": F, "mpi_over_M": mpiM, "Mpv_over_M": Mpv, "x_DPP": x, "solver": "none",
           "valence": ev, "I_val": [rnd(v1[0].real), rnd(v1[1].real)], "I_sea": [rnd(se1[0].real), rnd(se1[1].real)],
           "I_pv": [rnd(-q * se2[0].real), rnd(-q * se2[1].real)],
           "max_imag": rnd(max(abs(v1.imag).max(), abs(se1.imag).max(), abs(se2.imag).max())),
           "seconds": round(time.time() - t0, 1)}
    res["I1"] = rnd(res["I_val"][0] + res["I_sea"][0] + res["I_pv"][0])
    res["Ir2"] = rnd(res["I_val"][1] + res["I_sea"][1] + res["I_pv"][1])
    tmp = OUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8", newline="\n"); tmp.replace(OUT)
    print(res, flush=True); print("ROUND_BA_DONE", flush=True)

if __name__ == "__main__":
    main()
