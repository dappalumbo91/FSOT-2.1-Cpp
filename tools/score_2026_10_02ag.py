#!/usr/bin/env python3
"""Round-ag scores under audit/FREEZE_2026-10-02ag (committed first). z-only, dimensionless ratios; FSOT-only inputs.
AG-1 eta provenance (info); AG-2 soliton with box size D and cutoff kmax decoupled from K (audit/murun_2026-10-02ae_K12.json, audit/murun_2026-10-02ag_*.json); AG-3 deuteron omega piece breakdown and the topological-radius omega vertex.
  python tools/score_2026_10_02ag.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02ag.tsv
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
# ---------------- AD-1
s = "AD-1"; Hq = J("audit/heavy_2026-10-02q.json"); GT = J("audit/gatrace_2026-10-02ad.json")
SGg1 = 1 if mpf(Hq["Q1_sanity_M420_F93"]["DPP"]["A_im"]) > 0 else -1
DNc = (mpf("1232") - (mpf("938.27208943") + mpf("939.56542194")) / 2) / mpf("938.27208943")
Hw = J("audit/heavy_2026-10-02ab_wide_K12.json"); dw = Hw["AB1wide_info_K12"]; ow = dw["DPP"]; IM = mpf(GT["I_times_M"]); Mr = mpf(Hw["inputs"]["M_over_mp"]); xD = float(dw["x_DPP"])
q = (1 / mpf(GT["Mpv_over_M"])) ** 2
Areg = mpf(GT["A_val_im"]) + (mpf(GT["A_sea_im"]) - q * mpf(GT["A_pv_im"])) - (mpf(GT["A_vac_im"]) - q * mpf(GT["A_vacpv_im"]))
gA0 = mpf(ow["gA0"]); g1 = SGg1 * Areg / IM; gA = gA0 + g1
info(s, "AD-1 g_A input for AG-3 (round ad, K 12)", "round ad", gA, "FSOT · input", "")
# ---------------- AF-1 (diagnostic; conditional tail)
# ---------------- AG-1 (provenance; information only)
s = "AG-1"
info(s, "AG-1 FSOT eta (wave10) = Poof^11/(pi gamma)", "hub vendor/fsot_compute.py wave10 (pure constants pi, e, phi, gamma)", P["wave10|eta_baryon_photon"], "provenance", "no T_CMB, n_gamma or temperature enters; omega_b (wave1) = |S_cosm|(1 - S_chem) also has none (S_cosm is shared with the T_CMB pin formula, which the round-af route does not use)")
rec(s, "AG-1 round-af T_CMB route", "FSOT derivation (not circular)", "proposed record route for the hub (record rows change only through the hub); caveat: the observed eta used as eta's reference value is itself inferred with T_CMB^3 (target choice, not an input)")
# ---------------- AG-2 soliton box/cutoff decoupling
s = "AG-2"
def regx(sp, comp, IDX, sp_in):
    q_ = (1 / mpf(sp_in["Mpv_over_M"])) ** 2
    d_ = sp[comp]; tot, sea, pv, va, vb = [mpf(d_[k][IDX]) for k in ("tot", "sea", "pv", "vac", "vacpv")]
    return (tot - sea) + (sea - q_ * pv) - (va - q_ * vb)
SGq = {}
rq = Hq["Q1_sanity_M420_F93"]; oq = rq["DPP"]; Iq = mpf(oq["I_times_M"]); qq = mpf(rq["M_N_MeV"]) / mpf(rq["M_MeV"])
SGq["g1"] = 1 if mpf(oq["A_im"]) / Iq > 0 else -1; SGq["muS"] = 1 if qq * mpf(oq["B_re"]) / (6 * Iq) > 0 else -1; SGq["muV1"] = 1 if qq * mpf(oq["Amu_im"]) / Iq > 0 else -1
PTS = {"P1": ("audit/murun_2026-10-02ae_K12.json", "K 12, D 12, kmax 12 (round ae run, reused)"), "P2": ("audit/murun_2026-10-02ag_K12_D14_k12.json", "K 12, D 14, kmax 12"), "P3": ("audit/murun_2026-10-02ag_K14_D14_k12.json", "K 14, D 14, kmax 12")}
KR = {}
for nm, (pth, lab) in PTS.items():
    if not (R_ / pth).exists(): continue
    m_ = J(pth); sp_in = m_["inputs"]; o_ = m_["DPP"]; sp = m_["split"]; I_ = mpf(o_["I_times_M"]); Mr_ = mpf(sp_in["M_over_mp"]); qN = 1 / Mr_
    Ar = regx(sp, "A", 1, sp_in); Amr = regx(sp, "Amu", 1, sp_in); Br = regx(sp, "B", 0, sp_in)
    muS = SGq["muS"] * qN * Br / (6 * I_); mV0 = -qN / 3 * (mpf(o_["xat_val"]) + mpf(o_["xat_sea"])); muV = mV0 + SGq["muV1"] * qN * Amr / I_
    KR[nm] = {"mu_p": (muS + muV) / 2, "mu_n": (muS - muV) / 2, "g_A": mpf(o_["gA0"]) + SGq["g1"] * Ar / I_, "DN": 3 * Mr_ / (2 * I_)}
    info(s, "AG-2 %s (%s): g_A" % (nm, lab), "M/m_p 0.458168, window 0.5-1.6", KR[nm]["g_A"], "FSOT · grid point",
         "Delta-N/m_p %s; mu_p %s, mu_n %s; mu_V^(0) %s (xat_sea %s); x_DPP %s%s; I M %s; %s s" % (nstr(KR[nm]["DN"], 6), nstr(KR[nm]["mu_p"], 6), nstr(KR[nm]["mu_n"], 6), nstr(mV0, 6), nstr(mpf(o_["xat_sea"]), 6), nstr(mpf(m_["x_DPP"]), 5), " EDGE" if m_["edge_minimum"] else "", nstr(I_, 6), m_.get("seconds", "-")))
CEN = {"mu_p": ("2.79284734463", "0.00000001"), "mu_n": ("-1.91304276", "0.00000045"), "g_A": ("1.2754", "0.0013"), "DN": (DNc, mpf(2) / mpf("938.27208943"))}
if all(k in KR for k in ("P1", "P2", "P3")):
    for x_ in ("mu_p", "mu_n", "g_A", "DN"):
        dK = KR["P3"][x_] - KR["P2"][x_]; dD = KR["P2"][x_] - KR["P1"][x_]; tol = mpf("0.02") * fabs(KR["P3"][x_])
        nm_ = {"DN": "(M_Delta - M_N)/m_N"}.get(x_, x_)
        if fabs(dK) <= tol and fabs(dD) <= tol:
            emitz(s, "AG-2 %s (P3: K 14, D 14, kmax 12)" % nm_, "FSOT inputs", KR["P3"][x_], CEN[x_][0], CEN[x_][1], max(fabs(dK), fabs(dD)), "FSOT · measured", "converged both directions: K step %s, box step %s (2 %% of value %s)" % (nstr(dK, 4), nstr(dD, 4), nstr(tol, 4)))
        else:
            rec(s, "AG-2 %s" % nm_, "not scored", "K step (D 14) %s (%s %%), box step (K 12) %s (%s %%); 2 %% rule fails" % (nstr(dK, 4), nstr(dK / KR["P3"][x_] * 100, 3), nstr(dD, 4), nstr(dD / KR["P3"][x_] * 100, 3)))
    if (R_ / "audit/murun_2026-10-02ae_K14.json").exists():  # post-freeze cross-check (disclosed; information only): kmax 12 -> 14 at K 14, D 14
        m_ = J("audit/murun_2026-10-02ae_K14.json"); sp_in = m_["inputs"]; o_ = m_["DPP"]; sp = m_["split"]; I_ = mpf(o_["I_times_M"]); qN = 1 / mpf(sp_in["M_over_mp"])
        muS = SGq["muS"] * qN * regx(sp, "B", 0, sp_in) / (6 * I_); muV = -qN / 3 * (mpf(o_["xat_val"]) + mpf(o_["xat_sea"])) + SGq["muV1"] * qN * regx(sp, "Amu", 1, sp_in) / I_
        k4 = {"mu_p": (muS + muV) / 2, "mu_n": (muS - muV) / 2, "g_A": mpf(o_["gA0"]) + SGq["g1"] * regx(sp, "A", 1, sp_in) / I_, "DN": 3 * mpf(sp_in["M_over_mp"]) / (2 * I_)}
        info(s, "AG-2 post-freeze cross-check: kmax 12 -> 14 at K 14, D 14 (round-ae K 14 run): mu_p change", "audit/murun_2026-10-02ae_K14.json vs P3", k4["mu_p"] - KR["P3"]["mu_p"], "diagnostic (not in the freeze)",
             "relative changes: " + ", ".join("%s %s %%" % (x_, nstr((k4[x_] - KR["P3"][x_]) / KR["P3"][x_] * 100, 3)) for x_ in ("mu_p", "mu_n", "g_A", "DN")) + "; the 2 % rule in the cutoff direction would fail for mu_p, mu_n")
else:
    rec(s, "AG-2 grid", "incomplete", "points present: " + ", ".join(sorted(KR)))
# ---------------- AF-2 deuteron (pure Python, deterministic)
s = "AG-3"
def col(path, sec, key):
    for line in open(R_ / path, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if len(f) > 3 and f[0] == sec and f[1].startswith(key): return mpf(f[3])
mq = float(Hw["inputs"]["mpi_over_mp"]) / float(Mr)
def thf(r): return -2 * math.atan(xD * xD / (r * r) * (1 + mq * r) * math.exp(-mq * r))
def rB2():  # topological baryon density B = -(1/(2 pi^2)) sin^2(theta) theta'/r^2 (units 1/M), Simpson
    n = 60000; a, b = 1e-4, 60.0; h = (b - a) / n; num = den = 0.0
    for i in range(n + 1):
        r = a + i * h; d = (thf(r * (1 + 1e-6)) - thf(r * (1 - 1e-6))) / (2e-6 * r); Bd = abs(math.sin(thf(r))**2 * d / (2 * math.pi**2 * r * r))
        w = 1 if i in (0, n) else (4 if i % 2 else 2); num += w * 4 * math.pi * r**4 * Bd; den += w * 4 * math.pi * r**2 * Bd
    return num / den, den * h / 3
r2t, Bnorm = rB2(); rB = math.sqrt(r2t) / float(Mr); Lam = math.sqrt(6) / rB
Fr = float(col("audit/score_2026-10-02p.tsv", "FSOT", "P-4 F_pi with lbar4") / mpM); mpir = float(L["m_pi_pm_MeV"] / mpM); Mq = float(Mr); mnr = float(L["m_n_over_m_p"]); mu = mnr / (1 + mnr)
fpi2 = float(gA)**2 * mpir**2 / (16 * math.pi * Fr**2); Sv = GT["S_val"]; gs2 = (3 * Sv * Mq / Fr)**2 / (4 * math.pi); rS = math.sqrt(GT["rS2_valence_M"]) / Mq; LamS = math.sqrt(6) / rS; rV = math.sqrt(GT["rV2_valence_M"]) / Mq; LamV = math.sqrt(6) / rV; ms = 2 * Mq; gw2 = (6 * math.pi)**2 / (4 * math.pi); mw = 2 * math.sqrt(2) * math.pi * Fr
info(s, "AG-3 Lambda_B/m_p = sqrt6/r_B (topological baryon rms radius; pion vertex)", "AC-2 profile x_DPP, M/m_p", Lam, "FSOT · intermediate", "r_B m_p %.6g (%.4g fm byproduct); baryon number check %.6f; f^2/4pi %.5g, g_sigma^2/4pi %.5g (m %.4g), g_omega^2/4pi %.5g (m %.4g)" % (rB, rB * 197.3269804 / float(mpM), Bnorm, fpi2, gs2, ms, gw2, mw))
info(s, "AG-3 g_sigmaNN^2/4pi = (3 S_val M/F_pi)^2/4pi (soliton valence scalar charge)", "AD-1 soliton", gs2, "FSOT · intermediate", "S_val %.6g (quark counting had 1); Lambda_S/m_p = sqrt6/r_S = %.6g (r_S m_p %.5g); omega 6 pi unchanged (baryon number 1)" % (Sv, LamS, rS))
muSq = None
for line in open(R_ / "audit/score_2026-10-02q_late.tsv", encoding="utf-8"):
    f_ = line.rstrip("\n").split("\t")
    if len(f_) > 3 and f_[0] == "FSOT" and f_[1].startswith("Q-1 mu_p"): muSq = (muSq or 0) + mpf(f_[3])
    if len(f_) > 3 and f_[0] == "FSOT" and f_[1].startswith("Q-1 mu_n"): muSq = (muSq or 0) + mpf(f_[3])
info(s, "AG-3 Lambda_V/m_p = sqrt6/r_V (soliton valence Dirac radius; omega vertex)", "AD-1 soliton (K 12)", LamV, "FSOT · intermediate", "r_V m_p %.5g (%.4g fm byproduct); kappa_omega = mu_S - 1 = %s (enters the omega tensor and spin-orbit potentials, Bryan-Scott O(1/M^2))" % (rV, rV * 197.3269804 / float(mpM), nstr(muSq - 1, 5)))
def Gf(m, r, Lam=Lam):  # FT of Lam^4/((q^2+m^2)(q^2+Lam^2)^2) x 4 pi; returns G, lap G, (G'' - G'/r)
    K = Lam**2 / (Lam**2 - m**2); em, eL = math.exp(-m * r), math.exp(-Lam * r)
    G = K * K * (em - eL) / r - K * Lam * eL / 2
    lap = K * K * (m * m * em - Lam * Lam * eL) / r - K * Lam / 2 * (Lam * Lam - 2 * Lam / r) * eL
    T = K * K * (em * (m * m / r + 3 * m / r**2 + 3 / r**3) - eL * (Lam * Lam / r + 3 * Lam / r**2 + 3 / r**3)) - K * Lam / 2 * (Lam * Lam + Lam / r) * eL
    dG = K * K * ((-m * em + Lam * eL) / r - (em - eL) / r**2) + K * Lam * Lam * eL / 2
    return G, lap, T, -dG / r
kap = float(muSq - 1)
def wpots(r, LW):  # omega pieces only: central (Yukawa + sigma.sigma lapG), tensor, spin-orbit
    Gw, lpw, Tw, Z1w = Gf(mw, r, LW)
    return gw2 * (Gw * (1 + mw * mw / 2) + (1 + kap)**2 / 6 * lpw), -gw2 * (1 + kap)**2 / 12 * Tw, -gw2 * (3 + 4 * kap) / 2 * Z1w
def pots(r, ws=1.0, wc=1.0, wl=1.0, wt=1.0, LW=None):
    _, lp, Tp, _ = Gf(mpir, r); Gs, lps, Ts, Z1s = Gf(ms, r, LamS); c_, t_, l_ = wpots(r, LamV if LW is None else LW)
    Vc = -fpi2 * lp / mpir**2 - ws * gs2 * Gs * (1 - ms * ms / 4) + wc * c_
    Vt = -fpi2 * Tp / mpir**2 + wt * t_
    Vls = -ws * gs2 * Z1s / 2 + wl * l_
    return Vc, Vt, Vls
h, RM = 0.01, 150.0; NS = int(RM / h); r0 = 1e-3
def mkPT(**kw): return [pots(r0 + i * h / 2, **kw) for i in range(2 * NS + 1)]
PT = mkPT(wc=0.0, wl=0.0, wt=0.0)
def deriv(i2, y, E):
    r = r0 + i2 * h / 2; Vc, Vt, Vls = PT[i2]; u, up, w, wp = y
    return [up, 2 * mu * ((Vc - E) * u + math.sqrt(8) * Vt * w), wp, 6 / r**2 * w + 2 * mu * (math.sqrt(8) * Vt * u + (Vc - 2 * Vt - 3 * Vls - E) * w)]
def run(E, y, keep=False):
    tr = [] 
    for i in range(NS):
        k1 = deriv(2 * i, y, E); y2 = [a + h / 2 * b for a, b in zip(y, k1)]; k2 = deriv(2 * i + 1, y2, E)
        y3 = [a + h / 2 * b for a, b in zip(y, k2)]; k3 = deriv(2 * i + 1, y3, E); y4 = [a + h * b for a, b in zip(y, k3)]; k4 = deriv(2 * i + 2, y4, E)
        y = [a + h / 6 * (b + 2 * c + 2 * d + e) for a, b, c, d, e in zip(y, k1, k2, k3, k4)]
        if keep: tr.append((y[0], y[2]))
    return y, tr
def D(E):
    a, _ = run(E, [r0, 1.0, 0.0, 0.0]); b, _ = run(E, [0.0, 0.0, r0**3, 3 * r0**2])
    return a[0] * b[2] - b[0] * a[2], a, b
grid = [-(10 ** (-6 + 0.25 * k)) for k in range(0, 27)]   # -1e-6 ... -3.16 m_p (log grid, 4 points per decade)
def bisect(lo, hi):
    dlo = D(lo)[0]
    for _ in range(45):
        mid = 0.5 * (lo + hi); dm = D(mid)[0]
        if dm * dlo > 0: lo, dlo = mid, dm
        else: hi = mid
    return -0.5 * (lo + hi)
def boundQ():
    v = [D(E)[0] for E in grid]; Bs = [bisect(E1, E2) for (E1, d1), (E2, d2) in zip(zip(grid, v), zip(grid[1:], v[1:])) if d1 * d2 < 0]
    return ("bound states B/m_p: " + ", ".join("%.6g" % b for b in Bs)) if Bs else "unbound in (-3.16 m_p, 0)"
def solve():  # shallowest bound state of the current PT: (B, P_D, [(r, u, w)] normalised) or None
    vals = [D(E)[0] for E in grid]; root = None
    for (E1, d1), (E2, d2) in zip(zip(grid, vals), zip(grid[1:], vals[1:])):
        if d1 * d2 < 0: root = (E1, E2)
    if root is None: return None
    lo, hi = root; dlo = D(lo)[0]
    for _ in range(45):
        mid = 0.5 * (lo + hi); dm = D(mid)[0]
        if dm * dlo > 0: lo, dlo = mid, dm
        else: hi = mid
    E0 = 0.5 * (lo + hi); _, a, b = D(E0); ca, cb = b[0], -a[0]
    _, ta = run(E0, [r0, 1.0, 0.0, 0.0], True); _, tb = run(E0, [0.0, 0.0, r0**3, 3 * r0**2], True)
    cut = int(0.8 * NS); wf = []; su = sw = 0.0
    for i, ((ua, wa), (ub, wb)) in enumerate(list(zip(ta, tb))[:cut]):
        u = ca * ua + cb * ub; w = ca * wa + cb * wb; wf.append((r0 + (i + 1) * h, u, w)); su += u * u * h; sw += w * w * h
    kk = math.sqrt(-2 * mu * E0); su += wf[-1][1]**2 / (2 * kk)
    nn = math.sqrt(su + sw); return -E0, sw / (su + sw), [(r, u / nn, w / nn) for r, u, w in wf]
def expect(wf, LW):
    c = t = l = 0.0
    for r, u, w in wf:
        c_, t_, l_ = wpots(r, LW); c += c_ * (u * u + w * w) * h; t += t_ * (2 * math.sqrt(8) * u * w - 2 * w * w) * h; l += l_ * (-3 * w * w) * h
    return c, t, l
S0 = solve()
if S0 is None:
    rec(s, "AG-3 OPE + sigma (LS) reference state", "unbound", "breakdown not possible")
else:
    B0, PD0, wf0 = S0
    info(s, "AG-3 reference state: OPE + sigma (with LS), no omega", "round af", B0, "diagnostic", "B/m_p (MeV byproduct %s); P_D %.4g" % (nstr(mpf(B0) * mpM, 5), PD0))
    for LW, lab in ((LamV, "soliton form factor Lambda_V %.4f" % LamV), (1e4, "point vertex (no form factor)"), (Lam, "topological Lambda_B %.4f (F1)" % Lam)):
        c, t, l = expect(wf0, LW)
        info(s, "AG-3 <V_omega> pieces at E = -B0, %s: central" % lab, "first order, m_p units", c, "diagnostic", "tensor %.5g, spin-orbit %.5g, total %.5g; ratio total/B0 %.4g" % (t, l, c + t + l, (c + t + l) / B0))
    for tag, kw in (("omega central only", dict(wl=0.0, wt=0.0)), ("omega central + spin-orbit", dict(wt=0.0)), ("omega central + spin-orbit + tensor (full, Lambda_V)", {}), ("omega spin-orbit + tensor, no central", dict(wc=0.0))):
        PT = mkPT(**kw); r_ = solve()
        rec(s, "AG-3 cumulative: OPE + sigma + " + tag, ("bound B/m_p %.6g" % r_[0]) if r_ else "unbound in (-3.16 m_p, 0)", "diagnostic")
    PT = mkPT(LW=Lam); r_ = solve()
    if r_ is None:
        rec(s, "AG-3 F1 B_d/m_p (omega vertex with the topological baryon radius Lambda_B)", "miss (unbound in (-3.16 m_p, 0))", "")
    else:
        B, PDv, _ = r_; Bref = ref("B_H2_MeV")
        emitz(s, "AG-3 F1 B_d/m_p (omega vertex with the topological baryon radius Lambda_B)", "FSOT only", B, mpf(Bref[0]) / mpM, mpf(Bref[1]) / mpM, 0, "FSOT · measured", "MeV byproduct " + nstr(mpf(B) * mpM, 6))
        info(s, "AG-3 F1 P_D", "F1 wave function", PDv, "model-computed", "not an observable")
        muS = muSq; mud = muS - mpf(3) / 2 * (muS - mpf(1) / 2) * mpf(PDv)
        emitz(s, "AG-3 F1 mu_d = mu_S - (3/2)(mu_S - 1/2) P_D", "round-q FSOT mu_p + mu_n, F1 P_D", mud, "0.8574382335", "0.0000000022", 0, "FSOT · measured", "mu_S " + nstr(muS, 8))
rec("GATE", "record rows of the 91", "unchanged", "z-only")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02ag.py under audit/FREEZE_2026-10-02ag (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
