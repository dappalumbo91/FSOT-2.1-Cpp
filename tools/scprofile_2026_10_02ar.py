#!/usr/bin/env python3
"""Round-ar (FREEZE_2026-10-02ar, hashed before this run): self-consistent profile at the scoring kmax, then the sea at M/m_p = 1/3.
  python tools/scprofile_2026_10_02ar.py
Writes audit/scprofile_2026-10-02ar.json and audit/rv_2026-10-02ar_<case>_j<j>.json. Does not score the 91 and does not edit the freeze."""
import json, math, sys, time, traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
RT = Path(__file__).resolve().parents[1]
REV = 1
OUT = RT / "audit/scprofile_2026-10-02ar.json"
K, D0, KMAX, NQ = 14, 14.0, 12.0, 1500
MIX, TOL, ITMAX, NC = 0.2, 1e-3, 40, 3
rnd = lambda v: float("%.10g" % v)

def sums(sp, ev, rad, O):
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

def dump(man):
    tmp = OUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(OUT)

def block_from(th, conv, hist, spec, seconds):
    return {"M_over_mp": spec["M_over_mp"], "M_over_mp_exact": spec["exact"], "F_over_M": spec["F_over_M"], "mpi_over_M": spec["mpi_over_M"],
            "Mpv_over_M": spec["Mpv_over_M"], "x_DPP": spec["x_DPP"], "mix": MIX, "tol": TOL, "itmax": ITMAX, "Nc": NC,
            "K": K, "D": D0, "kmax": KMAX, "nq": NQ, "converged": bool(conv), "history": hist,
            "theta": [float(v) for v in th], "seconds": round(seconds, 1)}

def radius(case, j, th, O):
    f_ = RT / ("audit/rv_2026-10-02ar_%s_j%d.json" % (case, j))
    if f_.exists():
        print("radius", case, "j", j, "exists", flush=True)
        return json.loads(f_.read_text(encoding="utf-8"))
    t0 = time.time(); DD = D0 + j * (math.pi / KMAX) / 4; radj = C.Radial(DD, KMAX, NQ); C.RAD = radj; O.rcache = {}
    fn = R.profile_fn(rad, np.asarray(th, float))
    s1 = C.spectrum(fn, 1.0, ang, radj, K, True); s2 = C.spectrum(fn, Mpv, ang, radj, K, True); ev = C.valence(s1)
    if ev is None:
        res = {"case": case, "kmax": KMAX, "j": j, "D": rnd(DD), "valence": None, "seconds": round(time.time() - t0, 1)}
    else:
        v1, se1 = sums(s1, ev, radj, O); _, se2 = sums(s2, None, radj, O); q = (1.0 / Mpv) ** 2
        res = {"case": case, "kmax": KMAX, "j": j, "D": rnd(DD), "I_val": [rnd(v1[0].real), rnd(v1[1].real)], "I_sea": [rnd(se1[0].real), rnd(se1[1].real)],
               "I_pv": [rnd(-q * se2[0].real), rnd(-q * se2[1].real)], "max_imag": rnd(max(abs(v1.imag).max(), abs(se1.imag).max(), abs(se2.imag).max())),
               "seconds": round(time.time() - t0, 1)}
        res["I1"] = rnd(res["I_val"][0] + res["I_sea"][0] + res["I_pv"][0]); res["Ir2"] = rnd(res["I_val"][1] + res["I_sea"][1] + res["I_pv"][1])
    tmp = f_.with_suffix(".tmp"); tmp.write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8", newline="\n"); tmp.replace(f_)
    print("radius", res, flush=True)
    return res

def solve(spec):
    print("solve", spec["case"], "M/mp", spec["M_over_mp"], flush=True)
    t0 = time.time()
    th, conv, hist = R.self_consistent_m(spec["th0"], Mpv, ang, rad, K, NC, vac, spec["mpi_over_M"], spec["F_over_M"], mix=MIX, itmax=ITMAX, tol=TOL,
                                          log=lambda *a: print(*a, flush=True))
    hist = [[h[0], None if h[1] is None else float(h[1]), None if h[2] is None else float(h[2]), None if h[3] is None else float(h[3])] for h in hist]
    print("solve done", spec["case"], "converged", bool(conv), "s", round(time.time() - t0, 1), flush=True)
    return block_from(th, conv, hist, spec, time.time() - t0)

