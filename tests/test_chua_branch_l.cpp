// Golden check for fsot/host/chua_branch_l.hpp against the values published in
// dappalumbo91/FSOT-Chua-Circuit docs/BRANCH_L_DERIVATION.md @ 1a6bd91 (AEB2AD, mpmath dps 50).
// Circuit: L = 22 mH, C2 = 100 nF, R = 1800 ohm (sqrt(L/C2) = 469.04 ohm, beta = 14.7272...).
#include <cstdio>
#include <string>

#include "fsot/host/chua_branch_l.hpp"

using namespace fsot;

static int fails = 0;
template <class R> static void expect(const R& got, const char* want, const char* tol, const char* name) {
  const R d = m::fabs(got - lit<R>(want));
  const bool ok = d <= lit<R>(tol);
  std::printf("  %-6s %s  %s\n", name, to_string(got, 20).c_str(), ok ? "PASS" : "FAIL");
  if (!ok) ++fails;
}

int main() {
#if !defined(FSOT_HAVE_BOOST_MP)
  std::puts("CHUA BRANCH L: skipped (needs Boost.Multiprecision)");
  return 0;
#else
  using R = mp169;
  Engine<R> eng;
  chua::BranchL<R> b(eng);
  const R L = lit<R>("0.022"), C2 = lit<R>("1e-7"), Rr = lit<R>("1800");
  const R beta = Rr * Rr * C2 / L;
  expect(eng.domain_scalar("Electromagnetism"), "0.955728570095582708189529865", "1e-25", "S_EM");
  expect(b.eps(), "7.72509421698849555e-4", "1e-19", "eps");
  expect(b.inv_QL(), "0.0393143181831290647", "1e-17", "1/Q_L");
  expect(b.QL(), "25.4360255045483541", "1e-15", "Q_L");
  expect(b.r0(L, C2), "18.4400497592861384", "1e-14", "r0");
  expect(b.gamma(beta), "0.150873134394159315", "1e-17", "gamma");
  expect(b.r0(L, C2, "Materials_Science"), "18.42007", "1e-5", "r0_MS");
  if (fails) { std::printf("CHUA BRANCH L: %d failures\n", fails); return 1; }
  std::puts("CHUA BRANCH L: golden matches FSOT-Chua-Circuit@1a6bd91");
  return 0;
#endif
}
