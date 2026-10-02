// Balanced-ternary arithmetic tests:
//  1. TWord add/sub/mul/div/compare: exhaustive over all 5-trit pairs (with mod-3^5 wrap) and 9-trit (Tryte)
//     add/sub/compare, randomized 40-trit words against int64 / __int128 reference arithmetic.
//  2. BTFloat identities (sin^2+cos^2, exp(ln x), sqrt^2) evaluated in ternary.
//  3. Engine<BTFloat<P>>: the FSOT core evaluated with ternary arithmetic doing all of the math, compared
//     to golden/golden_AEB2AD.tsv (mpmath, dps=50, from the pinned authority). The relative error is itself
//     computed in balanced ternary from the golden decimal strings (no binary float in the comparison).
#if defined(_MSC_VER)
#include <intrin.h>
#endif
#include <algorithm>
#include <array>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <map>
#include <random>
#include <sstream>
#include <string>
#include <vector>

#include "fsot/ternary_real.hpp"
#include "fsot/engine.hpp"

using namespace fsot;
using namespace fsot::bt;

static int failures = 0;
#define CHECK(c, ...) do { if (!(c)) { if (failures < 20) { std::printf("FAIL %s:%d ", __FILE__, __LINE__); std::printf(__VA_ARGS__); std::printf("\n"); } ++failures; } } while (0)

static long long bal_wrap(long long x, long long mod) {  // balanced residue in [-(mod-1)/2, (mod-1)/2]
  const long long h = (mod - 1) / 2;
  long long r = ((x + h) % mod + mod) % mod;
  return r - h;
}

static void test_words() {
  using T5 = TWord<5>;
  long long n = 0;
  for (long long a = -121; a <= 121; ++a)
    for (long long b = -121; b <= 121; ++b) {
      const T5 A = T5::from_int(a), B = T5::from_int(b);
      CHECK((A + B).to_int() == bal_wrap(a + b, 243), "5t add %lld %lld", a, b);
      CHECK((A + B).overflow == (a + b != bal_wrap(a + b, 243)), "5t add overflow flag %lld %lld", a, b);
      CHECK((A - B).to_int() == bal_wrap(a - b, 243), "5t sub %lld %lld", a, b);
      CHECK((A * B).to_int() == bal_wrap(a * b, 243), "5t mul %lld %lld", a, b);
      CHECK(compare(A, B) == (a < b ? -1 : a > b ? 1 : 0), "5t cmp %lld %lld", a, b);
      if (b) {
        const long long q = (A / B).to_int();
        CHECK(2 * std::llabs(a - q * b) <= std::llabs(b), "5t div %lld/%lld -> %lld", a, b, q);
      }
      ++n;
    }
  std::printf("TWord<5>: %lld pairs exhaustive (add/sub/mul/div/cmp + overflow flag)\n", n);
  long long m = 0;
  for (long long a = -9841; a <= 9841; a += 1)
    for (long long b = -9841; b <= 9841; b += 97) {
      const Tryte A = Tryte::from_int(a), B = Tryte::from_int(b);
      CHECK((A + B).to_int() == bal_wrap(a + b, 19683), "tryte add");
      CHECK((A - B).to_int() == bal_wrap(a - b, 19683), "tryte sub");
      CHECK(compare(A, B) == (a < b ? -1 : a > b ? 1 : 0), "tryte cmp");
      ++m;
    }
  std::printf("Tryte (9 trits): %lld pairs add/sub/cmp\n", m);
  std::mt19937_64 g(20261001);
  const long long LIM = 2400000000LL;  // |a*b| <= 5.76e18 < (3^40-1)/2
  for (int it = 0; it < 200000; ++it) {
    const long long a = (long long)(g() % (2 * LIM + 1)) - LIM, b = (long long)(g() % (2 * LIM + 1)) - LIM;
    const Word40 A = Word40::from_int(a), B = Word40::from_int(b);
    CHECK((A + B).to_int() == a + b, "w40 add");
    CHECK((A - B).to_int() == a - b, "w40 sub");
    CHECK((A * B).to_int() == a * b, "w40 mul %lld %lld", a, b);
    CHECK(compare(A, B) == (a < b ? -1 : a > b ? 1 : 0), "w40 cmp");
    if (b) { const long long q = (A / B).to_int(); CHECK(2 * std::llabs(a - q * b) <= std::llabs(b), "w40 div"); }
    CHECK(A.shl(3).to_int() == a * 27, "w40 shl");
  }
  // 2-word integers: products of 60-trit operands checked with __int128 (fits 128 trits = 2 words)
  for (int it = 0; it < 20000; ++it) {
    const long long a = (long long)(g() >> 2) - (1LL << 61), b = (long long)(g() >> 2) - (1LL << 61);
    const BigT<1> A = from_binary<1>(a), B = from_binary<1>(b);
    const BigT<2> P = mul(A, B);
#if defined(__SIZEOF_INT128__)
    __int128 v = 0;
    for (int i = P.top(); i >= 0; --i) v = v * 3 + P.trit(i);
    CHECK(v == (__int128)a * b, "bigt mul");
#elif defined(_MSC_VER) && defined(_M_X64)
    // MSVC: no __int128. Horner in two's-complement (hi, lo) with _umul128; reference product from _mul128.
    unsigned long long hi = 0, lo = 0;
    for (int i = P.top(); i >= 0; --i) {
      unsigned long long carry = 0;
      lo = _umul128(lo, 3ULL, &carry); hi = hi * 3ULL + carry;
      const long long t = P.trit(i);
      const unsigned long long tlo = (unsigned long long)t, thi = t < 0 ? ~0ULL : 0ULL;
      const unsigned long long nlo = lo + tlo; hi += thi + (nlo < lo ? 1ULL : 0ULL); lo = nlo;
    }
    long long rhi = 0; const long long rlo = _mul128(a, b, &rhi);
    CHECK(lo == (unsigned long long)rlo && hi == (unsigned long long)rhi, "bigt mul");
#else
#error "test_ternary needs __int128 or MSVC x64 _mul128/_umul128"
#endif
  }
  std::printf("Word40 / BigT: 200000 random add/sub/mul/div/cmp/shift + 20000 double-width products\n");
}

