#!/usr/bin/env python3
"""Round-u scores under audit/FREEZE_2026-10-02u (committed first). z-only scoring (owner standing rule). mpmath/stdlib only.
U-1 soliton basis convergence (K 8 / 12 / 14) + Richardson extrapolation; U-2 g_A ordering bracket and surface bound; U-0 z re-report of earlier percentage-gate rows.

  python tools/score_2026_10_02u.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02u.tsv
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, sqrt, fabs, nstr
from mpmath import exp, matrix
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves(); R = Path(__file__).resolve().parents[1]
rows = []
def emitz(sec, name, inputs, v, c, s, th=0, cls="", note=""):
    v, c, s, th = mpf(v), mpf(c), mpf(s), mpf(th); sig = sqrt(s**2 + th**2); z = fabs(v - c) / sig
    rows.append([sec, name, inputs, nstr(v, 12), nstr(c, 10), nstr(sig, 4), nstr(z, 5), "agrees" if z <= 1 else "miss", nstr((v - c) / c * 100, 5) + " %", cls, note]); return z <= 1
def info(sec, name, inputs, v, cls="", note=""): rows.append([sec, name, inputs, nstr(mpf(v), 12), "-", "-", "-", "info", "-", cls, note])
def rec(sec, name, verdict, note): rows.append([sec, name, "-", "-", "-", "-", "-", verdict, "-", "-", note])
J = lambda f: json.loads((R / f).read_text(encoding="utf-8"))
Hq = J("audit/heavy_2026-10-02q.json")
def raw(c, o):
    M, MN = mpf(c["M_MeV"]), mpf(c["M_N_MeV"]); I = mpf(o["I_times_M"]); q_ = MN / M
    return {"g1": mpf(o["A_im"]) / I, "muS": q_ * mpf(o["B_re"]) / (6 * I), "muV1": q_ * mpf(o["Amu_im"]) / I, "muV0": -q_ / 3 * (mpf(o["xat_val"]) + mpf(o["xat_sea"]))}
rs = raw(Hq["Q1_sanity_M420_F93"], Hq["Q1_sanity_M420_F93"]["DPP"]); SG = {k: (1 if rs[k] > 0 else -1) for k in ("g1", "muS", "muV1")}
def obs(c):
    o = c["DPP"]; r = raw(c, o); M = mpf(c["M_MeV"]); I = mpf(o["I_times_M"])
    g0 = mpf(o["gA0"]); g1 = SG["g1"] * r["g1"]; muS = SG["muS"] * r["muS"]; muV = r["muV0"] + SG["muV1"] * r["muV1"]
    mpiM = mpf(L["m_pi_pm_MeV"]) / M; x = mpf(c["x_DPP"]); D = mpf(c["D"])
    return {"gA": g0 + g1, "gA0": g0, "gA1": g1, "sea": mpf(o["gA0_sea"]), "mup": (muS + muV) / 2, "mun": (muS - muV) / 2, "DN": 3 * M / (2 * I),
            "edge": 2 * (x / D)**2 * (1 + mpiM * D) * exp(-mpiM * D), "E": mpf(o["E_sol_over_M"])}
runs = [(8, obs(Hq["Q1_FSOT"])), (12, obs(J("audit/heavy_2026-10-02t.json")["T2_FSOT_massive_K12"]))]
pu = R / "audit/heavy_2026-10-02u.json"
if pu.exists(): runs.append((14, obs(J("audit/heavy_2026-10-02u.json")["U1_FSOT_massive_K14"])))
s = "U-1"
for K, o in runs:
    info(s, f"massive DPP K {K}: g_A", "M = m_p/3", o["gA"], "FSOT", f"g_A^(0) {nstr(o['gA0'], 6)} (sea {nstr(o['sea'], 5)}), g_A^(1) {nstr(o['gA1'], 6)}; mu_p {nstr(o['mup'], 6)}, mu_n {nstr(o['mun'], 6)}, Delta-N {nstr(o['DN'], 6)}, E/M {nstr(o['E'], 6)}")
REF = {"gA": (mpf("1.2754"), mpf("0.0013"), "g_A"), "mup": (mpf("2.79284734463"), mpf("0.00000000082"), "mu_p"), "mun": (mpf("-1.91304276"), mpf("0.00000045"), "mu_n"),
       "DN": (mpf("1232") - (mpf("938.27208943") + mpf("939.56542194")) / 2, mpf("2"), "M_Delta - M_N")}
if len(runs) == 3:
    for k, (c, sg, nm) in REF.items():
        v12, v14 = runs[1][1][k], runs[2][1][k]; vi = (196 * v14 - 144 * v12) / 52; th = fabs(vi - v14)
        emitz(s, f"U-1 {nm} extrapolated (Richardson 1/K^2, K 12-14)", "massive DPP, FSOT inputs", vi, c, sg, th, "FSOT", f"theory unc. {nstr(th, 3)}; K 14 {nstr(v14, 6)}")
else:
    rec(s, "K 14 run and extrapolation", "not completed", "the K 14 job exceeded the 10-minute cap (stopped at 15 min); convergence not established")
    for k, (c, sg, nm) in REF.items():
        d = runs[1][1][k] - runs[0][1][k]
        info(s, f"K 8 -> 12 shift of {nm}", "information", d, "FSOT", f"K 12 value {nstr(runs[1][1][k], 6)} ({nstr((runs[1][1][k] - c) / c * 100, 4)} %); unconverged")
s = "U-2"
for K, o in runs: info(s, f"surface-term bound |theta(D)| at K {K}", "massive tail", o["edge"], "FSOT", "")
info(s, "g_A classical ordering (g_A^(0) only), K 12, unconverged", "same", runs[1][1]["gA0"], "FSOT", "bracket lower end; z scoring waits for converged values")
info(s, "g_A time-ordered (g_A^(0) + g_A^(1)), K 12, unconverged", "same", runs[1][1]["gA"], "FSOT", "bracket upper end; ordering derivation open")
s = "U-0"
for path, sec, key, c, sg, lab in (("audit/score_2026-10-02t.tsv", "T-1", "T-1 chi^1/4", "185.3", "5.7", "chi^1/4 condensate (round t)"),
                                   ("audit/score_2026-10-02t.tsv", "T-1", "T-1 M_eta (", "547.862", "0.017", "M_eta LO (round t)"),
                                   ("audit/score_2026-10-02q.tsv", "FSOT", "Q-1 mu_p", "2.79284734463", "0.00000000082", "mu_p K 8 (round q)"),
                                   ("audit/score_2026-10-02q.tsv", "FSOT", "Q-1 mu_n", "-1.91304276", "0.00000045", "mu_n K 8 (round q)"),
                                   ("audit/score_2026-10-02p.tsv", "FSOT", "P-4 F_pi with", None, None, "F_pi one-loop LSM (round p)")):
    for line in open(R / path, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) > 6 and f[0] == sec and f[1].startswith(key):
            cc, ss = (mpf(c), mpf(sg)) if c else (mpf(f[4]), mpf(f[5]))
            emitz(s, "U-0 z re-report: " + lab, path, f[3], cc, ss, 0, f[9], "was '" + f[7] + "' under a percentage gate"); break
s = "U2-1"  # FREEZE_2026-10-02u2
from mpmath import log as _log, eigsy, atan, pi as _pi
from fsot02d import pi
P = X.pins(); G2 = P["wave9|Gluon_condensate"]; L3 = mpf("334.432838067")
for line in open(R / "audit/score_2026-10-02s2.tsv", encoding="utf-8"):
    f = line.rstrip("\n").split("\t")
    if len(f) > 3 and f[0] == "S2-1" and f[1].startswith("S2-1 Lambda^(3)"): L3 = mpf(f[3])
n3 = G2 / 8; n0 = mpf(9) / 11 * n3; q3 = n3**(mpf(1) / 4) * 1000; q0 = n0**(mpf(1) / 4) * 1000
L0 = q0 * exp(-mpf(1) / 22) / mpf("0.65"); Rt = q3 * exp(-mpf(1) / 22) / mpf("0.65") / L3
info(s, "R_FSOT = Lambda^(0)/Lambda^(3) (trace anomaly, eps fixed)", "pin G2, (9/11)^(1/4), DP, FSOT Lambda^(3)", L0 / L3, "FSOT", "Lambda^(0) = " + nstr(L0, 6) + " MeV; round t (G2 fixed) " + nstr(Rt, 5) + "; factor (9/11)^(1/4) = " + nstr((mpf(9) / 11)**(mpf(1) / 4), 5))
info(s, "residual to the lattice r0-fixed ratio 0.772 (info, external)", "info only", mpf("0.772277227723") / (L0 / L3), "", "eps-fixed vs r0-fixed matching; not fitted")
emitz(s, "U2-1 chi^1/4 = ((9/11) <(alpha_s/pi)G^2>/8)^(1/4)", "pin wave9, b0 = 11, b3 = 9", q0, "185.3", "5.7", 0, "FSOT", "round t (G2 fixed): " + nstr(q3, 6) + " MeV; disclosed pre-freeze hand estimate about 190")
L_ = X.leaves(); mpv = X.kg_to_GeV(L_["m_p_kg"]) * 1000
alpha = 1 / L_["alpha_inv"]; xx, yy = P["wave7|m_u/m_d"], P["wave7|m_s/m_d"]; mud = (1 + xx) / 2; Qf = sqrt((yy**2 - mud**2) / (1 - xx**2))
F3 = mpv / (2 * sqrt(3) * pi); MK = L_["m_K_pm_MeV"]; Mpi = L_["m_pi_pm_MeV"]
Dp = 12 * pi * alpha * _log(2) * F3**2; p0 = sqrt(Mpi**2 - Dp); DK = Dp; split = mpf(0)
for _ in range(60):
    MhK2 = MK**2 - DK + split / 2; split = MhK2 * (MhK2 - p0**2) / (Qf**2 * p0**2)
Bm, Bs = p0**2 / 2, MhK2 - p0**2 / 2
Fpi = None
for line in open(R / "audit/score_2026-10-02p.tsv", encoding="utf-8"):
    f = line.rstrip("\n").split("\t")
    if len(f) > 3 and f[0] == "FSOT" and f[1].startswith("P-4 F_pi with"): Fpi = mpf(f[3])
M0 = 6 * q0**4 / Fpi**2
Mm = matrix([[(2 * (Bm + 2 * Bs)) / 3, -(2 * sqrt(2) / 3) * (Bs - Bm)], [-(2 * sqrt(2) / 3) * (Bs - Bm), (2 * (2 * Bm + Bs)) / 3 + M0]])
E_, Q_ = eigsy(Mm)
emitz(s, "U2-1 M_eta (LO U(3)+WV, FSOT F_pi, chi from U2-1)", "same", sqrt(E_[0]), "547.862", "0.017", 0, "FSOT", "LO matrix failed validation in round t")
emitz(s, "U2-1 M_eta' (same)", "same", sqrt(E_[1]), "957.78", "0.06", 0, "FSOT", "")
rec("GATE", "record rows of the 91", "unchanged", "z-only rule; no record row recomputed")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02u.py under audit/FREEZE_2026-10-02u (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
