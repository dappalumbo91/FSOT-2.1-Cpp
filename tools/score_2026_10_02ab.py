#!/usr/bin/env python3
"""Round-ab scores under audit/FREEZE_2026-10-02ab (committed first). z-only, dimensionless ratios; FSOT-only inputs.
AB-1 instanton size from the DP variational minimum -> M/m_p -> soliton (audit/heavy_2026-10-02ab_K12.json); AB-2 deuteron trace step 1 (3S1 central OPE + sigma + omega, pure Python Numerov); AB-3 last-scattering information.
  python tools/score_2026_10_02ab.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02ab.tsv
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
# ---------------- AB-1
s = "AB-1"; GJ = J("audit/gap_2026-10-02ab.json"); Hq = J("audit/heavy_2026-10-02q.json")
info(s, "AB-1 rho_bar n^(1/4) (DP variational self-consistency, one loop)", "FSOT n (AA-1 reading), round-t Lambda^(0): n^(1/4)/Lambda_PV = 0.65", GJ["x_rho_n_quarter"], "FSOT · intermediate",
     "R/rho " + nstr(mpf(GJ["R_over_rho"]), 7) + " (DP model constant was 3); beta(rho_bar) " + nstr(mpf(GJ["beta_rho_bar"]), 5) + "; Lambda_PV rho_bar " + nstr(mpf(GJ["Lambda_PV_rho_bar"]), 5) + "; packing pi^2 n rho^4 " + nstr(mpf(GJ["packing_pi2_n_rho4"]), 4) + " (not dilute; beta ~ 5 is outside the semiclassical regime); two-loop variant: " + ("no solution" if GJ["info_two_loop_x"] is None else nstr(mpf(GJ["info_two_loop_x"]), 6)))
info(s, "AB-1 M/m_p (gap equation at rho = rho_bar)", "AB-1 rho_bar, AA-1 n", GJ["M_over_mp"], "FSOT · intermediate (scored via Delta-N, g_A)", "M0/n^(1/4) " + nstr(mpf(GJ["M0_over_n_quarter"]), 9) + "; round aa " + nstr(mpf(GJ["aa_M_over_mp"]), 9) + "; MeV byproduct " + nstr(mpf(GJ["M_over_mp"]) * mpM, 7))
def raw(c, o):
    I = mpf(o["I_times_M"]); return {"g1": mpf(o["A_im"]) / I}
SGg1 = 1 if raw(None, Hq["Q1_sanity_M420_F93"]["DPP"])["g1"] > 0 else -1
DNc = (mpf("1232") - (mpf("938.27208943") + mpf("939.56542194")) / 2) / mpf("938.27208943")
gA = None
if (R_ / "audit/heavy_2026-10-02ab_K12.json").exists() and "DPP" in J("audit/heavy_2026-10-02ab_K12.json").get("AB1_pu_massive_K12", {}):
    H = J("audit/heavy_2026-10-02ab_K12.json"); d = H["AB1_pu_massive_K12"]; o = d["DPP"]; Mr = mpf(H["inputs"]["M_over_mp"]); IM = mpf(o["I_times_M"])
    DN = 3 * Mr / (2 * IM); gA = mpf(o["gA0"]) + SGg1 * raw(d, o)["g1"]
    nt = "I M " + nstr(IM, 6) + "; E/M " + nstr(mpf(o["E_sol_over_M"]), 6) + "; eps_val/M " + nstr(mpf(o["eps_val"]), 6) + "; x_DPP " + nstr(mpf(d["x_DPP"]), 5) + (" EDGE" if d["edge_minimum"] else "") + "; K 12 only: no theory unc. (frozen)"
    emitz(s, "AB-1 (M_Delta - M_N)/m_p (K 12)", "proton units, FSOT inputs", DN, DNc, mpf(2) / mpf("938.27208943"), 0, "FSOT · measured", nt + "; MeV byproduct " + nstr(DN * mpM, 6))
    emitz(s, "AB-1 g_A time-ordered (K 12)", "proton units, FSOT inputs", gA, "1.2754", "0.0013", 0, "FSOT · measured", "classical " + nstr(mpf(o["gA0"]), 6) + "; round-y convention")
else:
    rec(s, "soliton at the AB-1 M/m_p", "not run", "")
if (R_ / "audit/heavy_2026-10-02ab_wide_K12.json").exists():
    Hw = J("audit/heavy_2026-10-02ab_wide_K12.json"); dw = Hw["AB1wide_info_K12"]; ow = dw["DPP"]; IMw = mpf(ow["I_times_M"]); Mw = mpf(Hw["inputs"]["M_over_mp"])
    info(s, "AB-1 post-freeze window 0.5-1.6 (information): (M_Delta - M_N)/m_p", "same inputs, wider DPP scan", 3 * Mw / (2 * IMw), "information (post-freeze, not scored)",
         "interior minimum x_DPP " + nstr(mpf(dw["x_DPP"]), 5) + "; I M " + nstr(IMw, 6) + "; z vs 0.31236 would be " + nstr(fabs(3 * Mw / (2 * IMw) - DNc) / (mpf(2) / mpf("938.27208943")), 4) + "; g_A " + nstr(mpf(ow["gA0"]) + SGg1 * mpf(ow["A_im"]) / IMw, 6) + "; eps_val/M " + nstr(mpf(ow["eps_val"]), 4) + "; scan kink between x 1.2 and 1.3")
# ---------------- AB-2 deuteron trace step 1 (pure Python, deterministic)
s = "AB-2"
def col(path, sec, key):
    for line in open(R_ / path, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) > 3 and f[0] == sec and f[1].startswith(key): return mpf(f[3])
Fr = float(col("audit/score_2026-10-02p.tsv", "FSOT", "P-4 F_pi with lbar4") / mpM); mpir = float(L["m_pi_pm_MeV"] / mpM); Mq = float(GJ["M_over_mp"]); mnr = float(L["m_n_over_m_p"])
mu = mnr / (1 + mnr)
def bound(terms, h=0.01, rmax=160.0):
    N = int(rmax / h)
    def shoot(E):
        k = lambda r: 2 * mu * (sum(c * math.exp(-m * r) / r for c, m in terms) - E)
        u0, u1 = 0.0, h; k0, k1 = 0.0, k(h); nodes = 0
        for i in range(1, N):
            r2 = (i + 1) * h; k2 = k(r2)
            u2 = (2 * u1 * (1 + 5 * h * h * k1 / 12) - u0 * (1 - h * h * k0 / 12)) / (1 - h * h * k2 / 12)
            if u2 * u1 < 0: nodes += 1
            u0, u1, k0, k1 = u1, u2, k1, k2
            if abs(u1) > 1e250: u0 /= 1e250; u1 /= 1e250
        return nodes, u1
    n0, _ = shoot(-1e-12)
    if n0 == 0: return None
    lo, hi = -0.05, -1e-12   # deepest-level search window (-47 MeV, 0)
    if shoot(lo)[0] >= n0: return "deeper than the window"
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if shoot(mid)[0] >= n0: hi = mid
        else: lo = mid
    return -0.5 * (lo + hi)
if gA is not None:
    fpi2 = float(gA)**2 * mpir**2 / (16 * math.pi * Fr**2)              # f^2/4pi, Goldberger-Treiman
    gs2 = (3 * Mq / Fr)**2 / (4 * math.pi); ms = 2 * Mq
    gw2 = (6 * math.pi)**2 / (4 * math.pi); mw = 2 * math.sqrt(2) * math.pi * Fr
    info(s, "inputs: f^2/4pi (OPE), g_sigma^2/4pi, g_omega^2/4pi", "AB-1 g_A, M; FSOT P-4 F_pi, m_pi", fpi2, "model-computed", "g_sigma^2/4pi %.5g at m_sigma/m_p %.5g; g_omega^2/4pi %.5g at m_omega/m_p %.5g" % (gs2, ms, gw2, mw))
    steps = [("(a) OPE central", [(-fpi2, mpir)]), ("(b) + sigma", [(-fpi2, mpir), (-gs2, ms)]), ("(c) + sigma + omega", [(-fpi2, mpir), (-gs2, ms), (gw2, mw)])]
    Bc = None
    for tag, tl in steps:
        B = bound(tl)
        if isinstance(B, float):
            info(s, "deuteron 3S1 central " + tag + ": B_d/m_p", "point Yukawas", B, "model-computed", "MeV byproduct " + nstr(mpf(B) * mpM, 6))
        else:
            rec(s, "deuteron 3S1 central " + tag, "unbound" if B is None else str(B), "no bound state with E in (-0.05 m_p, 0)" if B is None else "")
        if tag.startswith("(c)"): Bc = B
    Bref = ref("B_H2_MeV")
    if isinstance(Bc, float):
        emitz(s, "AB-2 B_d/m_p (step (c))", "FSOT only", Bc, mpf(Bref[0]) / mpM, mpf(Bref[1]) / mpM, 0, "FSOT · measured")
    else:
        rec(s, "AB-2 B_d/m_p (step (c))", "miss (unbound)" if Bc is None else "miss", "measured " + nstr(mpf(Bref[0]), 9) + " MeV; the record row (pin z 3.59) is unchanged")
else:
    rec(s, "deuteron trace", "not run", "needs the AB-1 g_A")
rec(s, "mu_d", "not traced", "needs P_D from the tensor force (step 2)")
# ---------------- AB-3 (information)
from mpmath import findroot
al = 1 / L["alpha_inv"]; eta = P["wave10|eta_baryon_photon"]; z3_ = zeta(3); me = X.kg_to_GeV(L["m_e_kg"]) * 10**9
def saha(u, x=mpf("0.1")):
    t = u * al**2; return ln(x**2 / (1 - x)) - (ln(pi**2 / (2 * z3_ * eta)) + mpf(3) / 2 * ln(1 / (2 * pi * t)) - 1 / (2 * u))
u = findroot(saha, (mpf("0.005"), mpf("0.03")), solver="anderson"); kB_eV = mpf("8.617333262e-5")
info("AB-3", "kT/(m_e alpha^2) at Saha x_e = 0.1, hydrogen only (H0-free local quantity)", "FSOT eta, alpha", u, "model-computed", "T = " + nstr(u * me * al**2 / kB_eV, 6) + " K (byproduct via m_e); T_CMB not derivable: H(T) needs rho_m/rho_b (no FSOT pin) and 1 + z_* = T_ls/T_0 needs T_0")
rec("GATE", "record rows of the 91", "unchanged", "z-only")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02ab.py under audit/FREEZE_2026-10-02ab (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
