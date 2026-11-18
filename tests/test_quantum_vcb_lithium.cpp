// Golden check for fsot/host/quantum_vcb_lithium.hpp: FSOT-Quantum docs/FORMULA_LIST.md @ 3c4375a,
// recomputed at AEB2AD (C_EFF from golden/golden_AEB2AD.tsv @ 27d8b48).
#include <cstdio>
#include <string>

#include "fsot/host/quantum_vcb_lithium.hpp"

using namespace fsot;

static int fails = 0;
template <class R> static void expect(const R& got, const char* want, const char* tol, const char* name) {
  const R d = m::fabs(got - lit<R>(want));
  const bool ok = d <= lit<R>(tol);
  std::printf("  %-10s %s  %s\n", name, to_string(got, 36).c_str(), ok ? "PASS" : "FAIL");
  if (!ok) ++fails;
}

int main() {
#if !defined(FSOT_HAVE_BOOST_MP)
  std::puts("QUANTUM VCB/LITHIUM: skipped (needs Boost.Multiprecision)");
  return 0;
#else
  using R = mp169;
  Engine<R> eng;
  expect(eng.C_EFF, "0.95774802133782426776708397717345371304644791865112", "1e-30", "C_EFF");
  expect(eng.domain_scalar("High_Energy_Physics"), "0.88732952237250877667399090532841493230786685759384", "1e-30", "S_HEP");
  expect(quantum::v_cb_exclusive(eng), "0.0391453985916171986849475260176087544874", "1e-30", "V_cb_ex");
  expect(quantum::v_cb_exclusive(eng), "0.0391453985916172", "1e-15", "V_cb_16");
  expect(quantum::lithium_factor(eng), "3.008854147825069257758199989604449919655", "1e-30", "Li_fac");
  expect(quantum::lithium_factor(eng), "3.0088541478250693", "1e-15", "Li_16");
  if (fails) { std::printf("QUANTUM VCB/LITHIUM: %d failures\n", fails); return 1; }
  std::puts("QUANTUM VCB/LITHIUM: goldens match FSOT-Quantum@3c4375a at AEB2AD");
  return 0;
#endif
}
