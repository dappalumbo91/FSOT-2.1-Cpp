#!/usr/bin/env python3
"""Round-ad (FREEZE_2026-10-02ad): AD-1 rotational g_A term split (valence, bare sea, PV sea, vacuum) and the inertia at the adopted
AC-2 soliton (round-ab wide run, K 12); AD-2 valence scalar charge S_val and scalar/vector rms radii. Writes audit/gatrace_2026-10-02ad.json (numpy/scipy)."""
import json, math, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
RT = Path(__file__).resolve().parents[1]
Hw = json.loads((RT / "audit/heavy_2026-10-02ab_wide_K12.json").read_text()); d = Hw["AB1wide_info_K12"]; inp = Hw["inputs"]
Mpv = inp["Mpv_over_M"]; mpiM = inp["mpi_over_mp"] / inp["M_over_mp"]; x = d["x_DPP"]; Km = 12; t0 = time.time()
ang = C.Angular(Km); rad = C.Radial(float(Km), float(Km)); C.RAD = rad; O = R.Ops(ang)
z = lambda r: 0 * r
v1 = C.spectrum(z, 1.0, ang, rad, Km, True); v2 = C.spectrum(z, Mpv, ang, rad, Km, True)
th = lambda r: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
s1 = C.spectrum(th, 1.0, ang, rad, Km, True); s2 = C.spectrum(th, Mpv, ang, rad, Km, True); ev = C.valence(s1)
X = [(O.sxt[c], "sxt%d" % c, "const") for c in range(3)]; Y = [(O.tau[c], "tau%d" % c, "const") for c in range(3)]
A = lambda sp, e: complex(R.rot_sum(O, sp, e, X, Y) / 6.0)
At, As, Ap, Av1, Av2 = A(s1, ev), A(s1, None), A(s2, None), A(v1, None), A(v2, None)
I = C.inertia(s1, s2, Mpv, ang, Km, 3, ev)
# valence densities (K = 0, P = +)
sec = R.densities(s1, ang, rad); e, v, blocks, off = s1[(0, 1)]; iv = int(np.argmin(np.abs(e - ev)))
s_, _ = sec(0, s1[(0, 1)]); sv = s_[:, iv]
nrm = np.zeros_like(sv)
for i, (t, c, lk) in enumerate(blocks):
    _, F, _ = rad.funcs(c[0], lk); u = F @ v[off[i]:off[i + 1], iv]; nrm = nrm + np.abs(u) ** 2
r = rad.r; w = rad.w
Sval = float(np.sum(w * sv) / np.sum(w * nrm)); rS2 = float(np.sum(w * r**2 * sv) / np.sum(w * sv)); rV2 = float(np.sum(w * r**2 * nrm) / np.sum(w * nrm))
out = {"generated_by": "tools/gatrace_2026_10_02ad.py", "freeze": "FREEZE_2026-10-02ad", "x_DPP": x, "eps_val": ev, "I_times_M": float(I),
       "A_total_im": At.imag, "A_sea_im": As.imag, "A_val_im": At.imag - As.imag, "A_pv_im": Ap.imag, "A_vac_im": Av1.imag, "A_vacpv_im": Av2.imag, "Mpv_over_M": Mpv,
       "S_val": Sval, "rS2_valence_M": rS2, "rV2_valence_M": rV2, "seconds": round(time.time() - t0, 1)}
out = {k: (float("%.10g" % v_) if isinstance(v_, float) else v_) for k, v_ in out.items()}
(RT / "audit/gatrace_2026-10-02ad.json").write_text(json.dumps(out, indent=1) + "\n"); print(out, flush=True)
