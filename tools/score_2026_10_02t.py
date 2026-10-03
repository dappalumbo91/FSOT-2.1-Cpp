#!/usr/bin/env python3
"""Round-t scores under audit/FREEZE_2026-10-02t (committed first). FSOT-only (owner directive); outside numbers only in validation rows. mpmath/stdlib only.
T-1 gluon-condensate pin -> instanton density -> chi_top, Lambda^(0), LO U(3)+WV eta/eta'; T-2 massive g_A at K 12 (audit/heavy_2026-10-02t.json).

  python tools/score_2026_10_02t.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02t.tsv
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
def col(path, sec, key):
    for line in open(R / path, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) > 3 and f[0] == sec and f[1].startswith(key): return mpf(f[3])
mp = X.kg_to_GeV(L["m_p_kg"]) * 1000
# ---------------- T-1
s = "T-1"
def chain(G2):  # G2 = <(alpha_s/pi) G^2> in GeV^4 -> n, chi^1/4 [MeV], Lambda^(0) MSbar [MeV]
    n = G2 / 8; q = n**(mpf(1) / 4) * 1000; return n, q, q * exp(-mpf(1) / 22) / mpf("0.65")
def mix(chi_, F_, mqq2, mss2):
    M0 = 6 * chi_ / F_**2; Bm, Bs = mqq2 / 2, mss2 / 2
    Mm = matrix([[(2 * (Bm + 2 * Bs)) / 3, -(2 * sqrt(2) / 3) * (Bs - Bm)], [-(2 * sqrt(2) / 3) * (Bs - Bm), (2 * (2 * Bm + Bs)) / 3 + M0]])
    E_, Q_ = eigsy(Mm); return sqrt(E_[0]), sqrt(E_[1]), atan(Q_[1, 0] / Q_[0, 0]) * 180 / pi
# validation: SVZ 0.012 GeV^4, PDG F_pi, isospin-limit PDG block
_, vq, vL = chain(mpf("0.012")); mpi0, MK0 = mpf("134.9768"), mpf("497.611")
v0 = emit("VALIDATION", "T-1 chi^1/4 = (<(alpha_s/pi)G^2>/8)^(1/4), SVZ 0.012 GeV^4", "SVZ", vq, "185.3", "5.7", "0.10", "", "tol 10 %; Lambda^(0) = " + nstr(vL, 6) + " MeV")
ve, vp, vt = mix(vq**4, mpf("130.2") / sqrt(2), mpi0**2, 2 * MK0**2 - mpi0**2)
v1 = emit("VALIDATION", "T-1 M_eta (LO U(3)+WV, PDG F_pi, SVZ chi)", "PDG", ve, "547.862", "0.017", "0.05", "", "tol 5 %; theta " + nstr(vt, 5) + " deg")
v2 = emit("VALIDATION", "T-1 M_eta' (same)", "PDG", vp, "957.78", "0.06", "0.05", "", "tol 5 %")
G2 = P["wave9|Gluon_condensate"]; n, q, L0 = chain(G2)
info(s, "FSOT <(alpha_s/pi)G^2> = C_cosm - e^-3 [GeV^4]", "pin wave9", G2, "FSOT", "unit read in GeV^4 (stated); SVZ phenomenology 0.012")
info(s, "instanton density n = <(alpha_s/pi)G^2>/8 [GeV^4]", "Int g^2G^2 = 32 pi^2 per instanton", n, "FSOT", "n = " + nstr(n / mpf("0.1973269804")**4, 5) + " fm^-4")
emit(s, "T-1 chi^1/4 = n^(1/4) (dilute pure-gauge ensemble)", "pin wave9", q, "185.3", "5.7", "0.10", "FSOT", "validation " + ("passed" if v0 else "FAILED") + "; disclosed before freeze: about +8 %")
info(s, "Lambda^(0)_MSbar = n^(1/4) e^(-1/22)/0.65", "DP relation", L0, "FSOT", "ratio to FSOT-only Lambda^(3) 334.43: " + nstr(L0 / col("audit/score_2026-10-02s2.tsv", "S2-1", "S2-1 Lambda^(3)"), 5))
alpha = 1 / L["alpha_inv"]; x, y = P["wave7|m_u/m_d"], P["wave7|m_s/m_d"]; mud = (1 + x) / 2; Qf = sqrt((y**2 - mud**2) / (1 - x**2))
F3 = mp / (2 * sqrt(3) * pi); MK = L["m_K_pm_MeV"]; Mpi = L["m_pi_pm_MeV"]
Dp = 12 * pi * alpha * log(2) * F3**2; p0 = sqrt(Mpi**2 - Dp); DK = Dp; split = mpf(0)
for _ in range(60):
    MhK2 = MK**2 - DK + split / 2; split = MhK2 * (MhK2 - p0**2) / (Qf**2 * p0**2)
mqq2, mss2 = p0**2, 2 * MhK2 - p0**2
Fpi = col("audit/score_2026-10-02p.tsv", "FSOT", "P-4 F_pi with lbar4"); vn = "validation " + ("passed" if (v1 and v2) else "FAILED")
e_, p_, th = mix((q / 1)**4, Fpi, mqq2, mss2)
emit(s, "T-1 M_eta (LO U(3)+WV, F = FSOT F_pi, chi from condensate)", "FSOT pi, K leaves, pins, P-4 F_pi " + nstr(Fpi, 7), e_, "547.862", "0.017", "0.05", "FSOT", vn + "; theta " + nstr(th, 5) + " deg")
emit(s, "T-1 M_eta' (same)", "same", p_, "957.78", "0.06", "0.05", "FSOT", vn)
ie, ip, _ = mix(q**4, F3, mqq2, mss2); info(s, "look-elsewhere F = F3: M_eta / M_eta'", "info", ip, "FSOT", "M_eta " + nstr(ie, 6) + " (M_eta' shown)")
rec(s, "F_K/F_pi inside FSOT", "open derivation", "needed for the next-order (FKS) scheme; not substituted")
# ---------------- T-2
s = "T-2"; GA, sGA = mpf("1.2754"), mpf("0.0013"); DN = mpf("1232") - (mpf("938.27208943") + mpf("939.56542194")) / 2
MUP, sMUP, MUN, sMUN = mpf("2.79284734463"), mpf("0.00000000082"), mpf("-1.91304276"), mpf("0.00000045")
Hq = json.loads((R / "audit/heavy_2026-10-02q.json").read_text(encoding="utf-8")); san = Hq["Q1_sanity_M420_F93"]["DPP"]
def raw(c, o):
    M, MN = mpf(c["M_MeV"]), mpf(c["M_N_MeV"]); I = mpf(o["I_times_M"]); q_ = MN / M
    return {"g1": 3 * mpf(o["A_im"]) / (3 * I), "muS": 3 * q_ * mpf(o["B_re"]) / (18 * I), "muV1": 3 * q_ * mpf(o["Amu_im"]) / (3 * I), "muV0": -3 * q_ / 9 * (mpf(o["xat_val"]) + mpf(o["xat_sea"]))}
rs = raw(Hq["Q1_sanity_M420_F93"], san); SG = {k: (1 if rs[k] > 0 else -1) for k in ("g1", "muS", "muV1")}
pt = R / "audit/heavy_2026-10-02t.json"
if pt.exists() and "DPP" in json.loads(pt.read_text(encoding="utf-8")).get("T2_FSOT_massive_K12", {}):
    c = json.loads(pt.read_text(encoding="utf-8"))["T2_FSOT_massive_K12"]; o = c["DPP"]; r = raw(c, o); I = mpf(o["I_times_M"]); M = mpf(c["M_MeV"])
    g = mpf(o["gA0"]) + SG["g1"] * r["g1"]; muS = SG["muS"] * r["muS"]; muV = r["muV0"] + SG["muV1"] * r["muV1"]
    info(s, "massive K 12: decomposition", "DPP", g, "FSOT", f"g_A^(0) {o['gA0']:.6g} (val {o['gA0_val']:.6g}, sea {o['gA0_sea']:.6g}), g_A^(1) {float(SG['g1'] * r['g1']):.6g}, E/M {o['E_sol_over_M']:.6g} (incl. E_m/M {o.get('E_m_over_M', 0):.4g})")
    emit(s, "T-2 g_A (massive DPP, K 12 basis)", "M = m_p/3, sqrt(e) M, pi+- leaf", g, GA, sGA, "0.02", "FSOT", "round-q K 8: 1.39120; ordering/surface corrections open")
    emit(s, "T-2 M_Delta - M_N (K 12)", "same", 3 * M / (2 * I), DN, "2", "0.15", "FSOT", "")
    emit(s, "T-2 mu_p (K 12)", "same", (muS + muV) / 2, MUP, sMUP, "0.02", "FSOT", "round-q K 8: 2.76602 (-0.96 %): the K 8 agreement is not basis-stable")
    emit(s, "T-2 mu_n (K 12)", "same", (muS - muV) / 2, MUN, sMUN, "0.02", "FSOT", "round-q K 8: -1.92582 (+0.67 %): the K 8 agreement is not basis-stable")
    info(s, "mu_d with K 12 mu_p + mu_n and round-o P_D", "information", (muS) - mpf(3) / 2 * (muS - mpf(1) / 2) * mpf("0.06281210418"), "FSOT", "round r (K 8): 0.80815")
else:
    rec(s, "massive K 12 run", "not completed", "time box; round-q K 8 values stand")
rec(s, "operator-ordering and surface-term corrections", "open derivation", "not derived this round; no correction applied")
rec("GATE", "record rows of the 91", "unchanged", "chi, eta, eta' are derivation-branch rows")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02t.py under audit/FREEZE_2026-10-02t (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
