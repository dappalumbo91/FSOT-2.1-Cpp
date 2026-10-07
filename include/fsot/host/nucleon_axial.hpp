// fsot/host/nucleon_axial.hpp — g_A on the nuclear rung of the P3 profile.
//
// The profile is the particle-sector soliton, audit/score_2026-10-02ag.tsv
// AG-2 P3 (K 14, D 14, kmax 12): g_A = 1.29168910489. The nucleon is read on
// the nuclear rung, so the coefficient is S(Nuclear_Physics)/S(Particle_Physics).
// Both scalars are domain_scalar. The interpretation C does not enter S.
// On that base the fine-structure window bare*(1 + alpha^n * seed), n = 1, 2, 3,
// both signs, holds one named seed: n = 1, plus, gamma*psi_con^2.
// The two-tank mix of depths 5 and 12 is the wider neighbor (z about 5.2) and
// its window holds both psi_con and 1/phi. The bare profile's window holds
// both phi and sqrt(e). Those readings are not this one.
// The bar is the published 1.2754 +/- 0.0013. Not a record row.
#pragma once
#include "fsot/host/seed_leaves.hpp"

namespace fsot::nucleon {

template <class R> struct Axial {
  R profile;
  R ratio;
  R seed;
  R value;
  R center;
  R sigma;
  R z() const { return (value - center) / sigma; }
};

template <class R> inline Axial<R> g_a(const Engine<R>& eng, const leaves::SeedLeaves<R>& seeds) {
  const R profile = lit<R>("1.29168910489");
  const R ratio = eng.domain_scalar("Nuclear_Physics") / eng.domain_scalar("Particle_Physics");
  const R seed = eng.GAMMA * eng.PSI_CON * eng.PSI_CON;
  Axial<R> out;
  out.profile = profile;
  out.ratio = ratio;
  out.seed = seed;
  out.value = profile * ratio * (R(1) + seeds.alpha() * seed);
  out.center = lit<R>("1.2754");
  out.sigma = lit<R>("0.0013");
  return out;
}

}  // namespace fsot::nucleon
