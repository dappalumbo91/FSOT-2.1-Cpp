"""Effective-coupling Z widths for DERIVATIONS_2026-10-02g: LEPTOP (Novikov, Okun, Rozanov, Vysotsky, hep-ph/9503308), transcribed equation by equation.
Equation numbers in comments are the LaTeX labels of hep-ph/9503308. Pure function of the inputs dict; no FSOT value is hard-wired."""
from mpmath import mp, mpf, sqrt, pi, log, asin, atan, zeta

Z3 = zeta(3)

def F_t(t):  # irok1
    if 4 * t > 1: return 2 * (1 - sqrt(4 * t - 1) * asin(1 / sqrt(4 * t)))
    return 2 * (1 - sqrt(1 - 4 * t) * log((1 + sqrt(1 - 4 * t)) / sqrt(4 * t)))
def F_h(h):  # irok2
    if h > 4: return 1 + (h / (h - 1) - h / 2) * log(h) + h * sqrt(1 - 4 / h) * log(sqrt(h / 4 - 1) + sqrt(h / 4))
    return 1 + (h / (h - 1) - h / 2) * log(h) - h * sqrt(4 / h - 1) * atan(sqrt(4 / h - 1))
def Fp_h(h):  # irok3
    if h > 4: return -1 + (h - 1) / 2 * log(h) + (3 - h) * sqrt(h / (h - 4)) * log(sqrt(h / 4 - 1) + sqrt(h / 4))
    return -1 + (h - 1) / 2 * log(h) + (3 - h) * sqrt(h / (4 - h)) * atan(sqrt((4 - h) / h))

TAB1 = [(0.0, .739, 5.710), (.1, 1.821, 4.671), (.2, 2.704, 3.901), (.3, 3.462, 3.304), (.4, 4.127, 2.834), (.5, 4.720, 2.461), (.6, 5.254, 2.163),
        (.7, 5.737, 1.924), (.8, 6.179, 1.735), (.9, 6.583, 1.586), (1.0, 6.956, 1.470), (1.1, 7.299, 1.382), (1.2, 7.617, 1.317), (1.3, 7.912, 1.272),
        (1.4, 8.186, 1.245), (1.5, 8.441, 1.232), (1.6, 8.679, 1.232), (1.7, 8.902, 1.243), (1.8, 9.109, 1.264), (1.9, 9.303, 1.293), (2.0, 9.485, 1.330)]
def tab1(x):  # LEPTOP table 1, linear interpolation in m_H/m_t
    x = mpf(x)
    for (x0, a0, t0), (x1, a1, t1) in zip(TAB1, TAB1[1:]):
        if mpf(x0) <= x <= mpf(x1):
            w = (x - mpf(x0)) / (mpf(x1) - mpf(x0)); return mpf(a0) + w * (mpf(a1) - mpf(a0)), mpf(t0) + w * (mpf(t1) - mpf(t0))
    raise ValueError("m_H/m_t outside table range used here")

# ---- alpha_s running (identical to tools/score_2026_10_02e.py)
def betas(nf):
    return ((11 - mpf(2) * nf / 3) / 4, (102 - mpf(38) * nf / 3) / 16, (mpf(2857) / 2 - mpf(5033) * nf / 18 + mpf(325) * nf**2 / 54) / 64,
            (mpf(149753) / 6 + 3564 * Z3 - (mpf(1078361) / 162 + mpf(6508) * Z3 / 27) * nf + (mpf(50065) / 162 + mpf(6472) * Z3 / 81) * nf**2 + mpf(1093) * nf**3 / 729) / 256)
def run(a, mu0, mu1, nf, steps=4000):
    b0, b1, b2, b3 = betas(nf)
    f = lambda x: -(b0 * x**2 + b1 * x**3 + b2 * x**4 + b3 * x**5)
    t0, t1 = log(mu0**2), log(mu1**2); h = (t1 - t0) / steps
    for _ in range(steps):
        k1 = f(a); k2 = f(a + h * k1 / 2); k3 = f(a + h * k2 / 2); k4 = f(a + h * k3); a += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    return a
def decouple(a, nl):
    return a * (1 + mpf(11) / 72 * a**2 + (mpf(564731) / 124416 - mpf(82043) * Z3 / 27648 - mpf(2633) * nl / 31104) * a**3)
def cfun(a, nf):  # two-loop mass running factor
    b0, b1 = betas(nf)[:2]; g0, g1 = mpf(1), (mpf(202) / 3 - mpf(20) * nf / 9) / 16
    return a ** (g0 / b0) * (1 + (g1 / b0 - b1 * g0 / b0**2) * a)