template <int P> static double rel_err(const BTFloat<P>& c, const std::string& golden) {
  const BTFloat<P> g = parse<P>(golden.c_str());
  if (g.is_zero()) return static_cast<double>(fabs(c));
  return static_cast<double>(fabs((c - g) / g));
}

template <int P> static void identities(double tol) {
  using F = BTFloat<P>;
  double worst = 0;
  for (int k = -7; k <= 9; ++k) {
    const F x = F(k) / F(3) + F(1) / F(7);
    const F s = sin(x), c = cos(x);
    worst = std::max(worst, static_cast<double>(fabs(s * s + c * c - F(1))));
    const F y = fabs(x) + F(1) / F(10);
    worst = std::max(worst, static_cast<double>(fabs((exp(log(y)) - y) / y)));
    const F r = sqrt(y);
    worst = std::max(worst, static_cast<double>(fabs((r * r - y) / y)));
  }
  CHECK(worst < tol, "identities P=%d worst %.3e", P, worst);
  std::printf("BTFloat<%d>: sin^2+cos^2, exp(ln x), sqrt^2 identities worst %.3e (tol %.0e)\n", P, worst, tol);
}

struct Row { std::string key, name, value; };

template <int P> static void golden(const std::vector<Row>& rows, double tol) {
  using R = BTFloat<P>;
  Engine<R> eng;
  std::map<std::string, R> consts = {
      {"PI", eng.PI}, {"E", eng.E}, {"PHI", eng.PHI}, {"GAMMA", eng.GAMMA}, {"G_CAT", eng.G_CAT},
      {"ALPHA", eng.ALPHA}, {"PSI_CON", eng.PSI_CON}, {"ETA_EFF", eng.ETA_EFF}, {"BETA", eng.BETA},
      {"GAMMA_C", eng.GAMMA_C}, {"OMEGA", eng.OMEGA}, {"THETA_S", eng.THETA_S}, {"POOF", eng.POOF},
      {"C_EFF", eng.C_EFF}, {"A_BLEED", eng.A_BLEED}, {"P_VAR", eng.P_VAR}, {"B_IN", eng.B_IN},
      {"A_IN", eng.A_IN}, {"SUCTION", eng.SUCTION}, {"CHAOS", eng.CHAOS}, {"P_BASE", eng.P_BASE},
      {"P_NEW", eng.P_NEW}, {"C_FACTOR", eng.C_FACTOR}, {"K", eng.K}, {"C_COSM", eng.C_COSM},
      {"S_COSM", eng.S_COSM}, {"S_QUANT", eng.S_QUANT}, {"S_CHEM", eng.S_CHEM}};
  int n = 0, bad = 0;
  double worst = 0;
  std::string wname;
  auto chk = [&](const std::string& label, const R& c, const std::string& g) {
    const double e = rel_err<P>(c, g);
    ++n;
    if (e > worst) { worst = e; wname = label; }
    if (e > tol) { ++bad; CHECK(false, "BTFloat<%d> %s rel %.3e", P, label.c_str(), e); }
  };
  for (auto& r : rows) {
    if (r.key == "const") chk("const." + r.name, consts.at(r.name), r.value);
    else if (r.key == "domain.look") chk(r.key + "." + r.name, eng.domain(r.name).delta_psi, r.value);
    else if (r.key == "domain.C") chk(r.key + "." + r.name, eng.domain(r.name).C, r.value);
    else if (r.key == "domain.S") chk(r.key + "." + r.name, eng.domain_scalar(r.name), r.value);
    else if (r.key == "correct72") chk(r.key + "." + r.name, eng.fsot_correct(R(72), r.name), r.value);
  }
  std::printf("Engine<BTFloat<%d>> (~%.0f bits): %d golden values, max rel err %.3e [%s], tol %.0e  %s\n", P, P * 1.58496, n,
              worst, wname.c_str(), tol, bad ? "FAIL" : "PASS");
}

