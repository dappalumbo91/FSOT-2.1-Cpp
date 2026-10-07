// The water/air sound ratio from the T2 lab suite. The test passes when the
// AEB2AD evaluation sits at z <= 1 on the printed-tenth bar. This row is not
// the precision record.
#include <cstdio>
#include <string>

#include "fsot/host/fluid_lab.hpp"

using namespace fsot;

static int fails = 0;

static void expect(bool ok, const char* name, const std::string& detail) {
  if (ok) return;
  std::printf("  FAIL %s %s\n", name, detail.c_str());
  ++fails;
}

int main() {
#if !defined(FSOT_HAVE_BOOST_MP)
  std::puts("FLUID LAB: skipped (needs Boost.Multiprecision)");
  return 0;
#else
  Engine<mp169> eng;
  leaves::SeedLeaves<mp169> seeds(eng);
  fluid::Lab<mp169> lab(seeds);
  const auto row = lab.water_air_sound_ratio();
  const mp169 z = row.z();
  const mp169 tol = lit<mp169>("1e-12");
  expect(m::fabs(row.value - lit<mp169>("4.31981336304940964574")) <= tol, "value", to_string(row.value, 20));
  expect(z <= mp169(1), "z", to_string(z, 16));
  expect(m::fabs(z - lit<mp169>("0.7215192737401")) <= lit<mp169>("1e-9"), "z lock", to_string(z, 16));
  const mp169 center = lit<mp169>("1482.4") / lit<mp169>("343.2");
  expect(m::fabs(row.center - center) <= tol, "center", to_string(row.center, 20));
  std::printf("water/air %s  z %s  %s\n", to_string(row.value, 20).c_str(), to_string(z, 12).c_str(),
              z <= mp169(1) ? "PASS" : "FAIL");
  if (fails) {
    std::printf("FLUID LAB: %d failures\n", fails);
    return 1;
  }
  std::puts("FLUID LAB: water/air passes, record unchanged");
  return 0;
#endif
}
