#!/usr/bin/env python3
"""Round-al (FREEZE_2026-10-02al, AL-1): sharp single-PV sums on the 4 boxes D_j = D0 + j (pi/kmax)/4 (one radial-shell period at fixed kmax).
  --level A (kmax 12, D0 14) | B (kmax 14, D0 14): E, g_A^(0), xat, I per sample; rotational A, Amu, B at D0 (K 14, round-ag kmax-12 profile)
  --level sigma: sigma-projected charge (round-ai definition) at the round-ab soliton, K 12, D0 12, kmax 12 and 14  -> audit/shellavg_2026-10-02al_<level>.json"""
import argparse, json, math, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
ap = argparse.ArgumentParser(); ap.add_argument("--level", required=True); a = ap.parse_args()
RT = Path(__file__).resolve().parents[1]; Nc = 3; rnd = lambda v: float("%.10g" % v); z = lambda r: 0 * r; t0 = time.time()
def prof(x, mpiM): return lambda r: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
out = {"generated_by": "tools/shellavg_2026_10_02al.py", "freeze": "FREEZE_2026-10-02al", "level": a.level, "samples": []}
if a.level == "sigma":
    Hw = json.loads((RT / "audit/heavy_2026-10-02ab_wide_K12.json").read_text()); d = Hw["AB1wide_info_K12"]; i2 = Hw["inputs"]; Mpv = i2["Mpv_over_M"]
    thf = prof(d["x_DPP"], i2["mpi_over_mp"] / i2["M_over_mp"]); ang = C.Angular(12)
    for kmax in (12.0, 14.0):
        for j in range(4):
            DD = 12.0 + j * (math.pi / kmax) / 4; rad = C.Radial(DD, kmax); C.RAD = rad; sec = R.densities(None, ang, rad); r, w = rad.r, rad.w; tt = thf(r)
            s1 = C.spectrum(thf, 1.0, ang, rad, 12, True); ev = C.valence(s1); S = np.zeros(len(r)); P = np.zeros(len(r)); Sv = np.zeros(len(r))
            for mm, c in ((1.0, 1.0), (Mpv, -(1.0 / Mpv) ** 2)):
                ss = s1 if mm == 1.0 else C.spectrum(thf, mm, ang, rad, 12, True); vv = C.spectrum(z, mm, ang, rad, 12, True)
                for (K, Pp), ent in ss.items():
                    s, p = sec(K, ent); wt = -0.5 * Nc * np.sign(ent[0]) * (2 * K + 1) * c * mm; S += s @ wt; P += p @ wt
                for (K, Pp), ent in vv.items():
                    s, p = sec(K, ent); Sv += s @ (-0.5 * Nc * np.sign(ent[0]) * (2 * K + 1) * c * mm)
            e0 = s1[(0, 1)]; i = int(np.argmin(np.abs(e0[0] - ev))); s, p = sec(0, e0); S += Nc * s[:, i]; P += Nc * p[:, i]
            sP = min((1, -1), key=lambda sg: float(np.sum(w * np.abs(P * np.cos(tt) - sg * S * np.sin(tt)))))
            rho = S * np.cos(tt) + sP * P * np.sin(tt) - Sv
            res = {"kmax": kmax, "D": rnd(DD), "s_P": sP, "Q_sigma": rnd(np.sum(w * rho)), "r2Q": rnd(np.sum(w * r**2 * rho)), "seconds": round(time.time() - t0, 1)}
            out["samples"].append(res); print(res, flush=True)
else:
    kmax = {"A": 12.0, "B": 14.0}[a.level]; D0 = 14.0
    m = json.loads((RT / "audit/murun_2026-10-02ag_K14_D14_k12.json").read_text()); inp = m["inputs"]; Mpv = inp["Mpv_over_M"]; q = (1.0 / Mpv) ** 2
    th = prof(m["x_DPP"], inp["mpi_over_mp"] / inp["M_over_mp"]); Km = 14; ang = C.Angular(Km); W = {"s1": 1.0, "s2": -q, "v1": -1.0, "v2": q}
    out.update({"kmax": kmax, "D0": D0, "K": Km, "x_DPP": m["x_DPP"], "inputs": inp})
    for j in range(4):
        DD = D0 + j * (math.pi / kmax) / 4; rad = C.Radial(DD, kmax); C.RAD = rad; O = R.Ops(ang)
        SP = {"s1": C.spectrum(th, 1.0, ang, rad, Km, True), "s2": C.spectrum(th, Mpv, ang, rad, Km, True), "v1": C.spectrum(z, 1.0, ang, rad, Km, True), "v2": C.spectrum(z, Mpv, ang, rad, Km, True)}
        ev = C.valence(SP["s1"])
        def diag(sp, kind):
            t = 0.0; val = None
            for (K, P), ent in sp.items():
                Mz = 0 if K == 0 else K
                d_ = np.real(np.diag(O.pair(ent, K, Mz, ent, K, Mz, O.rxs_dot_tau, "rdt", "rfield"))) if kind == "r" else C.op_diag(ent, ang, K, ang.st) / 3.0
                t += -0.5 * (2 * K + 1) * float(np.sum(np.sign(ent[0]) * d_))
                if (K, P) == (0, 1): val = float(d_[int(np.argmin(np.abs(ent[0] - ev)))])
            return t, val
        E = 3 * ev - 1.5 * sum(W[k] * C.esum(s) for k, s in SP.items())
        xs = {k: diag(s, "r") for k, s in SP.items()}; gs = {k: diag(s, "c") for k, s in SP.items()}
        res = {"j": j, "D": rnd(DD), "eps_val": rnd(ev), "E_sol": rnd(E), "xat_val": rnd(xs["s1"][1]), "xat_sea": rnd(sum(W[k] * xs[k][0] for k in xs)),
               "gA0": rnd(-(Nc / 3.0) * (gs["s1"][1] + sum(W[k] * gs[k][0] for k in gs))), "I": rnd(C.inertia(SP["s1"], SP["s2"], Mpv, ang, Km, Nc, ev))}
        if j == 0:
            OPS = {"A": ([(O.sxt[c], "sxt%d" % c, "const") for c in range(3)], [(O.tau[c], "tau%d" % c, "const") for c in range(3)], 6.0),
                   "Amu": ([(O.rxs_x_tau[c], "rxt%d" % c, "rfield") for c in range(3)], [(O.tau[c], "tau%d" % c, "const") for c in range(3)], 6.0),
                   "B": ([(O.tau[c], "tau%d" % c, "const") for c in range(3)], [(O.rxs[c], "rxs%d" % c, "rfield") for c in range(3)], 1.0)}
            for nm, (X_, Y_, dv) in OPS.items():
                f = lambda sp, e_: complex(R.rot_sum(O, sp, e_, X_, Y_) / dv)
                tot = f(SP["s1"], ev); sea = f(SP["s1"], None); reg = (tot - sea) + (sea - q * f(SP["s2"], None)) - (f(SP["v1"], None) - q * f(SP["v2"], None))
                res[nm + "_reg"] = [rnd(reg.real), rnd(reg.imag)]
        res["seconds"] = round(time.time() - t0, 1); out["samples"].append(res); print(res, flush=True)
out["seconds"] = round(time.time() - t0, 1)
(RT / ("audit/shellavg_2026-10-02al_%s.json" % a.level)).write_text(json.dumps(out, indent=1) + "\n"); print("written", out["seconds"], flush=True)
