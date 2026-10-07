// lbar_3 on the KSRF axial-partner mass ratio. Passes when the Durr-x
// reading matches the AEB2AD evaluation and |z| <= 1 on 2.9 +/- 2.4.
// Not a precision-record row.
#include <cstdio>
#include <string>

#include "fsot/host/lbar3.hpp"

using namespace fsot;

static int fails = 0;

static void expect(bool ok, const char* name, const std::string& detail) {
  if (ok) return;
  std::printf("  FAIL %s %s\n", name, detail.c_str());
  ++fails;
}

int main() {
#if !defined(FSOT_HAVE_BOOST_MP)
  std::puts("LBAR3: skipped (needs Boost.Multiprecision)");
  return 0;
#else
  Engine<mp169> eng;
  leaves::SeedLeaves<mp169> seeds(eng);
  const lbar3::Reading<mp169> row = lbar3::from_leaves<mp169>(eng, seeds);
  const mp169 z = row.z();
  const mp169 tol = lit<mp169>("1e-15");
  expect(m::fabs(row.value - lit<mp169>("3.0128360396658476572")) <= tol, "value", to_string(row.value, 21));
  expect(m::fabs(row.chiral - (mp169(24) - mp169(12) * m::sqrt(mp169(3)))) <= tol, "chiral",
         to_string(row.chiral, 21));
  expect(m::fabs(z) <= mp169(1), "bar", to_string(z, 16));
  expect(m::fabs(z - lit<mp169>("0.04701501652743652")) <= lit<mp169>("1e-12"), "z", to_string(z, 18));
  std::printf("lbar3 %s  z %s  chiral %s  %s\n", to_string(row.value, 18).c_str(), to_string(z, 8).c_str(),
              to_string(row.chiral, 12).c_str(), fails ? "FAIL" : "PASS");
  if (fails) {
    std::printf("LBAR3: %d failures\n", fails);
    return 1;
  }
  std::puts("LBAR3: pass, record unchanged");
  return 0;
#endif
}
