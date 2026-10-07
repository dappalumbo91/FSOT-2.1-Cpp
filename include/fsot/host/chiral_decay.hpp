// fsot/host/chiral_decay.hpp — lifetime F_pi and F_K/F_pi on one chiral reading.
//
// The one-loop piece is the leaf residue in axial_residue.hpp. That file stays
// the miss checkpoint. Durr arXiv:1310.3626 writes the two-loop as a completed
// square; k_F is omitted. The three-loop is Bijnens and Hermansson-Truedsson,
// arXiv:1710.01901 eqs. (28)-(31), with r_i and c_i left out. Its logarithm is
// the one on which the square's linear log coefficient vanishes.
// F_K/F_pi is the one-loop SU(3) ratio at L4 = L5/N_c, N_c = 3, using this F_pi.
// Neither reading is a record row.
#pragma once
#include "fsot/host/axial_residue.hpp"
#include "fsot/host/seed_leaves.hpp"

namespace fsot::decay {

template <class R> struct Pieces {
  R lbar1;
  R lbar2;
  R lbar3;
  R lbar4;
  R xi;
  R residue;
  R square;
  R n3;
  R value;
  R log_mu;
};

template <class R> struct Reading {
  Pieces<R> pi;
  R ratio;
  R pi_center;
  R pi_sigma;
  R ratio_center;
  R ratio_sigma;
  R z_pi() const { return (pi.value - pi_center) / pi_sigma; }
  R z_ratio() const { return (ratio - ratio_center) / ratio_sigma; }
};

namespace detail {

template <class R> inline R apery() { return lit<R>("1.2020569031595942853997381615114499907649862923405"); }

// Pennington and Portoles, hep-ph/9409426 eqs. (16), (24), (27), lambda = 1.
// The rho is the frozen KSRF resonance. FREEZE_2026-10-02bh.
template <class R> inline void d_wave(const R& F, const R& M_pi, R& l1, R& l2) {
  const R pi = real_traits<R>::pi();
  const R m2 = R(8) * pi * pi * F * F;
  const R m = m::sqrt(m2);
  const R phase = R(1) - R(4) * M_pi * M_pi / m2;
  const R gamma = (pi * m / R(12)) * m::pow(phase, R(3) / R(2));
  const R a20 = (R(24) / R(5)) * gamma * (m2 + R(4) * M_pi * M_pi) /
                (m2 * m2 * m::pow(m2 - R(4) * M_pi * M_pi, R(3) / R(2)));
  const R b11 = R(16) * gamma / (m2 * m2 * m::sqrt(m2 - R(4) * M_pi * M_pi));
  const R A = R(1440) * pi * pi * pi * F * F * F * F * a20;
  const R B = R(288) * pi * pi * pi * F * F * F * F * b11;
  const R sum4 = A + R(53) / R(8);
  const R diff = B - R(97) / R(120);
  l2 = (sum4 + diff) / R(5);
  l1 = l2 - diff;
}

template <class R> inline R lbar3_of(const R& xi) {
  const R R0 = (R(1) + m::sqrt(R(3))) / R(2);
  const R ratio = R(1) / m::sqrt(R(1) + R(6) * xi / (R0 * R0));
  return R(2) * (R(1) - ratio) / (xi / ratio);
}

template <class R> inline R lbar4_of(const R& xi) {
  const R pi = real_traits<R>::pi();
  const R C4 = (R(19) - R(3) * m::sqrt(R(3)) * pi) / R(2);
  return R(3) + m::ln(R(1) / (R(3) * xi)) - C4;
}

// a21^F = 0. L = ln(M^2/mu^2).
template <class R> inline R durr_log(const R& l1, const R& l2, const R& l3, const R& l4) {
  const R C = -l4 / R(2) + l3 / R(2) + (R(4) / R(3)) * l2 + (R(7) / R(6)) * l1 + R(23) / R(12);
  return -(R(2) / R(5)) * C;
}

template <class R> inline R n3_mev(const R& F, const R& xi, const R& l1, const R& l2, const R& l3, const R& l4,
                                   const R& L) {
  const R q1 = (l1 + L) / R(6);
  const R q2 = (l2 + L) / R(3);
  const R q3 = -(l3 + L) / R(4);
  const R q4 = l4 + L;
  const R z3 = apery<R>();
  const R a30 = -q3 * q4 - R(2) * q3 * q3 + q2 * q4 + R(4) * q2 * q3 + q1 * q4 / R(2) + R(12) * q1 * q3 +
                (R(313) / R(192)) * q4 + (R(241) / R(48)) * q3 + (R(1469) / R(800)) * q2 +
                (R(2359) / R(600)) * q1 - R(383293667) / R(1555200) + (R(8) / R(9)) * z3;
  const R a31 = -q3 * q4 - R(4) * q2 * q4 + R(16) * q2 * q3 - R(7) * q1 * q4 + R(28) * q1 * q3 -
                (R(13) / R(6)) * q4 + (R(17) / R(2)) * q3 + (R(569) / R(60)) * q2 + (R(77) / R(10)) * q1 -
                R(7499) / R(2160);
  const R a32 = (R(3) / R(8)) * q4 + (R(27) / R(2)) * q2 + R(33) * q1 + R(1037) / R(144);
  const R a33 = -R(83) / R(24);
  const R x3 = xi * xi * xi;
  return x3 * (a30 + a31 * L + a32 * L * L + a33 * L * L * L) * F;
}

template <class R> inline R square_mev(const R& F, const R& xi, const R& l1, const R& l2, const R& l3, const R& l4) {
  const R L12 = (R(7) * l1 + R(8) * l2) / R(15);
  const R ln_s = (R(6) * l3 - R(6) * l4 + R(23)) / R(30);
  const R hat = L12 + ln_s;
  return -(R(5) / R(4)) * xi * xi * hat * hat * F;
}

template <class R> inline R fk_ratio(const R& Fq, const R& F, const R& M_pi, const R& M_K, const R& l4) {
  const R pi = real_traits<R>::pi();
  const R rho = R(2) * m::sqrt(R(2)) * pi * F;
  const R Me2 = (R(4) * M_K * M_K - M_pi * M_pi) / R(3);
  const R c = R(32) * pi * pi * Fq * Fq;
  const auto mu = [&](const R& M2) { return M2 / c * m::ln(M2 / (rho * rho)); };
  const R l4r = (l4 + m::ln(M_pi * M_pi / (rho * rho))) / (R(16) * pi * pi);
  const R nuK = (m::ln(M_K * M_K / (rho * rho)) + R(1)) / (R(32) * pi * pi);
  const R L5 = R(3) * (l4r + nuK / R(2)) / R(20);
  return R(1) + (R(5) / R(4)) * mu(M_pi * M_pi) - mu(M_K * M_K) / R(2) - (R(3) / R(4)) * mu(Me2) +
         R(4) * (M_K * M_K - M_pi * M_pi) * L5 / (Fq * Fq);
}

template <class R> inline Pieces<R> pieces(const R& F, const R& M_pi, const R& residue, const R& L) {
  const R pi = real_traits<R>::pi();
  const R xi = M_pi * M_pi / (R(16) * pi * pi * F * F);
  Pieces<R> out;
  d_wave(F, M_pi, out.lbar1, out.lbar2);
  out.lbar3 = lbar3_of<R>(xi);
  out.lbar4 = lbar4_of<R>(xi);
  out.xi = xi;
  out.residue = residue;
  out.square = square_mev(F, xi, out.lbar1, out.lbar2, out.lbar3, out.lbar4);
  out.n3 = n3_mev(F, xi, out.lbar1, out.lbar2, out.lbar3, out.lbar4, L);
  out.value = residue + out.square + out.n3;
  out.log_mu = L;
  return out;
}

}  // namespace detail

template <class R> inline Pieces<R> at_log(const R& F, const R& M_pi, const R& residue, const R& L) {
  return detail::pieces<R>(F, M_pi, residue, L);
}

template <class R> inline Reading<R> from_leaves(const Engine<R>& eng, const leaves::SeedLeaves<R>& seeds) {
  const R mp = seeds.mev(seeds.proton_ratio() * seeds.m_e_kg());
  const R F = mp / (R(2) * m::sqrt(R(3)) * eng.PI);
  const R M_pi = seeds.pion_MeV();
  const R M_K = m::pow(eng.G_CAT, R(-7)) + m::pow(eng.P_BASE, R(-4)) - m::pow(eng.PI, R(-4));
  const axial::Residue<R> leaf = axial::leaf_curvature<R>(F, M_pi);
  const R pi = real_traits<R>::pi();
  const R xi = M_pi * M_pi / (R(16) * pi * pi * F * F);
  R l1, l2;
  detail::d_wave(F, M_pi, l1, l2);
  const R l3 = detail::lbar3_of<R>(xi);
  const R l4 = detail::lbar4_of<R>(xi);
  const Pieces<R> row = detail::pieces<R>(F, M_pi, leaf.F_pi, detail::durr_log(l1, l2, l3, l4));
  const axial::LifetimeBar<R> bar = axial::lifetime_bar<R>();
  Reading<R> out;
  out.pi = row;
  out.ratio = detail::fk_ratio(row.value, F, M_pi, M_K, l4);
  out.pi_center = bar.center;
  out.pi_sigma = bar.sigma;
  out.ratio_center = lit<R>("1.1932");
  out.ratio_sigma = lit<R>("0.0021");
  return out;
}

}  // namespace fsot::decay