def valence_lost(block):
    h = block.get("history") or []
    return (not h) or h[-1][2] is None

def main():
    global ang, rad, Mpv, vac
    ag = json.loads((RT / "audit/murun_2026-10-02ag_K14_D14_k12.json").read_text(encoding="utf-8")); inp = ag["inputs"]; x = float(ag["x_DPP"]); Mpv = float(inp["Mpv_over_M"])
    man = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else None
    if man and man.get("tool_revision") != REV:
        print("ROUND_AR_FAILED revision mismatch", flush=True); sys.exit(1)
    ang = C.Angular(K); rad = C.Radial(D0, KMAX, NQ); C.RAD = rad; O = R.Ops(ang)
    t0 = time.time(); z = lambda r: 0 * r
    v1 = C.spectrum(z, 1.0, ang, rad, K, True); v2 = C.spectrum(z, Mpv, ang, rad, K, True); vac = (float(C.esum(v1)), float(C.esum(v2)))
    print("vacuum", [rnd(v) for v in vac], round(time.time() - t0, 1), flush=True)
    if man is None:
        man = {"generated_by": "tools/scprofile_2026_10_02ar.py", "freeze": "FREEZE_2026-10-02ar", "tool_revision": REV,
               "basis": {"K": K, "D": D0, "kmax": KMAX, "nq": NQ, "mix": MIX, "tol": TOL, "itmax": ITMAX, "Nc": NC},
               "x_DPP": x, "vacuum_esum": [vac[0], vac[1]], "complete": False}
    def dpp(mpiM):
        return lambda r, mpiM=mpiM: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
    gap = {"case": "gap", "exact": "diagnostic", "M_over_mp": float(inp["M_over_mp"]), "F_over_M": float(inp["F_over_M"]),
           "mpi_over_M": float(inp["mpi_over_mp"]) / float(inp["M_over_mp"]), "Mpv_over_M": Mpv, "x_DPP": x, "th0": dpp(float(inp["mpi_over_mp"]) / float(inp["M_over_mp"]))}
    if "AR-1" not in man:
        man["AR-1"] = solve(gap); dump(man)
    b1 = man["AR-1"]
    if valence_lost(b1):
        man["complete"] = True; dump(man); print("ROUND_AR_DONE valence lost", flush=True); return
    radius("gap", 0, b1["theta"], O)
    if not b1["converged"]:
        man["complete"] = True; dump(man); print("ROUND_AR_DONE not converged", flush=True); return
    dppj = json.loads((RT / "audit/rv_2026-10-02aq_A_j0.json").read_text(encoding="utf-8"))
    gapj = json.loads((RT / "audit/rv_2026-10-02ar_gap_j0.json").read_text(encoding="utf-8"))
    r_dpp = dppj["Ir2"] / dppj["I1"]; r_sc = gapj["Ir2"] / gapj["I1"]; move = abs(r_sc - r_dpp) / r_dpp
    print("move", move, flush=True)
    if move > 0.02:
        for j in (1, 2, 3):
            radius("gap", j, b1["theta"], O)
    M3 = 1.0 / 3.0
    sigma = {"case": "sigma", "exact": "1/3", "M_over_mp": M3, "F_over_M": float(inp["F_over_mp"]) / M3,
             "mpi_over_M": float(inp["mpi_over_mp"]) / M3, "Mpv_over_M": Mpv, "x_DPP": x, "th0": dpp(float(inp["mpi_over_mp"]) / M3)}
    if "AR-2" not in man:
        C.RAD = rad; man["AR-2"] = solve(sigma); dump(man)
    b2 = man["AR-2"]
    if not valence_lost(b2):
        radius("sigma", 0, b2["theta"], O)
    man["complete"] = True; dump(man); print("ROUND_AR_DONE", flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc(); print("ROUND_AR_FAILED", flush=True); sys.exit(1)
