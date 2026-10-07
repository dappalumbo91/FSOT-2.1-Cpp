// fsot/host/pmns_phase.hpp — lepton CP phase with the suction term.
//
// The scored record is phi^3 - 1/e - Suction. Suction is the closest
// existing-constant subtraction from phi^3 - 1/e. Poof is the next one.
// P_base stays outside the flat 2% line. The pin phi^3 - 1/e stays in the
// report with record 0. apps/fsot_precision.cpp route cpleaf calls delta_cp.
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

template <class R> inline R delta_cp_pin(const Engine<R>& eng) {
  return m::ipow(eng.PHI, 3) - (R(1) / eng.E);
}

}  // namespace fsot::mixing
