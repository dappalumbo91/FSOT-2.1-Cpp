#!/usr/bin/env python3
"""Chiral quark soliton with the full Dirac sea in a Kahana-Ripka-type grand-spin basis (FREEZE_2026-10-02o, O-1).

Units: M = 1 (constituent mass). H = alpha.p + beta M (cos th + i gamma5 tau.rhat sin th), th(r) = 2 arctan(x^2/r^2).
Components: upper phi = sum_a g_a(r) Phi_a, lower chi = sum_b f_b(r) Phi_b, Phi = |l j K M> spinor-isospinor.
  E g = M cos th g - i S (d/dr - kappa/r) f + i M sin th T f ;  lower-upper block = Hermitian conjugate (r^2 dr measure).
Radial basis per component: j_l(k_n r), j_l(k_n D) = 0, k_n <= kmax. Requires numpy, scipy (run alone; results cached to JSON).
"""
import math, json, sys
import numpy as np
from scipy.special import spherical_jn, sph_harm_y
from scipy.optimize import brentq

def cg(j1, m1, j2, m2, J, M):
    if abs(m1 + m2 - M) > 1e-9 or J < abs(j1 - j2) - 1e-9 or J > j1 + j2 + 1e-9 or abs(m1) > j1 + 1e-9 or abs(m2) > j2 + 1e-9 or abs(M) > J + 1e-9:
        return 0.0
    f = math.factorial; r = lambda v: int(round(v))
    pre = math.sqrt((2 * J + 1) * f(r(J + j1 - j2)) * f(r(J - j1 + j2)) * f(r(j1 + j2 - J)) / f(r(j1 + j2 + J + 1)))
    pre *= math.sqrt(f(r(J + M)) * f(r(J - M)) * f(r(j1 - m1)) * f(r(j1 + m1)) * f(r(j2 - m2)) * f(r(j2 + m2)))
    s = 0.0
    for k in range(0, 200):
        d = [k, r(j1 + j2 - J - k), r(j1 - m1 - k), r(j2 + m2 - k), r(J - j2 + m1 + k), r(J - j1 - m2 + k)]
        if min(d) < 0:
            if d[1] < 0 or d[2] < 0 or d[3] < 0: break
            continue
        s += (-1) ** k / math.prod(f(v) for v in d)   # exact integer product (np.prod overflowed int64)
    return pre * s

class Angular:
    def __init__(self, Kmax):
        n = 2 * Kmax + 12
        x, w = np.polynomial.legendre.leggauss(n); self.th = np.arccos(x); nphi = 2 * n
        self.ph = 2 * np.pi * np.arange(nphi) / nphi
        TH, PH = np.meshgrid(self.th, self.ph, indexing="ij"); self.TH, self.PH = TH.ravel(), PH.ravel()
        self.w = np.repeat(w, nphi) * (2 * np.pi / nphi)
        st, ct = np.sin(self.TH), np.cos(self.TH); e = np.exp(1j * self.PH)
        P = np.array([[ct, st / e], [st * e, -ct]])            # (pauli . rhat)[i,j](pts)
        I2 = np.eye(2)
        # operators on 4-index s*2+t, as (4,4,pts) arrays
        self.sr = np.einsum("ijp,kl->ikjlp", P, I2).reshape(4, 4, -1)
        self.tr = np.einsum("ij,klp->ikjlp", I2, P).reshape(4, 4, -1)
        sig = [np.array([[0, 1], [1, 0]]), np.array([[0, -1j], [1j, 0]]), np.array([[1, 0], [0, -1]])]
        self.st = sum(np.kron(s, s) for s in sig); self.tz = np.kron(I2, sig[2])
        self.cache = {}
    def phi(self, l, j, K, M):
        key = (l, j, K, M)
        if key not in self.cache:
            out = np.zeros((len(self.w), 4), complex)
            for mt in (0.5, -0.5):
                mj = M - mt
                c1 = cg(j, mj, 0.5, mt, K, M)
                if c1 == 0.0: continue
                for ms in (0.5, -0.5):
                    ml = mj - ms
                    if abs(ml) > l: continue
                    c2 = cg(l, ml, 0.5, ms, j, mj)
                    if c2 == 0.0: continue
                    Y = sph_harm_y(l, int(round(ml)), self.TH, self.PH)
                    out[:, (0 if ms > 0 else 1) * 2 + (0 if mt > 0 else 1)] += c1 * c2 * Y
            self.cache[key] = out
        return self.cache[key]
    def mat_field(self, A, B, op):   # <A| op(pts) |B>
        return np.einsum("p,pi,ijp,pj->", self.w, A.conj(), op, B)
    def mat_const(self, A, B, op):
        return np.einsum("p,pi,ij,pj->", self.w, A.conj(), op, B)

