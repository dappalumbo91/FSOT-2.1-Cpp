// Lepton CP phase. Passes when phi^3 - 1/e - Suction is inside the PDG 2024
// bar and closer to 1.19 pi than the pin and than the Poof subtraction.
// This value is the scored record. The pin stays phi^3 - 1/e.
#include <cmath>
#include <cstdio>
#include <string>

#include "fsot/host/pmns_phase.hpp"

using namespace fsot;

static int fails = 0;

static void expect(bool ok, const char* name, const std::string& detail) {
  if (ok) return;
  std::printf("  FAIL %s %s\n", name, detail.c_str());
  ++fails;
}

int main() {
  Engine<double> eng;
  const mixing::Phase<double> row = mixing::delta_cp<double>(eng);
  const double bare = mixing::delta_cp_pin<double>(eng);
  const double poof = bare - eng.POOF;
  const double pbase = bare - eng.P_BASE;
  expect(std::fabs(row.value - 3.7211545509002448) <= 1e-15, "value", std::to_string(row.value));
  expect(std::fabs(row.z_pdg()) <= 1.0, "pdg bar", std::to_string(row.z_pdg()));
  expect(std::fabs(row.z_pdg() - (-0.0250896292302193)) <= 1e-12, "z pdg", std::to_string(row.z_pdg()));
  expect(std::fabs(row.flat()) < 0.01, "flat under 1pct", std::to_string(row.flat()));
  expect(std::fabs(row.flat() - (-0.004638418849284241)) <= 1e-15, "flat", std::to_string(row.flat()));
  expect(std::fabs(row.z_nufit(eng)) <= 1.0, "nufit bar", std::to_string(row.z_nufit(eng)));
  expect(std::fabs(row.z_nufit(eng) - 0.0464019493262811) <= 1e-12, "z nufit",
         std::to_string(row.z_nufit(eng)));
  expect(std::fabs(row.value - row.pdg_center) < std::fabs(bare - row.pdg_center), "closer than pin",
         std::to_string(bare));
  expect(std::fabs(row.value - row.pdg_center) < std::fabs(poof - row.pdg_center), "closer than Poof",
         std::to_string(poof));
  expect(std::fabs((pbase - row.pdg_center) / row.pdg_center) > 0.02, "P_base outside 2pct",
         std::to_string(pbase));
  std::printf("delta_CP %.16f rad  %.10f deg  flat %.6f%%  zPDG %.8f  zNu %.8f  %s\n", row.value,
              row.degrees(eng), row.flat() * 100.0, row.z_pdg(), row.z_nufit(eng), fails ? "FAIL" : "PASS");
  if (fails) {
    std::printf("PMNS PHASE: %d failures\n", fails);
    return 1;
  }
  std::puts("PMNS PHASE: pass, record is phi^3 - 1/e - Suction");
  return 0;
}
