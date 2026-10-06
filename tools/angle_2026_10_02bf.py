#!/usr/bin/env python3
"""Round-bf (FREEZE_2026-10-02bf, hashed before this run): filled weight on the PV valence partner.
  python -u tools/angle_2026_10_02bf.py
Does not edit cqsm_rot.py. Does not rescore the 91. Does not write a radius."""
import hashlib, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
RT = Path(__file__).resolve().parents[1]
OUT = RT / "audit/angle_2026-10-02bf.json"
K, D0, KMAX, NQ = 14, 14.0, 12.0, 1500
MIX, TOL, ITMAX, NC = 0.2, 1e-3, 80, 3
OV_MIN, TIE = 0.5, 1e-8

def freeze_ok():
    D = RT / "audit"; bad = 0
    for line in open(D / "FREEZE_2026-10-02bf.sha256", encoding="utf-8"):
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

def force_bf(s1, s2, Mpv, ang, rad, Nc, ev):
    """Physical weights match sc_force. One PV state gets the filled weight -Nc/(2 Mpv)."""
    S = np.zeros(len(rad.r)); P = np.zeros(len(rad.r)); sec = R.densities(None, ang, rad)
    wsea = -0.5 * Nc
    for (Kk, Pp), ent in s1.items():
        s, p = sec(Kk, ent)
        w = wsea * np.sign(ent[0]) * (2 * Kk + 1)
        if (Kk, Pp) == (0, 1):
            i = int(np.argmin(np.abs(ent[0] - ev))); w = np.array(w, dtype=float); w[i] += Nc
        S += s @ w; P += p @ w
    wsea = 0.5 * Nc / Mpv
    partner = {"applied": False, "reason": "missing_sector"}
    ent = s2.get((0, 1))
    vent = s1.get((0, 1))
    if ent is not None and vent is not None and ent[1].shape[0] == vent[1].shape[0]:
        i_val = int(np.argmin(np.abs(vent[0] - ev)))
        ov = np.abs(ent[1].conj().T @ vent[1][:, i_val])
        j = int(np.argmax(ov)); o = float(ov[j])
        second = float(np.max(np.where(np.arange(len(ov)) == j, -1.0, ov)))
        partner = {"applied": False, "j": j, "overlap": o, "second": second,
                   "E": float(ent[0][j]), "sign": float(np.sign(ent[0][j])),
                   "sea_weight": float(wsea * np.sign(ent[0][j])), "reason": "ok"}
        if o >= OV_MIN and o - second > TIE:
            partner["applied"] = True
            partner["weight"] = float(-wsea)
        else:
            partner["reason"] = "overlap" if o < OV_MIN else "tie"
    for (Kk, Pp), ent in s2.items():
        s, p = sec(Kk, ent)
        w = np.array(wsea * np.sign(ent[0]) * (2 * Kk + 1), dtype=float)
        if partner.get("applied") and (Kk, Pp) == (0, 1):
            w[partner["j"]] = -wsea * (2 * Kk + 1)
        S += s @ w; P += p @ w
    return S, P, partner

def main():
    if not freeze_ok():
        print("ROUND_BF_FAILED freeze hash", flush=True); sys.exit(1)
    print("ROUND_BF_START", flush=True)
    ag = json.loads((RT / "audit/murun_2026-10-02ag_K14_D14_k12.json").read_text(encoding="utf-8"))
    inp = ag["inputs"]; x = float(ag["x_DPP"]); Mpv = float(inp["Mpv_over_M"])
    mpi = float(inp["mpi_over_mp"]) / float(inp["M_over_mp"]); F = float(inp["F_over_M"])
    ang = C.Angular(K); rad = C.Radial(D0, KMAX, NQ); C.RAD = rad
    t0 = time.time(); z = lambda r: 0 * r
    v1 = C.spectrum(z, 1.0, ang, rad, K, True); v2 = C.spectrum(z, Mpv, ang, rad, K, True)
    vac = (float(C.esum(v1)), float(C.esum(v2)))
    print("vacuum", vac, "Mpv", Mpv, round(time.time() - t0, 1), flush=True)
    th0 = lambda r, mpiM=mpi: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
    th = R.edge_tail(th0(rad.r).copy(), rad, mpi)
    c = 4 * np.pi * mpi * mpi * F * F
    hist = []; reason = "itmax"; partner = None; gap = None; ev = None
    s1 = s2 = None
    for step in range(ITMAX):
        f = R.profile_fn(rad, th)
        s1 = C.spectrum(f, 1.0, ang, rad, K, True); s2 = C.spectrum(f, Mpv, ang, rad, K, True)
        ev = C.valence(s1)
        if ev is None:
            reason = "valence_lost"; gap = None; break
        S, P, partner = force_bf(s1, s2, Mpv, ang, rad, NC, ev)
        if not partner.get("applied"):
            reason = "partner_not_identified"; gap = None; break
        new = force_target(S, P, c, rad, mpi)
        gap = float(np.max(np.abs(new - th)))
        row = {"step": step, "dtheta": gap, "ev": float(ev), "partner_E": partner["E"],
               "overlap": partner["overlap"], "sign": partner["sign"], "mix": None}
        hist.append(row)
        print("sc", step, "dtheta", gap, "ev", ev, "partner_E", partner["E"], "ov", partner["overlap"], flush=True)
        if gap < TOL:
            reason = "tolerance"; break
        th = (1.0 - MIX) * th + MIX * new
        row["mix"] = MIX
    else:
        reason = "itmax"
        f = R.profile_fn(rad, th)
        s1 = C.spectrum(f, 1.0, ang, rad, K, True); s2 = C.spectrum(f, Mpv, ang, rad, K, True)
        ev = C.valence(s1)
        if ev is None:
            reason = "valence_lost"
        else:
            S, P, partner = force_bf(s1, s2, Mpv, ang, rad, NC, ev)
            if not partner.get("applied"):
                reason = "partner_not_identified"
            else:
                new = force_target(S, P, c, rad, mpi)
                gap = float(np.max(np.abs(new - th)))
                hist.append({"step": ITMAX, "dtheta": gap, "ev": float(ev), "partner_E": partner["E"],
                             "overlap": partner["overlap"], "sign": partner["sign"], "mix": None})
                print("sc", ITMAX, "dtheta", gap, "ev", ev, "partner_E", partner["E"], flush=True)
                if gap < TOL:
                    reason = "tolerance"
    if s1 is None:
        print("ROUND_BF_FAILED no spectrum", flush=True); sys.exit(1)
    if ev is None:
        old_gap = None
    else:
        Sold, Pold = R.sc_force(s1, s2, Mpv, ang, rad, NC, ev)
        old_gap = float(np.max(np.abs(force_target(Sold, Pold, c, rad, mpi) - th)))
    man = {"generated_by": "tools/angle_2026_10_02bf.py", "freeze": "FREEZE_2026-10-02bf",
           "Mpv_over_M": Mpv, "filled_weight": -0.5 * NC / Mpv,
           "stop_reason": reason, "gap": gap, "old_sc_force_gap": old_gap,
           "valence": None if ev is None else float(ev), "partner": partner,
           "accepted_steps": sum(1 for h in hist if h["mix"] is not None),
           "sign_changes": int(sum(hist[i]["sign"] != hist[i + 1]["sign"] for i in range(len(hist) - 1))),
           "history": hist, "seconds": round(time.time() - t0, 1)}
    dump(man)
    print("ROUND_BF_DONE", reason, gap, old_gap, flush=True)

if __name__ == "__main__":
    main()
