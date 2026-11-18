#!/usr/bin/env python3
"""Bank tracer §43.5vv route P3 (G_F) and §43.5vw route P3 (corrected Delta_R^V) for the C++ fold::vt hooks.

Read-only, like tools/gen_vt_package.py: imports the vw scorer (which imports vv -> vt -> vq/vn/vk read-only) with
bytecode writing off and NEVER calls score()/validate() (they write files). Hashes of every scorer / result file are
stamped in the header and asserted against the sha8 values in Tracer's FOLDs (vv f66b7985, vw ce51de78).
  - vv P3 (remainder unresummed, vv score.py solve_P3): the fixed point G = G0 [1/(1 - Dr_A(G)) + Dr_P1(G) - Dr_A(G)]
    is solved LIVE in C++ (fold::vt::Chain, Hooks::vv_p3) from the vt package coefficients; only reference outputs
    (G_chain, ratio, G_F, tau_n) are banked here, for the ~1e-12 reproduction test.
  - vw P3 (3-loop alpha_g1 BjSR interpolator, vw score.py make_route("P3")): the rebuilt tau_vk (vk_tau with
    dC = (d_route - d_eng)/(alpha/pi)) is banked as tau_vk_vwP3_s and enters through Hooks::tau_vk_override.
  PYTHONDONTWRITEBYTECODE=1 python tools/gen_vv_vw_package.py <tracer dialin dir> > golden/vv_vw_package.tsv
"""
import sys, os, hashlib, importlib.util
sys.dont_write_bytecode = True
D = os.path.abspath(sys.argv[1])
VV = os.path.join(D, "out_vv_tau_n_gf_dr_two_loop_remainder_completion")
VW = os.path.join(D, "out_vw_tau_n_drv_gamma_w_box_bjsr_interpolator")
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
EXPECT = {(VV, "score.py"): "74db1004", (VV, "results.tsv"): "2dc1e274", (VV, "DONE.md"): "56a8d211",
          (VW, "score.py"): "eb03ab5a", (VW, "results.tsv"): "69329adc", (VW, "DONE.md"): "2e4a2c39", (VW, "validate_run.txt"): "4c66f06d"}
for (d, f), h in EXPECT.items():
    assert sha(os.path.join(d, f))[:8] == h, f"{f} in {d} changed: {sha(os.path.join(d, f))[:8]} != {h}"
spec = importlib.util.spec_from_file_location("vw_score", os.path.join(VW, "score.py"))
vw = importlib.util.module_from_spec(spec); sys.modules["vw_score"] = vw; spec.loader.exec_module(vw)
vv, vn = vw.vv, vw.vn
from mpmath import mp, mpf, nstr
EN = vw.engine()                       # vv P3 engine (vv.build()), vk engine, d_eng, non-Born content
rows = []
with mp.workdps(50):
    R = EN["R"]; GZ2 = EN["GZ2"]
    for k in ("OFF", "A", "P1", "P3"):
        rows.append((f"vv_{k}_G_chain", R[k]["G"], f"vv score.py build() {k} fixed point (reference; C++ solves live)"))
    rows.append(("vv_P3_ratio", R["P3"]["ratio"], "G_P3/G_OFF (reference)"))
    rows.append(("vv_P3_GF", GZ2 * R["P3"]["ratio"], "vv P3 G_F = G_F,Z2 x ratio (reference; FOLD 1.16689392890418e-5)"))
    rows.append(("vv_P3_tau_n_s", EN["t_vk"] / R["P3"]["ratio"] ** 2, "vv P3 tau_n = tau_vk/ratio^2 (reference; FOLD 877.8657345)"))
with mp.workdps(30):
    rows.append(("vw_d_eng", EN["d"], "engine Delta_R^V (= vt package vk_dRV_us)"))
    rows.append(("vw_CnB", EN["CnB"], "engine non-Born box C_dis + C3pole (alpha/pi units)"))
    rows.append(("vw_C_dis", EN["cd"], "engine high-Q C_dis (one-loop, n_f=5 fixed alpha_s)"))
    rows.append(("vw_C3pole", EN["C3"], "engine low-Q 3-pole (C_INT_ug + Crem)"))
    rows.append(("vw_C_Born", EN["cb"], "engine Born"))
    for nm in ("P3", "P1", "P2"):
        r = vw.make_route(nm)
        d = vw.d_route(EN, r["I1"], r["I2"]); dC = (d - EN["d"]) / (vw.ALPHA / vw.MPI)
        tvk = vn.vk_tau(EN["E"], dC=dC)["t"]
        rows += [(f"vw_{nm}_Q0sq", mpf(r["Q0"]), f"vw {nm} Q0^2 by continuity [GeV^2]"),
                 (f"vw_{nm}_I1", mpf(r["I1"]), f"vw {nm} I1 (alpha/pi)"), (f"vw_{nm}_I2", mpf(r["I2"]), f"vw {nm} I2 (alpha/pi)"),
                 (f"vw_{nm}_dRV", d, f"vw {nm} corrected Delta_R^V = d_eng - (alpha/pi)(CnB - I1 - I2)"),
                 (f"tau_vk_vw{nm}_s", tvk, f"vk tau_n engine rebuilt with vw {nm} Delta_R^V (Hooks::tau_vk_override input)" + (" CARRIED" if nm == "P3" else " alternate")),
                 (f"vw_{nm}_tau_n_s", vw.tau_of(EN, d), f"vw {nm} tau_n on the vv P3 engine (reference; FOLD " + {"P3": "878.4325396", "P1": "878.5492161", "P2": "878.5971737"}[nm] + ")")]
print("#vv_vw_package\t" + "\t".join(f"{os.path.basename(d)[:6]}/{f}_sha256={sha(os.path.join(d, f))}" for (d, f) in EXPECT)
      + "\tvv_FOLD_sha8=f66b7985\tvw_FOLD_sha8=ce51de78\tvt_score.py_sha8=ebdda985")
print("#key\tvalue\tmeaning")
for k, v, m in rows:
    print(f"{k}\t{nstr(v, 50)}\t{m}")
