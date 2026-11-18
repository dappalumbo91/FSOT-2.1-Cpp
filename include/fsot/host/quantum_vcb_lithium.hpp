// fsot/host/quantum_vcb_lithium.hpp — FSOT 2.1 exclusive |V_cb| and cosmological-lithium factor
// (closed forms, no new constants).
//
// Provenance: dappalumbo91/FSOT-Quantum docs/FORMULA_LIST.md @ 3c4375a (published at pin D1D38A:
// V_cb_exclusive 0.039143, Lithium_factor 3.00871). In FSOT-Quantum these were routing defaults only.
// Recomputed at theory pin AEB2AD (FSOT-2.1-Lean) from FSOT-2.1-Cpp engine.hpp @ 27d8b48:
//   C_EFF  = (1 - POOF sin THETA_S)(1 + pi^-4 G_CAT/(pi PHI))       (engine.hpp:133-134)
//   S(HEP) = domain_scalar("High_Energy_Physics")  (nest gen3 D_eff 6, look 1 - POOF/pi)
// The D1D38A digits are a disclosed stale pin (C_EFF used 0.01 for pi^-4; HEP used hand D_eff 7,
// look 0.95) — intentional authority re-pin per Tracer note steward_aeb2ad_C_EFF_HEP.md, not a FAIL.
//
//   V_cb_exclusive = S(HEP) * (1/C_EFF - 1)   (= 0.0391453985916172...)
//   Lithium_factor = PI * C_EFF               (= 3.0088541478250693...)
//
// NOTE: this exclusive route is distinct from the tip V_cb (0.04189) route; do not conflate.
#pragma once
#include "fsot/engine.hpp"

namespace fsot::quantum {

template <class R> R v_cb_exclusive(const Engine<R>& F) {
  return F.domain_scalar("High_Energy_Physics") * (R(1) / F.C_EFF - R(1));
}

template <class R> R lithium_factor(const Engine<R>& F) { return F.PI * F.C_EFF; }

}  // namespace fsot::quantum
