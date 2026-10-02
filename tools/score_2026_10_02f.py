#!/usr/bin/env python3
"""Scoring under docs/freezes/DERIVATIONS_2026-10-02f (committed first): Delta r and alpha(M_Z) from FSOT leaves (H1 FSOT-only hadronic primary,
H2 PDG 0.02783 secondary), self-consistent G_F, round-d/e constructions rerun unchanged, historical sec. 67 versions found by the lost-route search.

  python tools/score_2026_10_02f.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02f.tsv
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, sqrt, pi, ln, fabs, nstr
from mpmath import zeta, mp
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); ref = X.refs(); P = X.pins(); L = X.leaves()
rows = []
def emit(sec, name, inputs, v, c, s, note=""):
    zz = fabs(v - c) / s
    rows.append([sec, name, inputs, nstr(v, 15), nstr(c, 12), nstr(s, 5), nstr(zz, 5), "PASS" if zz <= 1 else "FAIL", nstr((v - c) / c * 10**6, 6), note])
def info(sec, name, inputs, v, note=""):
    rows.append([sec, name, inputs, nstr(v, 15), "-", "-", "-", "info", "-", note])
z3 = zeta(3)
MW, MZ, al = L["m_W_MeV"] / 1000, L["m_Z_MeV"] / 1000, 1 / L["alpha_inv"]
s2 = 1 - (MW / MZ) ** 2; c2 = 1 - s2
mt = L["m_t_over_m_W"] * L["m_W_MeV"] / 1000; mb = mt / P["wave8|m_t/m_b"]; mc = L["m_c_over_m_b"] * mb; mH = L["m_H_MeV"] / 1000
ml = {"e": X.kg_to_GeV(L["m_e_kg"]), "mu": X.kg_to_GeV(L["m_mu_kg"]), "tau": L["m_tau_MeV"] / 1000}
mlight = X.kg_to_GeV(L["m_p_kg"]) / 3
als = 2 * (F.POOF / F.PSI_CON) ** 2
# Delta alpha pieces
da_lep1 = al / (3 * pi) * sum(ln(MZ**2 / m**2) - mpf(5) / 3 for m in ml.values())
da_lep2 = (al / pi) ** 2 * sum(ln(MZ**2 / m**2) / 4 + z3 - mpf(5) / 24 for m in ml.values())
da_lep = da_lep1 + da_lep2
da_top = -(al / pi) * mpf(4) / 45 * MZ**2 / mt**2
quarks = [("u", mpf(2) / 3, mlight), ("d", -mpf(1) / 3, mlight), ("s", -mpf(1) / 3, mlight), ("c", mpf(2) / 3, mc), ("b", -mpf(1) / 3, mb)]
da_had = {"H1": al / (3 * pi) * sum(3 * Q**2 * (ln(MZ**2 / m**2) - mpf(5) / 3) for _, Q, m in quarks) * (1 + als / pi), "H2": mpf("0.02783")}
# Delta r_rem (G_F-independent)
rem_toplog = -(al / (16 * pi * s2)) * 4 * (c2 / s2 - mpf(1) / 3 - 3 * mb**2 / (s2 * MZ**2)) * ln(mt / MZ)
rem_higgs = 11 * al / (24 * pi * s2) * ln(mH / MZ)
rem_const = al / (4 * pi * s2) * (6 + (7 - 4 * s2) / (2 * s2) * ln(c2))
rem = rem_toplog + rem_higgs + rem_const
qcd = 1 - mpf(2) / 3 * (1 + pi**2 / 3) * als / pi
sec = "inputs"
info(sec, "s2 on-shell", "1-(m_W/m_Z)^2 leaves", s2); info(sec, "m_t GeV", "m_t/m_W leaf * m_W", mt); info(sec, "m_b GeV", "m_t / wave8|m_t/m_b", mb)
info(sec, "m_c GeV", "m_c/m_b leaf * m_b", mc); info(sec, "m_H GeV", "leaf", mH); info(sec, "m_u=m_d=m_s GeV", "m_p/3 constituent (FSOT m_p leaf)", mlight)
info(sec, "alpha_s(M_Z)", "seed 2(POOF/psi_con)^2", als)
info("pieces", "Delta alpha_lep 1-loop", "e, mu, tau leaves", da_lep1); info("pieces", "Delta alpha_lep 2-loop", "", da_lep2)
info("pieces", "Delta alpha_lep", "1+2 loop (3-loop ~1.5e-6 omitted)", da_lep); info("pieces", "Delta alpha_top", "m_t leaf", da_top)
emit("pieces", "Delta alpha_had^(5) H1", "FSOT quark loop (1+alpha_s/pi), constituent light quarks", da_had["H1"], *ref("Delta_alpha_had5_MZ"), "H1 primary vs PDG dispersive")
info("pieces", "Delta alpha_had^(5) H2", "PDG 2024 EXTERNAL", da_had["H2"])
info("pieces", "Delta r_rem top log", "Hioki eq. 2.3 non-leading", rem_toplog); info("pieces", "Delta r_rem Higgs", "Hioki eq. 2.4", rem_higgs)
info("pieces", "Delta r_rem constant", "(alpha/4pi s2)[6+(7-4s2)/(2s2) ln c2]", rem_const); info("pieces", "Delta r_rem", "sum", rem)
GFs = {}
for H in ("H1", "H2"):
    GF = pi * al / (sqrt(2) * MW**2 * s2)
    for it in range(200):
        drho = 3 * GF * mt**2 / (8 * sqrt(2) * pi**2) * qcd
        da = da_lep + da_had[H] + da_top
        dr = da - c2 / s2 * drho + rem
        new = pi * al / (sqrt(2) * MW**2 * s2 * (1 - dr))
        if fabs(new - GF) / GF < mpf(10) ** -30: GF = new; break
        GF = new
    GFs[H] = GF
    tag = "PRIMARY (FSOT-only)" if H == "H1" else "secondary (external Delta alpha_had)"
    S = f"dr_{H}"
    info(S, "Delta rho", f"3G_F m_t^2/(8sqrt2 pi^2) x QCD {nstr(qcd, 6)}; iterations {it + 1}", drho)
    info(S, "-(c2/s2) Delta rho", "", -c2 / s2 * drho); info(S, "Delta alpha (lep+had+top)", "", da)
    emit(S, "Delta r", tag, dr, *ref("Delta_r_SM"), "vs PDG SM evaluation (consistency anchor)")
    info(S, "1/alpha(M_Z) on-shell", "alpha/(1-Delta alpha_lep-Delta alpha_had)", (1 - da_lep - da_had[H]) / al)
    info(S, "1/alpha(M_Z) incl. top", "alpha/(1-Delta alpha)", (1 - da) / al)
    emit(S, "G_F GeV^-2", tag, GF, *ref("G_F_GeVm2"), "frozen-pending new row")
    R = X.compute(hub, F, GF_override=GF)
    ztag = "frozen-pending" + ("; confirms Gamma_Z/M_Z only if z<=1 (H1)" if H == "H1" else "; never confirmed (external)")
    emit(S, "Gamma_Z/M_Z (A1)", "round-d A1 unchanged, G_F(" + H + ")", R["GZ_over_MZ_A1"], *ref("Gamma_Z_over_M_Z"), ztag)
    emit(S, "Gamma_Z GeV (A1)", "", R["Gamma_Z_A1"], *ref("Gamma_Z_GeV"))
    emit(S, "Gamma_inv MeV", "held-out", R["Gamma_inv"] * 1000, *ref("Gamma_inv_MeV"))
    emit(S, "Gamma_ll MeV", "held-out", R["Gamma_ee"] * 1000, *ref("Gamma_ll_MeV"))
    emit(S, "sigma_had0 nb", "held-out (G_F-free)", R["sigma_had0_nb"], *ref("sigma_had0_nb"))
    emit(S, "R_ell", "held-out (G_F-free)", R["R_ell_A1"], *ref("R_ell_derived"))
    emit(S, "Gamma_W GeV", "round-d unchanged", R["Gamma_W"], *ref("Gamma_W_GeV"))
    emit(S, "tau_mu s", "round-d unchanged", R["tau_mu"], *ref("tau_mu_s"))
    emit(S, "tau_tau s (external BR)", "round-d unchanged", R["tau_tau"], *ref("tau_tau_s"))
# round-e FSOT BR(tau->e) (same construction as tools/score_2026_10_02e.py), tau_tau with G_F(H)
def betas(nf):
    return ((11 - mpf(2) * nf / 3) / 4, (102 - mpf(38) * nf / 3) / 16, (mpf(2857) / 2 - mpf(5033) * nf / 18 + mpf(325) * nf**2 / 54) / 64,
            (mpf(149753) / 6 + 3564 * z3 - (mpf(1078361) / 162 + mpf(6508) * z3 / 27) * nf + (mpf(50065) / 162 + mpf(6472) * z3 / 81) * nf**2 + mpf(1093) * nf**3 / 729) / 256)
def run(x, mu0, mu1, nf, steps=4000):
    b0, b1, b2, b3 = betas(nf)
    f = lambda y: -(b0 * y**2 + b1 * y**3 + b2 * y**4 + b3 * y**5)
    t0, t1 = ln(mu0**2), ln(mu1**2); h = (t1 - t0) / steps
    for _ in range(steps):
        k1 = f(x); k2 = f(x + h * k1 / 2); k3 = f(x + h * k2 / 2); k4 = f(x + h * k3); x += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    return x
def decouple(x, nl):
    return x * (1 + mpf(11) / 72 * x**2 + (mpf(564731) / 124416 - mpf(82043) * z3 / 27648 - mpf(2633) * nl / 31104) * x**3)
mtau = ml["tau"]
aa = run(decouple(run(decouple(run(als / pi, MZ, mb, 5), 4), mb, mc, 4), 3), mc, mtau, 3)
dP = aa + mpf("5.2023") * aa**2 + mpf("26.366") * aa**3 + mpf("127.08") * aa**4
Rtau = 3 * (L["CKM_V_ud"] ** 2 + L["CKM_V_us"] ** 2) * (1 + 2 * al / pi * ln(MZ / mtau)) * (1 + dP)
x = (ml["mu"] / mtau) ** 2; BRe = 1 / (1 + (1 - 8 * x + 8 * x**3 - x**4 - 12 * x**2 * ln(x)) + Rtau)
for H in ("H1", "H2"):
    Ge = GFs[H] ** 2 * mtau**5 / (192 * pi**3) * (1 + al / (2 * pi) * (mpf(25) / 4 - pi**2))
    emit(f"dr_{H}", "tau_tau s (FSOT BR, round e)", "round-e BR row unchanged, G_F(" + H + ")", X.HBAR_EVS * BRe / (Ge * mpf(10) ** 9), *ref("tau_tau_s"), "frozen-pending")
# lost-route search: historical sec. 67 versions (hub vendor/cosmology/database copy, commit 5d0d5f31, 2026-07-10), ported unchanged
emit("lost_routes", "H-2 mu E/PI (historical #1036)", "hub 5d0d5f31 2026-07-10, vendor/cosmology/database", F.E / F.PI, *ref("mu_d_over_mu_N"), "historical version; current #1036 already scored")
emit("lost_routes", "He-3 mu -(E-GAMMA) (historical #1037)", "hub 5d0d5f31 2026-07-10, vendor/cosmology/database", -(F.E - F.GAMMA), *ref("mu_h_over_mu_N"), "historical version; current #1037 already scored")
rows.append(["lost_routes", "mu_n, mu_t, f_pi, P_D, Delta r, alpha(M_Z)", "40 repos, all refs, full history (678 raw hits inspected)", "-", "-", "-", "-", "n/a", "-",
             "NONE FOUND; tau_pi+ and two-nucleon mu_d not possible"])
with open(a.out, "w", encoding="utf-8") as o:
    o.write("# generated by tools/score_2026_10_02f.py under docs/freezes/DERIVATIONS_2026-10-02f (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tz<=1\tppm\tnote\n")
    for r in rows: o.write("\t".join(r) + "\n")
for r in rows: print(" | ".join(r))
