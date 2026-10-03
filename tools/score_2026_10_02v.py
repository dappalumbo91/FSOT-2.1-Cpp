#!/usr/bin/env python3
"""Round-v scores under audit/FREEZE_2026-10-02v (committed first). z-only scoring; FSOT-only inputs. mpmath/stdlib only.
V-1 soliton convergence (audit/heavy_2026-10-02v_K*.json); V-2 F_K/F_pi from FSOT l4bar (L4 = 0); V-3 FKS eta/eta' with FSOT inputs.

  python tools/score_2026_10_02v.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02v.tsv
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, sqrt, pi, fabs, nstr
from mpmath import log, exp, matrix, eigsy, atan
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves(); P = X.pins(); R = Path(__file__).resolve().parents[1]
rows = []
def emitz(sec, name, inputs, v, c, s, th=0, cls="", note=""):
    v, c, s, th = mpf(v), mpf(c), mpf(s), mpf(th); sig = sqrt(s**2 + th**2); z = fabs(v - c) / sig
    rows.append([sec, name, inputs, nstr(v, 12), nstr(c, 10), nstr(sig, 4), nstr(z, 5), "agrees" if z <= 1 else "miss", nstr((v - c) / c * 100, 5) + " %", cls, note]); return z <= 1
def info(sec, name, inputs, v, cls="", note=""): rows.append([sec, name, inputs, nstr(mpf(v), 12), "-", "-", "-", "info", "-", cls, note])
def rec(sec, name, verdict, note): rows.append([sec, name, "-", "-", "-", "-", "-", verdict, "-", "-", note])
def col(path, sec, key):
    for line in open(R / path, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) > 3 and f[0] == sec and f[1].startswith(key): return mpf(f[3])
J = lambda f: json.loads((R / f).read_text(encoding="utf-8"))
mp = X.kg_to_GeV(L["m_p_kg"]) * 1000
# ---------------- V-1
s = "V-1"; Hq = J("audit/heavy_2026-10-02q.json")
def raw(c, o):
    M, MN = mpf(c["M_MeV"]), mpf(c["M_N_MeV"]); I = mpf(o["I_times_M"]); q_ = MN / M
    return {"g1": mpf(o["A_im"]) / I, "muS": q_ * mpf(o["B_re"]) / (6 * I), "muV1": q_ * mpf(o["Amu_im"]) / I, "muV0": -q_ / 3 * (mpf(o["xat_val"]) + mpf(o["xat_sea"]))}
rs = raw(Hq["Q1_sanity_M420_F93"], Hq["Q1_sanity_M420_F93"]["DPP"]); SG = {k: (1 if rs[k] > 0 else -1) for k in ("g1", "muS", "muV1")}
def obs(c):
    o = c["DPP"]; r = raw(c, o); M = mpf(c["M_MeV"]); I = mpf(o["I_times_M"]); g0 = mpf(o["gA0"]); g1 = SG["g1"] * r["g1"]
    muS = SG["muS"] * r["muS"]; muV = r["muV0"] + SG["muV1"] * r["muV1"]
    return {"gA": g0 + g1, "gA0": g0, "mup": (muS + muV) / 2, "mun": (muS - muV) / 2, "DN": 3 * M / (2 * I), "x": mpf(c["x_DPP"]), "E": mpf(o["E_sol_over_M"])}
runs = {}
for K in (12, 14, 16):
    p = R / ("audit/heavy_2026-10-02v_K%d.json" % K)
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8")).get("V1_FSOT_massive_K%d" % K, {})
        if "DPP" in d: runs[K] = obs(d)
t12 = obs(J("audit/heavy_2026-10-02t.json")["T2_FSOT_massive_K12"])
if 12 in runs:
    dmax = max(fabs(runs[12][k] - t12[k]) / fabs(t12[k]) for k in ("gA", "mup", "mun", "DN"))
    rec("VALIDATION", "V-1 windowed scan reproduces the round-t full-scan K 12", "PASS" if dmax < mpf("1e-8") else "FAIL", "max relative difference " + nstr(dmax, 3))
for K in sorted(runs):
    o = runs[K]; info(s, f"massive DPP K {K} (D = k = K)", "M = m_p/3", o["gA"], "FSOT · measured", f"g_A^(0) {nstr(o['gA0'], 6)}; mu_p {nstr(o['mup'], 6)}, mu_n {nstr(o['mun'], 6)}, Delta-N {nstr(o['DN'], 6)}; x {nstr(o['x'], 6)}, E/M {nstr(o['E'], 6)}")
REF = {"gA": (mpf("1.2754"), mpf("0.0013"), "g_A (time-ordered)"), "mup": (mpf("2.79284734463"), mpf("0.00000000082"), "mu_p"), "mun": (mpf("-1.91304276"), mpf("0.00000045"), "mu_n"),
       "DN": (mpf("1232") - (mpf("938.27208943") + mpf("939.56542194")) / 2, mpf("2"), "M_Delta - M_N"), "gA0": (mpf("1.2754"), mpf("0.0013"), "g_A classical ordering (info end)")}
Ks = sorted(K for K in runs if K >= 12)
if 12 not in runs: runs[12] = t12; Ks = sorted(set(Ks) | {12})
if len(Ks) >= 2 and Ks[-1] > 12:
    K1, K2 = Ks[-2], Ks[-1]
    for k, (c, sg, nm) in REF.items():
        v1, v2 = runs[K1][k], runs[K2][k]; vi = (K2**2 * v2 - K1**2 * v1) / (K2**2 - K1**2); th = fabs(vi - v2)
        emitz(s, f"V-1 {nm} extrapolated (Richardson 1/K^2, K {K1}-{K2})", "massive DPP, FSOT inputs", vi, c, sg, th, "FSOT · measured", f"theory unc. {nstr(th, 3)}; K {K2} {nstr(v2, 6)}")
else:
    rec(s, "K 14 run", "not completed", "no extrapolation")
# ---------------- V-2
s = "V-2"
def fkfpi(Mpi, MK, Fq, l4b, mu=mpf(770)):
    Me2 = (4 * MK**2 - Mpi**2) / 3; c = 32 * pi**2 * Fq**2
    m = lambda M2: M2 / c * log(M2 / mu**2)
    l4r = (l4b + log(Mpi**2 / mu**2)) / (16 * pi**2); nuK = (log(MK**2 / mu**2) + 1) / (32 * pi**2); L5x4 = l4r + nuK / 2
    return 1 + mpf(5) / 4 * m(Mpi**2) - m(MK**2) / 2 - mpf(3) / 4 * m(Me2) + (MK**2 - Mpi**2) * L5x4 / Fq**2, L5x4 / 4
vr, vL5 = fkfpi(mpf("139.57039"), mpf("493.677"), mpf("130.2") / sqrt(2), mpf("4.40"))
info("VALIDATION", "V-2 F_K/F_pi with PDG masses, PDG F_pi, FLAG l4bar 4.40 (L4 = 0)", "information", vr, "", "L5^r(770) = " + nstr(vL5, 4) + "; FLAG F_K/F_pi 1.1932(21); tests the L4 = 0 approximation")
Fpi = col("audit/score_2026-10-02p.tsv", "FSOT", "P-4 F_pi with"); l4b = col("audit/score_2026-10-02p.tsv", "FSOT", "P-4 lbar4")
r, L5 = fkfpi(L["m_pi_pm_MeV"], L["m_K_pm_MeV"], Fpi, l4b)
emitz(s, "V-2 F_K/F_pi (one-loop SU(3), L5 from FSOT l4bar, L4 = 0)", "FSOT pi+-, K+- leaves, P-4 F_pi " + nstr(Fpi, 7) + ", lbar4 " + nstr(l4b, 6), r, "1.1932", "0.0021", 0, "FSOT · lattice-computed", "L5^r(770 MeV) = " + nstr(L5, 4) + "; disclosed pre-freeze estimate 1.25-1.27")
# ---------------- V-3
s = "V-3"
alpha = 1 / L["alpha_inv"]; x, y_ = P["wave7|m_u/m_d"], P["wave7|m_s/m_d"]; mud = (1 + x) / 2; Qf = sqrt((y_**2 - mud**2) / (1 - x**2))
F3 = mp / (2 * sqrt(3) * pi); MK = L["m_K_pm_MeV"]; Mpi = L["m_pi_pm_MeV"]
Dp = 12 * pi * alpha * log(2) * F3**2; p0 = sqrt(Mpi**2 - Dp); DK = Dp; split = mpf(0)
for _ in range(60):
    MhK2 = MK**2 - DK + split / 2; split = MhK2 * (MhK2 - p0**2) / (Qf**2 * p0**2)
mqq2, mss2 = p0**2, 2 * MhK2 - p0**2
chi = col("audit/score_2026-10-02u.tsv", "U2-1", "U2-1 chi^1/4")**4
fs = Fpi * sqrt(2 * r**2 - 1); yy = Fpi / fs; a2 = 2 * chi / Fpi**2
Mm = matrix([[mqq2 + 2 * a2, sqrt(2) * a2 * yy], [sqrt(2) * a2 * yy, mss2 + yy**2 * a2]]); E_, Q_ = eigsy(Mm); phi = fabs(atan(-Q_[1, 0] / Q_[0, 0]) * 180 / pi)
emitz(s, "V-3 M_eta (FKS, FSOT f_q, f_s from V-2, chi from U2-1)", "FSOT only", sqrt(E_[0]), "547.862", "0.017", 0, "FSOT · measured", "phi = " + nstr(phi, 5) + " deg; y = " + nstr(yy, 5) + "; a^2 = " + nstr(a2 / 10**6, 5) + " GeV^2")
emitz(s, "V-3 M_eta' (same)", "same", sqrt(E_[1]), "957.78", "0.06", 0, "FSOT · measured (scores chi_top, intermediate)", "chi route provisional (round u, post hoc)")
rec("V-4", "g_A operator ordering", "open derivation", "not derived this round; no interpolating factor")
rec("GATE", "record rows of the 91", "unchanged", "z-only; no record row recomputed")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02v.py under audit/FREEZE_2026-10-02v (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
