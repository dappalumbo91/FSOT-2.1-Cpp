#!/usr/bin/env python3
"""Round-be (FREEZE_2026-10-02be, hashed before this run): sign-safe shortening of the mix.
  python -u tools/angle_2026_10_02be.py
Does not edit cqsm_rot.py. Does not rescore the 91. Does not write a radius."""
import hashlib, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
RT = Path(__file__).resolve().parents[1]
OUT = RT / "audit/angle_2026-10-02be.json"
K, D0, KMAX, NQ = 14, 14.0, 12.0, 1500
MIX0, TOL, ITMAX, NC = 0.2, 1e-3, 80, 3
HALVES = 8
OV_MIN = 0.5
STEP0 = 0.17211904981809267

def freeze_ok():
    D = RT / "audit"; bad = 0
    for line in open(D / "FREEZE_2026-10-02be.sha256", encoding="utf-8"):
        want, name = line.split()
        if hashlib.sha256((D / name).read_bytes()).hexdigest() != want: bad += 1
    return bad == 0

def dump(man):
    tmp = OUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(OUT)

def force_target(S, P, c, rad, mpi):
    new = np.arctan2(-P, -(S - c))
    new = np.unwrap(new[::-1])[::-1]
    if new[0] > 0:
        new = new - 2 * np.pi * round(float(new[0]) / (2 * np.pi))
    return R.edge_tail(new, rad, mpi)

def closest(sp):
    best = None
    for (Kk, Pp), ent in sp.items():
        for ei in ent[0]:
            e = float(ei)
            if best is None or abs(e) < abs(best["E"]):
                best = {"K": int(Kk), "P": int(Pp), "E": e}
    return best

def match_flips(sp_a, sp_b, spectrum):
    flips = []
    if set(sp_a) != set(sp_b):
        return [{"spectrum": spectrum, "reason": "sector_set", "K": -1, "P": 0,
                 "overlap": 0.0, "E0": 0.0, "E1": 0.0}]
    for (Kk, Pp) in sp_a:
        ea, va = sp_a[(Kk, Pp)][0], sp_a[(Kk, Pp)][1]
        eb, vb = sp_b[(Kk, Pp)][0], sp_b[(Kk, Pp)][1]
        if va.shape != vb.shape or len(ea) != len(eb):
            flips.append({"spectrum": spectrum, "reason": "shape", "K": int(Kk), "P": int(Pp),
                          "overlap": 0.0, "E0": 0.0, "E1": 0.0})
            continue
        ov = np.abs(va.conj().T @ vb)
        n = int(ov.shape[0])
        used_r = np.zeros(n, dtype=bool); used_c = np.zeros(n, dtype=bool)
        pairs = []
        for flat in np.argsort(ov, axis=None)[::-1]:
            i, j = divmod(int(flat), n)
            if used_r[i] or used_c[j]:
                continue
            used_r[i] = True; used_c[j] = True
            pairs.append((i, j, float(ov[i, j])))
            if len(pairs) == n:
                break
        for i, j, o in pairs:
            e0, e1 = float(ea[i]), float(eb[j])
            reason = None
            if o < OV_MIN:
                reason = "overlap"
            elif float(np.sign(e0)) != float(np.sign(e1)):
                reason = "sign"
            if reason:
                flips.append({"spectrum": spectrum, "reason": reason, "K": int(Kk), "P": int(Pp),
                              "overlap": o, "E0": e0, "E1": e1})
    return flips

