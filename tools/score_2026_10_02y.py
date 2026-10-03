#!/usr/bin/env python3
"""Round-y scores under audit/FREEZE_2026-10-02y (committed first). z-only, dimensionless ratios; FSOT-only inputs.
Y-1 soliton in proton units (audit/heavy_2026-10-02y_K*.json); Y-2 Gamma_Z/M_Z: round-f one-loop chain with the quark-pole duality Delta alpha_had.
  python tools/score_2026_10_02y.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02y.tsv
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
# ---------------- Y-1
s = "Y-1"; Hq = J("audit/heavy_2026-10-02q.json")
def raw(c, o):
    M_, MN = mpf(c["M_MeV"]), mpf(c["M_N_MeV"]); I = mpf(o["I_times_M"]); q_ = MN / M_
    return {"g1": mpf(o["A_im"]) / I, "muS": q_ * mpf(o["B_re"]) / (6 * I), "muV1": q_ * mpf(o["Amu_im"]) / I, "muV0": -q_ / 3 * (mpf(o["xat_val"]) + mpf(o["xat_sea"]))}
rs = raw(Hq["Q1_sanity_M420_F93"], Hq["Q1_sanity_M420_F93"]["DPP"]); SG = {k: (1 if rs[k] > 0 else -1) for k in ("g1", "muS", "muV1")}
runs = {}
for K in (12, 14):
    p = R_ / ("audit/heavy_2026-10-02y_K%d.json" % K)
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8")); c = d.get("Y1_pu_massive_K%d" % K, {})
        if "DPP" in c:
            o = c["DPP"]; r = raw(c, o); Mr = mpf(d["inputs"]["M_over_mp"]); I = mpf(o["I_times_M"]); muS = SG["muS"] * r["muS"]; muV = r["muV0"] + SG["muV1"] * r["muV1"]
            runs[K] = {"DNr": 3 * Mr / (2 * I), "gA": mpf(o["gA0"]) + SG["g1"] * r["g1"], "gA0": mpf(o["gA0"]), "mup": (muS + muV) / 2, "mun": (muS - muV) / 2, "IM": I, "E": mpf(o["E_sol_over_M"]), "eps": mpf(o["eps_val"]), "x": mpf(c["x_DPP"]), "edge": c["edge_minimum"], "Mr": Mr, "MpvM": mpf(d["inputs"]["Mpv_over_M"]), "FM": mpf(d["inputs"]["F_over_M"])}
for K, o in sorted(runs.items()):
    info(s, "soliton in proton units K %d: (M_Delta - M_N)/m_p" % K, "M/m_p %s, F/M %s, M_PV/M %s" % (nstr(o["Mr"], 7), nstr(o["FM"], 7), nstr(o["MpvM"], 7)), o["DNr"], "FSOT · measured",
         "I M " + nstr(o["IM"], 6) + "; E/M " + nstr(o["E"], 6) + "; eps_val/M " + nstr(o["eps"], 6) + "; g_A " + nstr(o["gA"], 6) + " (classical " + nstr(o["gA0"], 6) + "); mu_p " + nstr(o["mup"], 6) + ", mu_n " + nstr(o["mun"], 6) + " (not scored); x " + nstr(o["x"], 5) + (" EDGE" if o["edge"] else "") + "; MeV byproduct " + nstr(o["DNr"] * mpM, 6))
    info(s, "nucleon-condition estimate M/m_p = 1/(E/M + 3/(8 I M)) (information)", "same run", 1 / (o["E"] + mpf(3) / (8 * o["IM"])), "diagnostic", "compare the gap-equation input M/m_p " + nstr(o["Mr"], 7))
DNc = (mpf("1232") - (mpf("938.27208943") + mpf("939.56542194")) / 2) / mpf("938.27208943")
if runs:
    Kl = max(runs); both = 12 in runs and 14 in runs
    th = fabs(runs[14]["DNr"] - runs[12]["DNr"]) if both else 0; thg = fabs(runs[14]["gA"] - runs[12]["gA"]) if both else 0
    note = "theory unc. |K14 - K12|" if both else "K 12 only: no theory uncertainty (stated in the freeze)"
    emitz(s, "Y-1 (M_Delta - M_N)/m_p (K %d)" % Kl, "proton units, FSOT inputs", runs[Kl]["DNr"], DNc, mpf(2) / mpf("938.27208943"), th, "FSOT · measured", note)
    emitz(s, "Y-1 g_A time-ordered (K %d)" % Kl, "proton units, FSOT inputs", runs[Kl]["gA"], "1.2754", "0.0013", thg, "FSOT · measured", note)
else:
    rec(s, "soliton in proton units", "not run", "")
rec(s, "mu_p, mu_n", "not scored", "mu_V^(0) sea sum unconverged (round x)")
# ---------------- Y-2
s = "Y-2"; src = (R_ / "tools/score_2026_10_02i.py").read_text(encoding="utf-8").split("\n")
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
emitz("VALIDATION", "Y-2 Delta alpha_had^(5), quark-pole thresholds, PDG inputs", "PDG m_c 1.2730, m_b 4.183, alpha_s 0.1180", float("%.10g" % dv), "0.02783", "0.00006", 0, "", "pole m_c %.5g, m_b %.5g GeV; round-i gate |dev| <= 0.00029: %s" % (mcpv, mbpv, "PASS" if VAL else "FAIL"))
MW, MZ, al = L["m_W_MeV"] / 1000, L["m_Z_MeV"] / 1000, 1 / L["alpha_inv"]; s2 = 1 - (MW / MZ) ** 2; c2 = 1 - s2
mt = L["m_t_over_m_W"] * MW; mb = mt / P["wave8|m_t/m_b"]; mc = L["m_c_over_m_b"] * mb; mH = L["m_H_MeV"] / 1000; als = 2 * (F.POOF / F.PSI_CON) ** 2; mtau = L["m_tau_MeV"] / 1000
dF, mcp, mbp = dah_pole(float(al), float(MZ), float(als), float(mtau), float(L["m_pi_pm_MeV"]) / 1000, float(L["m_K_pm_MeV"]) / 1000, float(mc), float(mb))
dh = mpf(float("%.10g" % dF))
emitz(s, "Y-2 Delta alpha_had^(5) (duality, quark-pole thresholds, FSOT inputs)", "FSOT alpha, M_Z, alpha_s, m_tau, m_pi, m_K, m_c, m_b", dh, "0.02783", "0.00006", 0, "FSOT · measured", "FSOT pole m_c %.5g, m_b %.5g GeV; validation %s" % (mcp, mbp, "passed" if VAL else "FAILED"))
z3 = zeta(3); ml = [X.kg_to_GeV(L["m_e_kg"]), X.kg_to_GeV(L["m_mu_kg"]), mtau]
da_lep = al / (3 * pi) * sum(ln(MZ**2 / m**2) - mpf(5) / 3 for m in ml) + (al / pi) ** 2 * sum(ln(MZ**2 / m**2) / 4 + z3 - mpf(5) / 24 for m in ml)
da_top = -(al / pi) * mpf(4) / 45 * MZ**2 / mt**2
rem = -(al / (16 * pi * s2)) * 4 * (c2 / s2 - mpf(1) / 3 - 3 * mb**2 / (s2 * MZ**2)) * ln(mt / MZ) + 11 * al / (24 * pi * s2) * ln(mH / MZ) + al / (4 * pi * s2) * (6 + (7 - 4 * s2) / (2 * s2) * ln(c2))
qcd = 1 - mpf(2) / 3 * (1 + pi**2 / 3) * als / pi
GF = pi * al / (sqrt(2) * MW**2 * s2)
for it in range(200):
    drho = 3 * GF * mt**2 / (8 * sqrt(2) * pi**2) * qcd; da = da_lep + dh + da_top; dr = da - c2 / s2 * drho + rem
    new = pi * al / (sqrt(2) * MW**2 * s2 * (1 - dr))
    if fabs(new - GF) / GF < mpf(10) ** -30: GF = new; break
    GF = new
info(s, "Delta r (round-f one-loop chain, Y-2 Delta alpha_had)", "no fit coefficients", dr, "model-computed", "Delta alpha " + nstr(da, 8) + "; Delta rho " + nstr(drho, 8) + "; Delta r_rem " + nstr(rem, 8) + "; PDG SM Delta r 0.03685(20) for reference")
emitz(s, "Y-2 G_F (FSOT chain)", "round-f chain", GF, *ref("G_F_GeVm2"), 0, "measured")
Rc = X.compute(hub, F, GF_override=GF)
emitz(s, "Y-2 Gamma_Z/M_Z (authority A1 width, G_F from the FSOT chain)", "FSOT only", Rc["GZ_over_MZ_A1"], *ref("Gamma_Z_over_M_Z"), 0, "measured", "record row changes only if z <= 1 and validation passes (gate unchanged)")
rec(s, "round-i GZ-1 (Freitas/ACFW coefficients, m_B 5.279 GeV)", "moved to scaffolding", "hybrid under the standing rule; its z 0.68 is not an FSOT result")
rec("GATE", "record rows of the 91", "unchanged unless a Y-2 row passes with validation", "z-only")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02y.py under audit/FREEZE_2026-10-02y (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