def comps(K, P):
    js = [K - 0.5, K + 0.5] if K > 0 else [0.5]
    allc = [(int(round(j + s)), j) for j in js for s in (-0.5, 0.5)]
    U = [c for c in allc if (-1) ** c[0] == P]; L = [c for c in allc if (-1) ** c[0] == -P]
    return U, L

def kappa(l, j): return j * (j + 1) - l * (l + 1) - 0.75

class Radial0:
    def __init__(self, D, kmax, nq=1500):
        self.D, self.kmax = D, kmax
        x, w = np.polynomial.legendre.leggauss(nq); self.r = 0.5 * D * (x + 1); self.w = 0.5 * D * w * self.r ** 2
        self.cache = {}
    def basis(self, l):
        if l not in self.cache:
            zs = []; xs = np.linspace(1e-6, self.kmax * self.D + 3, int(40 * self.kmax * self.D) + 400)
            v = spherical_jn(l, xs)
            for i in range(len(xs) - 1):
                if v[i] * v[i + 1] < 0:
                    z = brentq(lambda t: spherical_jn(l, t), xs[i], xs[i + 1])
                    if z / self.D <= self.kmax: zs.append(z / self.D)
            k = np.array(zs); kr = np.outer(self.r, k)
            F = spherical_jn(l, kr); dF = spherical_jn(l, kr, derivative=True) * k[None, :]
            nrm = np.sqrt(np.einsum("p,pn,pn->n", self.w, F, F)); self.cache[l] = (k, F / nrm, dF / nrm)
        return self.cache[l]

class Radial:
    """KR choice: each j-pair (upper l_U, lower l_L) shares the momenta k_n with j_{l_U}(k_n D) = 0; lower functions Lowdin-orthonormalized."""
    def __init__(self, D, kmax, nq=1500):
        self.D, self.kmax = D, kmax
        x, w = np.polynomial.legendre.leggauss(nq); self.r = 0.5 * D * (x + 1); self.w = 0.5 * D * w * self.r ** 2
        self.zc, self.cache = {}, {}
    def kset(self, l):
        if l not in self.zc:
            zs = []; xs = np.linspace(1e-6, self.kmax * self.D + 3, int(40 * self.kmax * self.D) + 400); v = spherical_jn(l, xs)
            for i in range(len(xs) - 1):
                if v[i] * v[i + 1] < 0:
                    z = brentq(lambda t: spherical_jn(l, t), xs[i], xs[i + 1])
                    if z / self.D <= self.kmax: zs.append(z / self.D)
            self.zc[l] = np.array(zs)
        return self.zc[l]
    def funcs(self, l, lk):
        key = (l, lk)
        if key not in self.cache:
            k = self.kset(lk); kr = np.outer(self.r, k)
            F = spherical_jn(l, kr); dF = spherical_jn(l, kr, derivative=True) * k[None, :]
            O = np.einsum("p,pn,pm->nm", self.w, F, F); ev, U = np.linalg.eigh(O); X = U @ np.diag(ev ** -0.5) @ U.T
            self.cache[key] = (k, F @ X, dF @ X)
        return self.cache[key]

def pair_l(c, K, P):
    """momentum-set label: the upper orbital of the j-pair containing component c"""
    l, j = c; U, L = comps(K, P)
    for cu in U:
        if cu[1] == j: return cu[0]
    return l

