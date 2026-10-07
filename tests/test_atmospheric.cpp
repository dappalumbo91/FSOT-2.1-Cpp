// Atmospheric angle. Passes when |S|/2 on the generation-9 specimen rung is
// inside NuFIT 6.1 normal ordering with SK, and closer than the other
// specimen halves that also sit in that bar. The PDG record stays outside
// this bar. Not a record row.
#include <cmath>
#include <cstdio>
#include <string>

#include "fsot/host/atmospheric.hpp"

using namespace fsot;

static int fails = 0;

static void expect(bool ok, const char* name, const std::string& detail) {
  if (ok) return;
  std::printf("  FAIL %s %s\n", name, detail.c_str());
  ++fails;
}

static double z_of(double v) {
  const double d = v - 0.470;
  return d / (d >= 0.0 ? 0.017 : 0.014);
}

int main() {
  Engine<double> eng;
  const mixing::Atmospheric<double> row = mixing::sin2_theta23<double>(eng);
  const double cm = mixing::specimen_half<double>(eng, "Condensed_Matter");
  const char* wider[] = {
      "Particle_Physics", "Physical_Chemistry", "Electromagnetism", "Optics",
      "Biochemistry",     "Thermodynamics",     "Psychology",        "Sociology"};
  expect(row.D_eff == 11, "D_eff", std::to_string(row.D_eff));
  expect(std::fabs(row.value - cm) <= 1e-15, "shared rung", std::to_string(cm));
  expect(std::fabs(row.value - 0.4706353135781523) <= 1e-15, "value", std::to_string(row.value));
  expect(std::fabs(row.z()) <= 1.0, "bar", std::to_string(row.z()));
  expect(std::fabs(row.z() - 0.0373713869501371) <= 1e-12, "z", std::to_string(row.z()));
  for (const char* name : wider) {
    const double h = mixing::specimen_half<double>(eng, name);
    expect(std::fabs(z_of(h)) <= 1.0, "wider inside", std::string(name) + " " + std::to_string(z_of(h)));
    expect(std::fabs(row.value - 0.470) < std::fabs(h - 0.470), "closer",
           std::string(name) + " " + std::to_string(h));
  }
  const double rec = std::fabs(eng.CHAOS) * std::sqrt(eng.E);
  expect(std::fabs(z_of(rec)) > 1.0, "record outside", std::to_string(z_of(rec)));
  std::printf("sin2_theta23 %.16f  z %.16f  %s\n", row.value, row.z(), fails ? "FAIL" : "PASS");
  if (fails) {
    std::printf("ATMOSPHERIC: %d failures\n", fails);
    return 1;
  }
  std::puts("ATMOSPHERIC: pass, record unchanged");
  return 0;
}
