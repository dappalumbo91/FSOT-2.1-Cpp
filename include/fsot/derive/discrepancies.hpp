// fsot/derive/discrepancies.hpp — D-01..D-10 of the unified archive (fsot_unified/DISCREPANCIES.md), each settled
// by a DERIVATION from the engine's own first principles where one exists. Nothing here edits a frozen value: every
// function re-derives a quantity and the tests (tests/test_derivations.cpp) assert which variant falls out.
//
//   D-01 pin hashing       -> pin is a property of the CONTENT: hash the CRLF-canonical byte stream (the form the pin
//                             was minted in), so LF and CRLF checkouts of the same file give the same pin.
//   D-02 C_cosm            -> the AEB2AD generation replaced decimal knobs by ONE substitution, 10 -> pi^2
//                             (0.01 = 10^-2 -> pi^-4 in C_EFF, 0.99 = 1 - 10^-2 -> 1 - pi^-4 in K). Applying that same map
//                             to C_cosm = 1/(10 phi) gives 1/(phi pi^2). 1/(10 phi) is consistent only with the whole
//                             D1D38A generation (decade = 10 in C_EFF and K too), which changes all 35 domain S.
//   D-03 Lean caches       -> derived live from the engine (S_cosm, S_quant, Wave-1, c_cosm bounds); see lean_sync().
//   D-04 QM rung           -> the nest rule round(5*5^{g/(G-1)}) gives 5.442 -> 5. No first-principles rule found that
//                             gives 6 without moving another rung; 6 is the owner decision of 2026-10-23. Both kept, FLAGGED.
//   D-05 Genetics D_eff    -> the nest rule gives the ChemLink table (10,11,7,7,6,6,6) and the long-range gate
//                             ceil(eta_eff * D_biochem) = ceil(4.669) = 5; the D1D38A table (13,14,9,9,8,8,7) and "= 7" are stale.
//   D-06 species scalars   -> species carry no rung of their own; they inherit Neuroscience's derived rung (11).
//   D-07/D-08/D-10         -> build/stamp/toolchain process items, no value to derive (documented, not computed).
//   D-09 trit encodings    -> both encodings are bijections on {-1,0,+1}; trit.hpp converts losslessly (test_trit).
#pragma once
#include <cmath>
#include <string>
#include <string_view>

#include "fsot/engine.hpp"
#include "fsot/host/sha256.hpp"

