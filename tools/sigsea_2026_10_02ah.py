#!/usr/bin/env python3
"""Round-ah (FREEZE_2026-10-02ah, AH-2): full soliton scalar charge (valence + PV-regularised sea - vacuum, cqsm_rot.sc_force weights) and its rms radius
at the adopted round-ab soliton (K 12, D 12), kmax 12 and 14. -> audit/sigsea_2026-10-02ah.json (numpy/scipy)"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
RT = Path(__file__).resolve().parents[1]
Hw = json.loads((RT / "audit/heavy_2026-10-02ab_wide_K12.json").read_text()); d = Hw["AB1wide_info_K12"]; inp = Hw["inputs"]
Mpv = inp["Mpv_over_M"]; mpiM = inp["mpi_over_mp"] / inp["M_over_mp"]; x = d["x_DPP"]; Km = 12; Nc = 3
out = {"generated_by": "tools/sigsea_2026_10_02ah.py", "freeze": "FREEZE_2026-10-02ah", "x_DPP": x, "K": Km, "D": 12.0, "Mpv_over_M": Mpv, "runs": []}
rnd = lambda v: float("%.10g" % v)
for kmax in (12.0, 14.0):
    t0 = time.time(); ang = C.Angular(Km); rad = C.Radial(12.0, kmax); C.RAD = rad
    z = lambda r: 0 * r; th = lambda r: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
    s1 = C.spectrum(th, 1.0, ang, rad, Km, True); s2 = C.spectrum(th, Mpv, ang, rad, Km, True); v1 = C.spectrum(z, 1.0, ang, rad, Km, True); v2 = C.spectrum(z, Mpv, ang, rad, Km, True)
    ev = C.valence(s1)
    Sf, _ = R.sc_force(s1, s2, Mpv, ang, rad, Nc, ev); Sv0, _ = R.sc_force(v1, v2, Mpv, ang, rad, Nc, 1e9)   # vacuum: no valence level (ev far away -> argmin picks a state; corrected below)
    # vacuum without valence: recompute sea-only
    sec = R.densities(None, ang, rad); Svac = np.zeros(len(rad.r))
    for sp, wsea in ((v1, -0.5 * Nc), (v2, 0.5 * Nc / Mpv)):
        for (K, P), ent in sp.items():
            s, _ = sec(K, ent); Svac += s @ (wsea * np.sign(ent[0]) * (2 * K + 1))
    Sval = np.zeros(len(rad.r)); e, v, bl, off = s1[(0, 1)]; i = int(np.argmin(np.abs(e - ev))); s, _ = sec(0, s1[(0, 1)]); Sval = Nc * s[:, i]
    Sfull = Sf - Svac; Ssea = Sfull - Sval; w = rad.w; r = rad.r
    res = {"kmax": kmax, "eps_val": rnd(ev), "Q_val": rnd(np.sum(w * Sval)), "Q_sea": rnd(np.sum(w * Ssea)), "Q_full": rnd(np.sum(w * Sfull)),
           "r2_full": rnd(np.sum(w * r**2 * Sfull) / np.sum(w * Sfull)), "r2_val": rnd(np.sum(w * r**2 * Sval) / np.sum(w * Sval)), "seconds": round(time.time() - t0, 1)}
    out["runs"].append(res); print(res, flush=True)
(RT / "audit/sigsea_2026-10-02ah.json").write_text(json.dumps(out, indent=1) + "\n"); print("written", flush=True)
