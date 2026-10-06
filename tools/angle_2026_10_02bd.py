#!/usr/bin/env python3
"""Round-bd (FREEZE_2026-10-02bd, hashed before this run): sea levels near zero when the step-44 gap opens.
  python -u tools/angle_2026_10_02bd.py
Does not edit cqsm_rot.py. Does not rescore the 91."""
import hashlib, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
RT = Path(__file__).resolve().parents[1]
OUT = RT / "audit/angle_2026-10-02bd.json"
K, D0, KMAX, NQ = 14, 14.0, 12.0, 1500
MIX, TOL, ITMAX, NC = 0.2, 1e-3, 44, 3
THRESH = 0.05
AV = {0: 0.17211904981809267, 39: 0.005631712767651509, 43: 0.005190733171335227}
AV44 = 0.19379649668786914
R_AZ = 0.9063180381993936
IMAX_AZ = 245

def freeze_ok():
    D = RT / "audit"; bad = 0
    for line in open(D / "FREEZE_2026-10-02bd.sha256", encoding="utf-8"):
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

def sea_rows(sp, ang, rad, imax, wsea):
    sec = R.densities(None, ang, rad)
    near, closest = [], None
    for (Kk, Pp), ent in sp.items():
        e = ent[0]
        s, p = sec(Kk, ent)
        for i in range(len(e)):
            ei = float(e[i])
            item = {"K": int(Kk), "P": int(Pp), "i": int(i), "E": ei,
                    "S_bin": float(s[imax, i]), "P_bin": float(p[imax, i]),
                    "sign": float(np.sign(ei)), "sea_weight": float(wsea * np.sign(ei) * (2 * Kk + 1))}
            if closest is None or abs(ei) < abs(closest["E"]):
                closest = item
            if abs(ei) < THRESH:
                near.append(item)
    near.sort(key=lambda z: abs(z["E"]))
    return near, closest

