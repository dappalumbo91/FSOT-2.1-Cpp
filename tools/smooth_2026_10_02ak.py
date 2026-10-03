#!/usr/bin/env python3
"""Round-ak (FREEZE_2026-10-02ak, AK-1b): single-PV sea sums with the smooth spectral convergence factor w_n = exp(-e_n^2/E_s^2), E_s = kmax/3
(valence level exempt; two-state sums carry w_n w_m via eigenvectors scaled by sqrt(w_n)), next to the sharp sums, at K 14, D 14 (round-ag kmax-12 profile).
  python tools/smooth_2026_10_02ak.py --kmax 12 [--full]  -> audit/smooth_2026-10-02ak_k12.json ; --sigma -> audit/smooth_2026-10-02ak_sigma.json"""
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
ap = argparse.ArgumentParser(); ap.add_argument("--kmax", type=float, default=12.0); ap.add_argument("--full", action="store_true"); ap.add_argument("--sigma", action="store_true"); a = ap.parse_args()
RT = Path(__file__).resolve().parents[1]; Nc = 3; rnd = lambda v: float("%.10g" % v); z = lambda r: 0 * r
def prof(x, mpiM): return lambda r: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
def smooth(sp, Es, ev=None):
    o = {}
    for k, (e, v, bl, off) in sp.items():
        w = np.exp(-e**2 / Es**2)
        if ev is not None and k == (0, 1): w[np.abs(e - ev) < 1e-12] = 1.0
        o[k] = (e, v * np.sqrt(w)[None, :], bl, off)
    return o
def esum_w(sp, Es): return sum((2 * K + 1) * np.sum(np.abs(v[0]) * np.exp(-v[0]**2 / Es**2)) for (K, P), v in sp.items())
if a.sigma:
    Hw = json.loads((RT / "audit/heavy_2026-10-02ab_wide_K12.json").read_text()); d = Hw["AB1wide_info_K12"]; i2 = Hw["inputs"]; Mpv = i2["Mpv_over_M"]
    thf = prof(d["x_DPP"], i2["mpi_over_mp"] / i2["M_over_mp"]); ang = C.Angular(12); out = {"generated_by": "tools/smooth_2026_10_02ak.py", "freeze": "FREEZE_2026-10-02ak", "runs": []}
    for kmax in (12.0, 14.0, 16.0):
        t0 = time.time(); Es = kmax / 3; rad = C.Radial(12.0, kmax); C.RAD = rad; sec = R.densities(None, ang, rad); r, w = rad.r, rad.w; tt = thf(r)
        s1 = C.spectrum(thf, 1.0, ang, rad, 12, True); ev = C.valence(s1); res = {"kmax": kmax, "E_s": Es}
        for tag, wfun in (("sharp", lambda sp, e_=None: sp), ("smooth", lambda sp, e_=None: smooth(sp, Es, e_))):
            S = np.zeros(len(r)); P = np.zeros(len(r)); Sv = np.zeros(len(r))
            for mm, c in ((1.0, 1.0), (Mpv, -(1.0 / Mpv) ** 2)):
                ss = wfun(s1 if mm == 1.0 else C.spectrum(thf, mm, ang, rad, 12, True)); vv = wfun(C.spectrum(z, mm, ang, rad, 12, True))
                for (K, Pp), ent in ss.items():
                    s, p = sec(K, ent); wt = -0.5 * Nc * np.sign(ent[0]) * (2 * K + 1) * c * mm; S += s @ wt; P += p @ wt
                for (K, Pp), ent in vv.items():
                    s, p = sec(K, ent); Sv += s @ (-0.5 * Nc * np.sign(ent[0]) * (2 * K + 1) * c * mm)
            e0 = s1[(0, 1)]; i = int(np.argmin(np.abs(e0[0] - ev))); s, p = sec(0, e0); S += Nc * s[:, i]; P += Nc * p[:, i]
            sP = min((1, -1), key=lambda sg: float(np.sum(w * np.abs(P * np.cos(tt) - sg * S * np.sin(tt)))))
            rho = S * np.cos(tt) + sP * P * np.sin(tt) - Sv
            res[tag] = {"s_P": sP, "Q_sigma": rnd(np.sum(w * rho)), "r2_sigma": rnd(np.sum(w * r**2 * rho) / np.sum(w * rho)), "Q_unprojected": rnd(np.sum(w * (S - Sv)))}
        res["seconds"] = round(time.time() - t0, 1); out["runs"].append(res); print(res, flush=True)
    (RT / "audit/smooth_2026-10-02ak_sigma.json").write_text(json.dumps(out, indent=1) + "\n"); print("written", flush=True); sys.exit()
