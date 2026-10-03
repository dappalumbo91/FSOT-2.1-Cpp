#!/usr/bin/env python3
"""Round-x scores under audit/FREEZE_2026-10-02x (committed first). z-only scoring against observations; FSOT-only inputs.
X-1 energy-cutoff sea sum (audit/ecut_2026-10-02x.jsonl); X-2 DP gap-equation M(0) and the soliton at M(0) (audit/gap_2026-10-02x.json from tools/gap_2026_10_02x.py, audit/heavy_2026-10-02x_K*.json);
X-3 Gamma_Z/M_Z step trace (round-i GZ-1 chain, sensitivity to the Delta alpha_had step).
  python tools/score_2026_10_02x.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02x.tsv
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, sqrt, pi, ln, fabs, nstr
from mpmath import zeta
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves(); P = X.pins(); R = Path(__file__).resolve().parents[1]; ref = X.refs()
rows = []
def emitz(sec, name, inputs, v, c, s, th=0, cls="", note=""):
    v, c, s, th = mpf(v), mpf(c), mpf(s), mpf(th); sig = sqrt(s**2 + th**2); z = fabs(v - c) / sig
    rows.append([sec, name, inputs, nstr(v, 12), nstr(c, 10), nstr(sig, 4), nstr(z, 5), "agrees" if z <= 1 else "miss", nstr((v - c) / c * 100, 5) + " %", cls, note]); return z
def info(sec, name, inputs, v, cls="", note=""): rows.append([sec, name, inputs, nstr(mpf(v), 12), "-", "-", "-", "info", "-", cls, note])
def rec(sec, name, verdict, note): rows.append([sec, name, "-", "-", "-", "-", "-", verdict, "-", "-", note])
def col(path, sec, key):
    for line in open(R / path, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) > 3 and f[0] == sec and f[1].startswith(key): return mpf(f[3])
J = lambda f: json.loads((R / f).read_text(encoding="utf-8"))
mp_ = X.kg_to_GeV(L["m_p_kg"]) * 1000
# ---------------- X-2 gap equation
s = "X-2"
GJ = J("audit/gap_2026-10-02x.json"); dpv = mpf(GJ["validation_DP_M0_MeV"])
emitz("VALIDATION", "X-2 DP gap equation with DP 1986 inputs n = (200 MeV)^4, rho = 1/600 MeV", "information", dpv, "345", str(0.03 * 345), 0, "", "freeze: must agree with 345 MeV within 3 %")
n4 = col("audit/score_2026-10-02t.tsv", "T-1", "T-1 chi^1/4 = n^(1/4)"); M0 = mpf(GJ["FSOT_M0_MeV"]); assert fabs(mpf(GJ["FSOT_n_quarter_MeV"]) - n4) < mpf("1e-6")
info(s, "X-2 M(0) = dynamical quark mass at zero momentum (DP gap equation, FSOT n, rho = R/3)", "n^(1/4) = " + nstr(n4, 9) + " MeV (round t pin route)", M0, "FSOT · intermediate (scored via Delta-N, g_A)", "versus m_p/3 = " + nstr(mp_ / 3, 8) + " MeV used so far")
Hq = J("audit/heavy_2026-10-02q.json")
def raw(c, o):
    M_, MN = mpf(c["M_MeV"]), mpf(c["M_N_MeV"]); I = mpf(o["I_times_M"]); q_ = MN / M_
    return {"g1": mpf(o["A_im"]) / I, "muS": q_ * mpf(o["B_re"]) / (6 * I), "muV1": q_ * mpf(o["Amu_im"]) / I, "muV0": -q_ / 3 * (mpf(o["xat_val"]) + mpf(o["xat_sea"]))}
rs = raw(Hq["Q1_sanity_M420_F93"], Hq["Q1_sanity_M420_F93"]["DPP"]); SG = {k: (1 if rs[k] > 0 else -1) for k in ("g1", "muS", "muV1")}
def obs(c):
    o = c["DPP"]; r = raw(c, o); M_ = mpf(c["M_MeV"]); I = mpf(o["I_times_M"]); g0 = mpf(o["gA0"]); muS = SG["muS"] * r["muS"]; muV = r["muV0"] + SG["muV1"] * r["muV1"]
    return {"gA": g0 + SG["g1"] * r["g1"], "gA0": g0, "mup": (muS + muV) / 2, "mun": (muS - muV) / 2, "DN": 3 * M_ / (2 * I), "IM": I, "x": mpf(c["x_DPP"]), "edge": c["edge_minimum"], "eps": mpf(o["eps_val"])}
runs = {}
for K in (12, 14):
    p = R / ("audit/heavy_2026-10-02x_K%d.json" % K)
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8")).get("X2_M0_massive_K%d" % K, {})
        if "DPP" in d: runs[K] = obs(d)
for K, o in sorted(runs.items()):
    info(s, "soliton at M(0), K %d: Delta-N (MeV)" % K, "massive DPP, M = M(0)", o["DN"], "FSOT · measured", "I M " + nstr(o["IM"], 6) + "; eps_val/M " + nstr(o["eps"], 6) + "; g_A " + nstr(o["gA"], 6) + " (classical " + nstr(o["gA0"], 6) + "); mu_p " + nstr(o["mup"], 6) + ", mu_n " + nstr(o["mun"], 6) + " (mu not scored: sea sum unconverged); x " + nstr(o["x"], 5) + (" EDGE" if o["edge"] else ""))
DNc = mpf("1232") - (mpf("938.27208943") + mpf("939.56542194")) / 2
if runs:
    Kl = max(runs); th = fabs(runs[14]["DN"] - runs[12]["DN"]) if (12 in runs and 14 in runs) else 0; thg = fabs(runs[14]["gA"] - runs[12]["gA"]) if (12 in runs and 14 in runs) else 0
    note = "theory unc. |K14 - K12|" if th else "K 12 only: no theory uncertainty (stated in the freeze)"
    emitz(s, "X-2 M_Delta - M_N at M(0) (K %d)" % Kl, "FSOT M(0)", runs[Kl]["DN"], DNc, "2", th, "FSOT · measured", note)
    emitz(s, "X-2 g_A (time-ordered) at M(0) (K %d)" % Kl, "FSOT M(0)", runs[Kl]["gA"], "1.2754", "0.0013", thg, "FSOT · measured", note)
else:
    rec(s, "soliton at M(0)", "not run", "")
# ---------------- X-1 energy cutoff
s = "X-1"; ep = R / "audit/ecut_2026-10-02x.jsonl"; Sx = {}
if ep.exists():
    for line in ep.read_text(encoding="utf-8").splitlines():
        d = json.loads(line); Sx[d["K"]] = d["xat_sea"]
        info(s, "cut sea sum, D = k = K = %d, E_c = %g M (x 0.8)" % (d["K"], d["E_c_over_M"]), "fixed DPP profile", d["xat_sea"], "diagnostic", "eps_val " + nstr(mpf(d["eps_val"]), 8) + "; I M " + nstr(mpf(d["I_M"]), 8) + " (round w: K 12 0.6299654 / 2.57195)")
conv = 16 in Sx and 14 in Sx and 12 in Sx and abs(Sx[16] - Sx[14]) < 0.01 * abs(Sx[16]) and (Sx[12] - Sx[14]) * (Sx[14] - Sx[16]) > 0
rec(s, "convergence criterion (freeze X-1)", "converged" if conv else "not established", "K values run: " + ", ".join(str(k) for k in sorted(Sx)) + "; mu_p, mu_n " + ("rescored" if conv else "not rescored"))
# ---------------- X-3 Gamma_Z/M_Z trace
s = "X-3"; src = (R / "tools/score_2026_10_02i.py").read_text(encoding="utf-8").split("\n")
i0 = next(i for i, l in enumerate(src) if l.startswith("# ---- GZ-1 building blocks")); i1 = next(i for i, l in enumerate(src) if l.startswith("# ---- (1) validations"))
ns = {"mpf": mpf, "sqrt": sqrt, "pi": pi, "ln": ln, "fabs": fabs, "z3": zeta(3)}; exec("\n".join(src[i0:i1]), ns)
MZ, MW, al = L["m_Z_MeV"] / 1000, L["m_W_MeV"] / 1000, 1 / L["alpha_inv"]
mt = L["m_t_over_m_W"] * MW; MH = L["m_H_MeV"] / 1000; als = 2 * (F.POOF / F.PSI_CON) ** 2; mtau = L["m_tau_MeV"] / 1000
dl = ns["dalep"](al, MZ, [X.kg_to_GeV(L["m_e_kg"]), X.kg_to_GeV(L["m_mu_kg"]), mtau]); ds = ns["d_s"](L["sin2_theta_W_MSbar"], als); s2leaf = 1 - (MW / MZ) ** 2
def chain(dh):
    dal = dl + dh; dr, MWfit = ns["delta_r"](MH, mt, MZ, dal, als); GZ = ns["GZ_ACFW"]
    for _ in range(30):
        G = ns["gf_from"](al, MW, MZ, dr, als, GZ); GZfit = ns["gz_freitas"](MH, mt, MZ, dal, als); dS2 = s2leaf - (1 - (MWfit / MZ) ** 2)
        new = GZfit * (G / ns["G_FR"]) * (1 + ds * dS2)
        if fabs(new - GZ) < mpf(10) ** -15: GZ = new; break
        GZ = new
    return GZ / MZ, G, dr, GZfit
c, sg = ref("Gamma_Z_over_M_Z")
emitz(s, "step 1: record pin phi^5/e^6 (bare, no physics)", "pin", P["wave5|Gamma_Z/M_Z"], c, sg, 0, "measured", "the record row; a closed form without a physics route")
dhF = col("audit/score_2026-10-02i.tsv", "HAD-2", "Delta alpha_had^(5) (duality, FSOT inputs")
emitz(s, "step 2: Delta alpha_had^(5) (HAD-2 duality, FSOT inputs; m_B external)", "round i", dhF, "0.02783", "0.00006", 0, "measured (dispersive e+e- data)", "first step that diverges: the light-quark resonance region; HAD-2 validation with PDG inputs also fails (z 18.4)")
gF, GF, drF, _ = chain(dhF); gP, GP, drP, _ = chain(mpf("0.02783"))
info(s, "step 3: Delta r (ACFW, with step 2)", "round-i chain", drF, "model-computed", "with the measured Delta alpha_had: " + nstr(drP, 8))
emitz(s, "step 4: G_F (with step 2)", "round-i chain", GF, *ref("G_F_GeVm2"), 0, "measured", "with the measured Delta alpha_had: " + nstr(GP, 10))
emitz(s, "step 5: Gamma_Z/M_Z physics route (with step 2)", "round-i GZ-1 chain", gF, c, sg, 0, "measured", "reproduces round i")
info(s, "sensitivity: Gamma_Z/M_Z shift from replacing step 2 by the measured Delta alpha_had (in units of the Gamma_Z/M_Z sigma)", "chain(0.02783) - chain(HAD-2)", (gP - gF) / sg, "diagnostic",
     "Gamma_Z/M_Z with measured Delta alpha_had = " + nstr(gP, 10) + " (information only, not FSOT)")
rec(s, "external items in the physics route", "flag for owner", "m_B = 5.27941 GeV threshold (HAD-2); Freitas and ACFW SM parametrisation coefficients (theory, not data); record row stays open")
rec("GATE", "record rows of the 91", "unchanged", "z-only; no record row recomputed")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02x.py under audit/FREEZE_2026-10-02x (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
