#!/usr/bin/env python3
"""Round-ae scores under audit/FREEZE_2026-10-02ae (committed first). z-only, dimensionless ratios; FSOT-only inputs.
AE-1 PV-regularised rotational mu and g_A at K 12/14 (audit/murun_2026-10-02ae_K*.json); AE-2 deuteron with the omega Dirac form factor; AE-3 T_CMB age-integral trace.
  python tools/score_2026_10_02ae.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02ae.tsv
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
info(s, "AD-1 g_A input for AE-2 (round ad, K 12)", "round ad", gA, "FSOT · input", "")
# ---------------- AE-1
s = "AE-1"
def regx(sp, comp):
    q_ = (1 / mpf(sp_in["Mpv_over_M"])) ** 2
    d_ = sp[comp]; tot, sea, pv, va, vb = [mpf(d_[k][IDX]) for k in ("tot", "sea", "pv", "vac", "vacpv")]
    return (tot - sea) + (sea - q_ * pv) - (va - q_ * vb)
SGq = {}
rq = Hq["Q1_sanity_M420_F93"]; oq = rq["DPP"]; Iq = mpf(oq["I_times_M"]); qq = mpf(rq["M_N_MeV"]) / mpf(rq["M_MeV"])
SGq["g1"] = 1 if mpf(oq["A_im"]) / Iq > 0 else -1; SGq["muS"] = 1 if qq * mpf(oq["B_re"]) / (6 * Iq) > 0 else -1; SGq["muV1"] = 1 if qq * mpf(oq["Amu_im"]) / Iq > 0 else -1
KR = {}
for K in (12, 14, 16):
    p_ = R_ / ("audit/murun_2026-10-02ae_K%d.json" % K)
    if not p_.exists(): continue
    m_ = J("audit/murun_2026-10-02ae_K%d.json" % K); sp_in = m_["inputs"]; o_ = m_["DPP"]; sp = m_["split"]; I_ = mpf(o_["I_times_M"]); Mr_ = mpf(sp_in["M_over_mp"]); qN = 1 / Mr_
    IDX = 1; Ar = regx(sp, "A"); Amr = regx(sp, "Amu"); IDX = 0; Br = regx(sp, "B")
    gA_ = mpf(o_["gA0"]) + SGq["g1"] * Ar / I_
    muS = SGq["muS"] * qN * Br / (6 * I_); muV = -qN / 3 * (mpf(o_["xat_val"]) + mpf(o_["xat_sea"])) + SGq["muV1"] * qN * Amr / I_
    IDX = 1; Au = mpf(sp["Amu"]["tot"][1]); IDX = 0; Bu = mpf(sp["B"]["tot"][0])
    KR[K] = {"gA": gA_, "DN": 3 * Mr_ / (2 * I_), "mup": (muS + muV) / 2, "mun": (muS - muV) / 2, "x": m_["x_DPP"], "edge": m_["edge_minimum"], "IM": I_}
    info(s, "AE-1 K %d: g_A, Delta-N/m_p, mu_p, mu_n (PV-regularised rotational terms)" % K, "M/m_p 0.458168, window 0.5-1.6", gA_, "FSOT · K step",
         "Delta-N/m_p %s; mu_p %s, mu_n %s; mu_V^(0) %s; x_DPP %s%s; I M %s; unregularised mu_p,n would be %s, %s" % (nstr(3 * Mr_ / (2 * I_), 6), nstr(KR[K]["mup"], 6), nstr(KR[K]["mun"], 6), nstr(-qN / 3 * (mpf(o_["xat_val"]) + mpf(o_["xat_sea"])), 6), nstr(mpf(m_["x_DPP"]), 5), " EDGE" if m_["edge_minimum"] else "", nstr(I_, 6),
         nstr((SGq["muS"] * qN * Bu / (6 * I_) + (-qN / 3 * (mpf(o_["xat_val"]) + mpf(o_["xat_sea"])) + SGq["muV1"] * qN * Au / I_)) / 2, 6), nstr((SGq["muS"] * qN * Bu / (6 * I_) - (-qN / 3 * (mpf(o_["xat_val"]) + mpf(o_["xat_sea"])) + SGq["muV1"] * qN * Au / I_)) / 2, 6)))
if 12 in KR and 14 in KR:
    Ks = sorted(KR); Km_, Kp_ = Ks[-1], Ks[-2]
    emitz(s, "AE-1 g_A (K %d, PV-regularised rotational term)" % Km_, "FSOT inputs", KR[Km_]["gA"], "1.2754", "0.0013", fabs(KR[Km_]["gA"] - KR[Kp_]["gA"]), "FSOT · measured", "theory unc. |K%d - K%d|" % (Km_, Kp_))
    emitz(s, "AE-1 (M_Delta - M_N)/m_p (K %d)" % Km_, "FSOT inputs", KR[Km_]["DN"], DNc, mpf(2) / mpf("938.27208943"), fabs(KR[Km_]["DN"] - KR[Kp_]["DN"]), "FSOT · measured", "theory unc. |K%d - K%d|" % (Km_, Kp_))
    conv = all(fabs(KR[Km_][k] - KR[Kp_][k]) <= mpf("0.02") * fabs(KR[Km_][k]) for k in ("mup", "mun")) and all(fabs(KR[K_][k] - KR[Kp_][k]) <= mpf("0.02") * fabs(KR[Km_][k]) for K_ in Ks for k in ("mup", "mun") if K_ >= 12)
    if conv:
        for k, nm_, c_ in (("mup", "mu_p", "2.79284734463"), ("mun", "mu_n", "-1.91304276")):
            emitz(s, "AE-1 %s (K %d, PV-regularised)" % (nm_, Km_), "FSOT inputs", KR[Km_][k], c_, "0.00000001", fabs(KR[Km_][k] - KR[Kp_][k]), "FSOT · measured", "converged under the 2 % rule")
    else:
        rec(s, "AE-1 mu_p, mu_n", "not scored", "K 12 -> %d change: mu_p %s, mu_n %s (2 %% rule fails)" % (Km_, nstr(KR[Km_]["mup"] - KR[Kp_]["mup"], 4), nstr(KR[Km_]["mun"] - KR[Kp_]["mun"], 4)))
else:
    rec(s, "AE-1 K runs", "incomplete", "")
# ---------------- AE-2 deuteron (pure Python, deterministic)
s = "AE-2"
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
info(s, "AE-2 Lambda_B/m_p = sqrt6/r_B (topological baryon rms radius; pion vertex)", "AC-2 profile x_DPP, M/m_p", Lam, "FSOT · intermediate", "r_B m_p %.6g (%.4g fm byproduct); baryon number check %.6f; f^2/4pi %.5g, g_sigma^2/4pi %.5g (m %.4g), g_omega^2/4pi %.5g (m %.4g)" % (rB, rB * 197.3269804 / float(mpM), Bnorm, fpi2, gs2, ms, gw2, mw))
info(s, "AE-2 g_sigmaNN^2/4pi = (3 S_val M/F_pi)^2/4pi (soliton valence scalar charge)", "AD-1 soliton", gs2, "FSOT · intermediate", "S_val %.6g (quark counting had 1); Lambda_S/m_p = sqrt6/r_S = %.6g (r_S m_p %.5g); omega 6 pi unchanged (baryon number 1)" % (Sv, LamS, rS))
muSq = None
for line in open(R_ / "audit/score_2026-10-02q_late.tsv", encoding="utf-8"):
    f_ = line.rstrip("\n").split("\t")
    if len(f_) > 3 and f_[0] == "FSOT" and f_[1].startswith("Q-1 mu_p"): muSq = (muSq or 0) + mpf(f_[3])
    if len(f_) > 3 and f_[0] == "FSOT" and f_[1].startswith("Q-1 mu_n"): muSq = (muSq or 0) + mpf(f_[3])
info(s, "AE-2 Lambda_V/m_p = sqrt6/r_V (soliton valence Dirac radius; omega vertex)", "AD-1 soliton (K 12)", LamV, "FSOT · intermediate", "r_V m_p %.5g (%.4g fm byproduct); kappa_omega = mu_S - 1 = %s (tensor-coupling potentials not implemented: stated in the freeze)" % (rV, rV * 197.3269804 / float(mpM), nstr(muSq - 1, 5)))
def Gf(m, r, Lam=Lam):  # FT of Lam^4/((q^2+m^2)(q^2+Lam^2)^2) x 4 pi; returns G, lap G, (G'' - G'/r)
    K = Lam**2 / (Lam**2 - m**2); em, eL = math.exp(-m * r), math.exp(-Lam * r)
    G = K * K * (em - eL) / r - K * Lam * eL / 2
    lap = K * K * (m * m * em - Lam * Lam * eL) / r - K * Lam / 2 * (Lam * Lam - 2 * Lam / r) * eL
    T = K * K * (em * (m * m / r + 3 * m / r**2 + 3 / r**3) - eL * (Lam * Lam / r + 3 * Lam / r**2 + 3 / r**3)) - K * Lam / 2 * (Lam * Lam + Lam / r) * eL
    return G, lap, T
def pots(r):
    _, lp, Tp = Gf(mpir, r)
    Vc = -fpi2 * lp / mpir**2 - gs2 * Gf(ms, r, LamS)[0] + gw2 * Gf(mw, r, LamV)[0]
    Vt = -fpi2 * Tp / mpir**2
    return Vc, Vt
h, RM = 0.01, 150.0; NS = int(RM / h); r0 = 1e-3
PT = []
for i in range(2 * NS + 1):
    PT.append(pots(r0 + i * h / 2))
def deriv(i2, y, E):
    r = r0 + i2 * h / 2; Vc, Vt = PT[i2]; u, up, w, wp = y
    return [up, 2 * mu * ((Vc - E) * u + math.sqrt(8) * Vt * w), wp, 6 / r**2 * w + 2 * mu * (math.sqrt(8) * Vt * u + (Vc - 2 * Vt - E) * w)]
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
PT0 = PT
for tag, fl in (("(i) OPE central + tensor only", (1, 0, 0)), ("(ii) OPE + sigma", (1, 1, 0))):
    PT = []
    for i in range(2 * NS + 1):
        r = r0 + i * h / 2; _, lp, Tp = Gf(mpir, r)
        PT.append((-fpi2 * lp / mpir**2 - fl[1] * gs2 * Gf(ms, r, LamS)[0], -fpi2 * Tp / mpir**2))
    rec(s, "AE-2 trace " + tag, boundQ(), "information (trace step); deuteron 2.2246 MeV = 0.002371 m_p")
PT = PT0
vals = [D(E)[0] for E in grid]
root = None
for (E1, d1), (E2, d2) in zip(zip(grid, vals), zip(grid[1:], vals[1:])):
    if d1 * d2 < 0: root = (E1, E2)
if root is None:
    rec(s, "AE-2 B_d/m_p (tensor OPE + soliton sigma + omega)", "miss (unbound in (-3.16 m_p, 0))", "")
    PDv = None
else:
    lo, hi = root
    dlo = D(lo)[0]
    for _ in range(45):
        mid = 0.5 * (lo + hi); dm = D(mid)[0]
        if dm * dlo > 0: lo, dlo = mid, dm
        else: hi = mid
    E0 = 0.5 * (lo + hi); _, a, b = D(E0)
    ca, cb = b[0], -a[0]
    _, ta = run(E0, [r0, 1.0, 0.0, 0.0], True); _, tb = run(E0, [0.0, 0.0, r0**3, 3 * r0**2], True)
    cut = int(0.8 * NS); su = sw = 0.0
    for (ua, wa), (ub, wb) in list(zip(ta, tb))[:cut]:
        u = ca * ua + cb * ub; w = ca * wa + cb * wb; su += u * u; sw += w * w
    kap = math.sqrt(-2 * mu * E0); uR = ca * ta[cut - 1][0] + cb * tb[cut - 1][0]; su += uR**2 / (2 * kap * h)   # S-wave tail beyond 0.8 r_max
    PDv = sw / (su + sw); B = -E0
    Bref = ref("B_H2_MeV")
    emitz(s, "AE-2 B_d/m_p (tensor OPE + soliton sigma + omega)", "FSOT only", B, mpf(Bref[0]) / mpM, mpf(Bref[1]) / mpM, 0, "FSOT · measured", "MeV byproduct " + nstr(mpf(B) * mpM, 6) + "; root bracket from a log grid down to -0.03 m_p (shallowest sign change)")
    info(s, "AE-2 P_D (D-state probability)", "AE-2 wave function", PDv, "model-computed", "not an observable; round-o value 0.0628")
    Q = "audit/score_2026-10-02q_late.tsv"
    def rowq(key):
        for line in open(R_ / Q, encoding="utf-8"):
            f = line.rstrip("\n").split("\t")
            if len(f) > 7 and f[0] == "FSOT" and f[1].startswith(key): return mpf(f[3])
    muS = rowq("Q-1 mu_p") + rowq("Q-1 mu_n"); mud = muS - mpf(3) / 2 * (muS - mpf(1) / 2) * mpf(PDv)
    emitz(s, "AE-2 mu_d = mu_S - (3/2)(mu_S - 1/2) P_D", "round-q FSOT mu_p + mu_n, AD-2 P_D", mud, "0.8574382335", "0.0000000022", 0, "FSOT · measured", "mu_S " + nstr(muS, 8))
# ---------------- AD-3 inputs: matter-to-baryon ratio (round ac) and T_ls
from mpmath import quad, findroot, exp as mexp
s = "AE-3"
ODM, Ob, Om, Ne_, eta = P["wave2|Omega_DM_h2"], P["wave1|Omega_b_h2"], P["wave2|Omega_m"], P["wave2|N_eff"], P["wave10|eta_baryon_photon"]
rmb = (ODM + Ob) / Ob
info(s, "AE-3 matter-to-baryon ratio (round ac) (Omega_DM h^2 + Omega_b h^2)/Omega_b h^2", "FSOT wave2 Omega_DM_h2, wave1 Omega_b_h2", rmb, "FSOT · intermediate", "Planck 2018 (0.1200 + 0.02237)/0.02237 = 6.364 for comparison (outside number, info); implied h from wave2 Omega_m: " + nstr(sqrt((ODM + Ob) / Om), 6))
al_ = 1 / L["alpha_inv"]; z3_ = zeta(3); Gn, cc, hb, kB = mpf("6.67430e-11"), mpf(299792458), mpf("1.054571817e-34"), mpf("1.380649e-23")
me_kg, mp_kg = L["m_e_kg"], L["m_p_kg"]; sT = 8 * pi / 3 * (al_ * hb / (me_kg * cc))**2; Bh = me_kg * cc**2 * al_**2 / 2
def ngam(T): return 2 * z3_ / pi**2 * (kB * T / (hb * cc))**3
def Hub(T):
    rg = pi**2 / 15 * (kB * T)**4 / (hb * cc)**3 / cc**2
    return sqrt(8 * pi * Gn / 3 * (rg * (1 + mpf(7) / 8 * (mpf(4) / 11)**(mpf(4) / 3) * Ne_) + rmb * mp_kg * eta * ngam(T)))
def xe(T):
    S = (me_kg * kB * T / (2 * pi * hb**2))**(mpf(3) / 2) * mexp(-Bh / (kB * T)) / (eta * ngam(T)); return (-S + sqrt(S * S + 4 * S)) / 2
def tau(T): return quad(lambda t: xe(t) * eta * ngam(t) * sT * cc / (t * Hub(t)), [1500, 2500, T])  # from T down to 1500 K (Saha x_e negligible below; freeze: 'from T downward')
Tls = findroot(lambda T: tau(T) - 1, (mpf(2600), mpf(4500)), solver='anderson')
ue = kB * Tls / (me_kg * cc**2 * al_**2)
s = "AE-3"
OL, Age, Or_, H0p = P["wave2|Omega_Lambda"], P["wave3|Age_Gyr"], P["wave9|Omega_r"], P["wave1|H0"]; h2 = (ODM + Ob) / Om
rc100 = 3 * (100 * 1000 / mpf("3.0856775814913673e22"))**2 / (8 * pi * Gn); Gyr = mpf("3.15576e16")
def T0of(nu_fac, rad_on, OLh2):
    rL = OLh2 * rc100
    def H(T):
        rg = pi**2 / 15 * (kB * T)**4 / (hb * cc)**3 / cc**2
        return sqrt(8 * pi * Gn / 3 * (rad_on * rg * (1 + nu_fac) + rmb * mp_kg * eta * ngam(T) + rL))
    age = lambda T0: quad(lambda lt: 1 / H(mexp(lt)), [ln(T0), ln(T0) + 3, ln(T0) + 8, ln(T0) + 25])
    return findroot(lambda T: age(T) / Gyr - Age, (mpf("2.6"), mpf("2.9")), solver="anderson")
nuf = mpf(7) / 8 * (mpf(4) / 11)**(mpf(4) / 3) * Ne_
steps = [("(a) no radiation", 0, 0, OL * h2), ("(b) photons only", 0, 1, OL * h2), ("(c) photons + FSOT N_eff (= AD-3)", nuf, 1, OL * h2),
         ("(d) Omega_Lambda from flatness 1 - Omega_m - Omega_r", nuf, 1, (1 - Om - Or_) * h2), ("(e) h from the H0 pin (deferred; info)", nuf, 1, OL * (H0p / 100)**2)]
for tag, nf_, ro, olh2 in steps:
    T_ = T0of(nf_, ro, olh2)
    info(s, "AE-3 trace " + tag + ": T_0 (K)", "FSOT pins", T_, "diagnostic", "vs FIRAS 2.7255: " + nstr((T_ / mpf("2.7255") - 1) * 100, 5) + " %")
info(s, "AE-3 pin consistency: Omega_m + Omega_Lambda + Omega_r", "wave2, wave9", Om + OL + Or_, "diagnostic", "flat = 1; Omega_m h^2 via H0 pin " + nstr(Om * (H0p / 100)**2, 6) + " vs Omega_DM_h2 + Omega_b_h2 = " + nstr(ODM + Ob, 6) + "; h from Omega_m " + nstr(sqrt(h2), 6) + " vs H0 pin " + nstr(H0p / 100, 6))
rec("GATE", "record rows of the 91", "unchanged", "z-only")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02ae.py under audit/FREEZE_2026-10-02ae (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
