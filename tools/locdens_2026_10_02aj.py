#!/usr/bin/env python3
"""Round-aj (FREEZE_2026-10-02aj): regularised local densities built from the spectra (single PV, vacuum-subtracted).
AJ-1: mu_V^(0) current-type density of (rhat x sigma).tau integrated with r applied to the density, and the g_A^(0) density (validation), K 14, D 14, kmax 12/14/16.
AJ-2: sigma-projected scalar charge (round-ai definition, single PV), round-ab soliton, K 12, D 12, kmax 12/14/16.  -> audit/locdens_2026-10-02aj.json"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
RT = Path(__file__).resolve().parents[1]; Nc = 3
rnd = lambda v: float("%.10g" % v)
z = lambda r: 0 * r
def prof(x, mpiM): return lambda r: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
def density(ent, K, ang, rad, op, kind, wn):
    e, v, bl, off = ent; Mz = 0 if K == 0 else K; rho = np.zeros(len(rad.r))
    for ia, (ta, ca, la) in enumerate(bl):
        _, Fa, _ = rad.funcs(ca[0], la); ua = Fa @ v[off[ia]:off[ia + 1], :]
        for ib, (tb, cb, lb) in enumerate(bl):
            if kind == "rfield" and (ta == tb or abs(ca[0] - cb[0]) != 1): continue
            if kind == "const" and (ta != tb or ca[0] != cb[0]): continue
            pa, pb = ang.phi(ca[0], ca[1], K, Mz), ang.phi(cb[0], cb[1], K, Mz)
            c = ang.mat_field(pa, pb, op) if kind == "rfield" else ang.mat_const(pa, pb, op)
            if abs(c) < 1e-12: continue
            _, Fb, _ = rad.funcs(cb[0], lb); ub = Fb @ v[off[ib]:off[ib + 1], :]
            rho += np.real(c * (np.conj(ua) * ub) @ wn)
    return rho
out = {"generated_by": "tools/locdens_2026_10_02aj.py", "freeze": "FREEZE_2026-10-02aj", "AJ1": [], "AJ2": []}
m = json.loads((RT / "audit/murun_2026-10-02ag_K14_D14_k12.json").read_text()); inp = m["inputs"]
Mpv = inp["Mpv_over_M"]; q = (1.0 / Mpv) ** 2; th = prof(m["x_DPP"], inp["mpi_over_mp"] / inp["M_over_mp"]); ang = C.Angular(14)
for kmax in (12.0, 14.0, 16.0):
    t0 = time.time(); rad = C.Radial(14.0, kmax); C.RAD = rad; O = R.Ops(ang)
    sp = {"s1": C.spectrum(th, 1.0, ang, rad, 14, True), "s2": C.spectrum(th, Mpv, ang, rad, 14, True), "v1": C.spectrum(z, 1.0, ang, rad, 14, True), "v2": C.spectrum(z, Mpv, ang, rad, 14, True)}
    ev = C.valence(sp["s1"]); wts = {"s1": 1.0, "s2": -q, "v1": -1.0, "v2": q}
    rmu = np.zeros(len(rad.r)); rga = np.zeros(len(rad.r)); gdiag = 0.0
    for nm, s in sp.items():
        for (K, P), ent in s.items():
            wn = -0.5 * (2 * K + 1) * np.sign(ent[0]) * wts[nm]
            rmu += density(ent, K, ang, rad, O.rxs_dot_tau, "rfield", wn); rga += density(ent, K, ang, rad, ang.st, "const", wn) / 3.0
            gdiag += float(np.sum(wn * C.op_diag(ent, ang, K, ang.st) / 3.0))
    e0 = sp["s1"][(0, 1)]; i = int(np.argmin(np.abs(e0[0] - ev))); wv = np.zeros(len(e0[0])); wv[i] = 1.0
    vmu = density(e0, 0, ang, rad, O.rxs_dot_tau, "rfield", wv); vga = density(e0, 0, ang, rad, ang.st, "const", wv) / 3.0
    r, w = rad.r, rad.w; cum = np.cumsum(w * r * rmu)
    res = {"kmax": kmax, "xat_val": rnd(np.sum(w * r * vmu)), "xat_sea": rnd(cum[-1]), "xat_sea_cum_r": {str(R_): rnd(np.interp(R_, r, cum)) for R_ in (1, 2, 3, 4, 6, 8, 10, 12, 14)},
           "gA0_val_d": rnd(np.sum(w * vga)), "gA0_sea_density": rnd(np.sum(w * rga)), "gA0_sea_matrix": rnd(gdiag), "gA0": rnd(-(Nc / 3.0) * (np.sum(w * vga) + np.sum(w * rga))), "seconds": round(time.time() - t0, 1)}
    out["AJ1"].append(res); print(res, flush=True)
Hw = json.loads((RT / "audit/heavy_2026-10-02ab_wide_K12.json").read_text()); d = Hw["AB1wide_info_K12"]; i2 = Hw["inputs"]
Mpv2 = i2["Mpv_over_M"]; thf = prof(d["x_DPP"], i2["mpi_over_mp"] / i2["M_over_mp"]); ang = C.Angular(12)
for kmax in (12.0, 14.0, 16.0):
    t0 = time.time(); rad = C.Radial(12.0, kmax); C.RAD = rad; sec = R.densities(None, ang, rad); r, w = rad.r, rad.w; tt = thf(r)
    S = np.zeros(len(r)); P = np.zeros(len(r)); Sv = np.zeros(len(r))
    s1 = C.spectrum(thf, 1.0, ang, rad, 12, True); ev = C.valence(s1)
    for mm, c in ((1.0, 1.0), (Mpv2, -(1.0 / Mpv2) ** 2)):
        ss = s1 if mm == 1.0 else C.spectrum(thf, mm, ang, rad, 12, True); vv = C.spectrum(z, mm, ang, rad, 12, True)
        for (K, Pp), ent in ss.items():
            s, p = sec(K, ent); wt = -0.5 * Nc * np.sign(ent[0]) * (2 * K + 1) * c * mm; S += s @ wt; P += p @ wt
        for (K, Pp), ent in vv.items():
            s, p = sec(K, ent); Sv += s @ (-0.5 * Nc * np.sign(ent[0]) * (2 * K + 1) * c * mm)
    e0 = s1[(0, 1)]; i = int(np.argmin(np.abs(e0[0] - ev))); s, p = sec(0, e0); S += Nc * s[:, i]; P += Nc * p[:, i]
    sP = min((1, -1), key=lambda sg: float(np.sum(w * np.abs(P * np.cos(tt) - sg * S * np.sin(tt)))))
    rho = S * np.cos(tt) + sP * P * np.sin(tt) - Sv; cum = np.cumsum(w * rho)
    res = {"kmax": kmax, "s_P": sP, "Q_sigma": rnd(cum[-1]), "r2_sigma": rnd(np.sum(w * r**2 * rho) / cum[-1]), "Q_sigma_cum_r": {str(R_): rnd(np.interp(R_, r, cum)) for R_ in (1, 2, 3, 4, 6, 8, 10, 12)}, "seconds": round(time.time() - t0, 1)}
    out["AJ2"].append(res); print(res, flush=True)
(RT / "audit/locdens_2026-10-02aj.json").write_text(json.dumps(out, indent=1) + "\n"); print("written", flush=True)
