// fsot/derive/derived_table.hpp — the single-engine table: the authority's closed forms with every literal-only or
// measured-input row replaced by the engine's own derived value where one exists.
//
//   * B-03 cube-root exponents: Mode::corrected (exact p/q instead of the 15-digit 0.333333333333333 literal).
//   * DNA_base_pair: a0 = 0.529177 (measured Bohr radius, 6 decimals) -> the seed leaf a_0 (seed_leaves.hpp, 1e10 * m).
//   * Proton_radius: formula "exact", value = target literal 0.8413 -> the seed leaf r_p = G^7 + P_new.
//   * Definition rows (STDP_Tau_*_ms = 20, Metatron_* = 13/27, Max_Trits = 27, Potts3_beta = 1/9, Quark_condensate = 1/4):
//     no seed derivation exists; kept, tagged "definition", and never scored.
// Variants for the two FLAGGED/derived constants are produced by re-seating the engine members the closed forms read:
//   with_qm_rung(5): S_QUANT and the QM domain at the nest-rule rung (D-04 alternative);
//   with_c_cosm_10phi(): C_COSM = 1/(10 phi) (D-02 alternative; the derivation rejects it, kept for the before/after).
#pragma once
#include <map>
#include <set>
#include <string>
#include <vector>

#include "fsot/host/seed_leaves.hpp"

namespace fsot::derive {

enum class RowKind { seed, derived_replacement, definition };
inline const char* kind_name(RowKind k) { return k == RowKind::seed ? "seed" : k == RowKind::derived_replacement ? "derived-replacement" : "definition"; }
inline bool is_definition_row(const std::string& n) {
  static const std::set<std::string> d = {"STDP_Tau_Plus_ms", "STDP_Tau_Minus_ms", "Metatron_Spheres", "Metatron_Pathways",
                                          "Max_Trits", "Potts3_beta", "Quark_condensate"};
  return d.count(n) > 0;
}

template <class R> struct Row {
  std::string section, name, formula;
  R value;
  std::optional<R> measured;
  std::optional<double> sigma;
  RowKind kind = RowKind::seed;
};

template <class R> void with_qm_rung(Engine<R>& F, int D) {
  for (auto& d : F.DOMAINS) if (d.name == "Quantum_Mechanics") d.D_eff = D;
  F.S_QUANT = F.domain_scalar("Quantum_Mechanics");
}
template <class R> void with_c_cosm_10phi(Engine<R>& F) {
  F.C_COSM = R(1) / (R(10) * F.PHI);
  for (auto& d : F.DOMAINS) if (d.name == "Cosmology") d.C = F.C_COSM;
}

template <class R> std::vector<Row<R>> table(const Engine<R>& F, bool derived) {
  std::vector<Row<R>> out;
  leaves::SeedLeaves<R> L(F);
  for (auto& [sec, fn] : F.sections()) {
    for (auto& r : (F.*fn)()) {
      Row<R> x{sec, r.name, r.formula, r.computed, r.measured, r.sigma, RowKind::seed};
      if (is_definition_row(x.name)) x.kind = RowKind::definition;
      if (derived && x.name == "DNA_base_pair") {
        R a0 = R(0);
        for (auto& [id, v] : L.mp_values()) if (id == "a_0") a0 = v * lit<R>("1e10");
        x.value = R(2) * F.PI * a0 * (R(1) + F.GAMMA / (m::ipow(F.PI, 2) * F.E));
        x.formula = "2\u03c0a\u2080(1 + \u03b3/(\u03c0\u00b2e)), a\u2080 = seed leaf a_0";
        x.kind = RowKind::derived_replacement;
      }
      if (derived && x.name == "Proton_radius") {
        x.value = m::ipow(F.G_CAT, 7) + F.P_NEW;
        x.formula = "G\u2077 + P_new (seed leaf r_p)";
        x.kind = RowKind::derived_replacement;
      }
      out.push_back(std::move(x));
    }
  }
  return out;
}

}  // namespace fsot::derive
