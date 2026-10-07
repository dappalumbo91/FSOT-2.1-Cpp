// fsot/host/neutral_mesons.hpp — the four neutral masses, each on its own branch.
//
// K0 is the quark-route Dashen mass with the strange ratio carried one base-5
// place, y = e^3 + gamma^(21/5). pi0 is the two-tank fixed point of the D=6 and
// D=7 scalars, times (1 - gamma^4 alpha^2). eta is the y-scaled axial 3x3
// eigenvalue times (1 + alpha/phi^2 + alpha^2). eta-prime is the kaon-leaf 3x3
// with the pin singlet divided by the axial ratio and dressed by (1 + alpha/4).
// Alpha is the inverse-alpha leaf. These rows are not on the 91. The pin stays AEB2AD.
#pragma once
#include "fsot/host/seed_leaves.hpp"

namespace fsot::neutral {

template <class R> struct Scored {
  R value;
  R center;
  R sigma;
  R z() const { return (value - center) / sigma; }
};

template <class R> struct Triple {
  R pi0;
  R eta;
  R etap;
};

template <class R> inline void sort3(R& a, R& b, R& c) {
  if (a > b) { const R t = a; a = b; b = t; }
  if (b > c) { const R t = b; b = c; c = t; }
  if (a > b) { const R t = a; a = b; b = t; }
}

// Symmetric 3x3 Jacobi. Numerical Recipes form: tau = (aqq-app)/(2 apq).
template <class R> inline void eigen3(R m[3][3], R out[3]) {
  for (int sweep = 0; sweep < 24; ++sweep) {
    for (int p = 0; p < 3; ++p) {
      for (int q = p + 1; q < 3; ++q) {
        const R apq = m[p][q];
        const R scale = m::fabs(m[p][p]) + m::fabs(m[q][q]) + R(1);
        if (m::fabs(apq) <= lit<R>("1e-40") * scale) continue;
        const R tau = (m[q][q] - m[p][p]) / (R(2) * apq);
        const R t = (tau >= 0 ? R(1) : R(-1)) / (m::fabs(tau) + m::sqrt(R(1) + tau * tau));
        const R c = R(1) / m::sqrt(R(1) + t * t);
        const R s = t * c;
        m[p][p] -= t * apq;
        m[q][q] += t * apq;
        m[p][q] = m[q][p] = R(0);
        for (int r = 0; r < 3; ++r) {
          if (r == p || r == q) continue;
          const R rp = m[r][p];
          const R rq = m[r][q];
          m[r][p] = m[p][r] = c * rp - s * rq;
          m[r][q] = m[q][r] = s * rp + c * rq;
        }
      }
    }
  }
  out[0] = m[0][0];
  out[1] = m[1][1];
  out[2] = m[2][2];
  sort3(out[0], out[1], out[2]);
}

template <class R> struct Masses {
  const leaves::SeedLeaves<R>& L;
  explicit Masses(const leaves::SeedLeaves<R>& leaves) : L(leaves) {}

  R alpha() const { return L.alpha(); }
  R pion() const { return L.pion_MeV(); }
  R kaon() const {
    const auto& F = L.F;
    return m::pow(F.G_CAT, R(-7)) + m::pow(F.P_BASE, R(-4)) - m::pow(F.PI, R(-4));
  }
  R x_ud() const { return m::sqrt(R(3)) - m::sqrt(L.F.PHI); }
  R proton_MeV() const { return L.mev(L.proton_ratio() * L.m_e_kg()); }
  R chiral_F() const { return proton_MeV() / (R(2) * m::sqrt(R(3)) * L.F.PI); }

  // Frozen axial ratio extended by the charged-pion mass: x_r = (1+sqrt(3))/2,
  // xi = M_pi^2 / (16 pi^2 F^2), R = 1 + (x_r-1)(1 + 6 xi / x_r).
  R axial_ratio() const {
    const R xr = (R(1) + m::sqrt(R(3))) / R(2);
    const R xi = pion() * pion() / (R(16) * L.F.PI * L.F.PI * chiral_F() * chiral_F());
    return R(1) + (xr - R(1)) * (R(1) + (R(6) / xr) * xi);
  }

  // Dashen shift at that ratio: 6 pi alpha F^2 * R ln(R) / (R-1).
  // At R=2 this is 12 pi alpha ln(2) F^2.
  R axial_D() const {
    const R ratio = axial_ratio();
    const R F = chiral_F();
    return R(6) * L.F.PI * alpha() * F * F * ratio * m::ln(ratio) / (ratio - R(1));
  }

  // Pin singlet M0 = sqrt(6 chi) / F, chi = (C_cosm - e^{-3})/8, in MeV.
  R singlet_MeV() const {
    const R pin = L.F.C_COSM - m::exp(R(-3));
    const R chi = pin / R(8);
    const R f_gev = chiral_F() / R(1000);
    return m::sqrt(R(6) * chi) / f_gev * R(1000);
  }

  R rung_scalar(int depth) const { return L.F.scalar_from_fold(depth, R(1), 0, true); }

  // Two-tank balance of the D=6 and D=7 scalars. gamma = |Chaos| + psi_con*Poof.
  // kappa = A_bleed * Poof * |S6| * |S7| / (1 + |6-7|/25). The mix weight is
  // YY = Poof/(Poof+Suction). The arithmetic midpoint of the two scalars is not used.
  R bleed_mass() const {
    const auto& F = L.F;
    const R s6 = rung_scalar(6);
    const R s7 = rung_scalar(7);
    const R yy = F.POOF / (F.POOF + F.SUCTION);
    const R gamma = m::fabs(F.CHAOS) + F.PSI_CON * F.POOF;
    const R kappa = F.A_BLEED * F.POOF * m::fabs(s6) * m::fabs(s7) / (R(1) + R(1) / R(25));
    const R pull = kappa / (R(2) * kappa + gamma);
    const R delta = pull * (s7 - s6);
    const R mix = (R(1) - yy) * (s6 + delta) + yy * (s7 - delta);
    const R bare = m::pow(F.B_IN, R(-2)) + m::pow(F.THETA_S, R(-4));
    return bare * mix;
  }

  // leaf_strange uses the charged-kaon leaf. Otherwise Bm_s = y_scale * Bm_d.
  Triple<R> eigenvalues(const R& m0, const R& y_scale, bool leaf_strange) const {
    const R mpi = pion();
    const R mk = kaon();
    const R x = x_ud();
    const R d = axial_D();
    const R m33 = mpi * mpi - d;
    const R bm = m33 / R(2);
    const R bm_u = m33 * x / (R(1) + x);
    const R bm_d = m33 / (R(1) + x);
    const R bm_s = leaf_strange ? (mk * mk - d - bm_u) : (y_scale * bm_d);
    const R m88 = (R(2) / R(3)) * (bm + R(2) * bm_s);
    const R m08 = -(R(2) * m::sqrt(R(2)) / R(3)) * (bm_s - bm);
    const R m38 = m33 * (x - R(1)) / ((R(1) + x) * m::sqrt(R(3)));
    const R m03 = m::sqrt(R(2) / R(3)) * m33 * (x - R(1)) / (R(1) + x);
    const R m00 = (R(2) / R(3)) * (R(2) * bm + bm_s) + m0 * m0;
    R a[3][3] = {{m33, m38, m03}, {m38, m88, m08}, {m03, m08, m00}};
    R ev[3];
    eigen3(a, ev);
    return {m::sqrt(ev[0]), m::sqrt(ev[1]), m::sqrt(ev[2])};
  }

  Scored<R> k0() const {
    const R y = m::ipow(L.F.E, 3) + m::pow(L.F.GAMMA, R(21) / R(5));
    const R mpi = pion();
    const R mk = kaon();
    const R b = (mk * mk - mpi * mpi) / (y - R(1));
    return {m::sqrt(b * (R(1) + y)), lit<R>("497.611"), lit<R>("0.013")};
  }

  Scored<R> pi0() const {
    const R dressed = R(1) - m::ipow(L.F.GAMMA, 4) * alpha() * alpha();
    return {bleed_mass() * dressed, lit<R>("134.9768"), lit<R>("0.0005")};
  }

  Scored<R> eta() const {
    const R y4 = m::ipow(L.F.E, 3) + m::ipow(L.F.GAMMA, 4);
    const R bare = eigenvalues(singlet_MeV(), y4, false).eta;
    const R dress = R(1) + alpha() / (L.F.PHI * L.F.PHI) + alpha() * alpha();
    return {bare * dress, lit<R>("547.862"), lit<R>("0.017")};
  }

  Scored<R> etap() const {
    const R m0 = (singlet_MeV() / axial_ratio()) * (R(1) + alpha() / R(4));
    const R mass = eigenvalues(m0, R(0), true).etap;
    return {mass, lit<R>("957.78"), lit<R>("0.06")};
  }
};

}  // namespace fsot::neutral
