#!/usr/bin/env python3
"""Round-s2 scores under audit/FREEZE_2026-10-02s2 (owner directive: no hybrid). FSOT-only quark thresholds for Lambda^(4), Lambda^(3);
Lambda^(0)/Lambda^(3) recorded as an open derivation. mpmath/stdlib only. J-1 machinery copied verbatim from tools/score_2026_10_02j.py.

  python tools/score_2026_10_02s2.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02s2.tsv
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, sqrt, pi, ln, fabs, nstr
from mpmath import mp, zeta, quad
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves(); P = X.pins(); Z3 = zeta(3)
rows = []
def emitz(sec, name, inputs, v, c, s, cls="", note=""):
    v, c, s = mpf(v), mpf(c), mpf(s); z = fabs(v - c) / s; verdict = "PASS" if z <= 1 else "FAIL"
    rows.append([sec, name, inputs, nstr(v, 12), nstr(c, 10), nstr(s, 4), nstr(z, 5), verdict, nstr((v - c) / c * 100, 5) + " %", cls, note]); return verdict == "PASS"
def info(sec, name, inputs, v, cls="", note=""): rows.append([sec, name, inputs, nstr(mpf(v), 12), "-", "-", "-", "info", "-", cls, note])
def rec(sec, name, verdict, note): rows.append([sec, name, "-", "-", "-", "-", "-", verdict, "-", "-", note])
# ---------------- J-1 machinery: exact-integral MSbar Lambda with the 4-loop beta function
def bcoef(nf):
    b0 = (33 - 2 * nf) / (12 * pi); b1 = (153 - 19 * nf) / (24 * pi**2)
    b2 = (2857 - mpf(5033) / 9 * nf + mpf(325) / 27 * nf**2) / (128 * pi**3)
    b3 = ((mpf(149753) / 6 + 3564 * Z3) - (mpf(1078361) / 162 + mpf(6508) / 27 * Z3) * nf + (mpf(50065) / 162 + mpf(6472) / 81 * Z3) * nf**2
          + mpf(1093) / 729 * nf**3) / (256 * pi**4)
    return b0, b1, b2, b3
def lnmu2_over_L2(al, nf):
    b0, b1, b2, b3 = bcoef(nf)
    R = lambda x: -1 / (x**2 * (b0 + b1 * x + b2 * x**2 + b3 * x**3)) + 1 / (b0 * x**2) - b1 / (b0**2 * x)
    return 1 / (b0 * al) + b1 / b0**2 * ln(b0 * al) + quad(R, [0, al])
def Lam(al, mu, nf): return mu * mp.exp(-lnmu2_over_L2(al, nf) / 2)
def alpha_at(mu, Lm, nf):  # bisection (f decreasing in alpha on (0.05, 0.6)); 90 halvings
    lo, hi, t = mpf("0.05"), mpf("0.6"), 2 * ln(mu / Lm)
    for _ in range(90):
        m = (lo + hi) / 2
        if lnmu2_over_L2(m, nf) > t: lo = m
        else: hi = m
    return (lo + hi) / 2
def decouple(al, nl):  # alpha^(nl) from alpha^(nl+1) at mu = m(m), 3-loop (Chetyrkin-Kniehl-Steinhauser)
    x = al / pi; c3 = mpf(564731) / 124416 - mpf(82043) / 27648 * Z3 - mpf(2633) / 31104 * nl
    return al * (1 + mpf(11) / 72 * x**2 + c3 * x**3)
def lambdas(asMZ, MZ, mb, mc):
    L5 = Lam(asMZ, MZ, 5); a5b = alpha_at(mb, L5, 5); a4b = decouple(a5b, 4); L4 = Lam(a4b, mb, 4)
    a4c = alpha_at(mc, L4, 4); a3c = decouple(a4c, 3); L3 = Lam(a3c, mc, 3)
    return [x * 1000 for x in (L5, L4, L3)]
FL = [(mpf(213), mpf(8)), (mpf(295), mpf(10)), (mpf(338), mpf(10))]
s = "S2-1"
asF = 2 * (F.POOF / F.PSI_CON) ** 2; MZF = L["m_Z_MeV"] / 1000
mt = L["m_t_over_m_W"] * L["m_W_MeV"] / 1000; mb = mt / P["wave8|m_t/m_b"]; mc = L["m_c_over_m_b"] * mb
info(s, "FSOT m_t = (m_t/m_W) m_W [GeV]", "leaves", mt, "FSOT", "")
info(s, "FSOT m_b = m_t/(m_t/m_b) [GeV]", "pin wave8", mb, "FSOT", "used as the MSbar m_b(m_b) decoupling scale (scheme stated in the freeze)")
info(s, "FSOT m_c = (m_c/m_b) m_b [GeV]", "leaf", mc, "FSOT", "used as m_c(m_c)")
v = lambdas(asF, MZF, mb, mc)
info(s, "Lambda^(5) FSOT (J-1, unchanged)", "FSOT alpha_s, M_Z", v[0], "FSOT", "")
emitz(s, "S2-1 Lambda^(4) FSOT-only (FSOT m_b threshold)", "FSOT alpha_s, M_Z, m_b", v[1], FL[1][0], FL[1][1], "FSOT", "replaces the external-threshold J-1 row; z <= 1 vs FLAG")
emitz(s, "S2-1 Lambda^(3) FSOT-only (FSOT m_b, m_c thresholds)", "same + m_c", v[2], FL[2][0], FL[2][1], "FSOT", "replaces the external-threshold J-1 row; z <= 1 vs FLAG")
vv = lambdas(asF, MZF, mb, P["wave4|m_c/m_b"] * mb)
info(s, "look-elsewhere: pin m_c/m_b (wave4): Lambda^(3)", "info", vv[2], "FSOT", "info only")
s = "S2-2"
rec(s, "Lambda^(0)/Lambda^(3) inside FSOT", "open derivation", "no absolute FSOT m_s, m_ud (ratios only); m_s, m_ud < Lambda^(3) so perturbative decoupling is undefined; needs an FSOT pure-gauge hadronic scale (sqrt(sigma), r0 or 0++ glueball) or a non-perturbative matching")
rec(s, "chi_top, M_eta, M_eta' rescoring", "not scored", "blocked on Lambda^(0); no external number substituted (owner directive)")
rec("SCAFFOLDING", "reclassified (not FSOT, not counted)", "external-input", "round-m U(3)+WV eta/eta' (lattice chi); round-l GMOR m_ud, m_s (external Sigma ratio); J-1 Lambda^(4,3) with FLAG thresholds; round-p chi (Lambda^(3) with FLAG thresholds); round-r chi (FLAG 0.772), eta, eta'; round-s FKS eta, eta' (FLAG F_K/F_pi)")
rec("GATE", "record rows of the 91", "unchanged", "scaffolding rows never enter confirmed or agreeing counts")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02s2.py under audit/FREEZE_2026-10-02s2 (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
