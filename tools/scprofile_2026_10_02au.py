#!/usr/bin/env python3
"""Round-au (FREEZE_2026-10-02au, hashed before this run): continue the mix-0.2 walk.
  python tools/scprofile_2026_10_02au.py
Does not edit the shared solver defaults, the ar, as or at freezes, or the 91."""
import hashlib, json, math, sys, time, traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
import scprofile_2026_10_02ar as AR
RT = Path(__file__).resolve().parents[1]
OUT = RT / "audit/scprofile_2026-10-02au.json"
K, D0, KMAX, NQ = 14, 14.0, 12.0, 1500
TOL, GUARD, RISES, MIX = 1e-3, 400, 5, 0.2
START = 0.005515527562609979
rnd = lambda v: float("%.10g" % v)

def freeze_ok():
    D = RT / "audit"; bad = 0
    for line in open(D / "FREEZE_2026-10-02au.sha256", encoding="utf-8"):
        want, name = line.split()
        if hashlib.sha256((D / name).read_bytes()).hexdigest() != want: bad += 1
    return bad == 0

def dump(man):
    tmp = OUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(OUT)

def one(th, mpi, F, Mpv, ang, rad, vac, tag):
    th0 = R.profile_fn(rad, np.asarray(th, float))
    out, ok, h = R.self_consistent_m(th0, Mpv, ang, rad, K, 3, vac, mpi, F, mix=MIX, itmax=1, tol=TOL, log=lambda *a: print(tag, *a, flush=True))
    return np.asarray(out, float), bool(ok), h

def rises_of(hist):
    rises = 0; prev = None
    for row in hist:
        d = row[3]
        if prev is not None and d is not None and d > prev: rises += 1
        else: rises = 0
        prev = d
    return rises, prev

def pack(th, conv, hist, seconds, why, spec):
    return {"M_over_mp": spec["M_over_mp"], "M_over_mp_exact": spec["exact"], "F_over_M": spec["F_over_M"], "mpi_over_M": spec["mpi_over_M"],
            "Mpv_over_M": spec["Mpv_over_M"], "x_DPP": spec["x_DPP"], "mix": MIX, "tol": TOL, "guard": GUARD, "rise_guard": RISES, "Nc": 3,
            "K": K, "D": D0, "kmax": KMAX, "nq": NQ, "converged": bool(conv), "stop": why, "history": hist,
            "theta": [float(v) for v in np.asarray(th, float)], "seconds": seconds}

def flow(th, mpi, F, Mpv, ang, rad, vac, hist, seconds0, on_step, check_start=False):
    hist = [list(row) for row in hist]; rises, prev = rises_of(hist); t0 = time.time()
    def clock(): return round(seconds0 + (time.time() - t0), 1)
    while len(hist) < GUARD:
        it = len(hist)
        th, ok, h = one(th, mpi, F, Mpv, ang, rad, vac, "map %d" % it)
        row = h[-1]
        hist.append([it, None if row[1] is None else float(row[1]), None if row[2] is None else float(row[2]), None if row[3] is None else float(row[3])])
        d = hist[-1][3]
        print("flow", it, "mix", MIX, "dtheta", d, "converged", bool(ok), flush=True)
        why = None
        if hist[-1][2] is None: why = "valence lost"
        elif check_start and it == 0 and (d is None or abs(float(d) - START) > 1e-9): why = "start gap"
        elif ok: why = "converged"
        elif prev is not None and d > prev:
            rises += 1
            if rises >= RISES: why = "gap rose 5 passes"
        else: rises = 0
        if why is None: prev = d
        on_step(th, hist, why, clock())
        if why: return th, why == "converged", hist, clock(), why
    why = "400 passes"; on_step(th, hist, why, clock()); return th, False, hist, clock(), why

def radius(case, j, th, ang, rad, Mpv, O):
    f_ = RT / ("audit/rv_2026-10-02au_%s_j%d.json" % (case, j))
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

def walk(man, key, partial_key, th0, hist0, sec0, mpi, F, Mpv, ang, rad, vac, spec, check_start=False):
    part = man.get(partial_key)
    if part and abs(float(part.get("mix")) - MIX) > 1e-15:
        print("ROUND_AU_FAILED partial mix", flush=True); sys.exit(1)
    def on_step(th, hist, why, seconds):
        man[partial_key] = pack(th, why == "converged", hist, seconds, why, spec); dump(man)
    if part and part.get("stop"):
        man[key] = part
    elif part and len(part.get("history") or []) >= GUARD:
        man[key] = pack(part["theta"], False, part["history"], part["seconds"], "400 passes", spec)
    else:
        th_s = th0 if not part else np.array(part["theta"], float)
        hist_s = [] if not part else part["history"]; sec_s = 0.0 if not part else float(part["seconds"])
        if hist0 is not None and not part:
            hist_s, sec_s = hist0, sec0
        th, conv, hist, sec, why = flow(th_s, mpi, F, Mpv, ang, rad, vac, hist_s, sec_s, on_step, check_start)
        man[key] = pack(th, conv, hist, sec, why, spec)
    man.pop(partial_key, None); dump(man)
    return man[key]

