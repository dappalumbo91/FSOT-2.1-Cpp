// fsot/host/nucleon_radius.hpp — isovector radius from the KSRF dipole.
//
// The dipole is 12 hbar c squared over the KSRF mass squared. The mass uses the
// chiral decay constant, m_rho = 2 sqrt(2) pi F. The length that is measured
// carries the installed lifetime decay constant under a square root, so the
// radius is the dipole times sqrt(F_pi/F). Both decay constants are FSOT
// quantities. The ratio itself and its square are the wider neighbors and sit
// outside 0.82236 +/- 0.00201. The fine-structure window on this value holds
// several named seeds, so no further seed is applied. hbar c is the MeV*fm
// conversion already used by the radius score scripts. Not a record row.
#pragma once
#include "fsot/host/chiral_decay.hpp"

namespace fsot::nucleon {

template <class R> struct Radius {
  R dipole;
  R weight;
  R value;
  R center;
  R sigma;
  R z() const { return (value - center) / sigma; }
};

template <class R> inline Radius<R> r_v2(const Engine<R>& eng, const leaves::SeedLeaves<R>& seeds) {
  const decay::Reading<R> dec = decay::from_leaves<R>(eng, seeds);
  const R mp = seeds.mev(seeds.proton_ratio() * seeds.m_e_kg());
  const R F = mp / (R(2) * m::sqrt(R(3)) * eng.PI);
  const R hc = lit<R>("197.3269804");
  const R mrho = R(2) * m::sqrt(R(2)) * eng.PI * F;
  Radius<R> out;
  out.dipole = R(12) * hc * hc / (mrho * mrho);
  out.weight = m::sqrt(dec.pi.value / F);
  out.value = out.dipole * out.weight;
  out.center = lit<R>("0.82236");
  out.sigma = lit<R>("0.00201");
  return out;
}

}  // namespace fsot::nucleon
