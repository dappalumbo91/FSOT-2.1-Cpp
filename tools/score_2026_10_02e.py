#!/usr/bin/env python3
"""Scoring under docs/freezes/DERIVATIONS_2026-10-02e (committed first): step 1 (v/G_F fix, round-d constructions rerun unchanged) and step 2.

  python tools/score_2026_10_02e.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02e.tsv
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, sqrt, pi, ln, fabs, nstr
from mpmath import zeta
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); ref = X.refs(); P = X.pins(); L = X.leaves()
rows = []
def emit(sec, name, inputs, v, c, s, note=""):
    zz = fabs(v - c) / s
    rows.append([sec, name, inputs, nstr(v, 15), nstr(c, 12), nstr(s, 5), nstr(zz, 5), "PASS" if zz <= 1 else "FAIL", nstr((v - c) / c * 10**6, 6), note])
# ---- step 1
mW, mZ, alpha0 = L["m_W_MeV"] / 1000, L["m_Z_MeV"] / 1000, 1 / L["alpha_inv"]
schemes = {"S1": (1 - (mW / mZ) ** 2, alpha0, "on-shell s2 from leaves, alpha(0) leaf [PRIMARY, FSOT-only]"),
           "S2": (L["sin2_theta_W_MSbar"], 1 / mpf("127.930"), "MS-bar s2 leaf, alpha_hat(M_Z)=1/127.930 EXTERNAL [secondary]")}
GFs = {}
vref = 1 / sqrt(sqrt(2) * ref("G_F_GeVm2")[0])
for S, (s2, al, lab) in schemes.items():
    v = 2 * mW * sqrt(s2) / sqrt(4 * pi * al); GF = 1 / (sqrt(2) * v * v); GFs[S] = GF
    tag = "frozen-pending" + ("; only S1 can confirm Gamma_Z/M_Z" if S == "S1" else "; never confirmed (external alpha_hat)")
    emit(f"step1_{S}", "v GeV", lab, v, vref, vref * ref("G_F_GeVm2")[1] / ref("G_F_GeVm2")[0] / 2, "reference v = (sqrt2 G_F,CODATA)^-1/2")
    emit(f"step1_{S}", "G_F GeV^-2", lab, GF, *ref("G_F_GeVm2"), tag)
    R = X.compute(hub, F, GF_override=GF)
    emit(f"step1_{S}", "Gamma_Z/M_Z (A1)", "round-d A1 unchanged, G_F(" + S + ")", R["GZ_over_MZ_A1"], *ref("Gamma_Z_over_M_Z"), tag)
    emit(f"step1_{S}", "Gamma_Z GeV (A1)", "", R["Gamma_Z_A1"], *ref("Gamma_Z_GeV"))
    for k, lab2 in (("Gamma_Z_A2", "A2"), ("Gamma_Z_A3", "A3"), ("Gamma_Z_A4", "A4")):
        emit(f"step1_{S}_alt", f"Gamma_Z GeV ({lab2})", "reported, not a candidate", R[k], *ref("Gamma_Z_GeV"))
    emit(f"step1_{S}", "Gamma_inv MeV", "held-out", R["Gamma_inv"] * 1000, *ref("Gamma_inv_MeV"))
    emit(f"step1_{S}", "Gamma_ll MeV", "held-out", R["Gamma_ee"] * 1000, *ref("Gamma_ll_MeV"))
    emit(f"step1_{S}", "sigma_had0 nb", "held-out (G_F-free)", R["sigma_had0_nb"], *ref("sigma_had0_nb"))
    emit(f"step1_{S}", "R_ell", "held-out (G_F-free)", R["R_ell_A1"], *ref("R_ell_derived"))
    emit(f"step1_{S}", "Gamma_W GeV", "round-d unchanged", R["Gamma_W"], *ref("Gamma_W_GeV"))
    emit(f"step1_{S}", "tau_mu s", "round-d unchanged", R["tau_mu"], *ref("tau_mu_s"))
    emit(f"step1_{S}", "tau_tau s (external BR)", "round-d unchanged", R["tau_tau"], *ref("tau_tau_s"))
# ---- step 2: alpha_s(m_tau)
z3 = zeta(3)
def betas(nf):
    return ((11 - mpf(2) * nf / 3) / 4, (102 - mpf(38) * nf / 3) / 16, (mpf(2857) / 2 - mpf(5033) * nf / 18 + mpf(325) * nf**2 / 54) / 64,
            (mpf(149753) / 6 + 3564 * z3 - (mpf(1078361) / 162 + mpf(6508) * z3 / 27) * nf + (mpf(50065) / 162 + mpf(6472) * z3 / 81) * nf**2 + mpf(1093) * nf**3 / 729) / 256)
def run(a, mu0, mu1, nf, steps=4000):
    b0, b1, b2, b3 = betas(nf)
    f = lambda x: -(b0 * x**2 + b1 * x**3 + b2 * x**4 + b3 * x**5)
    t0, t1 = ln(mu0**2), ln(mu1**2); h = (t1 - t0) / steps
    for _ in range(steps):
        k1 = f(a); k2 = f(a + h * k1 / 2); k3 = f(a + h * k2 / 2); k4 = f(a + h * k3); a += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    return a
def decouple(a, nl):
    return a * (1 + mpf(11) / 72 * a**2 + (mpf(564731) / 124416 - mpf(82043) * z3 / 27648 - mpf(2633) * nl / 31104) * a**3)
mt = L["m_t_over_m_W"] * L["m_W_MeV"] / 1000; mb = mt / P["wave8|m_t/m_b"]; mc = L["m_c_over_m_b"] * mb; mtau = L["m_tau_MeV"] / 1000
as_mz = 2 * (F.POOF / F.PSI_CON) ** 2
a5 = run(as_mz / pi, mZ, mb, 5); a4 = decouple(a5, 4); a4c = run(a4, mb, mc, 4); a3 = decouple(a4c, 3); a3tau = run(a3, mc, mtau, 3)
as_tau = a3tau * pi
emit("step2", "alpha_s(m_tau) nf=3", f"seed alpha_s(M_Z)={nstr(as_mz, 6)}, 4-loop, thresholds m_b={nstr(mb, 6)} m_c={nstr(mc, 6)} GeV (FSOT)", as_tau, *ref("alpha_s_mtau"), "frozen-pending new row")
# BR(tau -> e nu nu) and tau_tau, FSOT-only
aa = a3tau
dP = aa + mpf("5.2023") * aa**2 + mpf("26.366") * aa**3 + mpf("127.08") * aa**4
SEW = 1 + 2 * alpha0 / pi * ln(mZ / mtau)
Rtau = 3 * (L["CKM_V_ud"] ** 2 + L["CKM_V_us"] ** 2) * SEW * (1 + dP)
mmu = X.kg_to_GeV(L["m_mu_kg"]); x = (mmu / mtau) ** 2
fmu = 1 - 8 * x + 8 * x**3 - x**4 - 12 * x**2 * ln(x)
BRe = 1 / (1 + fmu + Rtau)
emit("step2", "BR(tau->e nu nu)", "alpha_s(m_tau) row, V_ud, V_us leaves, S_EW leading log (G_F-free)", BRe, *ref("BR_tau_enunu"), "frozen-pending new row")
for S in ("S1", "S2"):
    Ge = GFs[S] ** 2 * mtau**5 / (192 * pi**3) * (1 + alpha0 / (2 * pi) * (mpf(25) / 4 - pi**2))
    emit("step2", f"tau_tau s (FSOT BR, G_F {S})", "BR row, G_F(" + S + "), m_tau leaf", X.HBAR_EVS * BRe / (Ge * mpf(10) ** 9), *ref("tau_tau_s"),
         "frozen-pending new row" + (" (primary)" if S == "S1" else " (secondary, external alpha_hat)"))
rows.append(["step2", "mu_n, mu_t, f_pi, tau_pi+, two-nucleon mu_d", "no FSOT route exists (searched seeds, sec.66/67, data)", "-", "-", "-", "-", "n/a", "-", "NOT CONSTRUCTED"])
# sec. 67 recompute report (stored values are not replaced)
s67 = X.sec67(hub, F)
meas = {"H-2": ref("mu_d_over_mu_N"), "He-3": ref("mu_h_over_mu_N"), "Li-7": ref("mu_Li7"), "B-11": ref("mu_B11"), "N-14": ref("mu_N14"), "P-31": ref("mu_P31")}
for nm, (c, s) in meas.items():
    e = s67[nm]
    rows.append(["sec67", f"#{e['index']} {nm} {e['formula']}", f"stored {nstr(e['stored'], 15)}", nstr(e["recomputed"], 15), nstr(c, 12), nstr(s, 5),
                 f"stored z {nstr(fabs(e['stored'] - c) / s, 5)} / recomputed z {nstr(fabs(e['recomputed'] - c) / s, 5)}", "report",
                 nstr((e["recomputed"] - e["stored"]) / e["stored"] * 10**6, 6), "recomputed - stored (ppm); stored value kept"])
with open(a.out, "w", encoding="utf-8") as o:
    o.write("# generated by tools/score_2026_10_02e.py under docs/freezes/DERIVATIONS_2026-10-02e (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tz<=1\tppm\tnote\n")
    for r in rows: o.write("\t".join(r) + "\n")
for r in rows: print(" | ".join(r))
