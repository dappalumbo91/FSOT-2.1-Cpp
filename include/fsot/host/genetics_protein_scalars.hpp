// fsot/host/genetics_protein_scalars.hpp — FSOT 2.1 amino-acid chemical scalars (F01-F03, seed-only).
//
// Provenance: dappalumbo91/FSOT-Genetics crates/fsot_protein/formulas/FSOT_PROTEIN_DERIVATIONS.md
// @ f677663 (v7, "zero free parameters"), Rust source crates/fsot_protein/src/{secondary.rs
// trinary_phase, chemical.rs ChemicalPropensity / fsot_chemical_interaction} @ f677663.
// Pin-invariant: uses only seeds {PI, E, PHI, GAMMA} (no C_EFF / domain scalar), so identical at
// theory pin AEB2AD (FSOT-2.1-Lean). No new constant. Rust f64 outputs agree with these closed forms
// to <= 2.1e-16 relative (tests/test_genetics_protein_scalars.cpp).
//
//   F01  AA -> trinary (c, p, v) in {-1,0,+1}^3  (charge, polarity, volume)
//   F02  h = PHI^-p * e^(v/PI)    V = PI*E*PHI^v    q = c    mu = GAMMA * e^(|c|+p+1)
//   F03  disulfide C-C = PHI^6
// Note: the trinary collapse (e.g. I,L,M,F,W share (0,-1,+1); His charge lumped at +1) is by design
// in the source; F04+ (pair terms, distogram) are not ported here.
#pragma once
#include "fsot/engine.hpp"

namespace fsot::genetics {

struct Trit3 { int c, p, v; };

// F01 — mirrors FSOT-Genetics secondary::trinary_phase; unknown letters -> (0,0,0).
inline constexpr Trit3 aa_trinary(char aa) {
  switch (aa >= 'a' && aa <= 'z' ? char(aa - 32) : aa) {
    case 'A': return {0, -1, -1}; case 'R': return {1, 1, 1};   case 'N': return {0, 1, 0};
    case 'D': return {-1, 1, 0};  case 'C': return {0, 0, -1};  case 'Q': return {0, 1, 1};
    case 'E': return {-1, 1, 1};  case 'G': return {0, -1, -1}; case 'H': return {1, 1, 1};
    case 'I': return {0, -1, 1};  case 'L': return {0, -1, 1};  case 'K': return {1, 1, 1};
    case 'M': return {0, -1, 1};  case 'F': return {0, -1, 1};  case 'P': return {0, -1, 0};
    case 'S': return {0, 1, -1};  case 'T': return {0, 1, 0};   case 'W': return {0, -1, 1};
    case 'Y': return {0, 1, 1};   case 'V': return {0, -1, 0};  default: return {0, 0, 0};
  }
}

template <class R> R phi_pow_trit(const Engine<R>& F, int t) {
  return t > 0 ? F.PHI : (t < 0 ? R(1) / F.PHI : R(1));
}

template <class R> struct AaScalars { R h, V, q, mu; };

// F02
template <class R> AaScalars<R> aa_scalars(const Engine<R>& F, char aa) {
  const Trit3 t = aa_trinary(aa);
  const R h = phi_pow_trit(F, -t.p) * m::exp(R(t.v) / F.PI);
  const R V = F.PI * F.E * phi_pow_trit(F, t.v);
  const R mu = F.GAMMA * m::exp(R((t.c < 0 ? -t.c : t.c) + t.p + 1));
  return {h, V, R(t.c), mu};
}

// F03
template <class R> R disulfide(const Engine<R>& F) { return m::ipow(F.PHI, 6); }

}  // namespace fsot::genetics
