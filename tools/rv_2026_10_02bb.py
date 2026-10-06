#!/usr/bin/env python3
"""Round-bb (FREEZE_2026-10-02bb, hashed before this run): one force split on the diagnostic DPP.
  python -u tools/rv_2026_10_02bb.py
Does not edit cqsm_rot.py or rv_2026_10_02aq.py. Does not iterate. Does not score the 91."""
import hashlib, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
RT = Path(__file__).resolve().parents[1]
OUT = RT / "audit/rv_2026-10-02bb.json"
K, D0, KMAX, NQ, NC = 14, 14.0, 12.0, 1500, 3
AR0 = 0.17211904981809267
R_AZ = 0.9063180381993936

def freeze_ok():
    D = RT / "audit"; bad = 0
    for line in open(D / "FREEZE_2026-10-02bb.sha256", encoding="utf-8"):
        want, name = line.split()
        if hashlib.sha256((D / name).read_bytes()).hexdigest() != want: bad += 1
    return bad == 0

def force_pieces(sp1, sp2, Mpv, ang, rad, ev):
    n = len(rad.r)
    S_val = np.zeros(n); S_sea = np.zeros(n); S_pv = np.zeros(n)
    P_val = np.zeros(n); P_sea = np.zeros(n); P_pv = np.zeros(n)
    sec = R.densities(None, ang, rad)
    for (KK, Pp), ent in sp1.items():
        s, p = sec(KK, ent); w = (-0.5 * NC) * np.sign(ent[0]) * (2 * KK + 1)
        S_sea += s @ w; P_sea += p @ w
        if (KK, Pp) == (0, 1):
            i = int(np.argmin(np.abs(ent[0] - ev)))
            S_val += s[:, i] * NC; P_val += p[:, i] * NC
    for (KK, Pp), ent in sp2.items():
        s, p = sec(KK, ent); w = (0.5 * NC / Mpv) * np.sign(ent[0]) * (2 * KK + 1)
        S_pv += s @ w; P_pv += p @ w
    return S_val, S_sea, S_pv, P_val, P_sea, P_pv

def share(a, b, c_):
    den = abs(a) + abs(b) + abs(c_)
    if den == 0.0: return None
    return [abs(a) / den, abs(b) / den, abs(c_) / den]

def bin_at(i, rad, th, new, pieces, S, P, c):
    Sv, Ss, Sp, Pv, Ps, Pp = (float(pieces[k][i]) for k in range(6))
    return {"i": int(i), "r": float(rad.r[i]), "r_over_D": float(rad.r[i] / D0),
            "d": float(abs(new[i] - th[i])), "theta": float(th[i]), "new": float(new[i]),
            "S_val": Sv, "S_sea": Ss, "S_pv": Sp, "S": float(S[i]),
            "P_val": Pv, "P_sea": Ps, "P_pv": Pp, "P": float(P[i]), "c": float(c),
            "abs_share_S": share(Sv, Ss, Sp), "abs_share_P": share(Pv, Ps, Pp)}

def main():
    if not freeze_ok():
        print("ROUND_BB_FAILED freeze hash", flush=True); sys.exit(1)
    if OUT.exists():
        print("ROUND_BB_EXISTS", flush=True); return
    ag = json.loads((RT / "audit/murun_2026-10-02ag_K14_D14_k12.json").read_text(encoding="utf-8"))
    inp = ag["inputs"]; x = float(ag["x_DPP"]); Mpv = float(inp["Mpv_over_M"])
    M = float(inp["M_over_mp"]); F = float(inp["F_over_M"]); mpiM = float(inp["mpi_over_mp"]) / M
    ang = C.Angular(K); rad = C.Radial(D0, KMAX, NQ); C.RAD = rad
    th0 = lambda r, mpiM=mpiM: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
    th = R.edge_tail(th0(rad.r).copy(), rad, mpiM)
    print("BB-1 M/m_p", M, "mpi/M", mpiM, "F/M", F, "Mpv/M", Mpv, "x_DPP", x, flush=True)
    t0 = time.time()
    f = R.profile_fn(rad, th)
    s1 = C.spectrum(f, 1.0, ang, rad, K, True); s2 = C.spectrum(f, Mpv, ang, rad, K, True)
    ev = C.valence(s1)
    if ev is None:
        print("ROUND_BB_VALENCE_LOST", flush=True); return
    pieces = force_pieces(s1, s2, Mpv, ang, rad, ev)
    S, P = R.sc_force(s1, s2, Mpv, ang, rad, NC, ev)
    resS = float(np.max(np.abs(pieces[0] + pieces[1] + pieces[2] - S)))
    resP = float(np.max(np.abs(pieces[3] + pieces[4] + pieces[5] - P)))
    relS = resS / max(1.0, float(np.max(np.abs(S))))
    relP = resP / max(1.0, float(np.max(np.abs(P))))
    print("residual rel S", relS, "P", relP, "valence", ev, flush=True)
    if relS > 1e-12 or relP > 1e-12:
        print("ROUND_BB_FAILED piece residual", flush=True); sys.exit(1)
    c = 4 * np.pi * mpiM ** 2 * F ** 2
    new = np.arctan2(-P, -(S - c)); new = np.unwrap(new[::-1])[::-1]
    if new[0] > 0: new = new - 2 * np.pi * round(float(new[0]) / (2 * np.pi))
    new = R.edge_tail(new, rad, mpiM)
    d = np.abs(new - th); imax = int(np.argmax(d)); iaz = int(np.argmin(np.abs(rad.r - R_AZ)))
    res = {"freeze": "FREEZE_2026-10-02bb", "K": K, "D": D0, "kmax": KMAX, "nq": NQ, "Nc": NC,
           "M_over_mp": M, "F_over_M": F, "mpi_over_M": mpiM, "Mpv_over_M": Mpv, "x_DPP": x,
           "solver": "one step, no mix", "valence": float(ev), "c": float(c),
           "max_d": float(d[imax]), "step0_gap": AR0, "r_az": R_AZ,
           "rel_residual_S": relS, "rel_residual_P": relP,
           "max_bin": bin_at(imax, rad, th, new, pieces, S, P, c),
           "az_bin": bin_at(iaz, rad, th, new, pieces, S, P, c),
           "seconds": round(time.time() - t0, 1)}
    tmp = OUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8", newline="\n"); tmp.replace(OUT)
    print("max_d", res["max_d"], "i", imax, "r", res["max_bin"]["r"], "az", iaz, res["az_bin"]["r"], flush=True)
    print("ROUND_BB_DONE", flush=True)

if __name__ == "__main__":
    main()
