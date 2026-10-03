#!/usr/bin/env python3
"""Round-s scores under audit/FREEZE_2026-10-02s (committed first). mpmath/stdlib only.
S-1 g_A separation (information, from audit/heavy_2026-10-02s.json and rounds p, q); S-2 eta/eta' in the FKS scheme.

  python tools/score_2026_10_02s.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02s.tsv
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, sqrt, pi, fabs, nstr
from mpmath import log, matrix, eigsy, atan
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
# ---------------- S-1 g_A separation
s = "S-1"
J = lambda f: json.loads((R / f).read_text(encoding="utf-8"))
for tag, c in (("p chiral D12 K12", J("audit/heavy_2026-10-02p.json")["P1_FSOT"]), ("p chiral D14 K14", J("audit/heavy_2026-10-02p.json")["P1_FSOT_conv"]),
               ("s chiral D10 K8 (separation)", J("audit/heavy_2026-10-02s.json")["S1_FSOT_chiral_K8"]), ("q massive D10 K8", J("audit/heavy_2026-10-02q.json")["Q1_FSOT"])):
    o = c["DPP"]; g1 = mpf(o["A_im"]) / mpf(o["I_times_M"])
    info(s, "g_A " + tag, "DPP, M = m_p/3", mpf(o["gA0"]) + g1, "FSOT", f"g_A^(0) {o['gA0']:.6g} (val {o['gA0_val']:.6g}, sea {o['gA0_sea']:.6g}); g_A^(1) {float(g1):.6g} (A {o['A_im']:.6g}, I M {o['I_times_M']:.6g})")
rec(s, "separation finding", "located", "basis K 12 -> 8 at m_pi = 0: -1.8 %; m_pi = 0 -> pi+- leaf at K 8: +20.5 % (valence -0.6 %, Dirac-sea axial sum 0.011 -> 0.156, g_A^(1) +22 %): the pion-mass profile (tail) step drives it")
rec(s, "fix at that step", "not frozen", "ordering part of g_A^(1) vs chiral-limit tail/surface term: derivation deferred (time box); no g_A rescoring")
# ---------------- S-2 FKS eta/eta'
s = "S-2"
def block(mpi2_like, MK, alpha, F_em, Qf):
    Dp = 12 * pi * alpha * log(2) * F_em**2; p0 = sqrt(mpi2_like - Dp); DK = Dp; split = mpf(0)
    for _ in range(60):
        MhK2 = MK**2 - DK + split / 2; split = MhK2 * (MhK2 - p0**2) / (Qf**2 * p0**2)
    return p0**2, 2 * MhK2 - p0**2
def fks(mqq2, mss2, chi, fq, r):
    fs = fq * sqrt(2 * r**2 - 1); y = fq / fs; a2 = 2 * chi / fq**2
    Mm = matrix([[mqq2 + 2 * a2, sqrt(2) * a2 * y], [sqrt(2) * a2 * y, mss2 + y**2 * a2]])
    E_, Q_ = eigsy(Mm); phi = atan(-Q_[1, 0] / Q_[0, 0]) * 180 / pi
    return sqrt(E_[0]), sqrt(E_[1]), fabs(phi), y, a2
r = mpf("1.1932")
# validation: PDG F_pi, quenched lattice chi, isospin-limit PDG block (m_qq = M_pi0, m_ss^2 = 2 M_K0^2 - M_pi0^2, no EM)
mpi0, MK0 = mpf("134.9768"), mpf("497.611")
ve, vp, vphi, vy, va2 = fks(mpi0**2, 2 * MK0**2 - mpi0**2, mpf("185.3")**4, mpf("130.2") / sqrt(2), r)
v1 = emit("VALIDATION", "S-2 M_eta (FKS, PDG F_pi, F_K/F_pi 1.1932, chi^1/4 185.3)", "PDG/FLAG/lattice", ve, "547.862", "0.017", "0.05", "", "tol 5 %; phi = " + nstr(vphi, 5) + " deg, a^2 = " + nstr(va2 / 10**6, 5) + " GeV^2")
v2 = emit("VALIDATION", "S-2 M_eta' (same)", "same", vp, "957.78", "0.06", "0.05", "", "tol 5 %")
alpha = 1 / L["alpha_inv"]; x, y_ = P["wave7|m_u/m_d"], P["wave7|m_s/m_d"]; mud = (1 + x) / 2; Qf = sqrt((y_**2 - mud**2) / (1 - x**2))
F3 = mp / (2 * sqrt(3) * pi); mqq2, mss2 = block(L["m_pi_pm_MeV"]**2, L["m_K_pm_MeV"], alpha, F3, Qf)
fq = col("audit/score_2026-10-02p.tsv", "FSOT", "P-4 F_pi with lbar4"); chi = col("audit/score_2026-10-02r.tsv", "R-1", "R-1 chi^1/4")**4
e_, p_, phi, yy, a2 = fks(mqq2, mss2, chi, fq, r); vn = "validation " + ("passed" if (v1 and v2) else "FAILED")
emit(s, "S-2 M_eta (FKS: f_q = FSOT F_pi, f_s = f_q sqrt(2r^2 - 1), a^2 = 2 chi/f_q^2)", "P-4 F_pi " + nstr(fq, 7) + ", R-1 chi^1/4 " + nstr(chi**(mpf(1) / 4), 6) + ", FLAG r", e_, "547.862", "0.017", "0.05", "HYBRID", vn + "; disclosed hand estimate about -2 %")
emit(s, "S-2 M_eta' (same)", "same", p_, "957.78", "0.06", "0.05", "HYBRID", vn + "; disclosed hand estimate about -8 %")
info(s, "S-2 mixing angle phi (quark-flavour basis)", "same", phi, "HYBRID", "FKS phenomenology 39.3(1.0) deg; y = " + nstr(yy, 5) + ", a^2 = " + nstr(a2 / 10**6, 5) + " GeV^2 (FKS 0.265)")
ie, ip, _, _, _ = fks(mqq2, mss2, chi, F3, r)
info(s, "look-elsewhere: f_q = F3 (chiral F): M_eta'", "info", ip, "HYBRID", "M_eta " + nstr(ie, 6))
rec("GATE", "record rows of the 91", "unchanged", "eta, eta' HYBRID; g_A not rescored")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02s.py under audit/FREEZE_2026-10-02s (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
