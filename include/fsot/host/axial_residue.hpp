// fsot/host/axial_residue.hpp — one-loop axial residue at the charged-pion leaf.
//
// The installed truncation stays F (1 + ξ ℓ̄₄), with ℓ̄₄ = 3 + ln(M_σ²/M_π²) − C4
// and C4 = (19 − 3√3 π)/2. This file is the next term of that same residue: the
// exact tree vev, the σπ bubble counted once, and one third of the light tadpole
// on the curvature that holds the pion pole. It is not a record row.
//
// Units F = 1 inside the loop. M² = 16π²/3, λ = 8π²/3, ξ = M_π²/(16π² F²).
// φ = √(1+6ξ). The bubble vertex is −2λφ, so κ = 4λ²φ²/(16π²) = (M²/3) φ².
// The chiral kinetic counterterm is λ/(16π²) = 1/6, removed once.
//
// The full three-pion vacuum force linearizes to log coefficient 3/2. With the
// bubble's 1/2 that sum is 2. One third of the force is the share that leaves
// the coefficient of −ξ ln ξ equal to 1. That 1/3 is the coefficient constraint.
// It is not a flavor trace and it is not chosen to meet the lifetime center.
// The sigma-mass denominator M²(1+9ξ) is evaluated beside the residue and is not it.
#pragma once
#include "fsot/real.hpp"

