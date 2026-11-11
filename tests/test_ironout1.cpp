// IRONOUT-1 (Damian t995u/t987u): the re-derived rows of the single-engine table stay in bar against the accepted
// references (cited in reference/scoring_criteria_ironout1.tsv; references are test fixtures, never engine inputs),
// the scaling relations hold exactly, and the authority parity column is not re-derived.
#include <cmath>
#include <cstdio>
#include <map>
#include <string>

#include "fsot/derive/derived_table.hpp"

using namespace fsot;
using R = mp169;

int main() {
  Engine<R> canon(Mode::corrected), parity(Mode::parity);
  const auto T = derive::table(canon, true), P = derive::table(parity, false);
  std::map<std::string, R> v, pv;
  for (auto& r : T) v[r.section + "|" + r.name] = r.value;
  for (auto& r : P) pv[r.section + "|" + r.name] = r.value;
  int fails = 0;
  struct Ref { const char* key; double obs, sig; };
  const Ref refs[] = {
      {"wave3|Ising2D_beta", 0.326419, 3e-6},  {"wave3|Ising2D_nu", 0.629971, 4e-6},   {"wave3|Ising2D_gamma", 1.237075, 1e-5},
      {"wave7|Ising3D_alpha", 0.110087, 1.2e-5}, {"wave7|Ising3D_eta", 0.0362978, 2e-6}, {"wave7|Ising3D_delta", 4.78984, 1e-5},
      {"wave8|XY_beta", 0.348697, 6e-5},       {"wave8|XY_gamma", 1.317855, 2e-4},     {"chemistry_ionization|IE_H", 13.598434599702, 1e-4},
  };
  for (auto& r : refs) {
    const double z = (double(v.at(r.key)) - r.obs) / r.sig;
    const bool ok = std::fabs(z) <= 1;
    std::printf("  [%s] %-28s %.12g  ref %.12g +- %.1e  z %+.3f\n", ok ? "PASS" : "FAIL", r.key, double(v.at(r.key)), r.obs, r.sig, z);
    if (!ok) ++fails;
  }
  // scaling relations, d = 3 (exact to working precision)
  const R nu = v.at("dynamical_systems|Ising3D_nu_dyn"), be = v.at("dynamical_systems|Ising3D_beta_dyn");
  const R al = v.at("wave7|Ising3D_alpha"), ga = v.at("wave3|Ising2D_gamma"), et = v.at("wave7|Ising3D_eta"), de = v.at("wave7|Ising3D_delta");
  const R eps = lit<R>("1e-40");
  const R rel[] = {al + R(2) * be + ga - R(2), R(3) * nu - (R(2) - al), ga - nu * (R(2) - et), ga - be * (de - R(1)),
                   v.at("wave3|Ising2D_beta") - be, v.at("wave3|Ising2D_nu") - nu};
  const char* nm[] = {"Rushbrooke", "Josephson", "Fisher", "Widom", "wave3 beta = beta_dyn", "wave3 nu = nu_dyn"};
  for (int i = 0; i < 6; ++i) {
    const bool ok = m::fabs(rel[i]) < eps;
    std::printf("  [%s] %s residual %s\n", ok ? "PASS" : "FAIL", nm[i], rel[i].str(3).c_str());
    if (!ok) ++fails;
  }
  // parity column (authority, derived=false) is not re-derived: every moved row still differs there (tools/check.py [10]
  // verifies the parity column against the archive).
  for (auto& r : refs) if (pv.at(r.key) == v.at(r.key)) { std::printf("  [FAIL] parity column carries the IRONOUT value for %s\n", r.key); ++fails; }
  std::printf(fails ? "IRONOUT-1: %d FAIL\n" : "IRONOUT-1: ALL PASS\n", fails);
  return fails ? 1 : 0;
}
