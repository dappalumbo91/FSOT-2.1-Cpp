// Isovector radius. Passes when the KSRF dipole times sqrt(F_pi/F) is inside
// 0.82236 +/- 0.00201, and the unsquared ratio is outside. Not a record row.
#include <cstdio>
#include <string>

#include "fsot/host/nucleon_radius.hpp"

using namespace fsot;

static int fails = 0;

static void expect(bool ok, const char* name, const std::string& detail) {
  if (ok) return;
  std::printf("  FAIL %s %s\n", name, detail.c_str());
  ++fails;
}

int main() {
#if !defined(FSOT_HAVE_BOOST_MP)
  std::puts("NUCLEON RADIUS: skipped (needs Boost.Multiprecision)");
  return 0;
#else
  Engine<mp169> eng;
  leaves::SeedLeaves<mp169> seeds(eng);
  const nucleon::Radius<mp169> row = nucleon::r_v2<mp169>(eng, seeds);
  const mp169 z = row.z();
  const mp169 tol = lit<mp169>("1e-15");
  expect(m::fabs(row.value - lit<mp169>("0.824200116307649382")) <= tol, "value", to_string(row.value, 20));
  expect(m::fabs(z) <= mp169(1), "bar", to_string(z, 16));
  expect(m::fabs(z - lit<mp169>("0.9154807500743")) <= lit<mp169>("1e-12"), "z", to_string(z, 16));
  const mp169 z_bare = (row.dipole - row.center) / row.sigma;
  const mp169 z_ratio = (row.dipole * m::ipow(row.weight, 2) - row.center) / row.sigma;
  const mp169 z_square = (row.dipole * m::ipow(row.weight, 4) - row.center) / row.sigma;
  expect(m::fabs(z_bare) > mp169(1), "bare dipole outside", to_string(z_bare, 8));
  expect(m::fabs(z_ratio) > mp169(1), "full ratio outside", to_string(z_ratio, 8));
  expect(m::fabs(z_square) > mp169(1), "square outside", to_string(z_square, 8));
  std::printf("nucleon r_V2 %s  z %s  %s\n", to_string(row.value, 18).c_str(), to_string(z, 12).c_str(),
              fails ? "FAIL" : "PASS");
  if (fails) {
    std::printf("NUCLEON RADIUS: %d failures\n", fails);
    return 1;
  }
  std::puts("NUCLEON RADIUS: pass, record unchanged");
  return 0;
#endif
}
