// Owner-discretion catalog leaves. The test passes when each leaf matches the
// AEB2AD evaluation and sits at z <= 1 on the bar its script froze.
// These rows are not the precision record. A future edit that pushes one
// outside its bar fails here.
#include <cstdio>
#include <string>

#include "fsot/host/catalog_leaves.hpp"

using namespace fsot;

static int fails = 0;

static void expect(bool ok, const char* name, const std::string& detail) {
  if (ok) return;
  std::printf("  FAIL %s %s\n", name, detail.c_str());
  ++fails;
}

#if defined(FSOT_HAVE_BOOST_MP)
static void check(const char* name, const catalog::Scored<mp169>& row, const char* value, const char* z_lock) {
  const mp169 z = row.z();
  const mp169 tol_v = lit<mp169>("1e-12");
  const mp169 tol_z = lit<mp169>("1e-9");
  expect(m::fabs(row.value - lit<mp169>(value)) <= tol_v, name, to_string(row.value, 20));
  expect(z <= mp169(1), name, "z " + to_string(z, 16));
  expect(m::fabs(z - lit<mp169>(z_lock)) <= tol_z, name, "z " + to_string(z, 16));
  std::printf("%-8s %s  z %s  %s\n", name, to_string(row.value, 16).c_str(), to_string(z, 8).c_str(),
              z <= mp169(1) ? "PASS" : "FAIL");
}
#endif

int main() {
#if !defined(FSOT_HAVE_BOOST_MP)
  std::puts("CATALOG LEAVES: skipped (needs Boost.Multiprecision)");
  return 0;
#else
  Engine<mp169> eng;
  leaves::SeedLeaves<mp169> seeds(eng);
  catalog::Leaves<mp169> L(seeds);

  check("Al", L.aluminum_ie(), "5.985769137426847890", "0.045808949296524791");
  check("Cl", L.chlorine_ie(), "12.967632959415985732", "0.002536500891743281");
  check("Si", L.silicon_ie(), "8.151680003030119109", "0.000101003970304373");
  check("P", L.phosphorus_ie(), "10.486686001486598250", "0.000099106549971181");
  check("S", L.sulfur_ie(), "10.360016699986985559", "0.000009296029561140");
  check("Ar", L.argon_ie(), "15.759611898938518279", "0.002122963441968786");
  check("K", L.potassium_ie(), "4.340663729885916897", "0.001267590031447096");
  check("CH4", L.methane_bp(), "111.666696853990395145", "0.606292019209709201");
  check("NH3", L.ammonia_bp(), "239.834610236190766226", "0.263944961915098927");
  check("EtOH", L.ethanol_bp(), "351.438784066943641258", "0.243186611271748466");
  check("NaCl", L.nacl_lattice(), "785.891428589034057051", "0.217142821931885897");
  check("olive", L.olive_oil_viscosity(), "83.995865659429726716", "0.008268681140546567");
  check("C6H12", L.cyclohexane_kf(), "20.031616375711796662", "0.063232751423593324");

  const auto nh3 = L.ammonia_bp();
  expect(m::fabs(nh3.sigma - lit<mp169>("0.00988932")) <= lit<mp169>("1e-15"), "NH3 bar",
         to_string(nh3.sigma, 16));

  if (fails) {
    std::printf("CATALOG LEAVES: %d failures\n", fails);
    return 1;
  }
  std::puts("CATALOG LEAVES: 13 pass, record unchanged");
  return 0;
#endif
}
