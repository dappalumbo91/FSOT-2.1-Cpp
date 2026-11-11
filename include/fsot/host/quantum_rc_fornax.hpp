// fsot/host/quantum_rc_fornax.hpp — FSOT 2.1 Fornax dSph core-radius factor r_c (closed form, seed-only).
//
// Provenance: dappalumbo91/FSOT-Quantum docs/FORMULA_LIST.md @ 3c4375a (published at pin D1D38A:
// 0.6020461466908882). Rechecked at theory pin AEB2AD (FSOT-2.1-Lean) against FSOT-2.1-Cpp
// golden/golden_AEB2AD.tsv @ 27d8b48: pin-invariant (uses no C_EFF / domain scalar), |delta| ~ 5e-17.
// In FSOT-Quantum this was a routing default only; here it is an explicit closed form. No new constant.
//
//   r_c(Fornax) = ETA_EFF * PHI - POOF   (= 0.60204614669088815147...)
#pragma once
#include "fsot/engine.hpp"

namespace fsot::quantum {

template <class R> R r_c_fornax(const Engine<R>& F) { return F.ETA_EFF * F.PHI - F.POOF; }

}  // namespace fsot::quantum
