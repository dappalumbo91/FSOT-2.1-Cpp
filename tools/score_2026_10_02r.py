#!/usr/bin/env python3
"""Round-r scores under audit/FREEZE_2026-10-02r (committed first). mpmath/stdlib only.
R-0 reads audit/score_2026-10-02q_late.tsv (round q's frozen validation run late); R-1 the chi_top trace and fix; R-2 g_A trace (information).

  python tools/score_2026_10_02r.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02r.tsv
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, sqrt, pi, fabs, nstr
from mpmath import log, matrix, eigsy, atan, exp
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves(); P = X.pins(); R = Path(__file__).resolve().parents[1]
rows = []
def emit(sec, name, inputs, v, c, s, tol, cls="", note=""):
    v, c, s, tol = mpf(v), mpf(c), mpf(s), mpf(tol)
    rel = (v - c) / c; verdict = "PASS" if fabs(rel) <= tol else "FAIL"
    rows.append([sec, name, inputs, nstr(v, 12), nstr(c, 10), nstr(s, 4), nstr(fabs(v - c) / s, 5), verdict, nstr(rel * 100, 5) + " %", cls, note]); return verdict == "PASS"
def info(sec, name, inputs, v, cls="", note=""): rows.append([sec, name, inputs, nstr(mpf(v), 12), "-", "-", "-", "info", "-", cls, note])
def rec(sec, name, verdict, note): rows.append([sec, name, "-", "-", "-", "-", "-", verdict, "-", "-", note])
def row(path, sec, key):
    for line in open(R / path, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) > 7 and f[0] == sec and f[1].startswith(key): return f
mp = X.kg_to_GeV(L["m_p_kg"]) * 1000
# ---------------- R-0 late round-q validation -> mu_d
Q = "audit/score_2026-10-02q_late.tsv"
val = {k: row(Q, "VALIDATION", "Q-1 " + k)[7] == "PASS" for k in ("g_A", "M_Delta", "mu_p", "mu_n")}
fq = {k: row(Q, "FSOT", "Q-1 " + k) for k in ("g_A", "M_Delta", "mu_p", "mu_n")}
s = "R-0"
for k in fq: rec(s, "late validation of round-q " + k, "PASS" if val[k] else "FAIL", "FSOT row " + fq[k][3] + " (" + fq[k][8] + "), FSOT gate verdict " + fq[k][7] + "; " + fq[k][10])
MUD, sMUD, PD = mpf("0.8574382335"), mpf("0.0000000022"), mpf("0.06281210418")
muS = mpf(fq["mu_p"][3]) + mpf(fq["mu_n"][3]); mud = muS - mpf(3) / 2 * (muS - mpf(1) / 2) * PD
ok_mu = val["mu_p"] and val["mu_n"] and fq["mu_p"][7] == "PASS" and fq["mu_n"][7] == "PASS"
emit(s, "R-0 mu_d = mu_S - (3/2)(mu_S - 1/2) P_D (round-q soliton mu_p + mu_n, round-o P_D)", "Q-1 FSOT mu_p, mu_n; O-3 P_D", mud, MUD, sMUD, "0.02", "FSOT",
     ("mu_p, mu_n agree with passing late validation" if ok_mu else "mu_p/mu_n not promoted") + "; record row Deuteron_mu; disclosed before freeze: about -5.8 %")
# ---------------- R-1 chi_top trace
s = "R-1"; LPV = exp(mpf(1) / 22); cDP = mpf("0.65"); Rr = mpf("0.624") / mpf("0.808"); sR = Rr * sqrt((mpf("0.036") / mpf("0.624"))**2 + (mpf("0.029") / mpf("0.808"))**2)
def colv(path, sec, key):
    for line in open(R / path, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) > 3 and f[0] == sec and f[1].startswith(key): return mpf(f[3])
L3 = colv("audit/score_2026-10-02j.tsv", "FSOT", "J-1 Lambda^(3) from FSOT")
info(s, "trace 1: Lambda^(3)_MSbar FSOT (J-1)", "FSOT alpha_s", L3, "FSOT", "N_f = 2+1 scale; round p inserted this into a pure-gauge formula")
info(s, "trace 2: Lambda_PV/Lambda_MSbar = e^(1/22)", "one-loop b = 11 (N_f = 0)", LPV, "", "already the pure-gauge conversion (b = 11 N_c/3): consistent only with Lambda^(0)")
info(s, "trace 3: DP density n^(1/4) = 0.65 Lambda_PV (packing n rho-bar^4 ~ 0.1)", "DP variational", cDP, "", "pure-gauge instanton ensemble; chi_quenched = N/V")
info(s, "trace 4: round-p chi^1/4 with Lambda^(3) (divergent)", "steps 1-3", cDP * LPV * L3, "", "+23.7 % vs quenched lattice 185.3(5.7)")
info(s, "trace 5: R = r0 Lambda^(0) / r0 Lambda^(3) (FLAG 2021 0.624(36)/0.808(29))", "lattice ratio at fixed r0", Rr, "", "sigma " + nstr(sR, 3) + "; the fix at step 1")
chiq = cDP * LPV * Rr * L3; L0v = Rr * mpf(338)
vok = emit("VALIDATION", "R-1 chi^1/4 = 0.65 e^(1/22) R Lambda^(3), FLAG Lambda^(3) = 338", "FLAG", cDP * LPV * L0v, "185.3", "5.7", "0.10", "", "tol 10 %")
emit(s, "R-1 chi^1/4 = 0.65 e^(1/22) Lambda^(0), Lambda^(0) = R Lambda^(3)_FSOT (DP, quenched)", "FSOT Lambda^(3) " + nstr(L3, 9) + ", R " + nstr(Rr, 6), chiq, "185.3", "5.7", "0.10", "HYBRID",
     "validation " + ("passed" if vok else "FAILED") + "; Lambda^(0) = " + nstr(Rr * L3, 6) + " MeV; R uncertainty -> chi^1/4 +- " + nstr(chiq * sR / Rr, 3) + " MeV; disclosed before freeze: about -4.5 %")
for nm, rv in (("FLAG 2019 0.615/0.808", mpf("0.615") / mpf("0.808")), ("Dalla Brida 19 0.660/0.808", mpf("0.660") / mpf("0.808"))):
    info(s, "look-elsewhere R variant " + nm + ": chi^1/4", "same", cDP * LPV * rv * L3, "HYBRID", "info only")
chi = chiq**4
alpha = 1 / L["alpha_inv"]; x, y = P["wave7|m_u/m_d"], P["wave7|m_s/m_d"]; mud_ = (1 + x) / 2; Qf = sqrt((y**2 - mud_**2) / (1 - x**2))
F3 = mp / (2 * sqrt(3) * pi); MK = L["m_K_pm_MeV"]; Mpi = L["m_pi_pm_MeV"]
Dp = 12 * pi * alpha * log(2) * F3**2; p0 = sqrt(Mpi**2 - Dp); DK = Dp; split = mpf(0)
for _ in range(60):
    MhK2 = MK**2 - DK + split / 2; split = MhK2 * (MhK2 - p0**2) / (Qf**2 * p0**2)
Bm = p0**2 / 2; Bs = MhK2 - Bm
def mix(chi_, F_):
    M0 = 6 * chi_ / F_**2
    Mm = matrix([[(2 * (Bm + 2 * Bs)) / 3, -(2 * sqrt(2) / 3) * (Bs - Bm)], [-(2 * sqrt(2) / 3) * (Bs - Bm), (2 * (2 * Bm + Bs)) / 3 + M0]])
    E_, Q_ = eigsy(Mm); return sqrt(E_[0]), sqrt(E_[1]), atan(Q_[1, 0] / Q_[0, 0]) * 180 / pi
me_, mep, th = mix(chi, F3)
emit(s, "R-1 M_eta (U(3) + WV, quenched DP chi)", "round-p matrix, F = F3, R-1 chi", me_, "547.862", "0.017", "0.05", "HYBRID", "theta = " + nstr(th, 5) + " deg")
emit(s, "R-1 M_eta'", "same", mep, "957.78", "0.06", "0.05", "HYBRID", "chi-sensitive row (round p: +62 %)")
info(s, "trace 6: M_eta with chi = 0 (no anomaly)", "same", mix(chi * 0, F3)[0], "HYBRID", "round-p chi (x 2.34): M_eta " + nstr(mix((cDP * LPV * L3)**4, F3)[0], 6) + " MeV, octet-limit side; the round-p -0.17 % eta was reached with an oversized chi (coincidence), not a test of chi")
info(s, "trace 7: WV variant F = F_pi 92.07 MeV: M_eta", "info", mix(chi, mpf("130.2") / sqrt(2))[0], "HYBRID", "next divergent step after the Lambda fix: LO U(3) + WV normalization (F_0 vs F_pi, 1/N_c terms); info only")
info(s, "trace 7: WV variant F = F_pi 92.07 MeV: M_eta'", "info", mix(chi, mpf("130.2") / sqrt(2))[1], "HYBRID", "look-elsewhere (normalization), info only")
# ---------------- R-2 g_A trace (information)
s = "R-2"; Hp = json.loads((R / "audit/heavy_2026-10-02p.json").read_text(encoding="utf-8")); Hq = json.loads((R / "audit/heavy_2026-10-02q.json").read_text(encoding="utf-8"))
for tag, c in (("p chiral D12 K12", Hp["P1_FSOT"]), ("p chiral conv D14 K14", Hp["P1_FSOT_conv"]), ("q massive D10 K8", Hq["Q1_FSOT"])):
    o = c["DPP"]; g1 = 3 * mpf(o["A_im"]) / (3 * mpf(o["I_times_M"]))
    info(s, "g_A trace " + tag + ": g_A^(0) + g_A^(1)", "DPP", mpf(o["gA0"]) + g1, "FSOT", f"g_A^(0) {o['gA0']:.6g}, A {o['A_im']:.6g}, I M {o['I_times_M']:.6g}, g_A^(1) {float(g1):.6g}, eps_val {o['eps_val']:.4g}")
rec(s, "g_A trace finding", "open", "q vs p: g_A^(0) +17 %, A +13 %, I -7 %; two steps changed at once (pion-mass profile and K 12 -> 8 basis cap); next: chiral DPP in the K 8 basis to separate them")
rec("GATE", "record rows of the 91", "unchanged", "Deuteron_mu recomputed (" + ("inputs promoted" if ok_mu else "inputs not promoted") + ") and fails 2 %; mu_p, mu_n are not record rows; chi_top, eta, eta' are HYBRID")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02r.py under audit/FREEZE_2026-10-02r (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
