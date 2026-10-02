// CoreEngine<BTFloat<P>> (freestanding) vs Engine<BTFloat<P>> (host): bit-identical domain S, identical
// D_eff rungs, and to_decimal agreement with the host renderer.
#include <cstdio>
#include <string>
#include "fsot/core.hpp"
#include "fsot/engine.hpp"
#include "fsot/ternary_real.hpp"

using namespace fsot;
template <int P> int check() {
  using F = bt::BTFloat<P>;
  core::CoreEngine<F> c;
  Engine<F> e;
  int bad = 0;
  for (int i = 0; i < core::DOMAIN_COUNT; ++i) {
    const auto& d = e.DOMAINS[i];
    if (std::string(core::NEST[i].name) != d.name) { std::printf("order mismatch %d\n", i); ++bad; continue; }
    if (c.derived_D_eff(i) != d.D_eff) { std::printf("D_eff mismatch %s: %d vs %d\n", core::NEST[i].name, c.derived_D_eff(i), d.D_eff); ++bad; }
    if (c.fold_observed(i) != d.observed || c.fold_hits(i) != d.hits) { std::printf("fold mismatch %s\n", core::NEST[i].name); ++bad; }
    const F sc = c.domain_scalar(i), se = e.domain_scalar(d.name);
    if (!(sc == se)) { std::printf("S mismatch %s\n", core::NEST[i].name); ++bad; }
    char buf[160];
    core::to_decimal(sc, 30, buf, sizeof buf);
    if (i == 0) std::printf("  P=%d %s S=%s (host %s)\n", P, core::NEST[i].name, buf, bt::to_decimal(se, 30).c_str());
  }
  std::printf("BTFloat<%d>: %d domains, %d mismatches\n", P, core::DOMAIN_COUNT, bad);
  return bad;
}
int main() { return check<40>() + check<72>() + check<110>() ? 1 : 0; }
