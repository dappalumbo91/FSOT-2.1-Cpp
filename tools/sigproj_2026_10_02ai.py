#!/usr/bin/env python3
"""Round-ai (FREEZE_2026-10-02ai, AI-2): sigma-mode projected soliton scalar density rho_sigma = S cos(theta) + s_P P sin(theta) - S_vac
(valence N_c + regularised sea, single- and two-subtraction PV) at the adopted round-ab soliton, K 12, D 12, kmax 12 and 14. -> audit/sigproj_2026-10-02ai.json"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
RT = Path(__file__).resolve().parents[1]
Hw = json.loads((RT / "audit/heavy_2026-10-02ab_wide_K12.json").read_text()); d = Hw["AB1wide_info_K12"]; inp = Hw["inputs"]
mpiM = inp["mpi_over_mp"] / inp["M_over_mp"]; x = d["x_DPP"]; Km = 12; Nc = 3
SCH = {"single": [(1.0, 1.0), (inp["Mpv_over_M"], -(1.0 / inp["Mpv_over_M"]) ** 2)], "double": [(1.0, 1.0), (1.340129576, -0.5663113338), (6.959685111, 3.523179412e-4)]}
rnd = lambda v: float("%.10g" % v)
out = {"generated_by": "tools/sigproj_2026_10_02ai.py", "freeze": "FREEZE_2026-10-02ai", "x_DPP": x, "K": Km, "D": 12.0, "runs": []}
for kmax in (12.0, 14.0):
    t0 = time.time(); ang = C.Angular(Km); rad = C.Radial(12.0, kmax); C.RAD = rad; sec = R.densities(None, ang, rad)
    z = lambda r: 0 * r; thf = lambda r: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
    masses = sorted({mm for s in SCH.values() for mm, _ in s})
    SP = {mm: (C.spectrum(thf, mm, ang, rad, Km, True), C.spectrum(z, mm, ang, rad, Km, True)) for mm in masses}
    ev = C.valence(SP[1.0][0]); r = rad.r; w = rad.w; th = thf(r)
    dens = {}
    for mm, (s_, v_) in SP.items():
        Ss = np.zeros(len(r)); Ps = np.zeros(len(r)); Sv = np.zeros(len(r))
        for (K, P), ent in s_.items():
            s, p = sec(K, ent); wt = -0.5 * Nc * np.sign(ent[0]) * (2 * K + 1); Ss += s @ wt; Ps += p @ wt
        for (K, P), ent in v_.items():
            s, p = sec(K, ent); Sv += s @ (-0.5 * Nc * np.sign(ent[0]) * (2 * K + 1))
        dens[mm] = (Ss, Ps, Sv)
    e0 = SP[1.0][0][(0, 1)]; i = int(np.argmin(np.abs(e0[0] - ev))); s, p = sec(0, e0); Sval, Pval = Nc * s[:, i], Nc * p[:, i]
    res = {"kmax": kmax, "eps_val": rnd(ev)}
    for nm, lst in SCH.items():
        S = Sval.copy(); P = Pval.copy(); Sv = np.zeros(len(r))
        for mm, c in lst:
            Ss, Ps, Svv = dens[mm]; S += c * mm * Ss; P += c * mm * Ps; Sv += c * mm * Svv
        sP = min((1, -1), key=lambda sg: float(np.sum(w * np.abs(P * np.cos(th) - sg * S * np.sin(th)))))
        rho = S * np.cos(th) + sP * P * np.sin(th) - Sv; rv = Sval * np.cos(th) + sP * Pval * np.sin(th)
        res[nm] = {"s_P": sP, "Q_sigma": rnd(np.sum(w * rho)), "Q_sigma_val": rnd(np.sum(w * rv)), "r2_sigma": rnd(np.sum(w * r**2 * rho) / np.sum(w * rho)),
                   "Q_scalar_unprojected": rnd(np.sum(w * (S - Sv))), "depletion_Svac_cos_minus_1": rnd(np.sum(w * Sv * (np.cos(th) - 1))),
                   "stationarity_ratio": rnd(float(np.sum(w * np.abs(P * np.cos(th) - sP * S * np.sin(th))) / np.sum(w * np.abs(S - Sv))))}
    res["seconds"] = round(time.time() - t0, 1); out["runs"].append(res); print(res, flush=True)
(RT / "audit/sigproj_2026-10-02ai.json").write_text(json.dumps(out, indent=1) + "\n"); print("written", flush=True)
