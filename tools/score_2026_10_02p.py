#!/usr/bin/env python3
"""Round-p scores under audit/FREEZE_2026-10-02p (committed first). Validations first; gates exactly as frozen.
P-1/P-2 numbers come from audit/heavy_2026-10-02p.json (tools/heavy_2026_10_02p.py + tools/cqsm_rot.py, numpy/scipy, run alone);
everything else is computed here with mpmath.

  python tools/score_2026_10_02p.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02p.tsv
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, sqrt, pi, fabs, nstr
from mpmath import log, matrix, eigsy, atan, exp, zeta
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves(); P = X.pins(); R = Path(__file__).resolve().parents[1]
H = json.loads((R / "audit/heavy_2026-10-02p.json").read_text(encoding="utf-8"))
rows = []
def emit(sec, name, inputs, v, c, s, tol, cls="", note=""):
    v, c, s, tol = mpf(v), mpf(c), mpf(s), mpf(tol)
    rel = (v - c) / c; verdict = "PASS" if fabs(rel) <= tol else "FAIL"
    rows.append([sec, name, inputs, nstr(v, 12), nstr(c, 10), nstr(s, 4), nstr(fabs(v - c) / s, 5), verdict, nstr(rel * 100, 5) + " %", cls, note]); return verdict == "PASS"
def emitz(sec, name, inputs, v, c, s, cls="", note=""):
    v, c, s = mpf(v), mpf(c), mpf(s); z = fabs(v - c) / s; verdict = "PASS" if z <= 1 else "FAIL"
    rows.append([sec, name, inputs, nstr(v, 12), nstr(c, 10), nstr(s, 4), nstr(z, 5), verdict, nstr((v - c) / c * 100, 5) + " %", cls, note]); return verdict == "PASS"
def info(sec, name, inputs, v, cls="", note=""): rows.append([sec, name, inputs, nstr(mpf(v), 12), "-", "-", "-", "info", "-", cls, note])
def rec(sec, name, verdict, note): rows.append([sec, name, "-", "-", "-", "-", "-", verdict, "-", "-", note])
def col(path, sec, key):
    for line in open(R / path, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) > 3 and (sec is None or f[0] == sec) and f[1].startswith(key): return mpf(f[3])
def prec(rid):
    for line in open(R / "audit/precision_2026-10-02.tsv", encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if f[0] == rid: return mpf(f[3])
Nc = 3
me = X.kg_to_GeV(L["m_e_kg"]) * 1000; mp = X.kg_to_GeV(L["m_p_kg"]) * 1000; mn = X.kg_to_GeV(L["m_n_kg"]) * 1000
GA, sGA = mpf("1.2754"), mpf("0.0013"); DN = mpf("1232") - (mpf("938.27208943") + mpf("939.56542194")) / 2
MUP, sMUP, MUN, sMUN = mpf("2.79284734463"), mpf("0.00000000082"), mpf("-1.91304276"), mpf("0.00000045")
MUD, sMUD = mpf("0.8574382335"), mpf("0.0000000022"); PD = mpf("0.06281210418")
# ---------------- P-1 / P-2 derived quantities from the cached spectral sums
san = H["P1_sanity_M420_F93"]
def prim(c):
    if c.get("SC_converged") and "SC" in c and -1 < c["SC"]["eps_val"] < 1: return "SC", c["SC"]
    return "DPP", c["DPP"]
def raw(c, o):
    M, MN = mpf(c["M_MeV"]), mpf(c["M_N_MeV"]); I = mpf(o["I_times_M"]); q = MN / M
    return {"g1": Nc * mpf(o["A_im"]) / (3 * I), "muS": Nc * q * mpf(o["B_re"]) / (18 * I), "muV1": Nc * q * mpf(o["Amu_im"]) / (3 * I),
            "muV0": -Nc * q / 9 * (mpf(o["xat_val"]) + mpf(o["xat_sea"]))}
_, so = prim(san); rs = raw(san, so)
SG = {k: (1 if rs[k] > 0 else -1) for k in ("g1", "muS", "muV1")}   # frozen: sign of each Omega^1 term fixed to the (positive) literature sign at M = 420
def derive(c):
    tag, o = prim(c); r = raw(c, o); M = mpf(c["M_MeV"]); I = mpf(o["I_times_M"])
    g1, muS, muV1, muV0 = SG["g1"] * r["g1"], SG["muS"] * r["muS"], SG["muV1"] * r["muV1"], r["muV0"]
    muV = muV0 + muV1
    return {"profile": tag, "gA0": mpf(o["gA0"]), "gA1": g1, "gA": mpf(o["gA0"]) + g1, "DN": 3 * M / (2 * I), "E": mpf(o["E_sol_over_M"]), "MN": (mpf(o["E_sol_over_M"]) + 3 / (8 * I)) * M,
            "muS": muS, "muV0": muV0, "muV1": muV1, "mup": (muS + muV) / 2, "mun": (muS - muV) / 2, "bound": o["E_sol_over_M"] < 3 and -1 < o["eps_val"] < 1, "o": o}
def note(c, d): return (f"profile {d['profile']} (SC converged {c.get('SC_converged')}); E/M = {float(d['E']):.6g}; g_A^(0) = {nstr(d['gA0'], 6)}, g_A^(1) = {nstr(d['gA1'], 6)}; "
                        f"mu_S = {nstr(d['muS'], 6)}, mu_V^(0) = {nstr(d['muV0'], 6)}, mu_V^(1) = {nstr(d['muV1'], 6)}; Re A = {c[d['profile']]['A_re']:.2g}")
V = {}
s = "VALIDATION"
ds = derive(san)
rec(s, "P-1 sanity M = 420, F = 93: g_A in [1.1, 1.5]", "PASS" if 1.1 <= ds["gA"] <= 1.5 else "FAIL", "g_A = " + nstr(ds["gA"], 6) + "; " + note(san, ds))
rec(s, "P-1 sanity: M_Delta - M_N in [200, 350] MeV", "PASS" if 200 <= ds["DN"] <= 350 else "FAIL", "Delta-N = " + nstr(ds["DN"], 6))
rec(s, "P-2 sanity: mu_p in [1.6, 2.6], mu_n in [-2.0, -1.0]", "PASS" if (1.6 <= ds["mup"] <= 2.6 and -2.0 <= ds["mun"] <= -1.0) else "FAIL",
    f"mu_p = {nstr(ds['mup'], 6)}, mu_n = {nstr(ds['mun'], 6)} (literature 2.03, -1.41 with m_pi = 140; this solver is in the chiral limit)")
for t in ("DPP", "SC"):
    if t in san: info(s, f"P-1 sanity soliton energy ({t})", "E/M", san[t]["E_sol_over_M"], "", f"SC converged {san.get('SC_converged')}")
cv = H["P1_validation"]; dv = derive(cv)
rec(s, "P-1 validation soliton bound (E < N_c M)", "YES" if dv["bound"] else "NO", note(cv, dv))
V["gA"] = emit(s, "P-1 g_A = g_A^(0) + g_A^(1)", "PDG m_p/3, M_PV from FLAG F_pi", dv["gA"], GA, sGA, "0.10", "", "tol 10 %")
V["DN"] = emit(s, "P-1 M_Delta - M_N = 3/(2I)", "same", dv["DN"], DN, "2", "0.15", "", "tol 15 %")
V["mup"] = emit(s, "P-2 mu_p", "same, M_N = PDG m_p", dv["mup"], MUP, sMUP, "0.10", "", "tol 10 %")
V["mun"] = emit(s, "P-2 mu_n", "same", dv["mun"], MUN, sMUN, "0.10", "", "tol 10 %")
mpi_pdg, mp_pdg = mpf("139.57039"), mpf("938.27208943")
C4 = (19 - 3 * sqrt(3) * pi) / 2
def lbar4(MQ, Mp): return Nc + log(4 * MQ**2 / Mp**2) - C4
def fpi(MQ, Mp):
    F0 = MQ * sqrt(Nc) / (2 * pi); lb = lbar4(MQ, Mp); return F0 * (1 + Mp**2 * lb / (16 * pi**2 * F0**2)), F0, lb
fv, F0v, lbv = fpi(mp_pdg / 3, mpi_pdg)
V["l4"] = emit(s, "P-4 F_pi/F, lbar4 from the one-loop linear sigma model", "PDG m_p, M_pi+", fv / F0v, "1.062", "0.007", "0.02", "", "tol 2 %; lbar4 = " + nstr(lbv, 6))
LPV = exp(mpf(1) / 22)
chiv = (mpf("0.65") * LPV * 338)**4
V["chi"] = emit(s, "P-5 chi^1/4 = 0.65 Lambda_PV (DP), Lambda^(3) FLAG 338", "FLAG Lambda^(3)", chiv**(mpf(1) / 4), "185.3", "5.7", "0.10", "", "tol 10 %; same light-flavor-scale approximation")
c2 = mpf(299792458)**2; hb, cc, kB = mpf("1.054571817e-34"), mpf(299792458), mpf("1.380649e-23"); pc = mpf("3.0856775814913673e16")
def tcmb(ob, eta, G, u):
    rc = 3 * (mpf(100000) / (pc * 10**6))**2 / (8 * pi * G); ng = ob * rc / u / eta
    return hb * cc / kB * (pi**2 * ng / (2 * zeta(3)))**(mpf(1) / 3)
V["T"] = emit(s, "P-6 T_CMB from Omega_b h^2 and eta", "PDG 0.02237, 6.04e-10, CODATA G, u", tcmb(mpf("0.02237"), mpf("6.04e-10"), mpf("6.67430e-11"), mpf("1.66053906660e-27")), "2.7255", "0.0006", "0.01", "", "tol 1 % (information-level check of the formula)")
# ---------------- FSOT
s = "FSOT"
c = H["P1_FSOT"]; d = derive(c); cc_ = H["P1_FSOT_conv"]; dc = derive(cc_)
rec(s, "P-1 soliton bound at M = m_p/3 (E < N_c M)", "YES" if d["bound"] else "NO", note(c, d) + f"; self-consistent iteration converged: {c.get('SC_converged')}")
gok = emit(s, "P-1 g_A = g_A^(0) + g_A^(1)", "M = m_p/3, M_PV = sqrt(e) M, N_c = 3", d["gA"], GA, sGA, "0.02", "FSOT",
           "validation " + ("passed" if V["gA"] else "FAILED") + f"; convergence run {nstr(dc['gA'], 6)} ({dc['profile']})") and V["gA"]
emit(s, "P-1 M_Delta - M_N = 3/(2I) (held-out)", "same", d["DN"], DN, "2", "0.15", "FSOT", "validation " + ("passed" if V["DN"] else "FAILED") + f"; convergence run {nstr(dc['DN'], 6)}")
info(s, "P-1 nucleon mass E_sol + 3/(8I)", "same", d["MN"], "FSOT", "MeV; N_c M = " + nstr(mp, 9) + "; rotational energy raises M_N (cannot bind)")
emit(s, "P-2 mu_p (soliton)", "same, M_N = FSOT m_p", d["mup"], MUP, sMUP, "0.02", "FSOT", "validation " + ("passed" if V["mup"] else "FAILED") + f"; convergence run {nstr(dc['mup'], 6)}")
emit(s, "P-2 mu_n (soliton)", "same", d["mun"], MUN, sMUN, "0.02", "FSOT", "validation " + ("passed" if V["mun"] else "FAILED") + f"; convergence run {nstr(dc['mun'], 6)}")
muS2 = d["mup"] + d["mun"]
emit(s, "P-2 mu_d = mu_S - (3/2)(mu_S - 1/2) P_D (soliton mu_p + mu_n, round-o P_D)", "same", muS2 - mpf(3) / 2 * (muS2 - mpf(1) / 2) * PD, MUD, sMUD, "0.02", "FSOT", "record row Deuteron_mu")
for t in ("DPP", "SC"):
    if t in c: info(s, f"P-1 soliton energy E/M ({t})", "same", c[t]["E_sol_over_M"], "FSOT", "threshold N_c = 3")
hist = [h for h in c.get("SC_history", []) if h[1] is not None]
if hist: info(s, "P-1 self-consistent iteration: lowest E/M reached", "same", min(h[1] for h in hist), "FSOT", f"last max|dtheta| = {hist[-1][3]:.3g} after {len(hist)} iterations")
rec("GATE", "P-3 deuteron rerun with new g_piNN; KSRF/VMD -> Delta alpha_had -> Gamma_Z/M_Z", "RUN" if gok else "NOT RUN", f"frozen gate: g_A within 2 % with passing validation: {gok}")
Mpi = L["m_pi_pm_MeV"]; MQ = mp / 3
fF, F0, lb = fpi(MQ, Mpi)
emit(s, "P-4 F_pi with lbar4 = N_c + ln(4 M_Q^2/M_pi^2) - (19 - 3 sqrt3 pi)/2", "FSOT m_p, pi+- leaf", fF, mpf("130.2") / sqrt(2), mpf("0.8") / sqrt(2), "0.02", "FSOT",
     "validation " + ("passed" if V["l4"] else "FAILED") + "; F_pi/m_e = " + nstr(fF / me, 9) + "; disclosed before freeze: about +0.9 %")
emit(s, "P-4 lbar4", "same", lb, "4.40", "0.28", "0.10", "FSOT", "FLAG 2+1 information")
L3 = col("audit/score_2026-10-02j.tsv", "FSOT", "J-1 Lambda^(3) from FSOT")
chi = (mpf("0.65") * LPV * L3)**4
chok = emit(s, "P-5 chi^1/4 = 0.65 e^(1/22) Lambda^(3) (DP instanton liquid)", "FSOT alpha_s Lambda^(3) " + nstr(L3, 9), chi**(mpf(1) / 4), "185.3", "5.7", "0.10", "HYBRID",
            "validation " + ("passed" if V["chi"] else "FAILED") + "; disclosed before freeze: about +24 %")
alpha = 1 / L["alpha_inv"]; x, y = P["wave7|m_u/m_d"], P["wave7|m_s/m_d"]; mud = (1 + x) / 2; Qf = sqrt((y**2 - mud**2) / (1 - x**2))
F3 = mp / (2 * sqrt(3) * pi); MK = L["m_K_pm_MeV"]
Dp = 12 * pi * alpha * log(2) * F3**2; p0 = sqrt(Mpi**2 - Dp)
DK = Dp; split = mpf(0)
for _ in range(60):
    MhK2 = MK**2 - DK + split / 2; split = MhK2 * (MhK2 - p0**2) / (Qf**2 * p0**2)
Bm = p0**2 / 2; Bs = MhK2 - Bm; M0 = 6 * chi / F3**2
Mm = matrix([[(2 * (Bm + 2 * Bs)) / 3, -(2 * sqrt(2) / 3) * (Bs - Bm)], [-(2 * sqrt(2) / 3) * (Bs - Bm), (2 * (2 * Bm + Bs)) / 3 + M0]])
E_, Q_ = eigsy(Mm); th = atan(Q_[1, 0] / Q_[0, 0]) * 180 / pi
emit(s, "P-5 M_eta (U(3) + WV, DP chi)", "M-3a F, M-2a pi0, M-2b K0 (Q route), P-5 chi", sqrt(E_[0]), "547.862", "0.017", "0.05", "HYBRID", "theta = " + nstr(th, 5) + " deg")
emit(s, "P-5 M_eta'", "same", sqrt(E_[1]), "957.78", "0.06", "0.05", "HYBRID", "")
s = "P-6"
Tc = tcmb(prec("pin:wave1|Omega_b_h2"), prec("pin:wave10|eta_baryon_photon"), L["G_N"], L["u_kg"])
emitz(s, "Cosmology T_CMB = (hbar c/k_B)(pi^2 n_gamma/(2 zeta3))^(1/3), n_gamma = Omega_b h^2 rho_c100/(u eta)", "FSOT Omega_b h^2, eta, G_N, u", Tc, "2.7255", "0.0006", "FSOT",
      "validation " + ("passed" if V["T"] else "FAILED") + "; disclosed before freeze: about +0.27 %; T_CMB record row " + nstr(prec("pin:wave1|T_CMB"), 10))
mW = L["m_Z_MeV"] * sqrt(1 - L["sin2_theta_W_MSbar"])
emitz(s, "HEP tree m_W = m_Z sqrt(1 - sin^2 theta_W(MSbar))", "FSOT m_Z, sin^2 theta_W leaves", mW, "80369.2", "13.3", "FSOT", "radiative corrections absent; disclosed before freeze: about -0.5 %; m_W leaf " + nstr(L["m_W_MeV"], 9))
rec(s, "Particle_Physics, Nuclear_Physics", "no own-physics derivation", "frozen")
rec("GATE", "record rows of the 91", "see notes", "Deuteron_mu (P-2) is a record row; T_CMB stays frozen-pending")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02p.py under audit/FREEZE_2026-10-02p (committed first)\n"
            "#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("validations:", {k: ("PASS" if v else "FAIL") for k, v in V.items()})