def main():
    if not freeze_ok():
        print("ROUND_AU_FAILED freeze hash", flush=True); sys.exit(1)
    ar = json.loads((RT / "audit/scprofile_2026-10-02ar.json").read_text(encoding="utf-8"))
    a1 = ar["AR-1"]; x = float(a1["x_DPP"]); Mpv = float(a1["Mpv_over_M"]); th_ar = np.array(a1["theta"], float)
    man = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else None
    if man and man.get("tool_revision") != 1:
        print("ROUND_AU_FAILED revision", flush=True); sys.exit(1)
    ang = C.Angular(K); rad = C.Radial(D0, KMAX, NQ); C.RAD = rad; O = R.Ops(ang); AR.ang = ang
    t0 = time.time(); z = lambda r: 0 * r
    v1 = C.spectrum(z, 1.0, ang, rad, K, True); v2 = C.spectrum(z, Mpv, ang, rad, K, True); vac = (float(C.esum(v1)), float(C.esum(v2)))
    print("vacuum", [rnd(v) for v in vac], round(time.time() - t0, 1), flush=True)
    spec1 = {"M_over_mp": a1["M_over_mp"], "exact": "diagnostic", "F_over_M": a1["F_over_M"], "mpi_over_M": a1["mpi_over_M"], "Mpv_over_M": Mpv, "x_DPP": x}
    if man is None:
        man = {"generated_by": "tools/scprofile_2026_10_02au.py", "freeze": "FREEZE_2026-10-02au", "tool_revision": 1,
               "basis": {"K": K, "D": D0, "kmax": KMAX, "nq": NQ, "mix": MIX, "tol": TOL, "guard": GUARD, "rise_guard": RISES, "Nc": 3},
               "x_DPP": x, "vacuum_esum": [vac[0], vac[1]], "complete": False}
    if "AU-1" not in man:
        b1 = walk(man, "AU-1", "AU-1-partial", th_ar, [], 0.0, float(a1["mpi_over_M"]), float(a1["F_over_M"]), Mpv, ang, rad, vac, spec1, True)
    else:
        b1 = man["AU-1"]
    if b1.get("stop") == "start gap":
        print("ROUND_AU_FAILED start gap", flush=True); sys.exit(1)
    if b1["history"][-1][2] is None:
        man["complete"] = True; dump(man); print("ROUND_AU_DONE valence lost", flush=True); return
    C.RAD = rad
    radius("gap", 0, b1["theta"], ang, rad, Mpv, O)
    if not b1["converged"]:
        man["complete"] = True; dump(man); print("ROUND_AU_DONE", b1["stop"], flush=True); return
    dppj = json.loads((RT / "audit/rv_2026-10-02aq_A_j0.json").read_text(encoding="utf-8"))
    gapj = json.loads((RT / "audit/rv_2026-10-02au_gap_j0.json").read_text(encoding="utf-8"))
    move = abs(gapj["Ir2"] / gapj["I1"] - dppj["Ir2"] / dppj["I1"]) / (dppj["Ir2"] / dppj["I1"])
    print("move", move, flush=True)
    if move > 0.02:
        for j in (1, 2, 3):
            radius("gap", j, b1["theta"], ang, rad, Mpv, O)
    if "AU-2" not in man:
        ag = json.loads((RT / "audit/murun_2026-10-02ag_K14_D14_k12.json").read_text(encoding="utf-8"))
        M3 = 1.0 / 3.0; mpi = float(ag["inputs"]["mpi_over_mp"]) / M3; Fm = float(ag["inputs"]["F_over_mp"]) / M3
        r = rad.r; start = -2 * np.arctan(x * x / (r * r) * (1 + mpi * r) * np.exp(-mpi * r))
        spec2 = {"M_over_mp": M3, "exact": "1/3", "F_over_M": Fm, "mpi_over_M": mpi, "Mpv_over_M": Mpv, "x_DPP": x}
        C.RAD = rad
        walk(man, "AU-2", "AU-2-partial", start, [], 0.0, mpi, Fm, Mpv, ang, rad, vac, spec2, False)
    b2 = man["AU-2"]
    if b2["history"][-1][2] is not None:
        C.RAD = rad
        radius("sigma", 0, b2["theta"], ang, rad, Mpv, O)
    man["complete"] = True; dump(man); print("ROUND_AU_DONE", flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc(); print("ROUND_AU_FAILED", flush=True); sys.exit(1)