def sector_H(K, P, th, Mass, ang, rad):
    U, L = comps(K, P); cth, sth = np.cos(th(rad.r)), np.sin(th(rad.r))
    blocks = [("U", c) for c in U] + [("L", c) for c in L]
    R = {c: rad.funcs(c[0], pair_l(c, K, P)) for _, c in blocks}
    sizes = [len(R[c][0]) for _, c in blocks]; off = np.concatenate([[0], np.cumsum(sizes)]); N = off[-1]
    H = np.zeros((N, N), complex); Mz = 0 if K == 0 else K   # any M; use M = K (exists for all K)
    Phi = {c: ang.phi(c[0], c[1], K, Mz) for _, c in blocks}
    for ia, (ta, ca) in enumerate(blocks):
        ka, Fa, dFa = R[ca]
        for ib, (tb, cb) in enumerate(blocks):
            kb, Fb, dFb = R[cb]
            sl = np.s_[off[ia]:off[ia + 1], off[ib]:off[ib + 1]]
            if ta == tb and ca == cb:
                sgn = 1.0 if ta == "U" else -1.0
                H[sl] += sgn * Mass * np.einsum("p,pn,pm->nm", rad.w, Fa, cth[:, None] * Fb)
            if ta == "U" and tb == "L":
                S = ang.mat_field(Phi[ca], Phi[cb], ang.sr); T = ang.mat_field(Phi[ca], Phi[cb], ang.tr)
                kin = np.einsum("p,pn,pm->nm", rad.w, Fa, dFb - kappa(*cb) * Fb / rad.r[:, None])
                pot = np.einsum("p,pn,pm->nm", rad.w, Fa, sth[:, None] * Fb)
                H[sl] += -1j * S * kin + 1j * Mass * T * pot
    nU = off[len(U)]; H[nU:, :nU] = H[:nU, nU:].conj().T
    return H, [(t, c, pair_l(c, K, P)) for t, c in blocks], off

def spectrum(th, Mass, ang, rad, Kmax, want_vecs=False):
    out = {}
    for K in range(Kmax + 1):
        for P in (1, -1):
            H, blocks, off = sector_H(K, P, th, Mass, ang, rad)
            if want_vecs:
                e, v = np.linalg.eigh(H); out[(K, P)] = (e, v, blocks, off)
            else:
                out[(K, P)] = (np.linalg.eigvalsh(H),)
    return out

def esum(sp):
    return sum((2 * K + 1) * np.sum(np.abs(v[0])) for (K, P), v in sp.items())

def valence(sp):
    e = sp[(0, 1)][0]; c = e[(e > -1.0) & (e < 1.0)]
    return float(c[np.argmax(c)]) if len(c) else None

def energy(x, Mpv, ang, rad, Kmax, Nc, vac):
    th = lambda r: -2 * np.arctan(x * x / (r * r))   # sign: baryon-number-one hedgehog in this phase convention
    s1 = spectrum(th, 1.0, ang, rad, Kmax); s2 = spectrum(th, Mpv, ang, rad, Kmax)
    ev = valence(s1)
    sea = -0.5 * Nc * ((esum(s1) - vac[0]) - (1.0 / Mpv) ** 2 * (esum(s2) - vac[1]))
    return Nc * max(ev, 0.0) + sea, ev, sea

RAD = None
def ovl(l, la, lb):
    _, Fa, _ = RAD.funcs(l, la); _, Fb, _ = RAD.funcs(l, lb)
    return np.einsum("p,pn,pm->nm", RAD.w, Fa, Fb)

def op_diag(sp_entry, ang, K, op):
    e, v, blocks, off = sp_entry; Mz = 0 if K == 0 else K
    A = np.zeros((off[-1], off[-1]), complex)
    for ia, (ta, ca, la) in enumerate(blocks):
        for ib, (tb, cb, lb) in enumerate(blocks):
            if ta == tb and ca[0] == cb[0]:
                c = ang.mat_const(ang.phi(ca[0], ca[1], K, Mz), ang.phi(cb[0], cb[1], K, Mz), op)
                if abs(c) > 1e-12:
                    A[off[ia]:off[ia + 1], off[ib]:off[ib + 1]] = c * ovl(ca[0], la, lb)
    return np.real(np.einsum("in,ij,jn->n", v.conj(), A, v))

def gA0(sp1, sp2, Mpv, ang, Kmax, Nc, ev, vac1, vac2):
    """vacuum-subtracted (theta = 0 spectra vac1, vac2) so that the K-truncation of isovector sums cancels"""
    tot = 0.0; val = None
    for wt, sp in ((1.0, sp1), (-(1.0 / Mpv) ** 2, sp2), (-1.0, vac1), ((1.0 / Mpv) ** 2, vac2)):
        for (K, P), ent in sp.items():
            d = op_diag(ent, ang, K, ang.st) / 3.0            # <Sigma_3 tau_3> per M-state = <Sigma.tau>/3
            tot += wt * (-0.5) * (2 * K + 1) * np.sum(np.sign(ent[0]) * d)
            if sp is sp1 and (K, P) == (0, 1):
                i = int(np.argmin(np.abs(ent[0] - ev))); val = d[i]
    return -(Nc / 3.0) * (val + tot), -(Nc / 3.0) * val, -(Nc / 3.0) * tot

