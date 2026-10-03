#!/usr/bin/env python3
"""Round-p extensions of tools/cqsm_kr.py (numpy/scipy; run alone with ulimit -v 6000000):
  - generic matrix elements between grand-spin states with different (K, M): constant spin-isospin operators and
    off-diagonal (upper <-> lower) field operators with a radial factor r (for x cross alpha),
  - 1/N_c rotational sums of the time-ordered collective operators (g_A^(1), mu_V^(1), mu_S),
  - leading isovector magnetic moment mu_V^(0) (PV-regularized, vacuum-subtracted),
  - self-consistent hedgehog profile from the scalar/pseudoscalar densities (PV energy derivative).
Physics of the round-o solver is unchanged; see audit/FREEZE_2026-10-02p.md."""
import math
import numpy as np
import cqsm_kr as C

S2 = [np.array([[0, 1], [1, 0]], complex), np.array([[0, -1j], [1j, 0]]), np.array([[1, 0], [0, -1]], complex)]
I2 = np.eye(2)
EPS = np.zeros((3, 3, 3))
for a, b, c in ((0, 1, 2), (1, 2, 0), (2, 0, 1)): EPS[a, b, c], EPS[b, a, c] = 1, -1

class Ops:
    def __init__(self, ang):
        self.ang = ang
        st, ct = np.sin(ang.TH), np.cos(ang.TH)
        rh = [st * np.cos(ang.PH), st * np.sin(ang.PH), ct]
        self.tau = [np.kron(I2, S2[c]) for c in range(3)]
        self.sxt = [sum(EPS[c, a, b] * np.kron(S2[a], S2[b]) for a in range(3) for b in range(3)) for c in range(3)]   # (Sigma x tau)_c
        # (rhat x sigma)_a as (4,4,pts)
        self.rxs = []
        for a in range(3):
            f = np.zeros((4, 4, len(ang.w)), complex)
            for i in range(3):
                for j in range(3):
                    if EPS[a, i, j] != 0: f += EPS[a, i, j] * np.kron(S2[j], I2)[:, :, None] * rh[i][None, None, :]
            self.rxs.append(f)
        self.rxs_dot_tau = sum(np.einsum("ijp,jk->ikp", self.rxs[a], self.tau[a]) for a in range(3))
        self.rxs_x_tau = [sum(EPS[c, a, b] * np.einsum("ijp,jk->ikp", self.rxs[a], self.tau[b]) for a in range(3) for b in range(3)) for c in range(3)]
        self.acache, self.rcache = {}, {}

    def radial_r(self, la_l, la_k, lb_l, lb_k):
        key = (la_l, la_k, lb_l, lb_k)
        if key not in self.rcache:
            _, Fa, _ = C.RAD.funcs(la_l, la_k); _, Fb, _ = C.RAD.funcs(lb_l, lb_k)
            self.rcache[key] = np.einsum("p,pn,pm->nm", C.RAD.w * C.RAD.r, Fa, Fb)
        return self.rcache[key]

    def pair(self, ent1, K1, M1, ent2, K2, M2, op, name, kind):
        """<ent1 states, K1 M1| op |ent2 states, K2 M2>; kind 'const' (same upper/lower type, same l) or 'rfield' (upper<->lower, radial r)"""
        ang = self.ang; e1, v1, b1, o1 = ent1; e2, v2, b2, o2 = ent2
        A = np.zeros((o1[-1], o2[-1]), complex)
        for ia, (ta, ca, la) in enumerate(b1):
            for ib, (tb, cb, lb) in enumerate(b2):
                if kind == "const":
                    if ta != tb or ca[0] != cb[0]: continue
                elif ta == tb or abs(ca[0] - cb[0]) != 1: continue
                key = (name, ca, cb, K1, M1, K2, M2)
                if key not in self.acache:
                    pa, pb = ang.phi(ca[0], ca[1], K1, M1), ang.phi(cb[0], cb[1], K2, M2)
                    self.acache[key] = ang.mat_const(pa, pb, op) if kind == "const" else ang.mat_field(pa, pb, op)
                c = self.acache[key]
                if abs(c) < 1e-12: continue
                R = C.ovl(ca[0], la, lb) if kind == "const" else self.radial_r(ca[0], la, cb[0], lb)
                A[o1[ia]:o1[ia + 1], o2[ib]:o2[ib + 1]] = c * R
        return v1.conj().T @ A @ v2

