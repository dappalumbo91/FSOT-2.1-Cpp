// Seed leaves (hub scripts/*_seed_check.py @ 6f9c2560) in C++ vs the values printed by the hub's
// own Python (golden/seed_leaves_6f9c2560.tsv, written by tools/dump_seed_leaves_golden.py).
// mp169 leaves: relative difference <= 1e-40. CKM magnitudes (IEEE double in the hub): bit-identical.
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <map>
#include <sstream>
#include <string>

#include "fsot/host/seed_leaves.hpp"

using namespace fsot;

int main() {
#if !defined(FSOT_HAVE_BOOST_MP)
  std::puts("SEED LEAVES: skipped (needs Boost.Multiprecision)");
  {
    const double v = static_cast<double>(leaves::sqrt8t0_over_r0<double>());
    if (std::abs(v - 0.9428090415820634) > 1e-15) { std::fprintf(stderr, "sqrt8t0_over_r0 %.17g\n", v); return 1; }
  }
  return 0;
#else
  std::ifstream in(FSOT_SEED_LEAVES_TSV);
  if (!in) { std::fprintf(stderr, "cannot open %s\n", FSOT_SEED_LEAVES_TSV); return 2; }
  std::map<std::string, std::string> gold;
  std::string line;
  while (std::getline(in, line)) {
    if (line.empty() || line[0] == '#') continue;
    std::istringstream ss(line);
    std::string id, script, sha, key, val;
    std::getline(ss, id, '\t'); std::getline(ss, script, '\t'); std::getline(ss, sha, '\t');
    std::getline(ss, key, '\t'); std::getline(ss, val, '\t');
    gold[id] = val;
  }
  Engine<mp169> eng;
  leaves::SeedLeaves<mp169> L(eng);
  int checked = 0, failed = 0;
  double worst = 0; std::string worst_id;
  for (auto& [id, v] : L.mp_values()) {
    auto it = gold.find(id);
    if (it == gold.end()) { std::printf("  %-20s MISSING in golden\n", id.c_str()); ++failed; continue; }
    const mp169 g(it->second.c_str());
    const double rel = static_cast<double>(m::fabs(v - g) / m::fabs(g));
    ++checked;
    if (rel > worst) { worst = rel; worst_id = id; }
    if (!(rel <= 1e-40)) { std::printf("  %-20s FAIL rel=%.3e\n", id.c_str(), rel); ++failed; }
  }
  {  // 43.5tm mu_R host atom: CPT mu_pbar = -mu_p = -g_p/2
    const double mp = static_cast<double>(L.mu_p_host()), mpb = static_cast<double>(L.mu_pbar_host());
    if (std::abs(mp - 2.79284734443575) > 1e-12 || mp + mpb != 0.0) {
      std::fprintf(stderr, "mu_R host %.17g %.17g\n", mp, mpb); ++failed;
    }
  }
  auto ckm = leaves::ckm_double(eng);
  int ckm_ok = 0;
  for (auto& [k, v] : ckm.mags) {
    auto it = gold.find("CKM_" + k);
    if (it == gold.end()) { std::printf("  CKM_%s MISSING\n", k.c_str()); ++failed; continue; }
    const double g = std::strtod(it->second.c_str(), nullptr);
    ++checked;
    if (v == g) ++ckm_ok; else { std::printf("  CKM_%s FAIL %.17g vs %.17g\n", k.c_str(), v, g); ++failed; }
  }
  std::printf("seed leaves: %d checked (%zu golden), mp169 worst rel %.3e [%s], CKM %d/9 bit-identical, %d failed\n",
              checked, gold.size(), worst, worst_id.c_str(), ckm_ok, failed);
  if (checked != static_cast<int>(gold.size())) { std::puts("SEED LEAVES: count mismatch"); return 1; }
  std::puts(failed ? "SEED LEAVES: FAIL" : "SEED LEAVES: ALL PASS");
  return failed ? 1 : 0;
#endif
}
