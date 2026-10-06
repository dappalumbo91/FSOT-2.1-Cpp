#!/usr/bin/env python3
"""Round-az (FREEZE_2026-10-02az, hashed before this run): itmax 44 from the DPP, then one force balance.
  python -u tools/angle_2026_10_02az.py
Does not edit cqsm_rot.py, the av freeze, or the 91."""
import hashlib, json, sys, time, traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
RT = Path(__file__).resolve().parents[1]
OUT = RT / "audit/angle_2026-10-02az.json"
K, D0, KMAX, NQ = 14, 14.0, 12.0, 1500
MIX, TOL, ITMAX, NC = 0.2, 1e-3, 44, 3
AV = {0: 0.17211904981809267, 39: 0.005631712767651509, 43: 0.005190733171335227}
AV44 = 0.19379649668786914

def freeze_ok():
    D = RT / "audit"; bad = 0
    for line in open(D / "FREEZE_2026-10-02az.sha256", encoding="utf-8"):
        want, name = line.split()
        if hashlib.sha256((D / name).read_bytes()).hexdigest() != want: bad += 1
    return bad == 0

def dump(man):
    tmp = OUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(OUT)

def main():
    if not freeze_ok():
        print("ROUND_AZ_FAILED freeze hash", flush=True); sys.exit(1)
    ag = json.loads((RT / "audit/murun_2026-10-02ag_K14_D14_k12.json").read_text(encoding="utf-8"))
    inp = ag["inputs"]; x = float(ag["x_DPP"]); Mpv = float(inp["Mpv_over_M"])
    mpi = float(inp["mpi_over_mp"]) / float(inp["M_over_mp"]); F = float(inp["F_over_M"])
    ang = C.Angular(K); rad = C.Radial(D0, KMAX, NQ); C.RAD = rad
    t0 = time.time(); z = lambda r: 0 * r
    v1 = C.spectrum(z, 1.0, ang, rad, K, True); v2 = C.spectrum(z, Mpv, ang, rad, K, True)
    vac = (float(C.esum(v1)), float(C.esum(v2)))
    print("vacuum", vac, round(time.time() - t0, 1), flush=True)
    th0 = lambda r, mpiM=mpi: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
    t1 = time.time()
    th, conv, hist = R.self_consistent_m(th0, Mpv, ang, rad, K, NC, vac, mpi, F, mix=MIX, itmax=ITMAX, tol=TOL,
                                          log=lambda *a: print(*a, flush=True))
    hist = [[h[0], None if h[1] is None else float(h[1]), None if h[2] is None else float(h[2]), None if h[3] is None else float(h[3])] for h in hist]
    print("call done", "converged", bool(conv), "steps", len(hist), "s", round(time.time() - t1, 1), flush=True)
    bad = []
    for i, want in AV.items():
        got = None if len(hist) <= i else hist[i][3]
        if got is None or abs(got - want) > 1e-9:
            bad.append((i, got, want))
    if bad or len(hist) != ITMAX:
        print("ROUND_AZ_FAILED av mismatch", bad, "n", len(hist), flush=True); sys.exit(1)
    f = R.profile_fn(rad, th)
    s1 = C.spectrum(f, 1.0, ang, rad, K, True); s2 = C.spectrum(f, Mpv, ang, rad, K, True)
    ev = C.valence(s1)
    if ev is None:
        print("ROUND_AZ_FAILED valence lost", flush=True); sys.exit(1)
    c = 4 * np.pi * mpi * mpi * F * F
    S, P = R.sc_force(s1, s2, Mpv, ang, rad, NC, ev)
    new = np.arctan2(-P, -(S - c)); new = np.unwrap(new[::-1])[::-1]
    if new[0] > 0: new = new - 2 * np.pi * round(float(new[0]) / (2 * np.pi))
    new = R.edge_tail(new, rad, mpi)
    d = np.abs(new - th)
    E = NC * max(float(ev), 0.0) - 0.5 * NC * ((float(C.esum(s1)) - vac[0]) - (1.0 / Mpv) ** 2 * (float(C.esum(s2)) - vac[1])) + float(R.mass_energy(th, rad, mpi, F))
    imax = int(np.argmax(d)); r = rad.r; edge = 0.75 * rad.D
    interior = r <= edge; tail = r > edge
    step44 = float(d.max())
    if abs(step44 - AV44) > 1e-9:
        print("ROUND_AZ_FAILED step44", step44, AV44, flush=True); sys.exit(1)
    man = {"generated_by": "tools/angle_2026_10_02az.py", "freeze": "FREEZE_2026-10-02az",
           "basis": {"K": K, "D": D0, "kmax": KMAX, "nq": NQ, "mix": MIX, "tol": TOL, "itmax": ITMAX},
           "history": hist, "step44_dtheta": step44, "step44_E": E, "step44_valence": float(ev),
           "imax": imax, "r_imax": float(r[imax]), "r_over_D": float(r[imax] / rad.D), "in_tail": bool(r[imax] > edge),
           "max_interior": float(d[interior].max()) if interior.any() else None,
           "max_tail": float(d[tail].max()) if tail.any() else None,
           "r_interior_max": float(r[interior][int(np.argmax(d[interior]))]) if interior.any() else None,
           "r_tail_max": float(r[tail][int(np.argmax(d[tail]))]) if tail.any() else None,
           "n_bins": int(len(r)), "n_gt_0.05": int(np.sum(d > 0.05)),
           "n_interior_gt_0.05": int(np.sum(d[interior] > 0.05)), "n_tail_gt_0.05": int(np.sum(d[tail] > 0.05)),
           "edge_r": float(edge), "seconds": round(time.time() - t0, 1)}
    dump(man)
    print("step44", step44, "r", man["r_imax"], "r/D", man["r_over_D"], "tail", man["in_tail"],
          "max_interior", man["max_interior"], "max_tail", man["max_tail"], flush=True)
    print("ROUND_AZ_DONE", flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc(); print("ROUND_AZ_FAILED", flush=True); sys.exit(1)
