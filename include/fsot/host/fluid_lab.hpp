// fsot/host/fluid_lab.hpp — the one T2 lab formula that is a seed leaf.
//
// vendor/fsot_scale_interconnects.py water_air_sound_ratio(), on the AEB2AD seeds.
// Alpha is the inverse-alpha leaf. The row is not on the 91.
//
// The same suite's diatomic gamma is 1 + 2/D_eff with Particle_Physics at 5,
// which is 7/5. Its scale height is R*T/(mu*g) compared with that same quotient.
// Both equal their comparison by construction, so neither is installed as a solve.
#pragma once
#include "fsot/host/seed_leaves.hpp"

namespace fsot::fluid {

template <class R> struct Scored {
  R value;
  R center;
  R sigma;
  R z() const { return m::fabs(value - center) / sigma; }
};

template <class R> struct Lab {
  const Engine<R>& F;
  R a;
  explicit Lab(const leaves::SeedLeaves<R>& L) : F(L.F), a(L.alpha()) {}

  // (e + phi) * (1 - alpha / (1 + C_eff * cos(theta_S))).
  // Center is CRC/ISO 1482.4 / 343.2. The bar is the quadrature of half a
  // printed tenth (0.05 m/s) on each speed.
  Scored<R> water_air_sound_ratio() const {
    const R split = R(1) / (R(1) + F.C_EFF * m::cos(F.THETA_S));
    const R value = (F.E + F.PHI) * (R(1) - a * split);
    const R air = lit<R>("343.2");
    const R water = lit<R>("1482.4");
    const R half = lit<R>("0.05");
    const R center = water / air;
    const R dw = half / air;
    const R da = water * half / (air * air);
    const R sigma = m::sqrt(dw * dw + da * da);
    return {value, center, sigma};
  }
};

}  // namespace fsot::fluid
