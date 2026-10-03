#!/usr/bin/env python3
"""Round-af scores under audit/FREEZE_2026-10-02af (committed first). z-only, dimensionless ratios; FSOT-only inputs.
AF-1 mu_V^(0) per-sector decomposition (audit/musector_2026-10-02af.json); AF-2 deuteron with omega tensor/LS and sigma LS; AF-3 self-consistent flat FSOT cosmology branch.
  python tools/score_2026_10_02af.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02af.tsv
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
# ---------------- AF-1 (diagnostic; conditional tail)
s = "AF-1"
if (R_ / "audit/musector_2026-10-02af.json").exists():
    MS = J("audit/musector_2026-10-02af.json")
    for K in (12, 14):
        if "K%d" % K not in MS: continue
        d_ = MS["K%d" % K]
        info(s, "AF-1 K %d xat_sea (sector sum) vs run" % K, "AE-1 profile", d_["xat_sea"], "diagnostic", "run xat_sea %s, xat_val %s (run %s)" % (nstr(mpf(d_["xat_sea_run"]), 8), nstr(mpf(d_["xat_val"]), 8), nstr(mpf(d_["xat_val_run"]), 8)))
    if "K12" in MS and "K14" in MS:
        S12, S14 = MS["K12"]["sectors"], MS["K14"]["sectors"]
        for Kg in range(0, 15):
            for P_ in "+-":
                k_ = "%d%s" % (Kg, P_)
                a_ = S12.get(k_, {}); b_ = S14.get(k_, {})
                if not b_: continue
                info(s, "AF-1 sector K=%s: xat contribution K12 / K14" % k_, "s1 - q s2 - v1 + q v2", b_["total"], "diagnostic",
                     "K12 %s; K14 %s (s1 %s, PV %s, vac %s, vacPV %s)" % (nstr(mpf(a_.get("total", 0)), 6), nstr(mpf(b_["total"]), 6), nstr(mpf(b_["s1"]), 6), nstr(mpf(b_["s2"]), 6), nstr(mpf(b_["v1"]), 6), nstr(mpf(b_["v2"]), 6)))
        top = [sum(S14["%d%s" % (Kg, P_)]["total"] for P_ in "+-" if "%d%s" % (Kg, P_) in S14) for Kg in range(11, 15)]
        mono = all(abs(top[i_ + 1]) < abs(top[i_]) for i_ in range(3)) and all(v_ * top[0] > 0 for v_ in top)
        if mono:
            p_ = -math.log(abs(top[3] / top[2])) / math.log(14 / 13)
            rec(s, "AF-1 tail test (top 4 sectors at K 14)", "monotone", "p from the last two sectors %.4g; per the freeze the tail correction would apply only with one common p > 1 at both K maxima" % p_)
        else:
            rec(s, "AF-1 tail test (top 4 sectors at K 14)", "not a monotone power-law tail", "top-sector sums (K = 11..14): " + ", ".join("%.4g" % v_ for v_ in top) + "; no tail correction, no mu score")
else:
    rec(s, "AF-1 decomposition", "not run", "")
# ---------------- AF-2 deuteron (pure Python, deterministic)
s = "AF-2"
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
info(s, "AF-2 Lambda_B/m_p = sqrt6/r_B (topological baryon rms radius; pion vertex)", "AC-2 profile x_DPP, M/m_p", Lam, "FSOT · intermediate", "r_B m_p %.6g (%.4g fm byproduct); baryon number check %.6f; f^2/4pi %.5g, g_sigma^2/4pi %.5g (m %.4g), g_omega^2/4pi %.5g (m %.4g)" % (rB, rB * 197.3269804 / float(mpM), Bnorm, fpi2, gs2, ms, gw2, mw))
info(s, "AF-2 g_sigmaNN^2/4pi = (3 S_val M/F_pi)^2/4pi (soliton valence scalar charge)", "AD-1 soliton", gs2, "FSOT · intermediate", "S_val %.6g (quark counting had 1); Lambda_S/m_p = sqrt6/r_S = %.6g (r_S m_p %.5g); omega 6 pi unchanged (baryon number 1)" % (Sv, LamS, rS))
muSq = None
for line in open(R_ / "audit/score_2026-10-02q_late.tsv", encoding="utf-8"):
    f_ = line.rstrip("\n").split("\t")
    if len(f_) > 3 and f_[0] == "FSOT" and f_[1].startswith("Q-1 mu_p"): muSq = (muSq or 0) + mpf(f_[3])
    if len(f_) > 3 and f_[0] == "FSOT" and f_[1].startswith("Q-1 mu_n"): muSq = (muSq or 0) + mpf(f_[3])
info(s, "AF-2 Lambda_V/m_p = sqrt6/r_V (soliton valence Dirac radius; omega vertex)", "AD-1 soliton (K 12)", LamV, "FSOT · intermediate", "r_V m_p %.5g (%.4g fm byproduct); kappa_omega = mu_S - 1 = %s (enters the omega tensor and spin-orbit potentials, Bryan-Scott O(1/M^2))" % (rV, rV * 197.3269804 / float(mpM), nstr(muSq - 1, 5)))
def Gf(m, r, Lam=Lam):  # FT of Lam^4/((q^2+m^2)(q^2+Lam^2)^2) x 4 pi; returns G, lap G, (G'' - G'/r)
    K = Lam**2 / (Lam**2 - m**2); em, eL = math.exp(-m * r), math.exp(-Lam * r)
    G = K * K * (em - eL) / r - K * Lam * eL / 2
    lap = K * K * (m * m * em - Lam * Lam * eL) / r - K * Lam / 2 * (Lam * Lam - 2 * Lam / r) * eL
    T = K * K * (em * (m * m / r + 3 * m / r**2 + 3 / r**3) - eL * (Lam * Lam / r + 3 * Lam / r**2 + 3 / r**3)) - K * Lam / 2 * (Lam * Lam + Lam / r) * eL
    dG = K * K * ((-m * em + Lam * eL) / r - (em - eL) / r**2) + K * Lam * Lam * eL / 2
    return G, lap, T, -dG / r
kap = float(muSq - 1)
def pots(r, ws=1.0, ww=1.0):
    _, lp, Tp, _ = Gf(mpir, r); Gs, lps, Ts, Z1s = Gf(ms, r, LamS); Gw, lpw, Tw, Z1w = Gf(mw, r, LamV)
    Vc = -fpi2 * lp / mpir**2 - ws * gs2 * Gs * (1 - ms * ms / 4) + ww * gw2 * (Gw * (1 + mw * mw / 2) + (1 + kap)**2 / 6 * lpw)
    Vt = -fpi2 * Tp / mpir**2 - ww * gw2 * (1 + kap)**2 / 12 * Tw
    Vls = -ws * gs2 * Z1s / 2 - ww * gw2 * (3 + 4 * kap) / 2 * Z1w
    return Vc, Vt, Vls
h, RM = 0.01, 150.0; NS = int(RM / h); r0 = 1e-3
PT = []
for i in range(2 * NS + 1):
    PT.append(pots(r0 + i * h / 2))
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
PT0 = PT
for tag, fl in (("(i) OPE central + tensor only", (1, 0, 0)), ("(ii) OPE + sigma (with LS)", (1, 1, 0))):
    PT = [pots(r0 + i * h / 2, fl[1], 0.0) for i in range(2 * NS + 1)]
    rec(s, "AF-2 trace " + tag, boundQ(), "information (trace step); deuteron 2.2246 MeV = 0.002371 m_p")
PT = PT0
vals = [D(E)[0] for E in grid]
root = None
for (E1, d1), (E2, d2) in zip(zip(grid, vals), zip(grid[1:], vals[1:])):
    if d1 * d2 < 0: root = (E1, E2)
if root is None:
    rec(s, "AF-2 B_d/m_p (OPE + sigma + omega with tensor and spin-orbit)", "miss (unbound in (-3.16 m_p, 0))", "")
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
    emitz(s, "AF-2 B_d/m_p (OPE + sigma + omega with tensor and spin-orbit)", "FSOT only", B, mpf(Bref[0]) / mpM, mpf(Bref[1]) / mpM, 0, "FSOT · measured", "MeV byproduct " + nstr(mpf(B) * mpM, 6) + "; root bracket from a log grid down to -0.03 m_p (shallowest sign change)")
    info(s, "AF-2 P_D (D-state probability)", "AF-2 wave function", PDv, "model-computed", "not an observable; round-o value 0.0628")
    Q = "audit/score_2026-10-02q_late.tsv"
    def rowq(key):
        for line in open(R_ / Q, encoding="utf-8"):
            f = line.rstrip("\n").split("\t")
            if len(f) > 7 and f[0] == "FSOT" and f[1].startswith(key): return mpf(f[3])
    muS = rowq("Q-1 mu_p") + rowq("Q-1 mu_n"); mud = muS - mpf(3) / 2 * (muS - mpf(1) / 2) * mpf(PDv)
    emitz(s, "AF-2 mu_d = mu_S - (3/2)(mu_S - 1/2) P_D", "round-q FSOT mu_p + mu_n, AD-2 P_D", mud, "0.8574382335", "0.0000000022", 0, "FSOT · measured", "mu_S " + nstr(muS, 8))
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
s = "AF-3"
OL, Age, Or_, H0p = P["wave2|Omega_Lambda"], P["wave3|Age_Gyr"], P["wave9|Omega_r"], P["wave1|H0"]
rc100 = 3 * (100 * 1000 / mpf("3.0856775814913673e22"))**2 / (8 * pi * Gn); Gyr = mpf("3.15576e16"); H100 = 100 * 1000 / mpf("3.0856775814913673e22")
ng0 = Ob * rc100 / (mp_kg * eta); T0c = (ng0 * pi**2 / (2 * z3_))**(mpf(1) / 3) * hb * cc / kB
rg0 = pi**2 / 15 * (kB * T0c)**4 / (hb * cc)**3 / cc**2; om_r = rg0 * (1 + mpf(7) / 8 * (mpf(4) / 11)**(mpf(4) / 3) * Ne_) / rc100; om_m = ODM + Ob
def age_h(hh): return quad(lambda aa: aa / sqrt(om_r + om_m * aa + (hh**2 - om_m - om_r) * aa**4), [0, mpf("0.001"), mpf("0.1"), 1]) / H100 / Gyr
hc = findroot(lambda hh: age_h(hh) - Age, (mpf("0.6"), mpf("0.75")), solver="anderson")
Omc, Orc = om_m / hc**2, om_r / hc**2; OLc = 1 - Omc - Orc
emitz(s, "AF-3 T_CMB (self-consistent flat branch: omega_b and eta fix T_0)", "FSOT omega_b, eta (m_p units)", T0c, "2.7255", "0.0006", 0, "FSOT · measured", "kT_0/(m_e alpha^2) " + nstr(kB * T0c / (me_kg * cc**2 * al_**2), 8) + "; omega_r " + nstr(om_r, 6) + "; flagged: baryon-to-photon route (see freeze)")
info(s, "AF-3 h from the age (flat by construction)", "omega_m, omega_r, Age", hc, "information (H0 deferred)", "H0 = %s km/s/Mpc vs H0 pin %s (%s %%)" % (nstr(100 * hc, 6), nstr(H0p, 6), nstr((100 * hc / H0p - 1) * 100, 4)))
for nm_, v_, pin_ in (("Omega_m", Omc, Om), ("Omega_Lambda", OLc, OL), ("Omega_r", Orc, Or_)):
    info(s, "AF-3 branch " + nm_ + " vs pin", "flat branch", v_, "audit finding", "pin %s; branch - pin = %s %%" % (nstr(pin_, 6), nstr((v_ / pin_ - 1) * 100, 4)))
info(s, "AF-3 consistency: T_0 from the age route (round ad) vs this branch", "AD-3", T0c, "diagnostic", "round ad 2.72847 K used the Omega_Lambda pin and h from the Omega_m pin")
rec("GATE", "record rows of the 91", "unchanged", "z-only")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02af.py under audit/FREEZE_2026-10-02af (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
