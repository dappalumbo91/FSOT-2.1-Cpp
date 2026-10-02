// Ledger A emit + property routing vs golden/ledger_a_routing.tsv (hub Python, bit-exact via repr()).
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

#include "fsot/host/ledger_a.hpp"

using namespace fsot;
static std::string fmt(std::optional<double> v) { return v ? py::repr(*v) : "None"; }

int main(int argc, char** argv) {
  std::ifstream in(argc > 1 ? argv[1] : FSOT_LA_GOLDEN);
  long n[4] = {0, 0, 0, 0}, bad = 0, sig_bad = 0, dp_bad = 0;
  for (std::string line; std::getline(in, line);) {
    if (line.empty() || line[0] == '#') continue;
    std::vector<std::string> f;
    std::stringstream ss(line);
    for (std::string c; std::getline(ss, c, '\t');) f.push_back(c);
    if (line.back() == '\t') f.push_back("");
    std::string got, want;
    if (f[0] == "A") {
      auto r = ledger_a::compare_anchor(f[1]);
      got = r ? py::repr(r->first.value) + "\t" + py::repr(r->second) + "\t" + r->first.pin : "<missing>";
      want = f[2] + "\t" + f[3] + "\t" + f[4];
      ++n[0];
    } else if (f[0] == "MASS") {
      got = fmt(ledger_a::formula_mass(f[1])); want = f[2]; ++n[1];
    } else if (f[0] == "ROUTE") {
      auto [d, fac] = ledger_a::route_property(f[1], "<default>");
      got = d + "\t" + py::repr(fac); want = f[2] + "\t" + f[3]; ++n[2];
    } else if (f[0] == "REC") {
      auto r = ledger_a::make_fsot_record(f[1], std::strtod(f[4].c_str(), nullptr), f[2], f[3]);
      got = r ? py::repr(r->computed) + "\t" + py::repr(r->error_pct) + "\t" + r->eval_kind + "\t" + r->fsot_domain + "\t" + py::repr(r->fsot_scalar) : "<none>";
      want = f[5] + "\t" + f[6] + "\t" + f[7] + "\t" + f[8] + "\t" + f[9];
      ++n[3];
      // corrected emitter: error recomputed from the emitted (computed, measured) pair reproduces error_pct
      const double mv = std::strtod(f[4].c_str(), nullptr);
      if (auto rc = ledger_a::make_fsot_record(f[1], mv, f[2], f[3], /*corrected=*/true)) {
        const double back = ledger_a::err_pct(rc->computed, mv);
        if (std::fabs(back - rc->error_pct) > 1e-9 + 1e-6 * rc->error_pct) ++sig_bad;
        if (r) { const double back6 = ledger_a::err_pct(r->computed, mv);
                 if (std::fabs(back6 - r->error_pct) > 1e-6 + 1e-4 * r->error_pct) ++dp_bad; }
      }
    } else continue;
    if (got != want) { if (bad < 15) std::printf("MISMATCH %s\n  cpp:    %s\n  python: %s\n", line.substr(0, 80).c_str(), got.c_str(), want.c_str()); ++bad; }
  }
  std::printf("Ledger A %ld, formula_mass %ld, route_property %ld, make_fsot_record %ld: %ld mismatches -> %s\n", n[0], n[1], n[2], n[3], bad,
              bad || !n[0] ? "FAIL" : "PASS (bit-identical)");
  std::printf("emitter self-consistency (error recomputed from emitted computed): parity round(c,6) %ld irreproducible, corrected round_sig(c,12) %ld\n",
              dp_bad, sig_bad);
  return bad || !n[0] || sig_bad ? 1 : 0;
}
