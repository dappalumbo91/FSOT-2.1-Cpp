#!/usr/bin/env python3
"""Round-w diagnostic (post-freeze, not scored): rotational response of the soliton profile.
Within the massive DPP family, minimise E_J(x)/M = E_sol(x)/M + J(J+1)/(2 I(x) M) separately for J = 1/2 (N) and 3/2 (Delta)
instead of rotating the static minimum rigidly; report x_N, x_Delta, Delta-N and the observables at x_N.
  python tools/rot_2026_10_02w.py --hub HUB --K 12 --out audit/rot_2026-10-02w_K12.json
"""
import argparse, json, math, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
import fsot02d as X
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--K", type=int, default=12); ap.add_argument("--out", required=True); a = ap.parse_args()
X.setup(a.hub); L = X.leaves(); mp = float(X.kg_to_GeV(L["m_p_kg"]) * 1000); mpi = float(L["m_pi_pm_MeV"]); M = mp / 3
Mpv = math.sqrt(math.e); mpiM = mpi / M; FM = math.sqrt(3) / (2 * math.pi); K = a.K; Nc = 3
ang = C.Angular(K); rad = C.Radial(float(K), float(K)); C.RAD = rad; O = R.Ops(ang); z = lambda r: 0 * r
v1 = C.spectrum(z, 1.0, ang, rad, K, True); v2 = C.spectrum(z, Mpv, ang, rad, K, True); vac = (C.esum(v1), C.esum(v2))
prof = lambda x: (lambda r: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r)))
pts = []
for x in (0.7, 0.8, 0.9, 1.0, 1.1):
    th = prof(x); s1 = C.spectrum(th, 1.0, ang, rad, K, True); s2 = C.spectrum(th, Mpv, ang, rad, K, True); ev = C.valence(s1)
    E = 3 * max(ev, 0.0) - 1.5 * ((C.esum(s1) - vac[0]) - (1.0 / Mpv) ** 2 * (C.esum(s2) - vac[1])) + R.mass_energy(th(rad.r), rad, mpiM, FM)
    I = C.inertia(s1, s2, Mpv, ang, K, Nc, ev); pts.append([x, float(E), float(I), float(ev)]); print("x", x, "E", E, "IM", I, flush=True)
xs = np.array([p[0] for p in pts]); Es = np.array([p[1] for p in pts]); Is = np.array([p[2] for p in pts])
cE = np.polyfit(xs, Es, 3); cI = np.polyfit(xs, Is, 3); fine = np.linspace(xs[0], xs[-1], 4001)
res = {"K": K, "points": pts}
for nm, J in (("static", None), ("N", 0.5), ("Delta", 1.5)):
    f = np.polyval(cE, fine) + (0 if J is None else J * (J + 1) / (2 * np.polyval(cI, fine)))
    i = int(np.argmin(f)); res[nm] = {"x": float(fine[i]), "E_over_M": float(np.polyval(cE, fine[i])), "IM": float(np.polyval(cI, fine[i])), "E_J_over_M": float(f[i]), "edge": i in (0, len(fine) - 1)}
xs_ = res["static"]["x"]; Ist = float(np.polyval(cI, xs_))
res["DN_rigid_MeV"] = 3 * M / (2 * Ist); res["DN_response_MeV"] = (res["Delta"]["E_J_over_M"] - res["N"]["E_J_over_M"]) * M
print(json.dumps(res), flush=True)
for nm in ("static", "N"):
    o = R.observables(prof(res[nm]["x"]), Mpv, ang, rad, K, Nc, vac, v1, v2, O); res[nm]["obs"] = o; print(nm, o, flush=True)
    Path(a.out).write_text(json.dumps(res, indent=1) + "\n")
