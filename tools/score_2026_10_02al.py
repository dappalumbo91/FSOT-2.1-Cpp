#!/usr/bin/env python3
"""Round-al scores under audit/FREEZE_2026-10-02al (committed first). z-only, dimensionless ratios; FSOT-only inputs.
AL-1 shell-period averaging inside single PV (audit/shellavg_2026-10-02al_{A,B,sigma}.json); AL-2 Gamma_Z/M_Z via photon-rho beyond universality (not attempted).
  python tools/score_2026_10_02al.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02al.tsv
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
# ---------------- AL-1
s = "AL-1"
def avg(v): return sum(mpf(x_) for x_ in v) / len(v)
Hq = J("audit/heavy_2026-10-02q.json"); rq = Hq["Q1_sanity_M420_F93"]; oq = rq["DPP"]; Iq = mpf(oq["I_times_M"]); qq = mpf(rq["M_N_MeV"]) / mpf(rq["M_MeV"])
SGq = {"g1": 1 if mpf(oq["A_im"]) / Iq > 0 else -1, "muS": 1 if qq * mpf(oq["B_re"]) / (6 * Iq) > 0 else -1, "muV1": 1 if qq * mpf(oq["Amu_im"]) / Iq > 0 else -1}  # round-ag sign convention
lev = {}
for L_ in ("A", "B"):
    f_ = R_ / ("audit/shellavg_2026-10-02al_%s.json" % L_)
    if not f_.exists():
        rec(s, "AL-1 level %s (kmax 14, D0 14)" % L_, "abandoned (not completed)", "killed by the frozen 10-min cap (timeout 600 s) before finishing sample j=0 (level A finished all 4 samples in 550 s, j=0 in 313 s)"); continue
    d_ = J("audit/shellavg_2026-10-02al_%s.json" % L_); S_ = d_["samples"]; Mr = mpf(d_["inputs"]["M_over_mp"]); s0 = S_[0]
    for e_ in S_:
        info(s, "AL-1 level %s sample j=%d (kmax %g, D %s)" % (L_, e_["j"], d_["kmax"], nstr(mpf(e_["D"]), 8)), "round-ag kmax-12 profile, K 14", e_["E_sol"], "diagnostic",
             "E_sol; g_A^(0) %s; I %s; xat_sea %s; %s s" % (nstr(mpf(e_["gA0"]), 8), nstr(mpf(e_["I"]), 8), nstr(mpf(e_["xat_sea"]), 7), e_["seconds"]))
    E0, Ea = mpf(s0["E_sol"]), avg([e_["E_sol"] for e_ in S_]); I0, Ia = mpf(s0["I"]), avg([e_["I"] for e_ in S_])
    A_ = mpf(s0["A_reg"][1]); Am = mpf(s0["Amu_reg"][1]); B_ = mpf(s0["B_reg"][0])
    qN = 1 / Mr; g0 = mpf(s0["gA0"]) + SGq["g1"] * A_ / I0; ga = avg([e_["gA0"] for e_ in S_]) + SGq["g1"] * A_ / Ia
    mV = -qN / 3 * avg([mpf(e_["xat_val"]) + mpf(e_["xat_sea"]) for e_ in S_]) + SGq["muV1"] * qN * Am / Ia; mS = SGq["muS"] * qN * B_ / (6 * Ia)
    mV0s = -qN / 3 * (mpf(s0["xat_val"]) + mpf(s0["xat_sea"])) + SGq["muV1"] * qN * Am / I0; mS0 = SGq["muS"] * qN * B_ / (6 * I0)
    dE, dg, dI = (Ea - E0) / E0, (ga - g0) / g0, (Ia - I0) / I0
    info(s, "AL-1 level %s averaged E_sol" % L_, "4-box shell-period average", Ea, "diagnostic", "sharp D0 %s, change %s %%" % (nstr(E0, 10), nstr(dE * 100, 4)))
    info(s, "AL-1 level %s averaged g_A" % L_, "<g_A^(0)> + A(D0)/<I>", ga, "diagnostic", "sharp D0 %s, change %s %%" % (nstr(g0, 10), nstr(dg * 100, 4)))
    info(s, "AL-1 level %s averaged I" % L_, "4-box average", Ia, "diagnostic", "sharp D0 %s, change %s %%" % (nstr(I0, 10), nstr(dI * 100, 5)))
    info(s, "AL-1 level %s averaged mu_p (not scored)" % L_, "(mu_S + mu_V)/2, round-ag convention", (mS + mV) / 2, "diagnostic", "mu_V %s, mu_S %s; mu_n %s; sharp D0 mu_p %s, mu_n %s" % (nstr(mV, 7), nstr(mS, 7), nstr((mS - mV) / 2, 7), nstr((mS0 + mV0s) / 2, 7), nstr((mS0 - mV0s) / 2, 7)))
    ok_ = all(fabs(x_) <= mpf("0.02") for x_ in (dE, dg, dI))
    rec(s, "AL-1 level %s validation (E, g_A, I within 2 %% of sharp D0)" % L_, "passes" if ok_ else "fails", "E %s %%, g_A %s %%, I %s %%" % (nstr(dE * 100, 4), nstr(dg * 100, 4), nstr(dI * 100, 4)))
    lev[L_] = (ok_, (mS + mV) / 2, (mS - mV) / 2)
if "A" in lev and "B" in lev and lev["A"][0] and lev["B"][0]:
    rec(s, "AL-1 mu scoring", "see level-B rows", "A -> B mu_p change %s %%" % nstr((lev["B"][1] - lev["A"][1]) / lev["B"][1] * 100, 4))
else:
    rec(s, "AL-1 mu_p, mu_n", "not scored", "the frozen rule needs validated averages at both kmax levels; level B did not complete within the 10-min cap")
SG = J("audit/shellavg_2026-10-02al_sigma.json"); qs = {}
for km in (12.0, 14.0):
    v_ = [e_ for e_ in SG["samples"] if e_["kmax"] == km]; qs[km] = avg([e_["Q_sigma"] for e_ in v_])
    info(s, "AL-1 sigma charge, shell-averaged (kmax %g)" % km, "round-ab soliton, K 12, D0 12, 4 boxes", qs[km], "FSOT · intermediate",
         "samples " + ", ".join(nstr(mpf(e_["Q_sigma"]), 7) for e_ in v_))
cq = (qs[14.0] - qs[12.0]) / qs[14.0]
if qs[14.0] > 0 and fabs(cq) <= mpf("0.02"):
    rec(s, "AL-1 sigma charge adoption", "adopted", "kmax 12 -> 14 change %s %%" % nstr(cq * 100, 4))
else:
    rec(s, "AL-1 sigma charge", "not adopted; deuteron not rerun, nothing scored", "averaged kmax 12 -> 14 change %s %% > 2 %% (sharp-sample spread is shell-period: the j=0,1 vs j=2,3 pairs jump together)" % nstr(cq * 100, 4))
rec("AL-2", "AL-2 Gamma_Z/M_Z via photon-rho beyond universality", "not attempted", "time box; no freeze written for it, nothing rescored (Delta alpha_had, G_F, Gamma_Z/M_Z rows unchanged)")
rec("GATE", "record rows of the 91", "unchanged", "z-only; 88/91 since the owner record commit b99fc29 (eta:T_CMB); round al changes no record row")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02al.py under audit/FREEZE_2026-10-02al (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
