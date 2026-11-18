// Folded dial-in routes: re-derive every tip prediction inside the engine and re-score z against the held-out value.
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

#include "fsot/fold/folded_routes.hpp"

using namespace fsot;
int main() {
#if !defined(FSOT_HAVE_BOOST_MP)
  std::puts("FOLDED ROUTES: skipped (needs Boost.Multiprecision)"); return 0;
#else
  std::ifstream in(FSOT_FOLDED_TSV);
  if (!in) { std::fprintf(stderr, "cannot open %s\n", FSOT_FOLDED_TSV); return 2; }
  Engine<mp169> F; leaves::SeedLeaves<mp169> L(F);
  const auto vpk = fold::vt::Package<mp169>::load(FSOT_VT_PACKAGE_TSV);
  const fold::vt::Chain<mp169> vch{vpk, fold::vt::engine_inputs(L)};
  const auto vvwpk = fold::vt::Package<mp169>::load(FSOT_VV_VW_PACKAGE_TSV);
  fold::vt::Chain<mp169> vvw{vpk, fold::vt::engine_inputs(L)};
  vvw.hooks = fold::vt::vv_p3_vw_p3(vvwpk);
  fold::Live<mp169> live{F, L, &vch, &vvw};
  int flagged = 0;
  std::string line; int rows = 0, live_ok = 0, live_n = 0, z_ok = 0, z_n = 0, inbar = 0, outbar = 0, fails = 0, hooks = 0, rec_only = 0;
  double worst_rel = 0; std::string worst;
  while (std::getline(in, line)) {
    if (line.empty() || line[0] == '#') continue;
    std::vector<std::string> c; std::stringstream ss(line); std::string x;
    while (std::getline(ss, x, '\t')) c.push_back(x);
    c.resize(9);
    if (c[0] == "HOOK") { ++hooks; std::printf("  HOOK %s: %s\n", c[1].c_str(), c[6].c_str()); continue; }
    ++rows;
    if (c[0].rfind("43.5vt", 0) == 0 || c[0].rfind("43.5vv", 0) == 0 || c[0].rfind("43.5vw", 0) == 0) {  // t994u: every G_F-chain row carries the flag
      if (c[6].find(fold::vt::kStatus) == std::string::npos) { std::printf("  FAIL %s %s: missing %s\n", c[0].c_str(), c[1].c_str(), fold::vt::kStatus); ++fails; }
      else ++flagged;
    }
    if (c[2].empty()) { ++rec_only; continue; }
    const double pred_rec = std::strtod(c[2].c_str(), nullptr);
    double pred = pred_rec;
    if (!c[7].empty()) {
      auto v = live(c[7]);
      if (!v) { std::printf("  FAIL %s: no live function %s\n", c[0].c_str(), c[7].c_str()); ++fails; continue; }
      ++live_n;
      const mp169 rec(c[2].c_str());
      const double rel = static_cast<double>(m::fabs(*v - rec) / m::fabs(rec));
      const int digits = int(std::count_if(c[2].begin(), c[2].end(), ::isdigit));
      const double tol = std::max(1e-30, 6.0 * std::pow(10.0, -(digits - 1)));
      if (rel > worst_rel) { worst_rel = rel; worst = c[0] + " " + c[1]; }
      if (rel <= tol) ++live_ok; else { std::printf("  FAIL %s %s live %.20g vs recorded %s (rel %.2e)\n", c[0].c_str(), c[1].c_str(), double(*v), c[2].c_str(), rel); ++fails; }
      pred = static_cast<double>(*v);
    }
    if (!c[3].empty() && !c[4].empty()) {
      const double obs = std::strtod(c[3].c_str(), nullptr), sig = std::strtod(c[4].c_str(), nullptr);
      const double z = (pred - obs) / sig;
      std::fabs(z) <= 1.0 ? ++inbar : ++outbar;
      if (!c[5].empty()) {
        ++z_n;
        const double zr = std::strtod(c[5].c_str(), nullptr);
        if (std::fabs(std::fabs(z) - std::fabs(zr)) <= 2e-3 + 1e-4 * std::fabs(zr)) ++z_ok;
        else { std::printf("  FAIL z %s %s: engine %.6f recorded %s\n", c[0].c_str(), c[1].c_str(), z, c[5].c_str()); ++fails; }
      }
    }
  }
  std::printf("folded routes: %d rows (%d route-level records), %d/%d tip predictions re-derived live (worst rel %.2e [%s]), "
              "%d/%d z re-scored; in-bar |z|<=1: %d, out-of-bar: %d; hooks %d; %s rows %d\n", rows, rec_only, live_ok, live_n, worst_rel,
              worst.c_str(), z_ok, z_n, inbar, outbar, hooks, fold::vt::kStatus, flagged);
  std::puts(fails ? "FOLDED ROUTES: FAIL" : "FOLDED ROUTES: ALL PASS");
  return fails ? 1 : 0;
#endif
}