def occ_mask(e, K, P, ev):
    m = e < 0
    if (K, P) == (0, 1) and ev is not None: m = m | (np.abs(e - ev) < 1e-12)
    return m

def rot_sum(O, sp, ev, X, Y):
    """Sum_c Sum_{n unocc, m occ} <n|X_c|m><m|Y_c|n>/(e_n - e_m), all M substates (scalar contraction: M1 = 0 times 2K1+1).
    X, Y: lists over c of (op, name, kind)."""
    tot = 0.0 + 0.0j
    for (K1, P1), a in sp.items():
        un = ~occ_mask(a[0], K1, P1, ev)
        for (K2, P2), b in sp.items():
            if P2 != P1 or abs(K2 - K1) > 1: continue
            oc = occ_mask(b[0], K2, P2, ev)
            if not un.any() or not oc.any(): continue
            den = a[0][un][:, None] - b[0][oc][None, :]
            for M2 in (-1, 0, 1):
                if abs(M2) > K2: continue
                for (xo, xn, xk), (yo, yn, yk) in zip(X, Y):
                    Xm = O.pair(a, K1, 0, b, K2, M2, xo, xn, xk)[np.ix_(un, oc)]
                    Ym = O.pair(b, K2, M2, a, K1, 0, yo, yn, yk)[np.ix_(oc, un)]
                    tot += (2 * K1 + 1) * np.sum(Xm * Ym.T / den)
    return tot

def diag_scalar(O, sp, op, name, kind, ev=None, want_val=False):
    """(-1/2) Sum (2K+1) sign(e) <n|op|n> for a K-scalar operator; optionally the valence expectation"""
    tot, val = 0.0, None
    for (K, P), a in sp.items():
        Mz = 0 if K == 0 else K
        d = np.real(np.diag(O.pair(a, K, Mz, a, K, Mz, op, name, kind)))
        tot += -0.5 * (2 * K + 1) * np.sum(np.sign(a[0]) * d)
        if want_val and (K, P) == (0, 1):
            val = d[int(np.argmin(np.abs(a[0] - ev)))]
    return tot, val

def densities(sp, ang, rad):
    """per-sector weighted helper: returns function giving (s_n(r), p_n(r)) arrays (nr x nstates) for a sector entry"""
    def sector(K, ent):
        e, v, blocks, off = ent; Mz = 0 if K == 0 else K
        U = []; Lw = []
        for i, (t, c, lk) in enumerate(blocks):
            _, F, _ = rad.funcs(c[0], lk); u = F @ v[off[i]:off[i + 1], :]
            (U if t == "U" else Lw).append((c, u))
        s = sum(np.abs(u) ** 2 for _, u in U) - sum(np.abs(u) ** 2 for _, u in Lw)
        p = np.zeros_like(s)
        for ca, ua in U:
            for cb, ub in Lw:
                T = ang.mat_field(ang.phi(ca[0], ca[1], K, Mz), ang.phi(cb[0], cb[1], K, Mz), ang.tr)
                if abs(T) > 1e-12: p += 2 * np.real(np.conj(ua) * (1j * T) * ub)
        return s, p
    return sector

def sc_force(sp1, sp2, Mpv, ang, rad, Nc, ev):
    S = np.zeros(len(rad.r)); P = np.zeros(len(rad.r)); sec = densities(None, ang, rad)
    for sp, wsea, withval in ((sp1, -0.5 * Nc, True), (sp2, 0.5 * Nc / Mpv, False)):
        for (K, Pp), ent in sp.items():
            s, p = sec(K, ent); w = wsea * np.sign(ent[0]) * (2 * K + 1)
            if withval and (K, Pp) == (0, 1):
                i = int(np.argmin(np.abs(ent[0] - ev))); w = w.copy(); w[i] += Nc
            S += s @ w; P += p @ w
    return S, P