namespace fsot::derive {

// ---------------- D-01 ----------------
inline std::string to_crlf(std::string_view raw) {
  std::string out; out.reserve(raw.size() + raw.size() / 30);
  for (size_t i = 0; i < raw.size(); ++i) {
    const char c = raw[i];
    if (c == '\r') { out += "\r\n"; if (i + 1 < raw.size() && raw[i + 1] == '\n') ++i; }
    else if (c == '\n') out += "\r\n";
    else out += c;
  }
  return out;
}
inline std::string upper(std::string s) { for (auto& c : s) if (c >= 'a' && c <= 'f') c = char(c - 32); return s; }
inline std::string pin_raw(std::string_view raw) { return upper(host::sha256_hex(raw)).substr(0, 6); }
inline std::string pin_canonical(std::string_view raw) { return upper(host::sha256_hex(to_crlf(raw))).substr(0, 6); }

// ---------------- D-02 ----------------
// decade(): the seed image of the decimal base. AEB2AD uses decade = pi^2 everywhere; D1D38A used 10 everywhere.
template <class R> struct DecadeReading {
  R decade;              // the substitution the generation uses
  R c_eff, k, c_cosm;    // the three layer-2 constants rebuilt from that one decade
};
template <class R> DecadeReading<R> rebuild_layer2(const Engine<R>& F, const R& decade) {
  DecadeReading<R> d;
  d.decade = decade;
  const R inv2 = R(1) / m::ipow(decade, 2);  // 10^-2 image
  d.c_eff = (R(1) - F.POOF * m::sin(F.THETA_S)) * (R(1) + inv2 * F.G_CAT / (F.PI * F.PHI));
  d.k = F.PHI * (F.GAMMA / F.E) * m::sqrt(R(2)) / m::ln(F.PI) * (R(1) - inv2);
  d.c_cosm = R(1) / (F.PHI * decade);
  return d;
}
// Which C_cosm is consistent with the engine's own C_EFF and K? Returns the decade that reproduces C_EFF and K
// (pi^2 or 10), and the C_cosm that same decade implies.
template <class R> struct CCosmVerdict { bool pi2_reproduces_layer2, ten_reproduces_layer2; R c_cosm_derived; };
template <class R> CCosmVerdict<R> derive_c_cosm(const Engine<R>& F) {
  const auto p = rebuild_layer2(F, m::ipow(F.PI, 2));
  const auto t = rebuild_layer2(F, R(10));
  CCosmVerdict<R> v;
  v.pi2_reproduces_layer2 = (p.c_eff == F.C_EFF) && (p.k == F.K);
  v.ten_reproduces_layer2 = (t.c_eff == F.C_EFF) && (t.k == F.K);
  v.c_cosm_derived = v.pi2_reproduces_layer2 ? p.c_cosm : (v.ten_reproduces_layer2 ? t.c_cosm : R(0));
  return v;
}

// ---------------- D-04 ----------------
// Continuous nest rung and its nearest integer (the derivation); the owner override lives in derived_D_eff().
inline double nest_rung_continuous(int generation, int G = 20) { return 5.0 * std::pow(5.0, double(generation) / (G - 1)); }
inline int nest_rung_rule(std::string_view name) {
  const auto& gens = nest_generations();
  for (int g = 0; g < int(gens.size()); ++g)
    for (auto n : gens[g]) if (n == name) return int(std::nearbyint(nest_rung_continuous(g, int(gens.size()))));
  return -1;
}
// Alternative first-principles rounding rules, tried for QM. Each must leave the other 34 rungs where the nest puts them.
struct RungRuleTrial { const char* rule; int qm; int others_moved; };
inline std::vector<RungRuleTrial> qm_rung_trials() {
  std::vector<RungRuleTrial> out;
  const auto& gens = nest_generations();
  const int G = int(gens.size());
  auto run = [&](const char* nm, auto f) {
    RungRuleTrial t{nm, 0, 0};
    for (int g = 0; g < G; ++g) for (auto n : gens[g]) {
      const double x = nest_rung_continuous(g, G);
      const int r = f(x), base = int(std::nearbyint(x));
      if (n == "Quantum_Mechanics") t.qm = r; else if (r != base) ++t.others_moved;
    }
    out.push_back(t);
  };
  run("nearest (nest rule)", [](double x) { return int(std::nearbyint(x)); });
  run("geometric nearest (threshold sqrt(n(n+1)))", [](double x) { int n = int(std::floor(x)); return x >= std::sqrt(double(n) * (n + 1)) ? n + 1 : n; });
  run("ceil", [](double x) { return int(std::ceil(x)); });
  run("floor", [](double x) { return int(std::floor(x)); });
  run("nearest in log5", [](double x) { double l = std::log(x) / std::log(5.0); int n = int(std::floor(x)); double ln = std::log(double(n)) / std::log(5.0), lu = std::log(double(n + 1)) / std::log(5.0); return (l - ln) < (lu - l) ? n : n + 1; });
  return out;
}

// ---------------- D-05 ----------------
struct ChemLinkTable { int biochem, condensed, em, molecular, physchem, chem, atomic; };
inline ChemLinkTable chemlink_from_nest() {
  return {derived_D_eff("Biochemistry"), derived_D_eff("Condensed_Matter"), derived_D_eff("Electromagnetism"),
          derived_D_eff("Molecular_Chemistry"), derived_D_eff("Physical_Chemistry"), derived_D_eff("Chemistry"),
          derived_D_eff("Atomic_Physics")};
}
template <class R> int long_range_gate_biochem(const Engine<R>& F) {
  return int(std::ceil(static_cast<double>(F.ETA_EFF * R(derived_D_eff("Biochemistry")))));
}

// ---------------- D-03 ----------------
template <class R> struct LeanCaches {
  R S_cosm, S_quant, S_chem, c_cosm, H0, T_CMB, n_s, alpha_s, Omega_b_h2_engine, Omega_b_h2_lean_formula, r_star;
};
template <class R> LeanCaches<R> lean_sync(const Engine<R>& F) {
  LeanCaches<R> c;
  c.S_cosm = F.S_COSM; c.S_quant = F.S_QUANT; c.S_chem = F.S_CHEM; c.c_cosm = F.C_COSM;
  c.H0 = R(100) * (R(1) + F.S_COSM * F.A_BLEED / F.A_IN);
  c.T_CMB = m::ipow(F.PHI, 2) + F.P_BASE * m::fabs(F.S_COSM);
  c.n_s = R(1) + F.S_COSM * F.C_COSM * m::pow(F.PHI, R(1) / F.PI);
  c.alpha_s = R(1) / (F.E * F.PI);
  c.Omega_b_h2_engine = m::fabs(F.S_COSM) * (R(1) - F.S_CHEM);
  c.Omega_b_h2_lean_formula = m::fabs(F.S_COSM) * (R(1) - F.S_QUANT);
  c.r_star = m::ipow(F.PI, 3) / F.P_BASE - F.PHI;
  return c;
}

}  // namespace fsot::derive
