#!/usr/bin/env python3
"""Round-ak scores under audit/FREEZE_2026-10-02ak (committed first). z-only, dimensionless ratios; FSOT-only inputs.
AK-1a shell-counting scan (audit/shellscan_2026-10-02ak.json); AK-1b smooth spectral convergence factor (audit/smooth_2026-10-02ak_*.json).
  python tools/score_2026_10_02ak.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02ak.tsv
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
# ---------------- AD-1
# ---------------- AK-1a
s = "AK-1a"
SS = {(e_["kmax"], e_["D"]): e_ for e_ in J("audit/shellscan_2026-10-02ak.json")["scan"]}
for (k, D_), e_ in SS.items():
    info(s, "AK-1a xat_sea at (kmax, D) = (%g, %g), kmax D %g" % (k, D_, k * D_), "K 14, round-ag profile, single PV", e_["xat_sea"], "diagnostic", "bare sea - vac %s, PV part %s" % (nstr(mpf(e_["bare_minus_vac"]), 7), nstr(mpf(e_["pv_minus_vacpv_weighted"]), 7)))
d1 = fabs(mpf(SS[(12.0, 14.0)]["xat_sea"]) - mpf(SS[(14.0, 12.0)]["xat_sea"])); d2 = fabs(mpf(SS[(14.0, 14.0)]["xat_sea"]) - mpf(SS[(12.0, 12.0)]["xat_sea"]))
rec(s, "AK-1a shell discreteness (same kmax D vs different)", "confirmed" if d1 <= mpf("0.25") * d2 else "not confirmed", "|X(12,14) - X(14,12)| = %s vs 0.25 x |X(14,14) - X(12,12)| = %s" % (nstr(d1, 4), nstr(mpf("0.25") * d2, 4)))
# ---------------- AK-1b
s = "AK-1b"
Mr1 = mpf(J("audit/murun_2026-10-02ag_K14_D14_k12.json")["inputs"]["M_over_mp"]); SM = {}
for k in (12, 14, 16):
    d_ = J("audit/smooth_2026-10-02ak_k%d.json" % k); SM[k] = d_
    for tag in ("sharp", "smooth"):
        v_ = d_[tag]; mV0 = -(1 / Mr1) / 3 * (mpf(v_["xat_val"]) + mpf(v_["xat_sea"]))
        info(s, "AK-1b kmax %d %s: mu_V^(0)" % (k, tag), "K 14, D 14, E_s = kmax/3", mV0, "diagnostic", "E_sol/M %s; g_A^(0) %s; xat_sea %s" % (nstr(mpf(v_["E_sol"]), 7), nstr(mpf(v_["gA0"]), 7), nstr(mpf(v_["xat_sea"]), 7)))
val = {k: {q_: (mpf(SM[k]["smooth"][q_]) / mpf(SM[k]["sharp"][q_]) - 1) for q_ in ("E_sol", "gA0")} for k in (12, 14)}
ok = all(fabs(v_) <= mpf("0.02") for d_ in val.values() for v_ in d_.values())
rec(s, "AK-1b validation (smoothed vs sharp within 2 %: E, g_A; inertia not run once E failed)", "passes" if ok else "fails",
    "; ".join("kmax %d: E %s %%, g_A^(0) %s %%" % (k, nstr(v_["E_sol"] * 100, 3), nstr(v_["gA0"] * 100, 3)) for k, v_ in val.items()))
sm = [mpf(SM[k]["smooth"]["xat_sea"]) for k in (12, 14, 16)]; se = [mpf(SM[k]["smooth"]["E_sol"]) for k in (12, 14, 16)]
info(s, "AK-1b smoothed sums: kmax stability (information)", "kmax 12/14/16", sm[2], "diagnostic", "xat_sea changes %s %%, %s %%; E_sol changes %s %%, %s %% (sharp E_sol %s, %s, %s)" % (nstr((sm[1] / sm[0] - 1) * 100, 3), nstr((sm[2] / sm[1] - 1) * 100, 3), nstr((se[1] / se[0] - 1) * 100, 3), nstr((se[2] / se[1] - 1) * 100, 3), *[nstr(mpf(SM[k]["sharp"]["E_sol"]), 6) for k in (12, 14, 16)]))
if not ok:
    rec(s, "AK-1b mu_p, mu_n", "not scored", "validation fails: the factor at E_s = kmax/3 changes the regularised values (E +10 %), so it acts as an extra regulator rather than a convergence device; full (inertia/rotational) runs not made")
SGm = J("audit/smooth_2026-10-02ak_sigma.json")["runs"]
for e_ in SGm:
    info(s, "AK-1b sigma charge kmax %g: smooth / sharp" % e_["kmax"], "round-ab soliton, K 12, D 12", e_["smooth"]["Q_sigma"], "diagnostic", "sharp %s; unprojected smooth %s, sharp %s" % (nstr(mpf(e_["sharp"]["Q_sigma"]), 7), nstr(mpf(e_["smooth"]["Q_unprojected"]), 7), nstr(mpf(e_["sharp"]["Q_unprojected"]), 7)))
qs = [mpf(e_["smooth"]["Q_sigma"]) for e_ in SGm]
rec(s, "AK-1b sigma charge", "not adopted; deuteron not rerun", "validation fails; smoothed charge changes %s %%, %s %% (also > 2 %%)" % (nstr((qs[1] / qs[0] - 1) * 100, 3), nstr((qs[2] / qs[1] - 1) * 100, 3)))
rec("AK-2", "Gamma_Z / Delta alpha_had", "not attempted", "time box")
rec("GATE", "record rows of the 91", "unchanged", "z-only")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02ak.py under audit/FREEZE_2026-10-02ak (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
