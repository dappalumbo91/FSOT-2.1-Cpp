// fsot_report: C++ counterpart of `python fsot_compute.py` full_report (mp169 if available).
//   fsot_report              parity mode (byte-parity with the pinned authority)
//   fsot_report --corrected  truncated exponent literals evaluated as exact p/q (audit B-03); every changed
//                            row is listed with its parity value and relative shift.
// Both modes flag rows that are not predictions without changing any frozen value:
//   [computed=target]  computed value equals the target exactly (identity/definition rows, audit B-01)
//   [input:a0=...]     computed value uses a measured literal as input (audit B-02)
// and print the "within 5 %" headline with and without those rows.
#include <cstdio>
#include <cstring>
#include <map>
#include <string>
#include "fsot/engine.hpp"
using namespace fsot;
#if defined(FSOT_HAVE_BOOST_MP)
using R = mp169;
#else
using R = long double;
#endif
int main(int argc, char** argv) {
  const bool corrected = argc > 1 && std::strcmp(argv[1], "--corrected") == 0;
  Engine<R> e(corrected ? Mode::corrected : Mode::parity);
  Engine<R> parity;
  std::printf("FSOT 2.1 C++ engine (authority pin %s), type %s, mode %s\n", AUTHORITY_PIN_PREFIX.data(), real_traits<R>::name(),
              corrected ? "corrected" : "parity");
  std::printf("ALPHA=%s\nC_EFF=%s\nK=%s\n", to_string(e.ALPHA, 30).c_str(), to_string(e.C_EFF, 30).c_str(), to_string(e.K, 30).c_str());
  for (auto& d : e.DOMAINS)
    std::printf("  %-22s D=%2d hits=%d obs=%d S=%s\n", std::string(d.name).c_str(), d.D_eff, d.hits, d.observed, to_string(e.domain_scalar(d.name), 20).c_str());
  std::map<std::string, std::string> literal_input;
  for (auto& li : Engine<R>::LITERAL_INPUT_ROWS) literal_input[li.row] = std::string(li.input) + "=" + li.literal;
  int total = 0, pass = 0, flagged = 0, flagged_pass = 0, changed = 0;
  auto psecs = parity.sections();
  std::size_t si = 0;
  for (auto& [name, fn] : e.sections()) {
    std::printf("== %s\n", name);
    auto rows = (e.*fn)();
    auto prow = (parity.*(psecs[si++].second))();
    for (std::size_t i = 0; i < rows.size(); ++i) {
      auto& r = rows[i];
      std::printf("  %-36s %s", r.name.c_str(), to_string(r.computed, 15).c_str());
      if (r.measured && *r.measured != R(0)) {
        double err = static_cast<double>(m::fabs(r.computed - *r.measured) / m::fabs(*r.measured) * R(100));
        const bool identity = r.computed == *r.measured;
        const auto li = literal_input.find(r.name);
        ++total; pass += err < 5.0;
        std::printf("  target=%s err=%.4g%%", to_string(*r.measured, 8).c_str(), err);
        if (identity || li != literal_input.end()) {
          ++flagged; flagged_pass += err < 5.0;
          if (identity) std::printf("  [non-prediction: computed=target]");
          if (li != literal_input.end()) std::printf("  [non-prediction: input:%s]", li->second.c_str());
        }
      }
      if (corrected && i < prow.size() && prow[i].computed != r.computed) {
        ++changed;
        std::printf("  [corrected; parity=%s rel.shift=%.3g]", to_string(prow[i].computed, 20).c_str(),
                    static_cast<double>(m::fabs(r.computed - prow[i].computed) / m::fabs(prow[i].computed)));
      }
      std::printf("\n");
    }
  }
  std::printf("Total constants with targets: %d\nWithin 5%% of target: %d\n", total, pass);
  std::printf("Flagged non-predictions (computed=target or measured input): %d (%d within 5%%)\n", flagged, flagged_pass);
  std::printf("Genuine predictions with targets: %d\nGenuine predictions within 5%%: %d\n", total - flagged, pass - flagged_pass);
  if (corrected) std::printf("Rows changed by corrected mode: %d\n", changed);
}
