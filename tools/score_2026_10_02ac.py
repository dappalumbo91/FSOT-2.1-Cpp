#!/usr/bin/env python3
"""Round-ac scores under audit/FREEZE_2026-10-02ac (committed first). z-only, dimensionless ratios; FSOT-only inputs.
AC-2 soliton (pre-registered wide window, round-ab M/m_p) + kink diagnostic; AC-1 deuteron with tensor OPE and soliton form factors (pure Python RK4); AC-3 matter-to-baryon ratio and T_ls (information).
  python tools/score_2026_10_02ac.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02ac.tsv
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
# ---------------- AC-2
s = "AC-2"; Hq = J("audit/heavy_2026-10-02q.json")
SGg1 = 1 if mpf(Hq["Q1_sanity_M420_F93"]["DPP"]["A_im"]) > 0 else -1
DNc = (mpf("1232") - (mpf("938.27208943") + mpf("939.56542194")) / 2) / mpf("938.27208943")
Hw = J("audit/heavy_2026-10-02ab_wide_K12.json"); dw = Hw["AB1wide_info_K12"]; ow = dw["DPP"]; IM = mpf(ow["I_times_M"]); Mr = mpf(Hw["inputs"]["M_over_mp"])
DN = 3 * Mr / (2 * IM); g1 = SGg1 * mpf(ow["A_im"]) / IM; gA = mpf(ow["gA0"]) + g1; xD = float(dw["x_DPP"])
emitz(s, "AC-2 (M_Delta - M_N)/m_p (K 12, window 0.5-1.6, interior minimum)", "round-ab M/m_p 0.458168, FSOT inputs", DN, DNc, mpf(2) / mpf("938.27208943"), 0, "FSOT · measured",
      "x_DPP " + nstr(mpf(xD), 5) + "; I M " + nstr(IM, 6) + "; values already shown as round-ab information (disclosed); MeV byproduct " + nstr(DN * mpM, 6))
emitz(s, "AC-2 g_A time-ordered (K 12, same run)", "same", gA, "1.2754", "0.0013", 0, "FSOT · measured", "classical " + nstr(mpf(ow["gA0"]), 6) + " (valence " + nstr(mpf(ow["gA0_val"]), 5) + ", sea " + nstr(mpf(ow["gA0_sea"]), 5) + ") + rotational 1/N_c term g1 = A_im/(I M) " + nstr(g1, 6))
kp = R_ / "audit/kink_2026-10-02ac.jsonl"
if kp.exists():
    for line in kp.read_text(encoding="utf-8").splitlines():
        k = json.loads(line)
        info(s, "kink diagnostic E/M at x %.4g" % k["x"], "K 12, round-ab inputs", k["E"], "diagnostic", "3 eps_val %.5g (eps_val %.4g), sea %.5g, PV %.5g, mass %.5g" % (k["val3"], k["eps_val"], k["sea"], k["pv"], k["mass"]))
# ---------------- AC-1 deuteron (pure Python, deterministic)
s = "AC-1"
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
fpi2 = float(gA)**2 * mpir**2 / (16 * math.pi * Fr**2); gs2 = (3 * Mq / Fr)**2 / (4 * math.pi); ms = 2 * Mq; gw2 = (6 * math.pi)**2 / (4 * math.pi); mw = 2 * math.sqrt(2) * math.pi * Fr
info(s, "AC-1 Lambda/m_p = sqrt6/r_B (topological baryon rms radius of the AC-2 soliton)", "AC-2 profile x_DPP, M/m_p", Lam, "FSOT · intermediate", "r_B m_p %.6g (%.4g fm byproduct); baryon number check %.6f; f^2/4pi %.5g, g_sigma^2/4pi %.5g (m %.4g), g_omega^2/4pi %.5g (m %.4g)" % (rB, rB * 197.3269804 / float(mpM), Bnorm, fpi2, gs2, ms, gw2, mw))
def Gf(m, r):  # FT of Lam^4/((q^2+m^2)(q^2+Lam^2)^2) x 4 pi; returns G, lap G, (G'' - G'/r)
    K = Lam**2 / (Lam**2 - m**2); em, eL = math.exp(-m * r), math.exp(-Lam * r)
    G = K * K * (em - eL) / r - K * Lam * eL / 2
    lap = K * K * (m * m * em - Lam * Lam * eL) / r - K * Lam / 2 * (Lam * Lam - 2 * Lam / r) * eL
    T = K * K * (em * (m * m / r + 3 * m / r**2 + 3 / r**3) - eL * (Lam * Lam / r + 3 * Lam / r**2 + 3 / r**3)) - K * Lam / 2 * (Lam * Lam + Lam / r) * eL
    return G, lap, T
def pots(r):
    _, lp, Tp = Gf(mpir, r)
    Vc = -fpi2 * lp / mpir**2 - gs2 * Gf(ms, r)[0] + gw2 * Gf(mw, r)[0]
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
        PT.append((-fpi2 * lp / mpir**2 - fl[1] * gs2 * Gf(ms, r)[0], -fpi2 * Tp / mpir**2))
    rec(s, "AC-1 trace " + tag, boundQ(), "information (trace step); deuteron 2.2246 MeV = 0.002371 m_p")
PT = PT0
vals = [D(E)[0] for E in grid]
root = None
for (E1, d1), (E2, d2) in zip(zip(grid, vals), zip(grid[1:], vals[1:])):
    if d1 * d2 < 0: root = (E1, E2)
if root is None:
    rec(s, "AC-1 B_d/m_p (tensor OPE + sigma + omega, soliton form factors)", "miss (unbound in (-3.16 m_p, 0))", "")
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
    emitz(s, "AC-1 B_d/m_p (tensor OPE + sigma + omega, soliton form factors)", "FSOT only", B, mpf(Bref[0]) / mpM, mpf(Bref[1]) / mpM, 0, "FSOT · measured", "MeV byproduct " + nstr(mpf(B) * mpM, 6) + "; root bracket from a log grid down to -0.03 m_p (shallowest sign change)")
    info(s, "AC-1 P_D (D-state probability)", "AC-1 wave function", PDv, "model-computed", "not an observable; round-o value 0.0628")
    Q = "audit/score_2026-10-02q_late.tsv"
    def rowq(key):
        for line in open(R_ / Q, encoding="utf-8"):
            f = line.rstrip("\n").split("\t")
            if len(f) > 7 and f[0] == "FSOT" and f[1].startswith(key): return mpf(f[3])
    muS = rowq("Q-1 mu_p") + rowq("Q-1 mu_n"); mud = muS - mpf(3) / 2 * (muS - mpf(1) / 2) * mpf(PDv)
    emitz(s, "AC-1 mu_d = mu_S - (3/2)(mu_S - 1/2) P_D", "round-q FSOT mu_p + mu_n, AC-1 P_D", mud, "0.8574382335", "0.0000000022", 0, "FSOT · measured", "mu_S " + nstr(muS, 8))
# ---------------- AC-3 matter-to-baryon ratio and last scattering (information)
from mpmath import quad, findroot, exp as mexp
s = "AC-3"
ODM, Ob, Om, Ne_, eta = P["wave2|Omega_DM_h2"], P["wave1|Omega_b_h2"], P["wave2|Omega_m"], P["wave2|N_eff"], P["wave10|eta_baryon_photon"]
rmb = (ODM + Ob) / Ob
info(s, "AC-3 matter-to-baryon ratio (Omega_DM h^2 + Omega_b h^2)/Omega_b h^2", "FSOT wave2 Omega_DM_h2, wave1 Omega_b_h2", rmb, "FSOT · intermediate", "Planck 2018 (0.1200 + 0.02237)/0.02237 = 6.364 for comparison (outside number, info); implied h from wave2 Omega_m: " + nstr(sqrt((ODM + Ob) / Om), 6))
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
info(s, "AC-3 kT_ls/(m_e alpha^2) (Saha + Thomson tau = 1, FSOT eta and matter-to-baryon ratio)", "FSOT eta, Omega_DM_h2, Omega_b_h2, N_eff, alpha", ue, "model-computed", "T_ls = " + nstr(Tls, 6) + " K (byproduct); x_e(T_ls) " + nstr(xe(Tls), 4) + "; equilibrium Saha (no Peebles bottleneck), so T_ls is biased high; T_CMB not scored (1 + z_* needs T_0)")
rec("GATE", "record rows of the 91", "unchanged", "z-only")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02ac.py under audit/FREEZE_2026-10-02ac (committed first)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
