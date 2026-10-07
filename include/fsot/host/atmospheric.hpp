// fsot/host/atmospheric.hpp — atmospheric mixing on the closest specimen half.
//
// |S|/2 on the specimen rungs from particle physics through sociology sits
// inside NuFIT 6.1 normal ordering with SK, 0.470 +0.017/-0.014. Generation 9
// is the closest. Neuroscience and Condensed_Matter share that rung
// (D_eff = 11). The record |Chaos|*sqrt(e) stays the PDG 2024 row.
// Not a record row.
#pragma once
#include "fsot/engine.hpp"

namespace fsot::mixing {

template <class R> struct Atmospheric {
  R value;
  R center;
  R sigma_plus;
  R sigma_minus;
  int D_eff;
  R z() const {
    const R d = value - center;
    return d / (d >= R(0) ? sigma_plus : sigma_minus);
  }
};

template <class R> inline Atmospheric<R> sin2_theta23(const Engine<R>& eng) {
  Atmospheric<R> out;
  out.D_eff = eng.domain("Neuroscience").D_eff;
  out.value = m::fabs(eng.domain_scalar("Neuroscience")) / R(2);
  out.center = lit<R>("0.470");
  out.sigma_plus = lit<R>("0.017");
  out.sigma_minus = lit<R>("0.014");
  return out;
}

template <class R> inline R specimen_half(const Engine<R>& eng, std::string_view name) {
  return m::fabs(eng.domain_scalar(name)) / R(2);
}

}  // namespace fsot::mixing
