// g_A on the nuclear rung of the P3 profile. Passes when the dressed reading
// matches the AEB2AD evaluation and |z| <= 1 on 1.2754 +/- 0.0013.
// Not a precision-record row.
#include <cstdio>
#include <string>

#include "fsot/host/nucleon_axial.hpp"

using namespace fsot;

static int fails = 0;

static void expect(bool ok, const char* name, const std::string& detail) {
  if (ok) return;
  std::printf("  FAIL %s %s\n", name, detail.c_str());
  ++fails;
}

int main() {
#if !defined(FSOT_HAVE_BOOST_MP)
  std::puts("NUCLEON AXIAL: skipped (needs Boost.Multiprecision)");
  return 0;
#else
  Engine<mp169> eng;
  leaves::SeedLeaves<mp169> seeds(eng);
  const nucleon::Axial<mp169> row = nucleon::g_a<mp169>(eng, seeds);
  const mp169 z = row.z();
  const mp169 tol = lit<mp169>("1e-14");
  expect(m::fabs(row.value - lit<mp169>("1.27505846641964337")) <= tol, "value", to_string(row.value, 20));
  expect(m::fabs(z) <= mp169(1), "bar", to_string(z, 16));
  expect(m::fabs(z - lit<mp169>("-0.262718138735869")) <= lit<mp169>("1e-12"), "z", to_string(z, 18));
  const mp169 bare = row.profile * row.ratio;
  const mp169 zbare = (bare - row.center) / row.sigma;
  expect(m::fabs(zbare) > mp169(1), "bare ratio outside", to_string(zbare, 8));
  std::printf("nucleon g_A %s  z %s  %s\n", to_string(row.value, 18).c_str(), to_string(z, 8).c_str(),
              fails ? "FAIL" : "PASS");
  if (fails) {
    std::printf("NUCLEON AXIAL: %d failures\n", fails);
    return 1;
  }
  std::puts("NUCLEON AXIAL: pass, record unchanged");
  return 0;
#endif
}