#include "fsot/trit.hpp"
static void conformance() {  // docs/TRIT_SPEC.md section 5
  std::array<std::uint8_t, 32> codes{};
  const int tr[4] = {-1, 0, 1, 0};
  for (int i = 0; i < 32; ++i) codes[i] = trit::signed_to_code(trit::Trit(i < 4 ? tr[i] : 0));
  const std::uint64_t w = trit::pack_codes_u64(std::span<const std::uint8_t, 32>(codes));
  CHECK(w == 0x5555555555555564ull, "canonical pack %llx", (unsigned long long)w);
  // 2a <-> 2b (bit-planes) round trip
  BigT<1> planes;
  for (int i = 0; i < 32; ++i) planes.set_trit(i, trit::code_to_signed(std::uint8_t((w >> (2 * i)) & 3)));
  CHECK(planes.trit(0) == -1 && planes.trit(1) == 0 && planes.trit(2) == 1 && planes.top() == 2, "planes");
  const auto aug = trit::encode_codon('A', 'U', 'G');
  CHECK(aug.primary[0] == 1 && aug.primary[1] == -1 && aug.primary[2] == 1, "AUG primary");
  CHECK(aug.secondary[0] == 1 && aug.secondary[1] == -1 && aug.secondary[2] == 0, "AUG secondary");
  CHECK(trit::pack_codon(aug) == 317, "AUG pack %u", unsigned(trit::pack_codon(aug)));
  const long long big = (Word40::from_int(2400000000LL) * Word40::from_int(-2399999999LL)).to_int();
  CHECK(big == -5759999997600000000LL, "w40 vector %lld", big);
  std::printf("TRIT_SPEC conformance vectors: %s\n", failures ? "see failures" : "ok");
}

int main(int argc, char** argv) {
  conformance();
  test_words();
  identities<40>(1e-17);
  identities<72>(1e-32);
  identities<110>(1e-50);
  const char* path = argc > 1 ? argv[1] : FSOT_GOLDEN_TSV;
  std::ifstream in(path);
  std::vector<Row> rows;
  for (std::string line; std::getline(in, line);) {
    if (line.empty() || line[0] == '#') continue;
    std::istringstream ss(line);
    Row r;
    std::getline(ss, r.key, '\t'); std::getline(ss, r.name, '\t'); std::getline(ss, r.value, '\t');
    rows.push_back(r);
  }
  CHECK(!rows.empty(), "no golden rows");
  golden<40>(rows, 1e-16);
  golden<72>(rows, 1e-31);
  golden<110>(rows, 1e-48);
  std::printf("%s (%d failures)\n", failures ? "TERNARY: FAILURES" : "TERNARY: ALL PASS", failures);
  return failures ? 1 : 0;
}
