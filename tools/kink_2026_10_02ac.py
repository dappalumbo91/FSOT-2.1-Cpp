#!/usr/bin/env python3
"""Round-ac (FREEZE_2026-10-02ac, AC-2) kink diagnostic: E(x) split into 3 eps_val, sea, PV and mass parts near x = 1.2-1.3 (K 12, round-ab inputs).
Writes audit/kink_2026-10-02ac.jsonl (numpy/scipy; unscored)."""
import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
Hw = json.loads((Path(__file__).resolve().parents[1] / "audit/heavy_2026-10-02ab_wide_K12.json").read_text())
inp = Hw["inputs"]; Mpv = inp["Mpv_over_M"]; mpiM = inp["mpi_over_mp"] / inp["M_over_mp"]; FM = inp["F_over_M"]; Km = 12
ang = C.Angular(Km); rad = C.Radial(12.0, 12.0); C.RAD = rad
z = lambda r: 0 * r
v1 = C.spectrum(z, 1.0, ang, rad, Km, True); v2 = C.spectrum(z, Mpv, ang, rad, Km, True)
out = open(Path(__file__).resolve().parents[1] / "audit/kink_2026-10-02ac.jsonl", "w")
for x in [1.15, 1.2, 1.225, 1.25, 1.275, 1.3, 1.35]:
    th = (lambda x: (lambda r: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))))(x)
    s1 = C.spectrum(th, 1.0, ang, rad, Km); s2 = C.spectrum(th, Mpv, ang, rad, Km); ev = C.valence(s1)
    sea = -1.5 * (C.esum(s1) - C.esum(v1)); pv = 1.5 * (1.0 / Mpv) ** 2 * (C.esum(s2) - C.esum(v2)); em = R.mass_energy(th(rad.r), rad, mpiM, FM)
    rec = {"x": x, "E": float(3 * max(ev, 0) + sea + pv + em), "val3": float(3 * max(ev, 0)), "eps_val": float(ev), "sea": float(sea), "pv": float(pv), "mass": float(em)}
    out.write(json.dumps(rec) + "\n"); out.flush(); print(rec, flush=True)