def profile_fn(rad, th_arr):
    rr = rad.r.copy(); tt = th_arr.copy()
    return lambda r: np.interp(r, rr, tt)

def self_consistent(th0, Mpv, ang, rad, Kmax, Nc, vac, mix=0.5, itmax=60, tol=1e-4, log=print):
    th = th0(rad.r).copy(); hist = []
    for it in range(itmax):
        f = profile_fn(rad, th)
        s1 = C.spectrum(f, 1.0, ang, rad, Kmax, True); s2 = C.spectrum(f, Mpv, ang, rad, Kmax, True)
        ev = C.valence(s1)
        E = Nc * max(ev, 0.0) - 0.5 * Nc * ((C.esum(s1) - vac[0]) - (1.0 / Mpv) ** 2 * (C.esum(s2) - vac[1])) if ev is not None else float("nan")
        if ev is None: hist.append((it, None, None, None)); log("sc", it, "valence lost"); return th, False, hist
        S, P = sc_force(s1, s2, Mpv, ang, rad, Nc, ev)
        new = np.arctan2(-P, -S); new = np.unwrap(new[::-1])[::-1]
        if new[0] > 0: new = new - 2 * np.pi * round(new[0] / (2 * np.pi))
        d = float(np.max(np.abs(new - th))); hist.append((it, float(E), float(ev), d)); log("sc", it, "E", E, "ev", ev, "dtheta", d, "theta(0)", float(new[0]))
        if d < tol: return new, True, hist
        th = (1 - mix) * th + mix * new
    return th, False, hist

def observables(th_fn, Mpv, ang, rad, Kmax, Nc, vac, v1, v2, O):
    s1 = C.spectrum(th_fn, 1.0, ang, rad, Kmax, True); s2 = C.spectrum(th_fn, Mpv, ang, rad, Kmax, True)
    ev = C.valence(s1)
    E = Nc * max(ev, 0.0) - 0.5 * Nc * ((C.esum(s1) - vac[0]) - (1.0 / Mpv) ** 2 * (C.esum(s2) - vac[1]))
    g0, g0v, g0s = C.gA0(s1, s2, Mpv, ang, Kmax, Nc, ev, v1, v2)
    I = C.inertia(s1, s2, Mpv, ang, Kmax, Nc, ev)
    A = rot_sum(O, s1, ev, [(O.sxt[c], "sxt%d" % c, "const") for c in range(3)], [(O.tau[c], "tau%d" % c, "const") for c in range(3)]) / 6.0
    Amu = rot_sum(O, s1, ev, [(O.rxs_x_tau[c], "rxt%d" % c, "rfield") for c in range(3)], [(O.tau[c], "tau%d" % c, "const") for c in range(3)]) / 6.0
    B = rot_sum(O, s1, ev, [(O.tau[c], "tau%d" % c, "const") for c in range(3)], [(O.rxs[c], "rxs%d" % c, "rfield") for c in range(3)])
    # mu_V^(0): PV-regularized, vacuum-subtracted, valence included
    tot = 0.0; val = None
    for wt, sp in ((1.0, s1), (-(1.0 / Mpv) ** 2, s2), (-1.0, v1), ((1.0 / Mpv) ** 2, v2)):
        t, vv = diag_scalar(O, sp, O.rxs_dot_tau, "rdt", "rfield", ev, sp is s1)
        tot += wt * t
        if vv is not None: val = vv
    return {"E_sol_over_M": float(E), "eps_val": float(ev), "gA0": float(g0), "gA0_val": float(g0v), "gA0_sea": float(g0s), "I_times_M": float(I),
            "A_re": float(A.real), "A_im": float(A.imag), "Amu_re": float(Amu.real), "Amu_im": float(Amu.imag), "B_re": float(B.real), "B_im": float(B.imag),
            "xat_val": float(val), "xat_sea": float(tot)}
