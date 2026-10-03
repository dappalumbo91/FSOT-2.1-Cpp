#!/usr/bin/env python3
"""Round-ah (FREEZE_2026-10-02ah, AH-1): mu_V^(0) sea sum at K 14, D 14 (profile of the kmax-12 run) for kmax 12, 14, 16: bare sea, PV, vacuum pieces.
  python tools/kscan_2026_10_02ah.py -> audit/kscan_2026-10-02ah.json (numpy/scipy)"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
RT = Path(__file__).resolve().parents[1]
m = json.loads((RT / "audit/murun_2026-10-02ag_K14_D14_k12.json").read_text()); inp = m["inputs"]; x = m["x_DPP"]
Mpv = inp["Mpv_over_M"]; mpiM = inp["mpi_over_mp"] / inp["M_over_mp"]; q = (1.0 / Mpv) ** 2; Km = 14; ang = C.Angular(Km)
out = {"generated_by": "tools/kscan_2026_10_02ah.py", "freeze": "FREEZE_2026-10-02ah", "K": Km, "D": 14.0, "x_DPP": x, "Mpv_over_M": Mpv, "scan": []}
for kmax in (12.0, 14.0, 16.0):
    t0 = time.time(); rad = C.Radial(14.0, kmax); C.RAD = rad; O = R.Ops(ang)
    z = lambda r: 0 * r; th = lambda r: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
    sp = {"s1": C.spectrum(th, 1.0, ang, rad, Km, True), "s2": C.spectrum(th, Mpv, ang, rad, Km, True), "v1": C.spectrum(z, 1.0, ang, rad, Km, True), "v2": C.spectrum(z, Mpv, ang, rad, Km, True)}
    ev = C.valence(sp["s1"]); tot = {}; val = None
    for nm, s in sp.items():
        t = 0.0
        for (K, P), a in s.items():
            Mz = 0 if K == 0 else K
            d = np.real(np.diag(O.pair(a, K, Mz, a, K, Mz, O.rxs_dot_tau, "rdt", "rfield")))
            t += -0.5 * (2 * K + 1) * float(np.sum(np.sign(a[0]) * d))
            if nm == "s1" and (K, P) == (0, 1): val = float(d[int(np.argmin(np.abs(a[0] - ev)))])
        tot[nm] = t
    rnd = lambda v: float("%.10g" % v)
    out["scan"].append({"kmax": kmax, "xat_val": rnd(val), "bare_minus_vac": rnd(tot["s1"] - tot["v1"]), "pv_minus_vacpv_weighted": rnd(-q * (tot["s2"] - tot["v2"])),
                        "xat_sea": rnd(tot["s1"] - q * tot["s2"] - tot["v1"] + q * tot["v2"]), "seconds": round(time.time() - t0, 1)})
    print(out["scan"][-1], flush=True)
(RT / "audit/kscan_2026-10-02ah.json").write_text(json.dumps(out, indent=1) + "\n"); print("written", flush=True)
