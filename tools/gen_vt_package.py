#!/usr/bin/env python3
"""Bank the G-independent package terms of tracer §43.5vt (route P2 carried, P1 alternate) for the C++ engine.

Read-only: imports the vt scorer (which imports vq/vn/vk read-only) with bytecode writing off; never calls
score()/validate() (they write files). Everything that depends on G_F (x_t, Δρ, C5 Δr^(2), T_conv, C6) and the
fixed point itself is evaluated live in C++ (include/fsot/fold/vt_gf.hpp); only loop-invariant coefficients
(one-loop B0/polylog integrals, α_s running, Δα) are banked here at 50 digits.
  PYTHONDONTWRITEBYTECODE=1 python tools/gen_vt_package.py <tracer dialin dir> > golden/vt_package.tsv
"""
import sys, os, hashlib, importlib.util
sys.dont_write_bytecode = True
D = os.path.abspath(sys.argv[1]); VT = os.path.join(D, "out_vt_tau_n_gf_z2_mu_consistent_dr2_completion")
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
spec = importlib.util.spec_from_file_location("vt_score", os.path.join(VT, "score.py"))
vt = importlib.util.module_from_spec(spec); sys.modules["vt_score"] = vt; spec.loader.exec_module(vt)
vq, vn = vt.vq, vt.vn
from mpmath import mp, mpf, nstr
mp.dps = 50
with mp.workdps(50):
    MZ = vn.MZ; cf = vq.c5_coeffs(MZ); Y = vq.Ydrho1(MZ); c6 = vq.c6_of(vq.G0)
    E = vn.vk_engine(); t_vk = vn.vk_tau(E)["t"]
    rows = [
        ("MW_GeV", vn.MW, "vn score.py:62 (leaf m_W_MeV/1000)"), ("MZ_GeV", vn.MZ, "leaf m_Z_MeV/1000"),
        ("alpha", vn.al, "1/leaf alpha_inv"), ("s2", vn.s2, "1-(MW/MZ)^2"), ("mt_GeV", vn.mt, "leaf m_t_over_m_W * MW"),
        ("mH_GeV", vn.mH, "leaf m_H_MeV/1000"), ("a_s_mt", vn.a_s, "alpha_s(m_t)/pi, tip AlphaS"),
        ("a_s_MZ", vt.A_SZ, "alpha_s(M_Z)/pi (C7 FKS rule)"), ("Delta_alpha", vn.da, "lep + had(0.02734356558) + top"),
        ("rem_tip", vn.rem_tip, "Z-2 one-loop remainder (P0)"), ("rem_C1", vq.RF_C1, "C1 full one-loop remainder"),
        ("rho2_tip", vq.RHO2_TIP, "Z-2 rho2(M_H/m_t) (P0)"), ("rho2_C2", vq.RHO2_C2, "C2 DFFGV eq.(15a) lead"),
        ("q1", mpf("2.8599"), "O(alpha alpha_s)"), ("q2", mpf("14.594"), "O(alpha alpha_s^2)"), ("q3_C3", mpf("-93.1501"), "C3 O(alpha alpha_s^3)"),
        ("C5_fh", cf["fh"], "C5 (e2/s2) fbar hat / x_t, mu=M_Z"), ("C5_fa", cf["fa"], "C5 fbar add / x_t"),
        ("C5_Ar", cf["Ar"], "C5 sub Drho_bar2 x_t^2 coeff"), ("C5_Aa", cf["Aa"], "C5 sub x_t k8 coeff"),
        ("C5mu_Y", Y, "T_conv Y = (e2/s2) Drho_bar^(1)(mu=M_Z)"), ("C6_B1", c6["B1"], "C6 B1"), ("C6_B2", c6["B2"], "C6 B2"),
        ("CF", vq.CF, "4/3"), ("NC", mpf(vq.NC), "3"), ("C7", vt.c7(), "C7 light-doublet O(alpha alpha_s), G-independent (P1 only)"),
        ("GF_Z2", vn.carried_GZ2(), "carried Z-2 G_F (tw.GF_Z2; audit/score_2026-10-02z.tsv:13)"),
        ("tau_vk_s", t_vk, "vk P1 engine tau_n (f_vk, dRV_us, dRp_va, r_2B; V_ud, g_A hosted, unchanged)"),
        ("vk_dRV_us", vn.vk_tau(E)["d"], "hook vw (Delta_R^V) input inside tau_vk"),
    ]
print(f"#vt_package\tscore.py_sha256={sha(os.path.join(VT,'score.py'))}\tDONE.md_sha256={sha(os.path.join(VT,'DONE.md'))}\tresults.tsv_sha256={sha(os.path.join(VT,'results.tsv'))}\truling_t992u_sha8=c65ff89d")
print("#key\tvalue_50\tmeaning")
for k, v, m in rows:
    print(f"{k}\t{nstr(v, 50)}\t{m}")
