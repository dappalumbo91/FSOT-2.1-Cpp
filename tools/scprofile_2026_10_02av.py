#!/usr/bin/env python3
"""Round-av (FREEZE_2026-10-02av, hashed before this run): one self_consistent_m call, mix 0.2, itmax 400, from the DPP.
  python tools/scprofile_2026_10_02av.py
Does not edit the shared solver defaults, the ar, as, at or au freezes, or the 91."""
import hashlib, json, math, sys, time, traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
import scprofile_2026_10_02ar as AR
RT = Path(__file__).resolve().parents[1]
OUT = RT / "audit/scprofile_2026-10-02av.json"
REV = 1
K, D0, KMAX, NQ = 14, 14.0, 12.0, 1500
MIX, TOL, ITMAX, NC = 0.2, 1e-3, 400, 3
AR0, AR39 = 0.17211904981809267, 0.005631712767651509
rnd = lambda v: float("%.10g" % v)

def freeze_ok():
    D = RT / "audit"; bad = 0
    for line in open(D / "FREEZE_2026-10-02av.sha256", encoding="utf-8"):
        want, name = line.split()
        if hashlib.sha256((D / name).read_bytes()).hexdigest() != want: bad += 1
    return bad == 0

def dump(man):
    tmp = OUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(OUT)

def block_from(th, conv, hist, spec, seconds):
    return {"M_over_mp": spec["M_over_mp"], "M_over_mp_exact": spec["exact"], "F_over_M": spec["F_over_M"], "mpi_over_M": spec["mpi_over_M"],
            "Mpv_over_M": spec["Mpv_over_M"], "x_DPP": spec["x_DPP"], "mix": MIX, "tol": TOL, "itmax": ITMAX, "Nc": NC,
            "K": K, "D": D0, "kmax": KMAX, "nq": NQ, "converged": bool(conv), "history": hist,
            "theta": [float(v) for v in th], "seconds": round(seconds, 1)}

def solve(spec, ang, rad, Mpv, vac):
    print("solve", spec["case"], "M/mp", spec["M_over_mp"], "itmax", ITMAX, flush=True)
    t0 = time.time()
    th, conv, hist = R.self_consistent_m(spec["th0"], Mpv, ang, rad, K, NC, vac, spec["mpi_over_M"], spec["F_over_M"], mix=MIX, itmax=ITMAX, tol=TOL,
                                          log=lambda *a: print(*a, flush=True))
    hist = [[h[0], None if h[1] is None else float(h[1]), None if h[2] is None else float(h[2]), None if h[3] is None else float(h[3])] for h in hist]
    print("solve done", spec["case"], "converged", bool(conv), "steps", len(hist), "s", round(time.time() - t0, 1), flush=True)
    return block_from(th, conv, hist, spec, time.time() - t0)

def ar_note(block):
    h = block.get("history") or []
    d0 = None if not h else h[0][3]
    d39 = h[39][3] if len(h) > 39 else None
    block["ar_step0_dtheta"] = AR0
    block["ar_step39_dtheta"] = AR39
    block["step0_dtheta"] = d0
    block["step39_dtheta"] = d39
    print("ar compare step0", d0, "recorded", AR0, "step39", d39, "recorded", AR39, flush=True)

def radius(case, j, th, ang, rad, Mpv, O):
    f_ = RT / ("audit/rv_2026-10-02av_%s_j%d.json" % (case, j))
    if f_.exists():
        print("radius", case, j, "exists", flush=True)
        return json.loads(f_.read_text(encoding="utf-8"))
    t0 = time.time(); DD = D0 + j * (math.pi / KMAX) / 4; radj = C.Radial(DD, KMAX, NQ); C.RAD = radj; O.rcache = {}
    AR.ang = ang
    fn = R.profile_fn(rad, np.asarray(th, float))
    s1 = C.spectrum(fn, 1.0, ang, radj, K, True); s2 = C.spectrum(fn, Mpv, ang, radj, K, True); ev = C.valence(s1)
    if ev is None:
        res = {"case": case, "kmax": KMAX, "j": j, "D": rnd(DD), "valence": None, "seconds": round(time.time() - t0, 1)}
    else:
        v1, se1 = AR.sums(s1, ev, radj, O); _, se2 = AR.sums(s2, None, radj, O); q = (1.0 / Mpv) ** 2
        res = {"case": case, "kmax": KMAX, "j": j, "D": rnd(DD), "I_val": [rnd(v1[0].real), rnd(v1[1].real)], "I_sea": [rnd(se1[0].real), rnd(se1[1].real)],
               "I_pv": [rnd(-q * se2[0].real), rnd(-q * se2[1].real)], "max_imag": rnd(max(abs(v1.imag).max(), abs(se1.imag).max(), abs(se2.imag).max())),
               "seconds": round(time.time() - t0, 1)}
        res["I1"] = rnd(res["I_val"][0] + res["I_sea"][0] + res["I_pv"][0]); res["Ir2"] = rnd(res["I_val"][1] + res["I_sea"][1] + res["I_pv"][1])
    tmp = f_.with_suffix(".tmp"); tmp.write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8", newline="\n"); tmp.replace(f_)
    print("radius", res, flush=True)
    return res

