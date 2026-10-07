// Neutron moment. Passes when the physical-pion isoscalar, times sqrt(F_pi/F),
// times (1 + G alpha/(2 pi)), is inside the CODATA bar, and the nearer
// neighbors are outside. The proton from this fold stays outside. Not a record row.
#include <cstdio>
#include <string>

#include "fsot/host/nucleon_moment.hpp"

using namespace fsot;

static int fails = 0;

static void expect(bool ok, const char* name, const std::string& detail) {
  if (ok) return;
  std::printf("  FAIL %s %s\n", name, detail.c_str());
  ++fails;
}

int main() {
#if !defined(FSOT_HAVE_BOOST_MP)
  std::puts("NUCLEON MOMENT: skipped (needs Boost.Multiprecision)");
  return 0;
#else
  Engine<mp169> eng;
  leaves::SeedLeaves<mp169> seeds(eng);
  const nucleon::Moment<mp169> row = nucleon::magnetic<mp169>(eng, seeds);
  const mp169 z = row.z();
  const mp169 bare_n = (row.isoscalar - row.isovector) / mp169(2);
  const mp169 bare_p = (row.isoscalar + row.isovector) / mp169(2);
  const mp169 sqrt_n = (row.isoscalar * row.weight - row.isovector) / mp169(2);
  const mp169 minus_n = sqrt_n * (mp169(2) - row.dress);
  const mp169 alpha_n = sqrt_n * (mp169(1) + eng.G_CAT * seeds.alpha());
  const mp169 full_n = (row.isoscalar * row.weight * row.weight - row.isovector) / mp169(2) * row.dress;
  auto zn = [&](const mp169& v) { return (v - row.center) / row.sigma; };
  expect(m::fabs(bare_n - lit<mp169>("-1.92581799223")) <= lit<mp169>("1e-11"), "bare neutron", to_string(bare_n, 16));
  expect(m::fabs(bare_p - lit<mp169>("2.76601991939")) <= lit<mp169>("1e-11"), "bare proton", to_string(bare_p, 16));
  expect(m::fabs(row.neutron - lit<mp169>("-1.913042805746640751")) <= lit<mp169>("1e-15"), "value", to_string(row.neutron, 20));
  expect(m::fabs(z) <= mp169(1), "bar", to_string(z, 16));
  expect(m::fabs(z - lit<mp169>("-0.1016592016694")) <= lit<mp169>("1e-12"), "z", to_string(z, 16));
  expect(m::fabs(zn(bare_n)) > mp169(1), "bare outside", to_string(zn(bare_n), 8));
  expect(m::fabs(zn(sqrt_n)) > mp169(1), "sqrt outside", to_string(zn(sqrt_n), 8));
  expect(m::fabs(zn(minus_n)) > mp169(1), "minus seed outside", to_string(zn(minus_n), 8));
  expect(m::fabs(zn(alpha_n)) > mp169(1), "alpha seed outside", to_string(zn(alpha_n), 8));
  expect(m::fabs(zn(full_n)) > mp169(1), "full ratio outside", to_string(zn(full_n), 8));
  expect(m::fabs(row.proton_z()) > mp169(1), "proton outside", to_string(row.proton_z(), 8));
  std::printf("nucleon mu_n %s  z %s  %s\n", to_string(row.neutron, 18).c_str(), to_string(z, 12).c_str(),
              fails ? "FAIL" : "PASS");
  if (fails) {
    std::printf("NUCLEON MOMENT: %d failures\n", fails);
    return 1;
  }
  std::puts("NUCLEON MOMENT: pass, record unchanged");
  return 0;
#endif
}