def tz_pair(ent1, K1, ent2, K2, ang, M):
    e1, v1, b1, o1 = ent1; e2, v2, b2, o2 = ent2
    A = np.zeros((o1[-1], o2[-1]), complex)
    for ia, (ta, ca, la) in enumerate(b1):
        for ib, (tb, cb, lb) in enumerate(b2):
            if ta == tb and ca[0] == cb[0]:
                c = ang.mat_const(ang.phi(ca[0], ca[1], K1, M), ang.phi(cb[0], cb[1], K2, M), ang.tz)
                if abs(c) > 1e-12:
                    A[o1[ia]:o1[ia + 1], o2[ib]:o2[ib + 1]] = c * ovl(ca[0], la, lb)
    return v1.conj().T @ A @ v2

def inertia(sp1, sp2, Mpv, ang, Kmax, Nc, ev):
    """Cranking: I = Nc/2 sum_{occ n, unocc m} sum_M |<m|tau_z|n>|^2/(e_m - e_n); valence occupied; PV-subtracted sea."""
    tot = 0.0
    for wt, sp, withval in ((1.0, sp1, True), (-(1.0 / Mpv) ** 2, sp2, False)):
        for (K1, P1), a in sp.items():
            for (K2, P2), b in sp.items():
                if P1 != P2 or abs(K1 - K2) > 1: continue
                for M in range(-min(K1, K2), min(K1, K2) + 1):
                    X = np.abs(tz_pair(a, K1, b, K2, ang, M)) ** 2   # rows: states of a, cols: b
                    ea, eb = a[0], b[0]
                    occ_a = ea < 0; occ_b = eb < 0
                    if withval and (K1, P1) == (0, 1): occ_a = occ_a | (np.abs(ea - ev) < 1e-12)
                    if withval and (K2, P2) == (0, 1): occ_b = occ_b | (np.abs(eb - ev) < 1e-12)
                    den = eb[None, :] - ea[:, None]
                    m = occ_a[:, None] & (~occ_b[None, :])
                    tot += wt * 0.5 * Nc * np.sum(X[m] / den[m])
    return tot

def run(x_scan, Mpv, D, kmax, Kmax, Nc=3):
    global RAD
    ang = Angular(Kmax); rad = Radial(D, kmax); RAD = rad
    zero = lambda r: 0.0 * r
    v1 = spectrum(zero, 1.0, ang, rad, Kmax, True); v2 = spectrum(zero, Mpv, ang, rad, Kmax, True); vac = (esum(v1), esum(v2))
    scan = [(x,) + energy(x, Mpv, ang, rad, Kmax, Nc, vac) for x in x_scan]
    k = min(range(len(scan)), key=lambda i: scan[i][1])
    res = {"scan": [[float(a) for a in s] for s in scan], "edge_minimum": k in (0, len(scan) - 1)}
    if 0 < k < len(scan) - 1:   # parabola through the three points
        (x0, y0), (x1, y1), (x2, y2) = [(scan[i][0], scan[i][1]) for i in (k - 1, k, k + 1)]
        den = (x0 - x1) * (x0 - x2) * (x1 - x2); A = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / den
        B = (x2 * x2 * (y0 - y1) + x1 * x1 * (y2 - y0) + x0 * x0 * (y1 - y2)) / den; xs = -B / (2 * A)
    else:
        xs = scan[k][0]
    th = lambda r: -2 * np.arctan(xs * xs / (r * r))
    s1 = spectrum(th, 1.0, ang, rad, Kmax, True); s2 = spectrum(th, Mpv, ang, rad, Kmax, True)
    E, ev, sea = energy(xs, Mpv, ang, rad, Kmax, Nc, vac)
    g, gv, gs = gA0(s1, s2, Mpv, ang, Kmax, Nc, ev, v1, v2)
    I = inertia(s1, s2, Mpv, ang, Kmax, Nc, ev)
    res.update({"x": float(xs), "E_sol_over_M": float(E), "eps_val": ev, "E_sea_over_M": float(sea), "gA0": float(g), "gA0_val": float(gv), "gA0_sea": float(gs),
                "I_times_M": float(I), "D": D, "kmax": kmax, "Kmax": Kmax, "Mpv_over_M": Mpv})
    return res

if __name__ == "__main__":
    print("module; use tools/heavy_2026_10_02o.py")
