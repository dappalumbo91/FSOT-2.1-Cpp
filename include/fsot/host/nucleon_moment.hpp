// fsot/host/nucleon_moment.hpp — neutron moment from the physical-pion soliton.
//
// Round-q Q-1 is the nearer moment reading: mu_n = -1.92581799223 against
// -1.91304276. The pieces are the Christov assembly in score_2026_10_02q.py,
// DPP of audit/heavy_2026-10-02q.json, M = m_p/3. Signs are the M = 420 sanity
// signs. The isoscalar piece carries the mean-square size, so it takes the
// square root of F_pi/F already used for the isovector radius. The order-alpha
// named-seed window on that reading is empty. The Schwinger scale alpha/(2 pi)
// holds one named seed, Catalan's G. The full ratio with that same dressing
// sits outside the neutron bar. The proton from this fold sits outside
// 2.79284734463 +/- 8.2e-10. The proton moment remains the leaf g_p/2.
// Not a record row.
#pragma once
#include "fsot/host/chiral_decay.hpp"

namespace fsot::nucleon {

template <class R> struct Moment {
  R isoscalar;
  R isovector;
  R weight;
  R dress;
  R neutron;
  R proton;
  R center;
  R sigma;
  R proton_center;
  R proton_sigma;
  R z() const { return (neutron - center) / sigma; }
  R proton_z() const { return (proton - proton_center) / proton_sigma; }
};

template <class R> inline Moment<R> magnetic(const Engine<R>& eng, const leaves::SeedLeaves<R>& seeds) {
  const decay::Reading<R> dec = decay::from_leaves<R>(eng, seeds);
  const R mp = seeds.mev(seeds.proton_ratio() * seeds.m_e_kg());
  const R F = mp / (R(2) * m::sqrt(R(3)) * eng.PI);
  const R q = lit<R>("938.2720893") / lit<R>("312.7573631");
  const R I = lit<R>("2.46579607");
  const R B = lit<R>("-4.14353322");
  const R Amu = lit<R>("1.438742164");
  const R xat = lit<R>("-2.10265062") + lit<R>("-0.8387479327");
  const R Nc = R(3);
  // Sanity profile: B_re < 0, Amu_im > 0.
  const R muS = -Nc * q * B / (R(18) * I);
  const R muV = -Nc * q / R(9) * xat + Nc * q * Amu / (R(3) * I);
  Moment<R> out;
  out.isoscalar = muS;
  out.isovector = muV;
  out.weight = m::sqrt(dec.pi.value / F);
  out.dress = R(1) + eng.G_CAT * seeds.alpha() / (R(2) * eng.PI);
  out.neutron = (muS * out.weight - muV) / R(2) * out.dress;
  out.proton = (muS * out.weight + muV) / R(2) * out.dress;
  out.center = lit<R>("-1.91304276");
  out.sigma = lit<R>("0.00000045");
  out.proton_center = lit<R>("2.79284734463");
  out.proton_sigma = lit<R>("8.2e-10");
  return out;
}

}  // namespace fsot::nucleon
