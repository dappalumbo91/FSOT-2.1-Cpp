// fsot/host/chua_branch_l.hpp — FSOT 2.1 Branch L: inductor quality factor from Ledger B on a reactance.
//
// Provenance: dappalumbo91/FSOT-Chua-Circuit docs/BRANCH_L_DERIVATION.md @ 1a6bd91 (pin AEB2AD).
// Status there: new-branch HYPOTHESIS (bench test: measure Q_L of the 22 mH part at ~3.39 kHz).
// Ledger B (c = m(1+|S|ALPHA)) is a catalog dressing in this engine; Branch L applies it to |Z| = wL
// with passivity, so (wL)^2 (1+eps)^2 = r0^2 + (wL)^2. No new constant is introduced.
//
//   eps = |S_EM| * ALPHA                         (S_EM: Electromagnetism, D_eff 7)
//   k   = 1/Q_L = sqrt(2 eps + eps^2)
//   r0  = k * sqrt(L/C2)                         [ohm]
//   gamma = beta r0 / R = k * sqrt(beta),  beta = R^2 C2 / L
#pragma once
#include "fsot/engine.hpp"

namespace fsot::chua {

template <class R> struct BranchL {
  const Engine<R>& F;
  explicit BranchL(const Engine<R>& e) : F(e) {}
  R eps(std::string_view domain = "Electromagnetism") const { return m::fabs(F.domain_scalar(domain)) * F.ALPHA; }
  R inv_QL(std::string_view domain = "Electromagnetism") const { const R e = eps(domain); return m::sqrt(R(2) * e + e * e); }
  R QL(std::string_view domain = "Electromagnetism") const { return R(1) / inv_QL(domain); }
  R r0(const R& L, const R& C2, std::string_view domain = "Electromagnetism") const { return inv_QL(domain) * m::sqrt(L / C2); }
  R gamma(const R& beta, std::string_view domain = "Electromagnetism") const { return inv_QL(domain) * m::sqrt(beta); }
};

}  // namespace fsot::chua