m = json.loads((RT / "audit/murun_2026-10-02ag_K14_D14_k12.json").read_text()); inp = m["inputs"]; Mpv = inp["Mpv_over_M"]; q = (1.0 / Mpv) ** 2
th = prof(m["x_DPP"], inp["mpi_over_mp"] / inp["M_over_mp"]); Km = 14; ang = C.Angular(Km); kmax = a.kmax; Es = kmax / 3; t0 = time.time()
rad = C.Radial(14.0, kmax); C.RAD = rad; O = R.Ops(ang)
SP = {"s1": C.spectrum(th, 1.0, ang, rad, Km, True), "s2": C.spectrum(th, Mpv, ang, rad, Km, True), "v1": C.spectrum(z, 1.0, ang, rad, Km, True), "v2": C.spectrum(z, Mpv, ang, rad, Km, True)}
ev = C.valence(SP["s1"]); W = {"s1": 1.0, "s2": -q, "v1": -1.0, "v2": q}
out = {"generated_by": "tools/smooth_2026_10_02ak.py", "freeze": "FREEZE_2026-10-02ak", "K": Km, "D": 14.0, "kmax": kmax, "E_s": Es, "x_DPP": m["x_DPP"], "eps_val": ev, "inputs": inp}
def diag(sp, op, kind):
    t = 0.0; val = None
    for (K, P), ent in sp.items():
        Mz = 0 if K == 0 else K
        d = np.real(np.diag(O.pair(ent, K, Mz, ent, K, Mz, op, "rdt", "rfield"))) if kind == "r" else C.op_diag(ent, ang, K, ang.st) / 3.0
        t += -0.5 * (2 * K + 1) * float(np.sum(np.sign(ent[0]) * d))
        if (K, P) == (0, 1): val = float(d[int(np.argmin(np.abs(ent[0] - ev)))])
    return t, val
OPS = {"A": ([(O.sxt[c], "sxt%d" % c, "const") for c in range(3)], [(O.tau[c], "tau%d" % c, "const") for c in range(3)], 6.0),
       "Amu": ([(O.rxs_x_tau[c], "rxt%d" % c, "rfield") for c in range(3)], [(O.tau[c], "tau%d" % c, "const") for c in range(3)], 6.0),
       "B": ([(O.tau[c], "tau%d" % c, "const") for c in range(3)], [(O.rxs[c], "rxs%d" % c, "rfield") for c in range(3)], 1.0)}
for tag in ("sharp", "smooth"):
    sps = {k: (s if tag == "sharp" else smooth(s, Es, ev if k == "s1" else None)) for k, s in SP.items()}
    es = {k: (C.esum(s) if tag == "sharp" else esum_w(s, Es)) for k, s in SP.items()}
    E = 3 * ev - 1.5 * sum(W[k] * es[k] for k in es)
    xs = {k: diag(s, O.rxs_dot_tau, "r") for k, s in sps.items()}; gs = {k: diag(s, None, "c") for k, s in sps.items()}
    xat_sea = sum(W[k] * xs[k][0] for k in xs); gA0 = -(Nc / 3.0) * (gs["s1"][1] + sum(W[k] * gs[k][0] for k in gs))
    r_ = {"E_sol": rnd(E), "xat_val": rnd(xs["s1"][1]), "xat_sea": rnd(xat_sea), "gA0": rnd(gA0)}
    if a.full:
        r_["I"] = rnd(C.inertia(sps["s1"], sps["s2"], Mpv, ang, Km, Nc, ev))
        ops = ("A", "Amu", "B") if tag == "smooth" else ("A",)
        for nm in ops:
            X_, Y_, dv = OPS[nm]
            f = lambda sp, e_: complex(R.rot_sum(O, sp, e_, X_, Y_) / dv)
            tot = f(sps["s1"], ev); sea = f(sps["s1"], None); reg = (tot - sea) + (sea - q * f(sps["s2"], None)) - (f(sps["v1"], None) - q * f(sps["v2"], None))
            r_[nm + "_reg"] = [rnd(reg.real), rnd(reg.imag)]
    out[tag] = r_; print(tag, r_, round(time.time() - t0, 1), flush=True)
out["seconds"] = round(time.time() - t0, 1)
(RT / ("audit/smooth_2026-10-02ak_k%g%s.json" % (kmax, "_full" if a.full else ""))).write_text(json.dumps(out, indent=1) + "\n"); print("written", out["seconds"], flush=True)
