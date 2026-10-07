// fsot/host/lbar3.hpp — lbar_3 from the tree mass ratio of the KSRF axial partner.
//
// CGL hep-ph/0103088 eq. (7.1): M_pi^2 = M^2 {1 - (1/2) x lbar_3 + O(x^2)},
// with Durr's x = M^2 / (16 pi^2 F^2) and M^2 the leading-order mass.
// The frozen KSRF pair is m_rho^2 = 2 g_phys^2 F_pi^2, g_phys = g R,
// F_pi = phi / sqrt(R), m_a^2 = m_rho^2 + g^2 phi^2, g^2 = 4 pi^2.
// Those four fix R = (1 + sqrt(3)) / 2 at every mass.
// Lambda stays 8 pi^2 / 3. The chiral vev is F sqrt(R), so
// M_pi^2 / M^2 = 1 / sqrt(1 + 6 xi / R^2), xi = M_pi^2 / (16 pi^2 F^2).
// The selected reading is the physical-point inversion on Durr's x.
// The chiral limit 24 - 12 sqrt(3) is the same ratio with x -> 0.
// Nyffeler's one-loop value is not this reading. This row is not on the 91.
#pragma once
#include "fsot/host/seed_leaves.hpp"

namespace fsot::lbar3 {

template <class R> struct Reading {
  R xi;
  R ratio;
  R x;
  R value;
  R chiral;
  R center;
  R sigma;
  R z() const { return (value - center) / sigma; }
};

template <class R> inline Reading<R> durr_x(const R& F, const R& M_pi) {
  const R pi = real_traits<R>::pi();
  const R R0 = (R(1) + m::sqrt(R(3))) / R(2);
  const R xi = M_pi * M_pi / (R(16) * pi * pi * F * F);
  const R ratio = R(1) / m::sqrt(R(1) + R(6) * xi / (R0 * R0));
  const R x = xi / ratio;
  Reading<R> out;
  out.xi = xi;
  out.ratio = ratio;
  out.x = x;
  out.value = R(2) * (R(1) - ratio) / x;
  out.chiral = R(24) - R(12) * m::sqrt(R(3));
  out.center = lit<R>("2.9");
  out.sigma = lit<R>("2.4");
  return out;
}

template <class R> inline Reading<R> from_leaves(const Engine<R>& eng, const leaves::SeedLeaves<R>& seeds) {
  const R mp = seeds.mev(seeds.proton_ratio() * seeds.m_e_kg());
  const R F = mp / (R(2) * m::sqrt(R(3)) * eng.PI);
  return durr_x<R>(F, seeds.pion_MeV());
}

}  // namespace fsot::lbar3
