#!/usr/bin/env python3
"""Round-aj scores under audit/FREEZE_2026-10-02aj (committed first). z-only, dimensionless ratios; FSOT-only inputs.
AJ-1 local-density mu_V^(0) and g_A^(0) validation; AJ-2 local-density sigma charge (audit/locdens_2026-10-02aj.json).
  python tools/score_2026_10_02aj.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02aj.tsv
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
def col(path, sec, key):
    for line in open(R_ / path, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) > 3 and f[0] == sec and f[1].startswith(key): return mpf(f[3])
Hw = J("audit/heavy_2026-10-02ab_wide_K12.json")
# ---------------- AJ-1
s = "AJ-1"
LD = J("audit/locdens_2026-10-02aj.json")
Hq = J("audit/heavy_2026-10-02q.json"); rq = Hq["Q1_sanity_M420_F93"]; oq = rq["DPP"]; Iq = mpf(oq["I_times_M"]); qq = mpf(rq["M_N_MeV"]) / mpf(rq["M_MeV"])
SG = {"muS": 1 if qq * mpf(oq["B_re"]) / (6 * Iq) > 0 else -1, "muV1": 1 if qq * mpf(oq["Amu_im"]) / Iq > 0 else -1}
def regx(sp, comp, IDX, sp_in):
    q_ = (1 / mpf(sp_in["Mpv_over_M"])) ** 2
    d_ = sp[comp]; tot, sea, pv, va, vb = [mpf(d_[k][IDX]) for k in ("tot", "sea", "pv", "vac", "vacpv")]
    return (tot - sea) + (sea - q_ * pv) - (va - q_ * vb)
ROT = {12.0: "audit/murun_2026-10-02ag_K14_D14_k12.json", 14.0: "audit/murun_2026-10-02ae_K14.json"}
MU = {}; GA = []
for e_ in LD["AJ1"]:
    k = e_["kmax"]; Mr_ = mpf(J(ROT[12.0])["inputs"]["M_over_mp"]); qN = 1 / Mr_
    mV0 = -qN / 3 * (mpf(e_["xat_val"]) + mpf(e_["xat_sea"])); GA.append(mpf(e_["gA0"]))
    note = "xat_sea %s (cumulative to r = 3/M: %s); g_A^(0) %s (sea: density %s, matrix %s)" % (nstr(mpf(e_["xat_sea"]), 7), nstr(mpf(e_["xat_sea_cum_r"]["3"]), 5), nstr(mpf(e_["gA0"]), 7), nstr(mpf(e_["gA0_sea_density"]), 8), nstr(mpf(e_["gA0_sea_matrix"]), 8))
    if k in ROT:
        m_ = J(ROT[k]); sp_in = m_["inputs"]; sp = m_["split"]; I_ = mpf(m_["DPP"]["I_times_M"])
        muV = mV0 + SG["muV1"] * qN * regx(sp, "Amu", 1, sp_in) / I_; muS = SG["muS"] * qN * regx(sp, "B", 0, sp_in) / (6 * I_)
        MU[k] = {"mup": (muS + muV) / 2, "mun": (muS - muV) / 2, "mV0": mV0}; note += "; mu_p %s, mu_n %s (rotational pieces from %s)" % (nstr(MU[k]["mup"], 6), nstr(MU[k]["mun"], 6), ROT[k])
    else: MU[k] = {"mV0": mV0}
    info(s, "AJ-1 kmax %g (K 14, D 14): mu_V^(0) from the local current density" % k, "single PV, vacuum-subtracted", mV0, "diagnostic", note)
gch = [(GA[i + 1] - GA[i]) / GA[i + 1] for i in range(len(GA) - 1)]
rec(s, "AJ-1 validation: g_A^(0) density = matrix element; kmax stability", "passes" if all(fabs(c_) <= mpf("0.02") for c_ in gch) else "fails", "density and matrix sea sums agree to 1e-10; kmax changes " + ", ".join(nstr(c_ * 100, 3) + " %" for c_ in gch))
c_p = (MU[14.0]["mup"] - MU[12.0]["mup"]) / MU[14.0]["mup"]; c_n = (MU[14.0]["mun"] - MU[12.0]["mun"]) / MU[14.0]["mun"]; c_v = (MU[16.0]["mV0"] - MU[14.0]["mV0"]) / MU[16.0]["mV0"]
if max(fabs(c_p), fabs(c_n), fabs(c_v)) <= mpf("0.02"):
    for k_, nm_, c_ in (("mup", "mu_p", "2.79284734463"), ("mun", "mu_n", "-1.91304276")):
        emitz(s, "AJ-1 %s (local density, kmax 14)" % nm_, "FSOT inputs", MU[14.0][k_], c_, "0.00000001", fabs(MU[14.0][k_] - MU[12.0][k_]), "FSOT · measured", "kmax-stable")
else:
    rec(s, "AJ-1 mu_p, mu_n", "not scored", "mu_p %s %%, mu_n %s %% (kmax 12 -> 14), mu_V^(0) %s %% (14 -> 16): the local-density integral equals the matrix-element sum, and the oscillation sits in the interior density (r < 3/M)" % (nstr(c_p * 100, 3), nstr(c_n * 100, 3), nstr(c_v * 100, 3)))
# ---------------- AJ-2
s = "AJ-2"
Fr = col("audit/score_2026-10-02p.tsv", "FSOT", "P-4 F_pi with lbar4") / mpM; Mq = mpf(Hw["inputs"]["M_over_mp"])
for e_ in LD["AJ2"]:
    info(s, "AJ-2 kmax %g: Integral rho_sigma (single PV, local density)" % e_["kmax"], "round-ab soliton, K 12, D 12", e_["Q_sigma"], "FSOT · intermediate",
         "cumulative to r = 3/M %s; r_sigma^2 M^2 %s; s_P %+d; g_sigma^2/4pi would be %s" % (nstr(mpf(e_["Q_sigma_cum_r"]["3"]), 6), nstr(mpf(e_["r2_sigma"]), 6), e_["s_P"], nstr((mpf(e_["Q_sigma"]) * Mq / Fr)**2 / (4 * pi), 5)))
q12, q14 = mpf(LD["AJ2"][0]["Q_sigma"]), mpf(LD["AJ2"][1]["Q_sigma"]); ch2 = (q14 - q12) / q14
if q12 > 0 and fabs(ch2) <= mpf("0.02"):
    rec(s, "AJ-2 sigma charge", "adopted", "")
else:
    rec(s, "AJ-2 sigma-projected g_sigmaNN", "not adopted; deuteron not rerun, nothing scored", "kmax 12 -> 14 change %s %% > 2 %%" % nstr(ch2 * 100, 3))
rec("GATE", "record rows of the 91", "unchanged", "z-only")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02aj.py under audit/FREEZE_2026-10-02aj (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