def main():
    if not freeze_ok():
        print("ROUND_BD_FAILED freeze hash", flush=True); sys.exit(1)
    ag = json.loads((RT / "audit/murun_2026-10-02ag_K14_D14_k12.json").read_text(encoding="utf-8"))
    inp = ag["inputs"]; x = float(ag["x_DPP"]); Mpv = float(inp["Mpv_over_M"])
    mpi = float(inp["mpi_over_mp"]) / float(inp["M_over_mp"]); F = float(inp["F_over_M"])
    ang = C.Angular(K); rad = C.Radial(D0, KMAX, NQ); C.RAD = rad
    iaz = int(np.argmin(np.abs(rad.r - R_AZ)))
    if iaz != IMAX_AZ or abs(float(rad.r[iaz]) - R_AZ) > 1e-12:
        print("ROUND_BD_FAILED az bin", iaz, float(rad.r[iaz]), flush=True); sys.exit(1)
    t0 = time.time(); z = lambda r: 0 * r
    v1 = C.spectrum(z, 1.0, ang, rad, K, True); v2 = C.spectrum(z, Mpv, ang, rad, K, True)
    vac = (float(C.esum(v1)), float(C.esum(v2)))
    print("vacuum", vac, round(time.time() - t0, 1), flush=True)
    th0 = lambda r, mpiM=mpi: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
    th = R.edge_tail(th0(rad.r).copy(), rad, mpi)
    c = 4 * np.pi * mpi * mpi * F * F
    hist = []; snap = None
    t1 = time.time()
    for it in range(ITMAX):
        f = R.profile_fn(rad, th)
        s1 = C.spectrum(f, 1.0, ang, rad, K, True); s2 = C.spectrum(f, Mpv, ang, rad, K, True)
        ev = C.valence(s1)
        if ev is None:
            print("ROUND_BD_FAILED valence lost", it, flush=True); sys.exit(1)
        S, P = R.sc_force(s1, s2, Mpv, ang, rad, NC, ev)
        new = force_target(S, P, c, rad, mpi)
        d = float(np.max(np.abs(new - th)))
        hist.append([it, float(NC * max(ev, 0.0) - 0.5 * NC * ((float(C.esum(s1)) - vac[0]) - (1.0 / Mpv) ** 2 * (float(C.esum(s2)) - vac[1])) + float(R.mass_energy(th, rad, mpi, F))), float(ev), d])
        print("sc", it, "dtheta", d, "ev", ev, flush=True)
        if it == 43:
            snap = (th.copy(), S.copy(), P.copy(), new.copy(), s1, s2, float(ev))
        th = (1 - MIX) * th + MIX * new
    print("replay", round(time.time() - t1, 1), flush=True)
    bad = [(i, hist[i][3], want) for i, want in AV.items() if abs(hist[i][3] - want) > 1e-9]
    if bad or snap is None:
        print("ROUND_BD_FAILED av mismatch", bad, flush=True); sys.exit(1)
    f = R.profile_fn(rad, th)
    s1 = C.spectrum(f, 1.0, ang, rad, K, True); s2 = C.spectrum(f, Mpv, ang, rad, K, True)
    ev = C.valence(s1)
    if ev is None:
        print("ROUND_BD_FAILED valence lost after mix", flush=True); sys.exit(1)
    S, P = R.sc_force(s1, s2, Mpv, ang, rad, NC, ev)
    new = force_target(S, P, c, rad, mpi)
    d = np.abs(new - th); step44 = float(d.max()); imax = int(np.argmax(d))
    if abs(step44 - AV44) > 1e-9 or imax != IMAX_AZ:
        print("ROUND_BD_FAILED step44", step44, imax, flush=True); sys.exit(1)

    def pack(tag, th_a, S_a, P_a, new_a, s1_a, s2_a, ev_a):
        w1, w2 = -0.5 * NC, 0.5 * NC / Mpv
        n1, c1 = sea_rows(s1_a, ang, rad, IMAX_AZ, w1)
        n2, c2 = sea_rows(s2_a, ang, rad, IMAX_AZ, w2)
        drops = []
        for src, rows, wsea in (("M", n1, w1), ("Mpv", n2, w2)):
            sec = R.densities(None, ang, rad)
            sp = s1_a if src == "M" else s2_a
            for row in rows:
                ent = sp[(row["K"], row["P"])]
                s, p = sec(row["K"], ent)
                Ss = S_a - s[:, row["i"]] * row["sea_weight"]
                Ps = P_a - p[:, row["i"]] * row["sea_weight"]
                alt = force_target(Ss, Ps, c, rad, mpi)
                drops.append({"spectrum": src, "K": row["K"], "P": row["P"], "E": row["E"],
                              "angle": float(alt[IMAX_AZ]), "delta_angle": float(alt[IMAX_AZ] - new_a[IMAX_AZ])})
        return {"tag": tag, "valence": ev_a, "theta": float(th_a[IMAX_AZ]), "force_angle": float(new_a[IMAX_AZ]),
                "gap_bin": float(abs(new_a[IMAX_AZ] - th_a[IMAX_AZ])),
                "S": float(S_a[IMAX_AZ]), "P": float(P_a[IMAX_AZ]),
                "near_M": n1, "near_Mpv": n2, "closest_M": c1, "closest_Mpv": c2,
                "sea_weight_removed": drops}

    th43, S43, P43, new43, s143, s243, ev43 = snap
    man = {"generated_by": "tools/angle_2026_10_02bd.py", "freeze": "FREEZE_2026-10-02bd",
           "threshold": THRESH, "az_bin": IMAX_AZ, "r_az": float(rad.r[IMAX_AZ]),
           "step43": pack("iteration-43", th43, S43, P43, new43, s143, s243, ev43),
           "step44": pack("after-mix", th, S, P, new, s1, s2, float(ev)),
           "step44_dtheta": step44, "seconds": round(time.time() - t0, 1)}
    dump(man)
    print("ROUND_BD_DONE", step44, "near43", len(man["step43"]["near_M"]), len(man["step43"]["near_Mpv"]),
          "near44", len(man["step44"]["near_M"]), len(man["step44"]["near_Mpv"]), flush=True)

if __name__ == "__main__":
    main()
