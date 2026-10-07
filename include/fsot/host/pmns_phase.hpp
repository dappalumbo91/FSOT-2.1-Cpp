// fsot/host/pmns_phase.hpp — lepton CP phase with the suction term.
//
// The record is phi^3 - 1/e = 3.86818853632835 rad, 3.469% above PDG 2024
// 1.19 pi. Subtracting one existing constant, the closest to that center is
// Suction. Poof is the next one. P_base stays outside the flat 2% line.
// The record row is unchanged.
// Not a record row.
#pragma once
#include "fsot/engine.hpp"

namespace fsot::mixing {

template <class R> struct Phase {
  R value;
  R pdg_center;
  R pdg_sigma;
  R nufit_deg;
  R nufit_plus;
  R nufit_minus;
  R z_pdg() const { return (value - pdg_center) / pdg_sigma; }
  R degrees(const Engine<R>& eng) const { return value * R(180) / eng.PI; }
  R z_nufit(const Engine<R>& eng) const {
    const R d = degrees(eng) - nufit_deg;
    return d / (d >= R(0) ? nufit_plus : nufit_minus);
  }
  R flat() const { return (value - pdg_center) / pdg_center; }
};

template <class R> inline Phase<R> delta_cp(const Engine<R>& eng) {
  Phase<R> out;
  out.value = m::ipow(eng.PHI, 3) - (R(1) / eng.E) - eng.SUCTION;
  out.pdg_center = lit<R>("1.19") * eng.PI;
  out.pdg_sigma = lit<R>("0.22") * eng.PI;
  out.nufit_deg = R(212);
  out.nufit_plus = R(26);
  out.nufit_minus = R(36);
  return out;
}

template <class R> inline R delta_cp_record(const Engine<R>& eng) {
  return m::ipow(eng.PHI, 3) - (R(1) / eng.E);
}

}  // namespace fsot::mixing
