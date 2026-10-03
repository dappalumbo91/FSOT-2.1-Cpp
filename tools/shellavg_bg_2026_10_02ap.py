#!/usr/bin/env python3
"""Round-ap (FREEZE_2026-10-02ap, AP-0 additive rule): resumable detached job for the level-C shell-average samples
(kmax 16, D0 14, K 14, round-ag kmax-12 profile; same sums as the round-am level-B job). Files audit/shellavg_2026-10-02ap_C_j<j>.json,
audit/shellavg_2026-10-02ap_C_rot.json, merged audit/shellavg_2026-10-02ap_C.json; spectra cache $FSOT_AP_CACHE (default /home/box/fsot-ap-cache).
  setsid nohup python3 tools/shellavg_bg_2026_10_02ap.py > log 2>&1 < /dev/null &"""
import json, math, os, pickle, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import cqsm_kr as C
import cqsm_rot as R
RT = Path(__file__).resolve().parents[1]; AU = RT / "audit"; Nc = 3; rnd = lambda v: float("%.10g" % v); z = lambda r: 0 * r; t0 = time.time()
CACHE = Path(os.environ.get("FSOT_AP_CACHE", "/home/box/fsot-ap-cache")); CACHE.mkdir(parents=True, exist_ok=True)
def prof(x, mpiM): return lambda r: -2 * np.arctan(x * x / (r * r) * (1 + mpiM * r) * np.exp(-mpiM * r))
kmax, D0, Km = 16.0, 14.0, 14
m = json.loads((AU / "murun_2026-10-02ag_K14_D14_k12.json").read_text())
inp = m["inputs"]; Mpv = inp["Mpv_over_M"]; q = (1.0 / Mpv) ** 2
th = prof(m["x_DPP"], inp["mpi_over_mp"] / inp["M_over_mp"]); ang = C.Angular(Km); W = {"s1": 1.0, "s2": -q, "v1": -1.0, "v2": q}
def setup(j):
    DD = D0 + j * (math.pi / kmax) / 4; rad = C.Radial(DD, kmax); C.RAD = rad; O = R.Ops(ang); cf = CACHE / ("C_j%d.pkl" % j)
    if cf.exists(): SP = pickle.loads(cf.read_bytes()); print("j=%d spectra from cache" % j, flush=True)
    else:
        SP = {"s1": C.spectrum(th, 1.0, ang, rad, Km, True), "s2": C.spectrum(th, Mpv, ang, rad, Km, True), "v1": C.spectrum(z, 1.0, ang, rad, Km, True), "v2": C.spectrum(z, Mpv, ang, rad, Km, True)}
        tmp = cf.with_suffix(".tmp"); tmp.write_bytes(pickle.dumps(SP)); tmp.replace(cf); print("j=%d spectra cached %.1f s" % (j, time.time() - t0), flush=True)
    return DD, O, SP, C.valence(SP["s1"])
def wr(path, obj): tmp = path.with_suffix(".tmp"); tmp.write_text(json.dumps(obj, indent=1) + "\n"); tmp.replace(path)
for j in range(4):
    f_ = AU / ("shellavg_2026-10-02ap_C_j%d.json" % j)
    if f_.exists(): print("j=%d done (file)" % j, flush=True); continue
    ts = time.time(); DD, O, SP, ev = setup(j)
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
           "gA0": rnd(-(Nc / 3.0) * (gs["s1"][1] + sum(W[k] * gs[k][0] for k in gs))), "I": rnd(C.inertia(SP["s1"], SP["s2"], Mpv, ang, Km, Nc, ev)), "seconds": round(time.time() - ts, 1)}
    wr(f_, res); print(res, flush=True)
fr = AU / "shellavg_2026-10-02ap_C_rot.json"
if not fr.exists():
    ts = time.time(); DD, O, SP, ev = setup(0); rot = {}
    OPS = {"A": ([(O.sxt[c], "sxt%d" % c, "const") for c in range(3)], [(O.tau[c], "tau%d" % c, "const") for c in range(3)], 6.0),
           "Amu": ([(O.rxs_x_tau[c], "rxt%d" % c, "rfield") for c in range(3)], [(O.tau[c], "tau%d" % c, "const") for c in range(3)], 6.0),
           "B": ([(O.tau[c], "tau%d" % c, "const") for c in range(3)], [(O.rxs[c], "rxs%d" % c, "rfield") for c in range(3)], 1.0)}
    for nm, (X_, Y_, dv) in OPS.items():
        fp = AU / ("shellavg_2026-10-02ap_C_rot_%s.part.json" % nm)
        if fp.exists(): rot[nm + "_reg"] = json.loads(fp.read_text()); continue
        f = lambda sp, e_: complex(R.rot_sum(O, sp, e_, X_, Y_) / dv)
        tot = f(SP["s1"], ev); sea = f(SP["s1"], None); reg = (tot - sea) + (sea - q * f(SP["s2"], None)) - (f(SP["v1"], None) - q * f(SP["v2"], None))
        rot[nm + "_reg"] = [rnd(reg.real), rnd(reg.imag)]; wr(fp, rot[nm + "_reg"]); print(nm, rot[nm + "_reg"], round(time.time() - ts, 1), flush=True)
    rot["seconds"] = round(time.time() - ts, 1); wr(fr, rot)
    for nm in ("A", "Amu", "B"): (AU / ("shellavg_2026-10-02ap_C_rot_%s.part.json" % nm)).unlink(missing_ok=True)
S = [json.loads((AU / ("shellavg_2026-10-02ap_C_j%d.json" % j)).read_text()) for j in range(4)]; rot = json.loads(fr.read_text())
for k in ("A_reg", "Amu_reg", "B_reg"): S[0][k] = rot[k]
out = {"generated_by": "tools/shellavg_bg_2026_10_02am.py (resumable; FREEZE_2026-10-02ap level C)", "freeze": "FREEZE_2026-10-02al", "level": "C", "samples": S,
       "kmax": kmax, "D0": D0, "K": Km, "x_DPP": m["x_DPP"], "inputs": inp, "seconds": round(sum(s_["seconds"] for s_ in S) + rot["seconds"], 1)}
wr(AU / "shellavg_2026-10-02ap_C.json", out); print("written", out["seconds"], flush=True)