def main():
    if not freeze_ok():
        print("ROUND_BE_FAILED freeze hash", flush=True); sys.exit(1)
    print("ROUND_BE_START", flush=True)
    ag = json.loads((RT / "audit/murun_2026-10-02ag_K14_D14_k12.json").read_text(encoding="utf-8"))
    inp = ag["inputs"]; x = float(ag["x_DPP"]); Mpv = float(inp["Mpv_over_M"])
    mpi = float(inp["mpi_over_mp"]) / float(inp["M_over_mp"]); F = float(inp["F_over_M"])
    ang = C.Angular(K); rad = C.Radial(D0, KMAX, NQ); C.RAD = rad
    t0 = time.time(); z = lambda r: 0 * r
    v1 = C.spectrum(z, 1.0, ang, rad, K, True); v2 = C.spectrum(z, Mpv, ang, rad, K, True)
    vac = (float(C.esum(v1)), float(C.esum(v2)))
    print("vacuum", vac, round(time.time() - t0, 1), flush=True)
    th0 = lambda r, mpiM=mpi: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
    th = R.edge_tail(th0(rad.r).copy(), rad, mpi)
    c = 4 * np.pi * mpi * mpi * F * F
    hist = []; s1 = s2 = None
    reason = "itmax"; full_would_cross = None; stop_flips = []; stop_mix = None
    for step in range(ITMAX):
        if s1 is None:
            f = R.profile_fn(rad, th)
            s1 = C.spectrum(f, 1.0, ang, rad, K, True); s2 = C.spectrum(f, Mpv, ang, rad, K, True)
        ev = C.valence(s1)
        if ev is None:
            if step == 0:
                print("ROUND_BE_FAILED valence lost", flush=True); sys.exit(1)
            reason = "valence_lost"; break
        S, P = R.sc_force(s1, s2, Mpv, ang, rad, NC, ev)
        new = force_target(S, P, c, rad, mpi)
        d = float(np.max(np.abs(new - th)))
        Em = NC * max(ev, 0.0) - 0.5 * NC * ((float(C.esum(s1)) - vac[0]) - (1.0 / Mpv) ** 2 * (float(C.esum(s2)) - vac[1])) + float(R.mass_energy(th, rad, mpi, F))
        hist.append({"step": step, "dtheta": d, "ev": float(ev), "E": float(Em), "mix": None})
        print("sc", step, "dtheta", d, "ev", ev, flush=True)
        if step == 0 and abs(d - STEP0) > 1e-9:
            print("ROUND_BE_FAILED step0", d, flush=True); sys.exit(1)
        if d < TOL:
            trial = match_flips(s1, C.spectrum(R.profile_fn(rad, new), 1.0, ang, rad, K, True), "M")
            trial += match_flips(s2, C.spectrum(R.profile_fn(rad, new), Mpv, ang, rad, K, True), "Mpv")
            full_would_cross = bool(trial)
            stop_flips = trial
            stop_mix = 1.0
            reason = "tolerance"
            break
        accepted = False
        flips = []
        for k in range(HALVES + 1):
            mix = MIX0 * 2.0 ** (-k)
            th_c = (1.0 - mix) * th + mix * new
            f = R.profile_fn(rad, th_c)
            t1 = C.spectrum(f, 1.0, ang, rad, K, True); t2 = C.spectrum(f, Mpv, ang, rad, K, True)
            flips = match_flips(s1, t1, "M") + match_flips(s2, t2, "Mpv")
            print("trial", step, "k", k, "mix", mix, "flips", len(flips), flush=True)
            if not flips:
                th = th_c; s1, s2 = t1, t2
                hist[-1]["mix"] = mix
                stop_mix = mix
                accepted = True
                break
        if not accepted:
            reason = "floor_sign_change"
            stop_flips = flips
            stop_mix = MIX0 * 2.0 ** (-HALVES)
            break
    else:
        reason = "itmax"
        f = R.profile_fn(rad, th)
        s1 = C.spectrum(f, 1.0, ang, rad, K, True); s2 = C.spectrum(f, Mpv, ang, rad, K, True)
        ev = C.valence(s1)
        if ev is None:
            reason = "valence_lost"
        else:
            S, P = R.sc_force(s1, s2, Mpv, ang, rad, NC, ev)
            new = force_target(S, P, c, rad, mpi)
            d = float(np.max(np.abs(new - th)))
            Em = NC * max(ev, 0.0) - 0.5 * NC * ((float(C.esum(s1)) - vac[0]) - (1.0 / Mpv) ** 2 * (float(C.esum(s2)) - vac[1])) + float(R.mass_energy(th, rad, mpi, F))
            hist.append({"step": ITMAX, "dtheta": d, "ev": float(ev), "E": float(Em), "mix": None})
            print("sc", ITMAX, "dtheta", d, "ev", ev, flush=True)
    if s1 is None:
        print("ROUND_BE_FAILED no spectrum", flush=True); sys.exit(1)
    stop_flips = sorted(stop_flips, key=lambda z: abs(z["E0"]))
    man = {"generated_by": "tools/angle_2026_10_02be.py", "freeze": "FREEZE_2026-10-02be",
           "stop_reason": reason, "gap": hist[-1]["dtheta"] if hist else None,
           "mix": stop_mix, "valence": hist[-1]["ev"] if hist else None,
           "full_replacement_would_cross": full_would_cross,
           "accepted_steps": sum(1 for h in hist if h["mix"] is not None),
           "closest_M": closest(s1), "closest_Mpv": closest(s2),
           "n_sign_changes": len(stop_flips), "sign_changes": stop_flips[:8],
           "history": hist, "seconds": round(time.time() - t0, 1)}
    dump(man)
    print("ROUND_BE_DONE", reason, man["gap"], stop_mix, flush=True)

if __name__ == "__main__":
    main()
