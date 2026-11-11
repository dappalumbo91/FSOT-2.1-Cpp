// Golden check for fsot/host/quantum_rc_fornax.hpp: FSOT-Quantum docs/FORMULA_LIST.md @ 3c4375a,
// recomputed at AEB2AD (mpmath dps 40; seeds from golden/golden_AEB2AD.tsv).
#include <cstdio>
#include <string>

#include "fsot/host/quantum_rc_fornax.hpp"

using namespace fsot;

static int fails = 0;
template <class R> static void expect(const R& got, const char* want, const char* tol, const char* name) {
  const R d = m::fabs(got - lit<R>(want));
  const bool ok = d <= lit<R>(tol);
  std::printf("  %-8s %s  %s\n", name, to_string(got, 20).c_str(), ok ? "PASS" : "FAIL");
  if (!ok) ++fails;
}

int main() {
#if !defined(FSOT_HAVE_BOOST_MP)
  std::puts("QUANTUM R_C FORNAX: skipped (needs Boost.Multiprecision)");
  return 0;
#else
  using R = mp169;
  Engine<R> eng;
  expect(eng.ETA_EFF, "0.46694220692425985998339481323366757", "1e-30", "ETA_EFF");
  expect(eng.POOF, "0.15348221489445079910819397263148312", "1e-30", "POOF");
  expect(quantum::r_c_fornax(eng), "0.60204614669088815147084257396459141", "1e-30", "r_c");
  expect(quantum::r_c_fornax(eng), "0.6020461466908882", "1e-15", "r_c_pub");  // D1D38A published value
  if (fails) { std::printf("QUANTUM R_C FORNAX: %d failures\n", fails); return 1; }
  std::puts("QUANTUM R_C FORNAX: golden matches FSOT-Quantum@3c4375a at AEB2AD");
  return 0;
#endif
}