namespace fsot::axial {

template <class R> struct LifetimeBar {
  R center;  // 130.56/√2 MeV, PDG 2026 review eq. 71.23
  R sigma;   // quadrature of (0.02), (0.04), (0.13), divided by √2
};

template <class R> inline LifetimeBar<R> lifetime_bar() {
  const R root2 = m::sqrt(R(2));
  const R a = lit<R>("0.02"), b = lit<R>("0.04"), c = lit<R>("0.13");
  return {lit<R>("130.56") / root2, m::sqrt(a * a + b * b + c * c) / root2};
}

template <class R> inline R c4() {
  return (R(19) - R(3) * m::sqrt(R(3)) * real_traits<R>::pi()) / R(2);
}

namespace detail {

template <class R> struct MapNode { R x; R dxdt; bool live; };

// x = (1 + tanh((π/2) sinh t))/2. Weights below ~1e-69 are dropped; that is
// past the 169-bit unit in the last place of an O(1) integrand.
template <class R> inline MapNode<R> tanh_sinh_node(const R& t) {
  const R pi = real_traits<R>::pi();
  const R et = m::exp(t);
  const R sinh_t = (et - R(1) / et) / R(2);
  const R cosh_t = (et + R(1) / et) / R(2);
  const R au = m::fabs((pi / R(2)) * sinh_t);
  if (au > R(80)) return {sinh_t >= 0 ? R(1) : R(0), R(0), false};
  const R e2 = m::exp(-R(2) * au);
  const R tanh_abs = (R(1) - e2) / (R(1) + e2);
  const R tanh_u = sinh_t >= 0 ? tanh_abs : -tanh_abs;
  const R eu = m::exp(-au);
  const R sech = R(2) * eu / (R(1) + e2);
  const R dxdt = (pi / R(4)) * cosh_t * sech * sech;
  return {(R(1) + tanh_u) / R(2), dxdt, true};
}

template <class R, class Fn> inline R tanh_sinh_level(Fn f, int level) {
  R h(1);
  for (int i = 0; i < level + 1; ++i) h /= R(2);
  const double hd = static_cast<double>(h);
  const int kmax = static_cast<int>(6.5 / hd) + 2;
  R sum(0);
  for (int k = -kmax; k <= kmax; ++k) {
    const MapNode<R> n = tanh_sinh_node<R>(h * R(k));
    if (!n.live) continue;
    sum += f(n.x) * n.dxdt;
  }
  return sum * h;
}

template <class R, class Fn> inline R integrate_01(Fn f) {
  const R tol = lit<R>("1e-28");
  R prev = tanh_sinh_level<R>(f, 3);
  for (int level = 4; level <= 8; ++level) {
    const R cur = tanh_sinh_level<R>(f, level);
    if (m::fabs(cur - prev) <= tol) return cur;
    prev = cur;
  }
  return prev;
}

}  // namespace detail

template <class R, class Fn> inline R integrate_unit_interval(Fn f) {
  return detail::integrate_01<R>(f);
}

// σπ bubble with the chiral counterterm removed. Returns Ub = L_bubble − 1
// and the tree vev φ, both in units F = 1.
template <class R> struct Bubble { R Ub; R phi; };

template <class R> inline Bubble<R> sigma_pion_bubble(const R& xi) {
  const R pi = real_traits<R>::pi();
  const R M2 = R(16) * pi * pi / R(3);
  const R m2 = xi * R(16) * pi * pi;
  const R phi2 = R(1) + R(6) * xi;
  const R phi = m::sqrt(phi2);
  const R ms2 = M2 * (R(1) + R(9) * xi);
  const R kappa = (M2 / R(3)) * phi2;
  const R spchi = -R(1) / R(6);
  const R delta = kappa * detail::integrate_01<R>([&](const R& x) {
    const R one = R(1) - x;
    const R Dp = x * ms2 + m2 * one * one;
    const R D0 = x * ms2 + one * m2;
    return m::ln(D0 / Dp);
  });
  const R Sp = -kappa * detail::integrate_01<R>([&](const R& x) {
    const R one = R(1) - x;
    const R Dp = x * ms2 + m2 * one * one;
    return x * one / Dp;
  });
  const R Zinv = R(1) + Sp - spchi;
  const R dR = delta + spchi * m2;
  const R Lb = m::sqrt(R(1) / Zinv) * (R(1) - dR / m2);
  return {Lb - R(1), phi};
}

template <class R> struct Residue {
  R F;             // chiral-limit decay constant, MeV
  R M_pi;          // charged-pion leaf, MeV
  R xi;
  R C4;
  R L;             // ln(M_σ0² / M_π²)
  R phi;           // √(1+6ξ)
  R Ub;            // bubble, counterterm removed
  R Ut;            // leaf-curvature tadpole, weight 1/3
  R Ut_sigma;      // same tadpole on M²(1+9ξ); not the residue
  R H;             // −C4 ξ
  R ratio;         // leaf residue / F
  R ratio_sigma;   // sigma-mass sibling / F
  R truncation;    // 1 + ξ (3 + L − C4)
  R F_pi;          // leaf residue, MeV
  R F_sigma;       // sigma-mass sibling, MeV
  R F_trunc;       // installed truncation, MeV
  R d_phi;         // MeV, exact vev with linear loops held
  R d_bubble;      // MeV
  R d_tadpole;     // MeV
};

// F and M_pi are MeV. The loop is built from those two leaves and from C4.
template <class R> inline Residue<R> leaf_curvature(const R& F, const R& M_pi) {
  const R pi = real_traits<R>::pi();
  const R xi = M_pi * M_pi / (R(16) * pi * pi * F * F);
  const R C4 = c4<R>();
  const R M2 = R(16) * pi * pi / R(3);
  const R L = m::ln(M2 / (xi * R(16) * pi * pi));
  const Bubble<R> bub = sigma_pion_bubble<R>(xi);
  const R r_leaf = (R(3) * xi) / (R(1) + R(6) * xi);
  const R r_sigma = (R(3) * xi) / (R(1) + R(9) * xi);
  // (1/6) r (L+1) is one third of the three-pion shift (1/2) r (L+1).
  const R Ut = (R(1) / R(6)) * r_leaf * (L + R(1));
  const R Ut_sigma = (R(1) / R(6)) * r_sigma * (L + R(1));
  const R H = -C4 * xi;
  const R loop = R(1) + bub.Ub + Ut + H;
  const R ratio = bub.phi * loop;
  const R ratio_sigma = bub.phi * (R(1) + bub.Ub + Ut_sigma + H);
  const R truncation = R(1) + xi * (R(3) + L - C4);
  const R Ulin_b = xi * (L - R(1)) / R(2);
  const R Ulin_t = xi * (L + R(1)) / R(2);
  const R s1 = bub.phi * (R(1) + Ulin_b + Ulin_t + H);
  const R s2 = bub.phi * (R(1) + bub.Ub + Ulin_t + H);
  Residue<R> out;
  out.F = F;
  out.M_pi = M_pi;
  out.xi = xi;
  out.C4 = C4;
  out.L = L;
  out.phi = bub.phi;
  out.Ub = bub.Ub;
  out.Ut = Ut;
  out.Ut_sigma = Ut_sigma;
  out.H = H;
  out.ratio = ratio;
  out.ratio_sigma = ratio_sigma;
  out.truncation = truncation;
  out.F_pi = ratio * F;
  out.F_sigma = ratio_sigma * F;
  out.F_trunc = truncation * F;
  out.d_phi = (s1 - truncation) * F;
  out.d_bubble = (s2 - s1) * F;
  out.d_tadpole = (ratio - s2) * F;
  return out;
}

// Log slopes at a small ξ, in units F = 1. Used to lock the coefficient of −ξ ln ξ.
template <class R> struct Slopes { R Ub_over_xi; R Ut_over_xi; R half_Lm1; R half_Lp1; R d_ratio; };

template <class R> inline Slopes<R> small_xi_slopes(const R& xi) {
  const R pi = real_traits<R>::pi();
  const R M2 = R(16) * pi * pi / R(3);
  const R L = m::ln(M2 / (xi * R(16) * pi * pi));
  const Bubble<R> bub = sigma_pion_bubble<R>(xi);
  const R r_leaf = (R(3) * xi) / (R(1) + R(6) * xi);
  const R Ut = (R(1) / R(6)) * r_leaf * (L + R(1));
  const R H = -c4<R>() * xi;
  const R ratio = bub.phi * (R(1) + bub.Ub + Ut + H);
  const R truncation = R(1) + xi * (R(3) + L - c4<R>());
  return {bub.Ub / xi, Ut / xi, (L - R(1)) / R(2), (L + R(1)) / R(2), ratio - truncation};
}

}  // namespace fsot::axial
