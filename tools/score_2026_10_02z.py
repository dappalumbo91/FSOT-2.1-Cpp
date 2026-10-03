#!/usr/bin/env python3
"""Round-z scores under audit/FREEZE_2026-10-02z (committed first). z-only, dimensionless ratios; FSOT-only inputs.
Z-1 inertia trace (audit/itrace_2026-10-02z.jsonl); Z-2 higher-order Delta r -> G_F, Gamma_Z/M_Z.
  python tools/score_2026_10_02z.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02z.tsv
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
# ---------------- Z-1 inertia trace (diagnostic)
s = "Z-1"; tp = R_ / "audit/itrace_2026-10-02z.jsonl"
if tp.exists():
    for line in tp.read_text(encoding="utf-8").splitlines():
        d = json.loads(line); IM = mpf(d["I_M"])
        info(s, "I M at M/m_p %.6g, x %.6g, K %d" % (d["M_over_mp"], d["x"], d["K"]), "round-y inputs, M_PV/M %.6g" % d["M_over_mp"] if False else "round-y inputs", IM, "diagnostic",
             "val " + nstr(mpf(d["I_val_M"]), 6) + ", bare sea " + nstr(mpf(d["I_sea_M"]), 6) + ", PV " + nstr(mpf(d["I_pv_M"]), 6) + "; eps_val/M " + nstr(mpf(d["eps_val"]), 6) + "; Delta-N/m_p = 3(M/m_p)/(2 I M) = " + nstr(3 * mpf(d["M_over_mp"]) / (2 * IM), 6))
# ---------------- Y-2
s = "Z-2"; src = (R_ / "tools/score_2026_10_02i.py").read_text(encoding="utf-8").split("\n")
i0 = next(i for i, l in enumerate(src) if l.startswith("# ---- HAD-2: quark-hadron duality")); i1 = next(i for i, l in enumerate(src) if l.startswith("def f10"))
ns = {"math": math}; exec("\n".join(src[i0:i1]), ns); dalpha_had = ns["dalpha_had"]
def pole(m, AS): return m * (1 + 4 * AS(m) / (3 * math.pi))
def dah_pole(alpha, MZ, asMZ, mtau, mpi, mK, mc, mb):
    AS0 = ns["AlphaS"](asMZ, MZ, mb, mc, mtau)  # flavour switching at the MSbar masses for the pole conversion only
    mcp, mbp = pole(mc, AS0), pole(mb, AS0)
    d, AS = dalpha_had(alpha, MZ, asMZ, mtau, mpi, mK, mcp, mbp)
    return d, mcp, mbp
dv, mcpv, mbpv = dah_pole(1 / 137.035999177, 91.1880, 0.1180, 1.77693, 0.13957039, 0.493677, 1.2730, 4.183)
VAL = abs(dv - 0.02783) <= 0.00029
emitz("VALIDATION", "Z-2 (= Y-2) Delta alpha_had^(5), quark-pole thresholds, PDG inputs", "PDG m_c 1.2730, m_b 4.183, alpha_s 0.1180", float("%.10g" % dv), "0.02783", "0.00006", 0, "", "pole m_c %.5g, m_b %.5g GeV; round-i gate |dev| <= 0.00029: %s" % (mcpv, mbpv, "PASS" if VAL else "FAIL"))
MW, MZ, al = L["m_W_MeV"] / 1000, L["m_Z_MeV"] / 1000, 1 / L["alpha_inv"]; s2 = 1 - (MW / MZ) ** 2; c2 = 1 - s2
mt = L["m_t_over_m_W"] * MW; mb = mt / P["wave8|m_t/m_b"]; mc = L["m_c_over_m_b"] * mb; mH = L["m_H_MeV"] / 1000; als = 2 * (F.POOF / F.PSI_CON) ** 2; mtau = L["m_tau_MeV"] / 1000
dF, mcp, mbp = dah_pole(float(al), float(MZ), float(als), float(mtau), float(L["m_pi_pm_MeV"]) / 1000, float(L["m_K_pm_MeV"]) / 1000, float(mc), float(mb))
dh = mpf(float("%.10g" % dF))
info(s, "Delta alpha_had^(5) input (round-y quark-pole duality, FSOT)", "FSOT alpha, M_Z, alpha_s, m_tau, m_pi, m_K, m_c, m_b", dh, "FSOT · measured", "scored in round y (z 8.1); FSOT pole m_c %.5g, m_b %.5g GeV; validation %s" % (mcp, mbp, "passed" if VAL else "FAILED"))
z3 = zeta(3); ml = [X.kg_to_GeV(L["m_e_kg"]), X.kg_to_GeV(L["m_mu_kg"]), mtau]
da_lep = al / (3 * pi) * sum(ln(MZ**2 / m**2) - mpf(5) / 3 for m in ml) + (al / pi) ** 2 * sum(ln(MZ**2 / m**2) / 4 + z3 - mpf(5) / 24 for m in ml)
da_top = -(al / pi) * mpf(4) / 45 * MZ**2 / mt**2
rem = -(al / (16 * pi * s2)) * 4 * (c2 / s2 - mpf(1) / 3 - 3 * mb**2 / (s2 * MZ**2)) * ln(mt / MZ) + 11 * al / (24 * pi * s2) * ln(mH / MZ) + al / (4 * pi * s2) * (6 + (7 - 4 * s2) / (2 * s2) * ln(c2))

AS0 = ns["AlphaS"](float(als), float(MZ), float(mb), float(mc), float(mtau)); mbp_ = pole(float(mb), AS0); mcp_ = pole(float(mc), AS0)
ASt = ns["AlphaS"](float(als), float(MZ), mbp_, mcp_, float(mtau)); a_s = mpf(ASt(float(mt))) / pi
r = mH / mt
rho2 = 19 - mpf(33) / 2 * r + mpf(43) / 12 * r**2 + mpf(7) / 120 * r**3 - pi * sqrt(r) * (4 - mpf(3) / 2 * r + mpf(3) / 32 * r**2 + r**3 / 256) - pi**2 * (2 - 2 * r + r**2 / 2) - ln(r) * (3 * r - r**2 / 2)
q1 = 1 - mpf("2.8599") * a_s; q2 = q1 - mpf("14.594") * a_s**2
da = da_lep + dh + da_top
def solve(two_loop, qcd2, resum):
    GF = pi * al / (sqrt(2) * MW**2 * s2)
    for _ in range(300):
        xt = GF * mt**2 / (8 * sqrt(2) * pi**2); drho = 3 * xt * (1 + (xt * rho2 if two_loop else 0)) * (q2 if qcd2 else q1)
        omr = (1 - da) * (1 + c2 / s2 * drho) - rem if resum else 1 - (da - c2 / s2 * drho + rem)
        new = pi * al / (sqrt(2) * MW**2 * s2 * omr)
        if fabs(new - GF) / GF < mpf(10) ** -30: GF = new; break
        GF = new
    return GF, 1 - omr, drho
info(s, "inputs: alpha_s(m_t), r = M_H/m_t, rho2(r)", "FSOT seed, leaves", a_s * pi, "intermediate", "r " + nstr(r, 6) + "; rho2 " + nstr(rho2, 6) + "; Delta r_rem " + nstr(rem, 8) + "; Delta alpha " + nstr(da, 8))
for tag, args in (("one loop (alpha_s at m_t)", (False, False, False)), ("+ resummation", (False, False, True)), ("+ resummation + O(alpha alpha_s^2)", (False, True, True)), ("+ resummation + O(alpha alpha_s^2) + O(G_F^2 m_t^4)  [Z-2 primary]", (True, True, True))):
    GF_, dr_, drho_ = solve(*args)
    info(s, "Delta r, " + tag, "FSOT chain", dr_, "model-computed", "Delta rho " + nstr(drho_, 8) + "; G_F " + nstr(GF_, 10) + "; PDG SM Delta r 0.03685(20) for reference")
GFz, drz, _ = solve(True, True, True)
emitz(s, "Z-2 G_F (higher-order FSOT chain)", "FSOT only", GFz, *ref("G_F_GeVm2"), 0, "measured")
Rc = X.compute(hub, F, GF_override=GFz)
emitz(s, "Z-2 Gamma_Z/M_Z (authority A1 width, Z-2 G_F)", "FSOT only", Rc["GZ_over_MZ_A1"], *ref("Gamma_Z_over_M_Z"), 0, "measured", "record row changes only if z <= 1 with the Delta alpha_had validation passing (it does not: round y)")
# ---------------- Z-4 T_CMB direct route (information; post-freeze; uses the contested H0 pin)
from mpmath import mpf as _m
Or_, H0_, Ne_ = P["wave9|Omega_r"], P["wave1|H0"], P["wave2|N_eff"]
Og_ = Or_ / (1 + mpf(7) / 8 * (mpf(4) / 11) ** (mpf(4) / 3) * Ne_)
Gn, cc, hb, kB, Mpc = mpf("6.67430e-11"), mpf(299792458), mpf("1.054571817e-34"), mpf("1.380649e-23"), mpf("3.0856775814913673e22")
u_ = Og_ * 3 * (H0_ * 1000 / Mpc) ** 2 / (8 * pi * Gn) * cc**2; Tg = (15 * u_ * (hb * cc) ** 3 / (pi**2 * kB**4)) ** (mpf(1) / 4)
info("Z-4", "T_CMB from FSOT radiation density: Omega_gamma = Omega_r/(1 + (7/8)(4/11)^(4/3) N_eff), rho_gamma = Omega_gamma rho_c, T = (15 rho_gamma c^2 (hbar c)^3/(pi^2 k^4))^(1/4)", "FSOT Omega_r, N_eff, H0 (contested, deferred)", Tg, "information", "FIRAS 2.7255(6) K: " + nstr((Tg / mpf("2.7255") - 1) * 100, 4) + " %; not scored (post-freeze and depends on the deferred H0)")
rec("GATE", "record rows of the 91", "unchanged", "z-only")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02z.py under audit/FREEZE_2026-10-02z (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
