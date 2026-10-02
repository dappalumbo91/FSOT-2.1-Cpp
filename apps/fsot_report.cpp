// fsot_report: C++ counterpart of `python fsot_compute.py` full_report (mp169 if available).
#include <cstdio>
#include "fsot/engine.hpp"
using namespace fsot;
#if defined(FSOT_HAVE_BOOST_MP)
using R = mp169;
#else
using R = long double;
#endif
int main() {
  Engine<R> e;
  std::printf("FSOT 2.1 C++ engine (authority pin %s), type %s\n", AUTHORITY_PIN_PREFIX.data(), real_traits<R>::name());
  std::printf("ALPHA=%s\nC_EFF=%s\nK=%s\n", to_string(e.ALPHA, 30).c_str(), to_string(e.C_EFF, 30).c_str(), to_string(e.K, 30).c_str());
  for (auto& d : e.DOMAINS)
    std::printf("  %-22s D=%2d hits=%d obs=%d S=%s\n", std::string(d.name).c_str(), d.D_eff, d.hits, d.observed, to_string(e.domain_scalar(d.name), 20).c_str());
  int total = 0, pass = 0;
  for (auto& [name, fn] : e.sections()) {
    std::printf("== %s\n", name);
    for (auto& r : (e.*fn)()) {
      std::printf("  %-36s %s", r.name.c_str(), to_string(r.computed, 15).c_str());
      if (r.measured && *r.measured != R(0)) {
        double err = static_cast<double>(m::fabs(r.computed - *r.measured) / m::fabs(*r.measured) * R(100));
        ++total; pass += err < 5.0;
        std::printf("  target=%s err=%.4g%%", to_string(*r.measured, 8).c_str(), err);
      }
      std::printf("\n");
    }
  }
  std::printf("Total constants with targets: %d\nWithin 5%% of target: %d\n", total, pass);
}