def valence_lost(block):
    h = block.get("history") or []
    return (not h) or h[-1][2] is None

def main():
    if not freeze_ok():
        print("ROUND_AV_FAILED freeze hash", flush=True); sys.exit(1)
    ag = json.loads((RT / "audit/murun_2026-10-02ag_K14_D14_k12.json").read_text(encoding="utf-8")); inp = ag["inputs"]; x = float(ag["x_DPP"]); Mpv = float(inp["Mpv_over_M"])
    man = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else None
    if man and man.get("complete") is True and "AV-1" in man:
        print("ROUND_AV_DONE already complete", flush=True); return
    if man and man.get("tool_revision") != REV:
        print("ROUND_AV_FAILED revision", flush=True); sys.exit(1)
    ang = C.Angular(K); rad = C.Radial(D0, KMAX, NQ); C.RAD = rad; O = R.Ops(ang); AR.ang = ang
    t0 = time.time(); z = lambda r: 0 * r
    v1 = C.spectrum(z, 1.0, ang, rad, K, True); v2 = C.spectrum(z, Mpv, ang, rad, K, True); vac = (float(C.esum(v1)), float(C.esum(v2)))
    print("vacuum", [rnd(v) for v in vac], round(time.time() - t0, 1), flush=True)
    def dpp(mpiM):
        return lambda r, mpiM=mpiM: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
    gap = {"case": "gap", "exact": "diagnostic", "M_over_mp": float(inp["M_over_mp"]), "F_over_M": float(inp["F_over_M"]),
           "mpi_over_M": float(inp["mpi_over_mp"]) / float(inp["M_over_mp"]), "Mpv_over_M": Mpv, "x_DPP": x,
           "th0": dpp(float(inp["mpi_over_mp"]) / float(inp["M_over_mp"]))}
    if man is None:
        man = {"generated_by": "tools/scprofile_2026_10_02av.py", "freeze": "FREEZE_2026-10-02av", "tool_revision": REV,
               "basis": {"K": K, "D": D0, "kmax": KMAX, "nq": NQ, "mix": MIX, "tol": TOL, "itmax": ITMAX, "Nc": NC},
               "x_DPP": x, "vacuum_esum": [vac[0], vac[1]], "complete": False}
        dump(man)
    if "AV-1" not in man:
        man["AV-1"] = solve(gap, ang, rad, Mpv, vac); ar_note(man["AV-1"]); dump(man)
    b1 = man["AV-1"]
    if valence_lost(b1):
        man["complete"] = True; dump(man); print("ROUND_AV_DONE valence lost", flush=True); return
    C.RAD = rad
    radius("gap", 0, b1["theta"], ang, rad, Mpv, O)
    if not b1["converged"]:
        man["complete"] = True; dump(man); print("ROUND_AV_DONE not converged", flush=True); return
    dppj = json.loads((RT / "audit/rv_2026-10-02aq_A_j0.json").read_text(encoding="utf-8"))
    gapj = json.loads((RT / "audit/rv_2026-10-02av_gap_j0.json").read_text(encoding="utf-8"))
    move = abs(gapj["Ir2"] / gapj["I1"] - dppj["Ir2"] / dppj["I1"]) / (dppj["Ir2"] / dppj["I1"])
    print("move", move, flush=True)
    if move > 0.02:
        for j in (1, 2, 3):
            radius("gap", j, b1["theta"], ang, rad, Mpv, O)
    if "AV-2" not in man:
        M3 = 1.0 / 3.0
        sigma = {"case": "sigma", "exact": "1/3", "M_over_mp": M3, "F_over_M": float(inp["F_over_mp"]) / M3,
                 "mpi_over_M": float(inp["mpi_over_mp"]) / M3, "Mpv_over_M": Mpv, "x_DPP": x, "th0": dpp(float(inp["mpi_over_mp"]) / M3)}
        C.RAD = rad
        man["AV-2"] = solve(sigma, ang, rad, Mpv, vac); dump(man)
    b2 = man["AV-2"]
    if not valence_lost(b2):
        C.RAD = rad
        radius("sigma", 0, b2["theta"], ang, rad, Mpv, O)
    man["complete"] = True; dump(man); print("ROUND_AV_DONE", flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc(); print("ROUND_AV_FAILED", flush=True); sys.exit(1)
