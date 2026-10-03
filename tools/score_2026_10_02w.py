#!/usr/bin/env python3
"""Round-w scores under audit/FREEZE_2026-10-02w (committed first). z-only scoring; FSOT-only inputs. mpmath/stdlib only.
W-1 directive (b)/(c) observable rescoring; W-2 soliton diagnostic (audit/diag_2026-10-02w.jsonl); W-3 L4, L5, L8 by FSOT scalar saturation -> F_K/F_pi, FKS eta/eta'.

  python tools/score_2026_10_02w.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02w.tsv
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

Fpi = col("audit/score_2026-10-02p.tsv", "FSOT", "P-4 F_pi with"); F0 = mp / (2 * sqrt(3) * pi)
chi4 = col("audit/score_2026-10-02u.tsv", "U2-1", "U2-1 chi^1/4"); chi = chi4**4
Meta, Metap, MKc = mpf("547.862"), mpf("957.78"), mpf("493.677")
# ---------------- W-1 (directive b/c)
s = "W-1"
wv = 6 * chi / Fpi**2; obsv = Meta**2 + Metap**2 - 2 * MKc**2
sg = sqrt((2 * Meta * mpf("0.017"))**2 + (2 * Metap * mpf("0.06"))**2 + (4 * MKc * mpf("0.015"))**2)
emitz(s, "W-1 Witten-Veneziano combination M_eta^2 + M_eta'^2 - 2 M_K^2 = 6 chi/F_pi^2 (MeV^2)", "chi U2-1 (intermediate), P-4 F_pi " + nstr(Fpi, 7), wv, obsv, sg, 0, "FSOT · measured (scores chi_top)", "LO WV; chi^(1/4) = " + nstr(chi4, 6) + " MeV")
info(s, "chi_top^(1/4) vs quenched lattice 185.3(5.7) (information, not scored)", "U2-1", chi4, "FSOT · lattice-computed (intermediate)", "gap " + nstr((chi4 / 185.3 - 1) * 100, 3) + " % = information (directive b)")
rec(s, "Lambda^(5), Lambda^(4), Lambda^(3) (FSOT 209.52 / 292.07 / 334.43 MeV)", "info (intermediate)", "RG-invariant scale of the FSOT alpha_s; scored only through the alpha_s(M_Z) record row and the round-d R_ell (z 1.29, cited); FLAG gaps are information")
rec(s, "scheme-dependent record rows (m_u/m_d, m_c/m_b, m_t/m_W, m_H/m_t, MSbar sin2, alpha_s)", "route documented", "observables: K0-K+ splitting (rounds m-n), onia masses, direct/pole masses, on-shell and effective sin2 / asymmetries, R_ell; no new score")
rec(s, "string tension sqrt(sigma) via Regge slope alpha'", "open derivation", "no FSOT sqrt(sigma) route; target observable alpha' of the rho/a2 trajectories")
rec(s, "H0, neutron lifetime", "deferred", "contested rows; status unchanged, totals given with and without them")
# ---------------- W-2 (diagnostic, not scored)
s = "W-2"; dp = R / "audit/diag_2026-10-02w.jsonl"
if dp.exists():
    for line in dp.read_text(encoding="utf-8").splitlines():
        d = json.loads(line); sec = d["xat_sea_by_sector"]; top = sorted(sec.items(), key=lambda kv: -abs(kv[1]))[:3]
        info(s, "D %g k %g K %d (x %g)" % (d["D"], d["k"], d["K"], d["x"]), "fixed DPP profile", d["xat_sea"], "diagnostic",
             "eps_val " + nstr(mpf(d["eps_val"]), 7) + "; I M = " + nstr(mpf(d["I_M"]), 6) + " (val " + nstr(mpf(d["I_val_M"]), 6) + ", sea " + nstr(mpf(d["I_sea_M"]), 6) + "); largest sectors " + ", ".join(k + " " + nstr(mpf(v), 4) for k, v in top))
else:
    rec(s, "soliton diagnostic", "not run", "")
rp = R / "audit/rot_2026-10-02w_K12.json"
if rp.exists():
    rr = J("audit/rot_2026-10-02w_K12.json"); Mq = mp / 3
    info(s, "rotational response K 12: Delta-N with J-dependent profile (MeV)", "min_x E_sol + J(J+1)/(2I) separately for N and Delta", rr["DN_response_MeV"], "diagnostic",
         "rigid rotation of the static minimum " + nstr(mpf(rr["DN_rigid_MeV"]), 5) + " MeV; x static " + nstr(mpf(rr["static"]["x"]), 4) + ", x_N " + nstr(mpf(rr["N"]["x"]), 4) + ", x_Delta " + nstr(mpf(rr["Delta"]["x"]), 4) + (" (scan edge)" if rr["Delta"]["edge"] else "") + "; I M static " + nstr(mpf(rr["static"]["IM"]), 4) + ", N " + nstr(mpf(rr["N"]["IM"]), 4) + ", Delta " + nstr(mpf(rr["Delta"]["IM"]), 4))
    Hq = J("audit/heavy_2026-10-02q.json")
    def raw(c, o):
        M_, MN = mpf(c["M_MeV"]), mpf(c["M_N_MeV"]); I = mpf(o["I_times_M"]); q_ = MN / M_
        return {"g1": mpf(o["A_im"]) / I, "muS": q_ * mpf(o["B_re"]) / (6 * I), "muV1": q_ * mpf(o["Amu_im"]) / I, "muV0": -q_ / 3 * (mpf(o["xat_val"]) + mpf(o["xat_sea"]))}
    rs = raw(Hq["Q1_sanity_M420_F93"], Hq["Q1_sanity_M420_F93"]["DPP"]); SG = {k: (1 if rs[k] > 0 else -1) for k in ("g1", "muS", "muV1")}
    for nm in ("static", "N"):
        if "obs" in rr[nm]:
            o = rr[nm]["obs"]; r_ = raw({"M_MeV": Mq, "M_N_MeV": mp}, o); muS = SG["muS"] * r_["muS"]; muV = r_["muV0"] + SG["muV1"] * r_["muV1"]
            info(s, "rotational response K 12: mu_p at the %s profile" % nm, "same", (muS + muV) / 2, "diagnostic", "mu_n " + nstr((muS - muV) / 2, 6) + "; g_A " + nstr(mpf(o["gA0"]) + SG["g1"] * r_["g1"], 6) + "; x " + nstr(mpf(rr[nm]["x"]), 4))
info(s, "round-q sanity run at M = 420 MeV, F = 93 MeV, K 8 (external M; information): Delta-N", "audit/heavy_2026-10-02q.json", 3 * mpf(420) / (2 * mpf(Hq0 := J("audit/heavy_2026-10-02q.json")["Q1_sanity_M420_F93"]["DPP"]["I_times_M"])), "diagnostic", "I M " + nstr(mpf(Hq0), 5) + "; FSOT M = m_p/3 at K 8 gives 190.3 MeV: the Delta-N miss sits at the constituent-mass step")
# ---------------- W-3
s = "W-3"
MS = 2 * mp / 3
def fk(Mpi, MK, Fq, L5, mu):
    Me2 = (4 * MK**2 - Mpi**2) / 3; c = 32 * pi**2 * Fq**2; m = lambda M2: M2 / c * log(M2 / mu**2)
    return 1 + mpf(5) / 4 * m(Mpi**2) - m(MK**2) / 2 - mpf(3) / 4 * m(Me2) + 4 * (MK**2 - Mpi**2) * L5 / Fq**2
L5 = F0**2 / (4 * MS**2); L8 = F0**2 / (16 * MS**2); L4 = 0
info(s, "L5^r(mu = M_S) = F^2/(4 M_S^2), M_S = 2 m_p/3", "FSOT F = m_p/(2 sqrt3 pi), quark-level scalar", L5, "FSOT · intermediate", "L4 = 0 (degenerate quark-level scalar nonet, OZI); L8 = " + nstr(L8, 5) + "; M_S = " + nstr(MS, 6) + " MeV")
MKf, Mpif = L["m_K_pm_MeV"], L["m_pi_pm_MeV"]
r = fk(Mpif, MKf, Fpi, L5, MS)
emitz(s, "W-3 F_K/F_pi (one-loop SU(3), L5 by FSOT scalar saturation, L4 = 0 derived)", "FSOT pi+-, K+- leaves, P-4 F_pi, F, M_S = 2 m_p/3", r, "1.1932", "0.0021", 0, "FSOT · measured", "pre-freeze mental estimate ~1.5 disclosed")
rv = fk(mpf("139.57039"), mpf("493.677"), mpf("130.2") / sqrt(2), (mpf("130.2") / sqrt(2))**2 / (4 * mpf(980)**2), mpf(980))
info("VALIDATION", "W-3 same formula with M_S = 980 MeV (a0(980), PDG) and PDG F_pi", "information (not FSOT)", rv, "", "sensitivity to M_S")
alpha = 1 / L["alpha_inv"]; x, y_ = P["wave7|m_u/m_d"], P["wave7|m_s/m_d"]; mud = (1 + x) / 2; Qf = sqrt((y_**2 - mud**2) / (1 - x**2))
MK = MKf; Mpi = Mpif; Dp = 12 * pi * alpha * log(2) * F0**2; p0 = sqrt(Mpi**2 - Dp); DK = Dp; split = mpf(0)
for _ in range(60):
    MhK2 = MK**2 - DK + split / 2; split = MhK2 * (MhK2 - p0**2) / (Qf**2 * p0**2)
mqq2, mss2 = p0**2, 2 * MhK2 - p0**2
fs = Fpi * sqrt(2 * r**2 - 1); yy = Fpi / fs; a2 = 2 * chi / Fpi**2
Mm = matrix([[mqq2 + 2 * a2, sqrt(2) * a2 * yy], [sqrt(2) * a2 * yy, mss2 + yy**2 * a2]]); E_, Q_ = eigsy(Mm); phi = fabs(atan(-Q_[1, 0] / Q_[0, 0]) * 180 / pi)
emitz(s, "W-3 M_eta (FKS, f_s/f_q from W-3, chi U2-1)", "FSOT only", sqrt(E_[0]), "547.862", "0.017", 0, "FSOT · measured", "phi = " + nstr(phi, 5) + " deg; y = " + nstr(yy, 5))
emitz(s, "W-3 M_eta' (same)", "same", sqrt(E_[1]), "957.78", "0.06", 0, "FSOT · measured (scores chi_top, intermediate)", "chi route provisional (round u, post hoc)")
rec("GATE", "record rows of the 91", "unchanged", "z-only; no record row recomputed; H0 and tau_n deferred")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02w.py under audit/FREEZE_2026-10-02w (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
