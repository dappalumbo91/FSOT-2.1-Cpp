// fsot/host/nucleon_delta.hpp — Delta-N on the P3 profile.
//
// The profile fraction is AG-2 P3, audit/score_2026-10-02ag.tsv: 0.327460495368.
// The MeV value is that fraction times the proton-mass leaf. N_c = 3, the same
// count as L4 = L5/N_c in the kaon-to-pion ratio. The weight is
// (F/F_pi)^((N_c-1)/N_c). F is the chiral leaf and F_pi is the installed
// lifetime value. The power 1 and the power 1/2 are the wider neighbors and
// sit outside 293.081 +/- 2 MeV. Not a record row.
#pragma once
#include "fsot/host/chiral_decay.hpp"

namespace fsot::nucleon {

template <class R> struct Delta {
  R profile_MeV;
  R weight;
  R value;
  R center;
  R sigma;
  R z() const { return (value - center) / sigma; }
};

template <class R> inline Delta<R> delta_n(const Engine<R>& eng, const leaves::SeedLeaves<R>& seeds) {
  const decay::Reading<R> dec = decay::from_leaves<R>(eng, seeds);
  const R mp = seeds.mev(seeds.proton_ratio() * seeds.m_e_kg());
  const R F = mp / (R(2) * m::sqrt(R(3)) * eng.PI);
  const R mn = lit<R>("939.56542194");
  const R md = lit<R>("1232");
  Delta<R> out;
  out.profile_MeV = lit<R>("0.327460495368") * mp;
  out.weight = m::pow(F / dec.pi.value, R(2) / R(3));
  out.value = out.profile_MeV * out.weight;
  out.center = md - (mp + mn) / R(2);
  out.sigma = lit<R>("2");
  return out;
}

}  // namespace fsot::nucleon
