// Delta-N. Passes when the P3 profile times (F/F_pi)^((N_c-1)/N_c) is inside
// the published +/- 2 MeV bar, and the power 1 and power 1/2 readings are
// outside. Not a record row.
#include <cstdio>
#include <string>

#include "fsot/host/nucleon_delta.hpp"

using namespace fsot;

static int fails = 0;

static void expect(bool ok, const char* name, const std::string& detail) {
  if (ok) return;
  std::printf("  FAIL %s %s\n", name, detail.c_str());
  ++fails;
}

int main() {
#if !defined(FSOT_HAVE_BOOST_MP)
  std::puts("NUCLEON DELTA: skipped (needs Boost.Multiprecision)");
  return 0;
#else
  Engine<mp169> eng;
  leaves::SeedLeaves<mp169> seeds(eng);
  const nucleon::Delta<mp169> row = nucleon::delta_n<mp169>(eng, seeds);
  const mp169 z = row.z();
  const mp169 tol = lit<mp169>("1e-12");
  expect(m::fabs(row.value - lit<mp169>("293.3782747823462506")) <= tol, "value", to_string(row.value, 20));
  expect(m::fabs(z) <= mp169(1), "bar", to_string(z, 16));
  expect(m::fabs(z - lit<mp169>("0.1485151937584")) <= lit<mp169>("1e-12"), "z", to_string(z, 16));
  const mp169 z_full = (row.profile_MeV * m::pow(row.weight, mp169(3) / mp169(2)) - row.center) / row.sigma;
  const mp169 z_half = (row.profile_MeV * m::pow(row.weight, mp169(3) / mp169(4)) - row.center) / row.sigma;
  expect(m::fabs(z_full) > mp169(1), "power 1 outside", to_string(z_full, 8));
  expect(m::fabs(z_half) > mp169(1), "power 1/2 outside", to_string(z_half, 8));
  std::printf("nucleon Delta-N %s MeV  z %s  %s\n", to_string(row.value, 18).c_str(), to_string(z, 12).c_str(),
              fails ? "FAIL" : "PASS");
  if (fails) {
    std::printf("NUCLEON DELTA: %d failures\n", fails);
    return 1;
  }
  std::puts("NUCLEON DELTA: pass, record unchanged");
  return 0;
#endif
}