def running_masses(as_mz, MZ, mb, mc):
    a5_mz = as_mz / pi
    a5_mb = run(a5_mz, MZ, mb, 5); a4_mb = decouple(a5_mb, 4); a4_mc = run(a4_mb, mb, mc, 4)
    mb_MZ = mb * cfun(a5_mz, 5) / cfun(a5_mb, 5)
    mc_mb = mc * cfun(a4_mb, 4) / cfun(a4_mc, 4)
    mc_MZ = mc_mb * cfun(a5_mz, 5) / cfun(a5_mb, 5)
    return mb_MZ, mc_MZ, dict(alpha_s_mb5=a5_mb * pi, alpha_s_mc4=a4_mc * pi)

def compute(inp):
    G, MZ, ab = mpf(inp["G_mu"]), mpf(inp["MZ"]), mpf(inp["alpha_bar"])
    mt, mH, als = mpf(inp["mt"]), mpf(inp["mH"]), mpf(inp["alpha_s"])
    t, h = (mt / MZ) ** 2, (mH / MZ) ** 2
    x = pi * ab / (sqrt(2) * G * MZ**2)                       # eq. 303: s^2 c^2
    s2 = (1 - sqrt(1 - 4 * x)) / 2; c2 = 1 - s2; s, c = sqrt(s2), sqrt(c2)
    ds2 = mpf("0.23117") - s2
    Ft = F_t(t)
    T = {"m": (mpf(2) / 3 - mpf(8) / 9 * s2) * log(t) - mpf(4) / 3 + mpf(32) / 9 * s2
              + mpf(2) / 3 * (c2 - s2) * (t**3 / c2**3 - 3 * t / c2 + 2) * log(abs(1 - c2 / t))
              + mpf(2) / 3 * (c2 - s2) / c2**2 * t**2 + mpf(1) / 3 * (c2 - s2) / c2 * t
              + (mpf(2) / 3 - mpf(16) / 9 * s2 - mpf(2) / 3 * t - mpf(32) / 9 * s2 * t) * Ft,                        # eq. 34
         "A": mpf(2) / 3 - mpf(8) / 9 * s2 + mpf(16) / 27 * s2**2 - (1 - 2 * t * Ft) / (4 * t - 1)
              + (mpf(32) / 9 * s2**2 - mpf(8) / 3 * s2 - mpf(1) / 2) * (mpf(4) / 3 * t * Ft - mpf(2) / 3 * (1 + 2 * t) * (1 - 2 * t * Ft) / (4 * t - 1)),  # eq. 35
         "R": mpf(2) / 9 * log(t) + mpf(4) / 9 - mpf(2) / 9 * (1 + 11 * t) * Ft}                                 # eq. 36
    T["nu"] = T["A"]
    Fh, Fhc, Fph = F_h(h), F_h(h / c2), Fp_h(h)
    H = {"m": -h / (h - 1) * log(h) + c2 * h / (h - c2) * log(h / c2) - s2 / (18 * c2) * h - mpf(8) / 3 * s2
              + (h**2 / 9 - 4 * h / 9 + mpf(4) / 3) * Fh - (c2 - s2) * (h**2 / (9 * c2**2) - mpf(4) / 9 * h / c2 + mpf(4) / 3) * Fhc
              + (mpf("1.1205") - mpf("2.59") * ds2),
         "A": c2 / (1 - c2 / h) * log(h / c2) - 8 * h / (9 * (h - 1)) * log(h) + (mpf(4) / 3 - mpf(2) / 3 * h + mpf(2) / 9 * h**2) * Fh
              - (mpf(4) / 3 - mpf(4) / 9 * h + h**2 / 9) * Fph - h / 18 + (mpf("0.7751") + mpf("1.07") * ds2),
         "R": -mpf(4) / 3 - h / 18 + c2 / (1 - c2 / h) * log(h / c2) + (mpf(4) / 3 - mpf(4) / 9 * h + h**2 / 9) * Fh + h / (1 - h) * log(h)
              + (mpf("1.3590") + mpf("0.51") * ds2)}
    H["nu"] = H["A"]
    C = {"m": mpf("-1.3500") + mpf("4.13") * ds2, "A": mpf("-2.2619") - mpf("2.63") * ds2, "R": mpf("-3.5041") - mpf("5.72") * ds2,
         "nu": mpf("-1.1638") - mpf("4.88") * ds2}                                                                 # eqs. 501-504
    dWa = 1 / (2 * pi) * ((3 + 4 * c2) * (1 - sqrt(4 * c2 - 1) * asin(1 / (2 * c))) - mpf(1) / 3)                   # eq. 307
    dta = -4 / (9 * pi) * ((1 + 2 * t) * Ft - mpf(1) / 3)                                                          # eq. 308
    d1 = {"m": -mpf(16) / 3 * pi * s2**2 * (dWa + dta), "R": -mpf(16) / 3 * pi * s2 * c2 * (dWa + dta), "A": mpf(0), "nu": mpf(0)}
    a = als / pi
    d2q = {"m": 2 * mpf(4) / 3 * a * (c2 - s2) * log(c2), "A": 2 * mpf(4) / 3 * a * (c2 - s2 + mpf(20) / 9 * s2**2), "R": mpf(0)}  # eqs. 309-311
    d2q["nu"] = d2q["A"]
    ast = als / (1 + 23 / (12 * pi) * als * log(t)); at = ast / pi                                                 # eq. 11105a
    d2t = {"m": at * (-mpf("2.86") * t + mpf("0.46") * log(t) - mpf("1.540") - mpf("0.68") / t - mpf("0.21") / t**2),
           "A": at * (-mpf("2.86") * t + mpf("0.493") - mpf("0.19") / t - mpf("0.05") / t**2),
           "R": at * (-mpf("2.86") * t + mpf("0.22") * log(t) - mpf("1.513") - mpf("0.42") / t - mpf("0.08") / t**2)}   # eqs. 312-314
    d2t["nu"] = d2t["A"]
    d3 = -(mpf("2.38") - mpf("0.18") * 5) * ast**2 * t                                                              # eq. 315
    Afun, taub = tab1(mH / mt)
    d4 = -ab / (16 * pi * s2 * c2) * Afun * t**2                                                                    # eq. 316
    d5 = {"m": ab / (24 * pi) * h * mpf("0.747") / c2, "A": ab / (24 * pi) * h * mpf("1.199") / s2,
          "R": -ab / (24 * pi) * h * (c2 - s2) / (s2 * c2) * mpf("0.973")}                                          # eqs. 317-319
    d5["nu"] = d5["A"]
    V = {i: t + T[i] + H[i] + C[i] + d1[i] + d2q[i] + d2t[i] + d3 + d4 + d5[i] for i in ("m", "A", "R", "nu")}
    # leptons, eq. 31
    gAl = -mpf(1) / 2 - 3 * ab * V["A"] / (64 * pi * s2 * c2)
    Rl = 1 - 4 * s2 + 3 * ab * V["R"] / (4 * pi * (c2 - s2))
    gVl = gAl * Rl
    gnu = mpf(1) / 2 + 3 * ab * V["nu"] / (64 * pi * s2 * c2)
    # quarks, eqs. 320-325, 741-746, 11109-11110, 402-403
    k = ab / (4 * pi)
    FAl, FVl = k * (mpf("3.0088") + mpf("16.4") * ds2), k * (mpf("3.1868") + mpf("14.9") * ds2)
    FAu, FVu = -k * (mpf("2.6792") + mpf("14.7") * ds2), -k * (mpf("2.7319") + mpf("14.2") * ds2)
    FAd, FVd = k * (mpf("2.2212") + mpf("13.5") * ds2), k * (mpf("2.2278") + mpf("13.5") * ds2)
    KA = 128 * pi * s**3 * c**3 / (3 * ab); KR = 16 * pi * s * c * (c2 - s2) / (3 * ab)
    VAu = V["A"] + KA * (FAl + FAu); VAd = V["A"] + KA * (FAl - FAd)
    VRu = V["R"] + KR * (FVl - (1 - 4 * s2) * FAl + mpf(3) / 2 * (-(1 - mpf(8) / 3 * s2) * FAu + FVu))
    VRd = V["R"] + KR * (FVl - (1 - 4 * s2) * FAl + 3 * ((1 - mpf(4) / 3 * s2) * FAd - FVd))
    L = log(t / c2)
    phi = (3 - 2 * s2) / (2 * s2 * c2) * (t + c2 * (mpf("2.88") * L - mpf("6.716") + (mpf("8.368") * c2 * L - mpf("3.408") * c2) / t
                                                     + (mpf("9.126") * c2**2 * L + mpf("2.26") * c2**2) / t**2 + (mpf("4.043") * c2**3 * L + mpf("7.41") * c2**3) / t**3))
    dphi = (3 - 2 * s2) / (2 * s2 * c2) * (-pi**2 / 3 * at * t + 1 / (16 * s2 * c2) * (ab / pi) * t**2 * taub)
    VAb = VAd - 8 * s2 * c2 * (phi + dphi) / (3 * (3 - 2 * s2)); VRb = VRd - 4 * s2 * (c2 - s2) * (phi + dphi) / (3 * (3 - 2 * s2))
    mbZ, mcZ, mx = running_masses(als, MZ, mpf(inp["mb"]), mpf(inp["mc"]))
    I2 = -mpf("3.083") - log(t) + mpf("0.086") / t + mpf("0.013") / t**2                                          # eq. 13
    I3 = -mpf("15.988") - mpf("3.722") * log(t) + mpf("1.917") * log(t) ** 2                                      # eq. 14
    dvm = 1 + mpf("8.7") * a + mpf("45.15") * a**2; d1am = 1 + mpf("3.67") * a + (mpf("11.29") - log(t)) * a**2; d2am = mpf(8) / 81 + log(t) / 54
    def RVA(Q, T3, m):  # eqs. 11-12
        r2 = (m / MZ) ** 2
        RV = (1 + a + mpf(3) / 4 * Q**2 * ab / pi - mpf(1) / 4 * Q**2 * (ab / pi) * a + (mpf("1.409") + (mpf("0.065") + mpf("0.015") * log(t)) / t) * a**2
              - mpf("12.77") * a**3 + 12 * r2 * a * dvm)
        RA = RV - (2 * T3) * (I2 * a**2 + I3 * a**3) - 12 * r2 * a * dvm - 6 * r2 * d1am - 10 * (m / mt) ** 2 * a**2 * d2am
        return RV, RA
    G0 = G * MZ**3 / (24 * sqrt(2) * pi)                                                                          # eq. 8
    def quark(Q, T3, VA, VR, m):
        gA = T3 * (1 + 3 * ab * VA / (32 * pi * s2 * c2)); gV = gA * (1 - 4 * abs(Q) * s2 + 3 * abs(Q) * ab * VR / (4 * pi * (c2 - s2)))
        RV, RA = RVA(Q, T3, m)
        return 12 * (gA**2 * RA + gV**2 * RV) * G0, gA, gV
    up, dn = (mpf(2) / 3, mpf(1) / 2), (-mpf(1) / 3, -mpf(1) / 2)
    Gu, gAu, gVu = quark(*up, VAu, VRu, mpf(0)); Gc, _, _ = quark(*up, VAu, VRu, mcZ)
    Gd, gAd, gVd = quark(*dn, VAd, VRd, mpf(0)); Gb, gAb, gVb = quark(*dn, VAb, VRb, mbZ)
    Gs = Gd
    lep = lambda ml: 4 * G0 * (gVl**2 * (1 + 3 * ab / (4 * pi)) + gAl**2 * (1 + 3 * ab / (4 * pi) - 6 * (ml / MZ) ** 2))   # eq. 7
    Ge, Gtau, Gnu = lep(mpf(0)), lep(mpf(inp["mtau"])), 8 * gnu**2 * G0
    Gh = Gu + Gd + Gc + Gs + Gb
    GZ = Gh + 2 * Ge + Gtau + 3 * Gnu
    return dict(s2=s2, t=t, h=h, V=V, VAb=VAb, VRb=VRb, phi=phi, dphi=dphi, gAl=gAl, gVl=gVl, gnu=gnu, gAb=gAb, gVb=gVb,
                mW_over_mZ=c + 3 * c / (32 * pi * s2 * (c2 - s2)) * ab * V["m"],
                rho_l=(2 * gAl) ** 2, sin2_eff=(1 - Rl) / 4, mb_MZ=mbZ, mc_MZ=mcZ, alpha_s_mt=ast, **mx,
                Gamma_e=Ge, Gamma_tau=Gtau, Gamma_nu=Gnu, Gamma_u=Gu, Gamma_d=Gd, Gamma_c=Gc, Gamma_b=Gb, Gamma_h=Gh, Gamma_Z=GZ,
                Gamma_inv=3 * Gnu, R_ell=Gh / Ge, R_b=Gb / Gh, R_c=Gc / Gh,
                sigma_had0_GeVm2=12 * pi * Ge * Gh / (MZ**2 * GZ**2))
