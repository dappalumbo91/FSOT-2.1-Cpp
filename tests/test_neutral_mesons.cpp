// Neutral K0, pi0, eta, and eta-prime. The test passes when each selected
// branch matches the AEB2AD evaluation and sits at |z| <= 1 on its PDG bar.
// These rows are not the precision record.
#include <cmath>
#include <cstdio>
#include <string>

#include "fsot/host/neutral_mesons.hpp"

using namespace fsot;

static int fails = 0;

static void expect(bool ok, const char* name, const std::string& detail) {
  if (ok) return;
  std::printf("  FAIL %s %s\n", name, detail.c_str());
  ++fails;
}

#if defined(FSOT_HAVE_BOOST_MP)
static void check(const char* name, const neutral::Scored<mp169>& row, const char* value, const char* z_lock) {
  const mp169 z = row.z();
  const mp169 tol_v = lit<mp169>("1e-9");
  const mp169 tol_z = lit<mp169>("1e-6");
  expect(m::fabs(row.value - lit<mp169>(value)) <= tol_v, name, to_string(row.value, 20));
  expect(m::fabs(z) <= mp169(1), name, "z " + to_string(z, 16));
  expect(m::fabs(z - lit<mp169>(z_lock)) <= tol_z, name, "z " + to_string(z, 16));
  std::printf("%-6s %s  z %s  %s\n", name, to_string(row.value, 16).c_str(), to_string(z, 8).c_str(),
              m::fabs(z) <= mp169(1) ? "PASS" : "FAIL");
}
#endif

int main() {
#if !defined(FSOT_HAVE_BOOST_MP)
  std::puts("NEUTRAL MESONS: skipped (needs Boost.Multiprecision)");
  return 0;
#else
  Engine<mp169> eng;
  leaves::SeedLeaves<mp169> seeds(eng);
  neutral::Masses<mp169> M(seeds);

  check("K0", M.k0(), "497.61120080088705497", "0.01544622208115139");
  check("pi0", M.pi0(), "134.97679871406545433", "-0.002571869091349485");
  check("eta", M.eta(), "547.86869881331816316", "0.394047842244892");
  check("etap", M.etap(), "957.79231160159958598", "0.2051933599930997");

  if (fails) {
    std::printf("NEUTRAL MESONS: %d failures\n", fails);
    return 1;
  }
  std::puts("NEUTRAL MESONS: 4 pass, record unchanged");
  return 0;
#endif
}
