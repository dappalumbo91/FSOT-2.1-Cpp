#!/usr/bin/env python3
"""Round-o heavy computations under FREEZE_2026-10-02o (run alone: ulimit -v 6000000). Needs numpy + scipy.
Writes audit/heavy_2026-10-02o.json, read by tools/score_2026_10_02o.py (CI does not rerun this job).

  python tools/heavy_2026_10_02o.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/heavy_2026-10-02o.json
"""
import argparse, json, math, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from scipy.sparse import diags, bmat
from scipy.sparse.linalg import eigsh
from scipy.optimize import brentq
import cqsm_kr as C
import fsot02d as X
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves()
HC = 197.3269804
mp = float(X.kg_to_GeV(L["m_p_kg"]) * 1000); mn = float(X.kg_to_GeV(L["m_n_kg"]) * 1000); mpi = float(L["m_pi_pm_MeV"])
def tk(key):
    for line in open(Path(__file__).resolve().parents[1] / "audit/trace_2026-10-02k.tsv", encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) > 3 and f[2].startswith(key): return float(f[3])
B2 = tk("B(2H)")
g_n = None
for line in open(Path(__file__).resolve().parents[1] / "audit/score_2026-10-02n.tsv", encoding="utf-8"):
    f = line.rstrip("\n").split("\t")
    if len(f) > 3 and f[0] == "FSOT" and f[1].startswith("N-2 GT g_piNN"): g_n = float(f[3])
out = {"generated_by": "tools/heavy_2026_10_02o.py", "freeze": "FREEZE_2026-10-02o", "inputs": {"m_p": mp, "m_n": mn, "m_pi": mpi, "B2H": B2, "g_piNN": g_n}}
xs = [0.6 + 0.1 * i for i in range(15)]
def cq(tag, M, Mpv_over_M, D=12.0, km=12.0, Km=12):
    t = time.time(); r = C.run(xs, Mpv_over_M, D, km, Km); r["M_MeV"] = M; r["seconds"] = round(time.time() - t, 1)
    r["bound"] = (not r["edge_minimum"]) and r["E_sol_over_M"] < 3.0
    r["gA0"], r["I_MeV^-1"] = r["gA0"], r["I_times_M"] / M; r["Delta_N_MeV"] = 3.0 / (2.0 * r["I_times_M"] / M)
    print(tag, {k: r[k] for k in ("x", "E_sol_over_M", "eps_val", "gA0", "Delta_N_MeV", "bound", "seconds")}, flush=True)
    out[tag] = r
Fpi = 130.2 / math.sqrt(2)
cq("O1_FSOT", mp / 3, math.sqrt(math.e))
cq("O1_FSOT_conv", mp / 3, math.sqrt(math.e), 14.0, 14.0, 14)
mpP = 938.27208943
cq("O1_validation", mpP / 3, math.exp(0.5 * 4 * math.pi**2 * Fpi**2 / (3 * (mpP / 3)**2)))
cq("O1_sanity_M420_F93", 420.0, math.exp(0.5 * 4 * math.pi**2 * 93.0**2 / (3 * 420.0**2)))
# ---- deuteron (O-3)
def deuteron(g, mpi_, mN, B, R, h=0.005, rmax=25.0):
    hb2 = HC * HC / mN; V0 = (g * g / (4 * math.pi)) * (mpi_ / (2 * mN))**2 * (mpi_ / 3) * (-3.0)
    r = np.arange(1, int(rmax / h) + 1) * h; x = mpi_ * r / HC; Y = np.exp(-x) / x; T = (1 + 3 / x + 3 / x**2) * Y
    out_ = r > R; Vss = np.where(out_, V0 * Y, 0.0); Vsd = np.where(out_, V0 * math.sqrt(8) * T, 0.0); Vdd = np.where(out_, V0 * (Y - 2 * T), 0.0)
    n = len(r); lap = diags([np.ones(n - 1), -2 * np.ones(n), np.ones(n - 1)], [-1, 0, 1]) / h**2
    def H(Cw):
        core = np.where(out_, 0.0, Cw)
        Hs = -hb2 * lap + diags(Vss + core); Hd = -hb2 * lap + diags(Vdd + core + 6 * hb2 / r**2)
        return bmat([[Hs, diags(Vsd)], [diags(Vsd), Hd]]).tocsc()
    def E0(Cw): return eigsh(H(Cw), k=1, sigma=-3000.0, which="LM")[0][0]   # shift-invert below the spectrum -> ground state
    grid = np.linspace(-400, 2000, 49); vals = [E0(c) for c in grid]
    br = None
    for i in range(len(grid) - 1):
        if (vals[i] + B) * (vals[i + 1] + B) < 0: br = (grid[i], grid[i + 1]); break
    if br is None: return {"R": R, "solved": False, "E0_range": [float(min(vals)), float(max(vals))]}
    Cw = brentq(lambda c: E0(c) + B, *br, xtol=1e-10)
    e, v = eigsh(H(Cw), k=1, sigma=-3000.0, which="LM"); u, w = v[:n, 0], v[n:, 0]
    if u[np.argmax(np.abs(u))] < 0: u, w = -u, -w
    nrm = np.sum(u * u + w * w) * h; PD = np.sum(w * w) * h / nrm
    rm = 0.5 * math.sqrt(np.sum(r * r * (u * u + w * w)) * h / nrm); Q = np.sum(r * r * w * (math.sqrt(8) * u - w)) * h / (20 * nrm)
    gam = math.sqrt(mN * B) / HC; i = np.searchsorted(r, 12.0); gr = gam * r[i]
    eta = (w[i] / u[i]) / (1 + 3 / gr + 3 / gr**2)
    return {"R": R, "solved": True, "C_MeV": Cw, "E": float(e[0]), "P_D": PD, "r_m": rm, "Q_d": Q, "eta": eta}
mN = (mp + mn) / 2; MQ = mp / 3
for tag, R in (("primary", HC / MQ), ("half", HC / (2 * MQ)), ("double", 2 * HC / MQ)):
    out["O3_FSOT_" + tag] = deuteron(g_n, mpi, mN, B2, R); print("O3", tag, out["O3_FSOT_" + tag], flush=True)
mNP = (938.27208943 + 939.56542194) / 2
out["O3_validation"] = deuteron(13.17, 139.57039, mNP, 2.224566, HC / (mpP / 3)); print("O3 val", out["O3_validation"], flush=True)
def rnd(o):
    if isinstance(o, dict): return {k: rnd(v) for k, v in o.items()}
    if isinstance(o, list): return [rnd(v) for v in o]
    if isinstance(o, (float, np.floating)): return float("%.10g" % o)
    if isinstance(o, (np.bool_,)): return bool(o)
    return o
Path(a.out).write_text(json.dumps(rnd(out), indent=1) + "\n", encoding="utf-8")
print("written", a.out)
