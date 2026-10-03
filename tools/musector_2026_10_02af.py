#!/usr/bin/env python3
"""Round-af (FREEZE_2026-10-02af, AF-1): mu_V^(0) sea sum per grand-spin sector (K,P) at the AE-1 K 12 and K 14 DPP profiles:
contributions of s1, s2 (PV), v1, v2 (vacuum) with the weights of cqsm_rot.observables. Writes audit/musector_2026-10-02af.json (numpy/scipy)."""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
RT = Path(__file__).resolve().parents[1]; out = {"generated_by": "tools/musector_2026_10_02af.py", "freeze": "FREEZE_2026-10-02af"}
for Km in (12, 14):
    t0 = time.time(); m = json.loads((RT / ("audit/murun_2026-10-02ae_K%d.json" % Km)).read_text()); inp = m["inputs"]; x = m["x_DPP"]
    Mpv = inp["Mpv_over_M"]; mpiM = inp["mpi_over_mp"] / inp["M_over_mp"]; q = (1.0 / Mpv) ** 2
    ang = C.Angular(Km); rad = C.Radial(float(Km), float(Km)); C.RAD = rad; O = R.Ops(ang)
    z = lambda r: 0 * r; th = lambda r: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
    sp = {"s1": C.spectrum(th, 1.0, ang, rad, Km, True), "s2": C.spectrum(th, Mpv, ang, rad, Km, True), "v1": C.spectrum(z, 1.0, ang, rad, Km, True), "v2": C.spectrum(z, Mpv, ang, rad, Km, True)}
    ev = C.valence(sp["s1"]); wts = {"s1": 1.0, "s2": -q, "v1": -1.0, "v2": q}; sec = {}; val = None
    for nm, s in sp.items():
        for (K, P), a in s.items():
            Mz = 0 if K == 0 else K
            d = np.real(np.diag(O.pair(a, K, Mz, a, K, Mz, O.rxs_dot_tau, "rdt", "rfield")))
            c = -0.5 * (2 * K + 1) * float(np.sum(np.sign(a[0]) * d))
            sec.setdefault("%d%s" % (K, "+" if P > 0 else "-"), {})[nm] = wts[nm] * c
            if nm == "s1" and (K, P) == (0, 1): val = float(d[int(np.argmin(np.abs(a[0] - ev)))])
    tot = {k: sum(v.values()) for k, v in sec.items()}
    out["K%d" % Km] = {"x_DPP": x, "xat_val": val, "xat_sea": sum(tot.values()), "xat_val_run": m["DPP"]["xat_val"], "xat_sea_run": m["DPP"]["xat_sea"],
                       "sectors": {k: {"total": tot[k], **sec[k]} for k in sec}, "seconds": round(time.time() - t0, 1)}
    print(Km, out["K%d" % Km]["xat_sea"], out["K%d" % Km]["xat_sea_run"], round(time.time() - t0, 1), flush=True)
    (RT / "audit/musector_2026-10-02af.json").write_text(json.dumps(out, indent=1) + "\n")
print("written", flush=True)
