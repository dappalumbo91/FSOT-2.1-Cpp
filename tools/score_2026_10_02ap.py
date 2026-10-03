#!/usr/bin/env python3
"""Round-ap scores under audit/FREEZE_2026-10-02ap (committed first). z-only, dimensionless ratios; FSOT-only inputs.
AP-1 soliton isovector charge form factor (audit/vff_2026-10-02ap.json) -> r_V validation -> HLS rho pole -> f_rho, Gamma_ee(rho); AP-0 level-C (kmax 16) job status.
  python tools/score_2026_10_02ap.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02ap.tsv
"""
import argparse, json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, sqrt, pi, ln, fabs, nstr
from mpmath import zeta
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves(); P = X.pins(); ref = X.refs(); R_ = Path(__file__).resolve().parents[1]
rows = []
def emitz(sec, name, inputs, v, c, s, th=0, cls="", note=""):
    v, c, s, th = mpf(v), mpf(c), mpf(s), mpf(th); sig = sqrt(s**2 + th**2); z = fabs(v - c) / sig
    rows.append([sec, name, inputs, nstr(v, 12), nstr(c, 10), nstr(sig, 4), nstr(z, 5), "agrees" if z <= 1 else "miss", nstr((v - c) / c * 100, 5) + " %", cls, note]); return z
def info(sec, name, inputs, v, cls="", note=""): rows.append([sec, name, inputs, nstr(mpf(v), 12), "-", "-", "-", "info", "-", cls, note])
def rec(sec, name, verdict, note): rows.append([sec, name, "-", "-", "-", "-", "-", verdict, "-", "-", note])
J = lambda f: json.loads((R_ / f).read_text(encoding="utf-8"))
mpM = X.kg_to_GeV(L["m_p_kg"]) * 1000
def col(path, sec, key):
    for line in open(R_ / path, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) > 3 and f[0] == sec and f[1].startswith(key): return mpf(f[3])
# ---------------- AP-1
s = "AP-1"; V = J("audit/vff_2026-10-02ap.json"); Mr = mpf(V["M_over_mp"]); I1 = mpf(V["I"]["one"][0]); hbc = mpf("0.1973269804"); mpG = mpM / 1000
info(s, "AP-1 I[1] (cranking double sum, PV-regularised)", "round-ag soliton, K 14, kmax 12, D 14", I1, "check", "I[1]/2 = %s equals the level-A sharp moment of inertia I M = 2.098733467 (normalisation check); s1 %s, s2 %s; %s s" % (nstr(I1 / 2, 10), nstr(mpf(V["I_s1"]["one"]), 8), nstr(mpf(V["I_s2"]["one"]), 8), V["seconds"]))
r2 = mpf(V["I"]["r2"][0]) / I1 / Mr**2; r2c = (mpf("0.84075")**2 + mpf("0.1155")) * (mpG / hbc)**2; r2s = sqrt((2 * mpf("0.84075") * mpf("0.00064"))**2 + mpf("0.0017")**2) * (mpG / hbc)**2
zr = emitz(s, "AP-1 step 1: isovector charge radius r_V^2 m_p^2 (validation)", "FSOT soliton", r2, r2c, r2s, 0, "validation (PDG r_p, <r_n^2>)", "r_V^2 %s fm^2 vs r_p^2 - r_n^2 = 0.82236(201) fm^2" % nstr(r2 * (hbc / mpG)**2, 6))
VAL = zr <= 1
Q2 = [mpf(x) for x in V["Q2_over_mp2"]]; G = [mpf(V["I"]["j0_%d" % i][0]) / I1 for i in range(len(Q2))]
for q_, g_ in zip(Q2, G): info(s, "AP-1 G_V(Q^2) at Q^2/m_p^2 = %s" % nstr(q_, 6), "I[j0(qr)]/I[1]", g_, "diagnostic", "Q^2 %s GeV^2 (byproduct); dipole 1/(1+Q^2/0.71)^2 = %s for reference" % (nstr(q_ * mpG**2, 4), nstr(1 / (1 + q_ * mpG**2 / mpf("0.71"))**2, 5)))
def afit(L2):
    x = [-q_ / (L2 + q_) / 2 for q_ in Q2]; y = [g_ - 1 for g_ in G]
    a_ = sum(xi * yi for xi, yi in zip(x, y)) / sum(xi * xi for xi in x); return a_, sum((yi - a_ * xi)**2 for xi, yi in zip(x, y))
lo, hi = mpf("0.01"), mpf("20"); gr = (sqrt(5) - 1) / 2
for _ in range(200):
    c1, c2 = hi - gr * (hi - lo), lo + gr * (hi - lo)
    if afit(c1)[1] < afit(c2)[1]: hi = c2
    else: lo = c1
L2 = (lo + hi) / 2; a_, ss = afit(L2); Mrho = sqrt(L2)
info(s, "AP-1 step 2: HLS rho-pole fit, M_rho/m_p", "fit of (1 - a/2) + (a/2) M^2/(M^2 + Q^2)", Mrho, "information (after the break)" if not VAL else "FSOT · intermediate", "M_rho %s MeV (PDG 775.26); a %s (universality 2); rms residual %s" % (nstr(Mrho * mpM, 6), nstr(a_, 6), nstr(sqrt(ss / len(Q2)), 4)))
Fr = col("audit/score_2026-10-02p.tsv", "FSOT", "P-4 F_pi with lbar4") / mpM; al = 1 / L["alpha_inv"]
fQ = sqrt(a_) * Fr; Gee = 4 * pi * al**2 * fQ**2 / (3 * Mrho)
info(s, "AP-1 step 3: f_rho Q_rho / m_p = sqrt(a) F_pi/m_p", "HLS, round-p F_pi", fQ, "information (after the break)" if not VAL else "FSOT · intermediate", "f_rho Q_rho %s MeV (PDG-implied 156.4)" % nstr(fQ * mpM, 6))
emitz(s, "AP-1 step 4: Gamma_ee(rho)/M_rho", "HLS f_rho, soliton pole", Gee / Mrho, mpf("7.04e-6") / mpf("0.77526"), mpf("0.06e-6") / mpf("0.77526"), 0, "information (after the break)" if not VAL else "measured",
      "Gamma_ee %s keV (PDG 7.04(6))" % nstr(Gee * mpG * 1e6, 5))
if VAL: rec(s, "AP-1 rescore", "pending", "validation passed")
else: rec(s, "AP-1 Delta alpha_had, G_F, Gamma_Z/M_Z", "not rescored", "chain breaks at step 1: soliton isovector radius r_V^2 %s fm^2 vs 0.82236(201) (z %s); rows after the break are information" % (nstr(r2 * (hbc / mpG)**2, 6), nstr(zr, 4)))
rec("AP-0", "AP-0 level C (kmax 16) job", "started after AP-1 finished (running at commit)", "tools/shellavg_bg_2026_10_02ap.py; additive B -> C rule applied in the round it finishes")
rec("GATE", "record rows of the 91", "unchanged", "z-only; 88/91 since owner record commit b99fc29")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02ap.py under audit/FREEZE_2026-10-02ap (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
