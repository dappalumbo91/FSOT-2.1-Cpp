// Ternary vs binary: the same FSOT core (Engine<R>) evaluated with balanced-ternary arithmetic
// (fsot::bt::BTFloat<P>) and with the binary types, plus raw word-op throughput.
// Reports, per type: time to build the engine (seeds+layers+folds) and evaluate all 35 domain S,
// and the max relative error of the 35 S vs golden/golden_AEB2AD.tsv (mpmath dps=50).
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <fstream>
#include <map>
#include <random>
#include <sstream>
#include <string>
#include <vector>

#include "fsot/ternary_real.hpp"
#include "fsot/engine.hpp"

using namespace fsot;
using clk = std::chrono::steady_clock;
static std::map<std::string, std::string> goldS;
static volatile double sink;

template <class R> double relS(Engine<R>& e) {
  double w = 0;
  for (auto& d : e.DOMAINS) {
    const std::string& g = goldS.at(std::string(d.name));
    const R s = e.domain_scalar(d.name);
    double r;
    if constexpr (requires { R::W; }) {
      constexpr int P = decltype(s.m)::TRITS;  (void)P;
      const R gv = real_traits<R>::lit(g.c_str());
      r = static_cast<double>(bt::fabs((s - gv) / gv));
    } else {
#if defined(FSOT_HAVE_BOOST_MP)
      const mp169 gv(g.c_str());
      mp169 sv;
      if constexpr (std::is_same_v<R, mp169>) sv = s; else sv = mp169(to_string(s, 40));
      r = static_cast<double>(abs((sv - gv) / gv));
#else
      r = std::fabs(static_cast<double>(s) / std::strtod(g.c_str(), nullptr) - 1);
#endif
    }
    w = std::max(w, r);
  }
  return w;
}

template <class R> void row(const char* label, int reps) {
  std::vector<double> t;
  double err = 0;
  for (int i = 0; i < reps; ++i) {
    const auto t0 = clk::now();
    Engine<R> e;
    double acc = 0;
    for (auto& d : e.DOMAINS) acc += static_cast<double>(e.domain_scalar(d.name));
    sink = acc;
    t.push_back(std::chrono::duration<double, std::micro>(clk::now() - t0).count());
    if (i == 0) err = relS(e);
  }
  std::sort(t.begin(), t.end());
  std::printf("| %-26s | %12.1f | %10.2e |\n", label, t[t.size() / 2], err);
}

template <class F> double ns_per(F&& f, long n) {
  const auto t0 = clk::now();
  f(n);
  return std::chrono::duration<double, std::nano>(clk::now() - t0).count() / double(n);
}

int main(int argc, char** argv) {
  std::ifstream in(argc > 1 ? argv[1] : FSOT_GOLDEN_TSV);
  for (std::string line; std::getline(in, line);) {
    std::istringstream ss(line); std::string k, n, v;
    std::getline(ss, k, '\t'); std::getline(ss, n, '\t'); std::getline(ss, v, '\t');
    if (k == "domain.S") goldS[n] = v;
  }
  std::printf("Engine build + 35 domain S (median wall time) and max rel. error of the 35 S vs mpmath golden\n\n");
  std::printf("| type                       | time (us)    | max rel err |\n|---|---:|---:|\n");
  row<double>("binary double (53 bit)", 201);
  row<long double>("binary long double (64 bit)", 201);
#if defined(FSOT_HAVE_FLOAT128)
  row<f128>("binary __float128 (113 bit)", 51);
#endif
#if defined(FSOT_HAVE_BOOST_MP)
  row<mp169>("binary cpp_bin_float<169>", 11);
#endif
  row<bt::BT40>("ternary BTFloat<40> (63.4b)", 11);
  row<bt::BT72>("ternary BTFloat<72> (114b)", 7);
  row<bt::BT110>("ternary BTFloat<110> (174b)", 5);

  std::printf("\nRaw operations (ns/op)\n\n| op | binary | ternary |\n|---|---:|---:|\n");
  std::mt19937_64 g(7);
  std::vector<long long> a(1024), b(1024);
  for (int i = 0; i < 1024; ++i) { a[i] = (long long)(g() % 4000000000ull) - 2000000000; b[i] = (long long)(g() % 4000000000ull) - 2000000000; }
  std::vector<bt::Word40> A(1024), B(1024);
  for (int i = 0; i < 1024; ++i) { A[i] = bt::Word40::from_int(a[i]); B[i] = bt::Word40::from_int(b[i]); }
  auto bin_add = ns_per([&](long n) { long long s = 0; for (long i = 0; i < n; ++i) s += a[i & 1023] + b[(i * 7) & 1023]; sink = double(s); }, 20000000);
  auto ter_add = ns_per([&](long n) { bt::Word40 s; for (long i = 0; i < n; ++i) s = A[i & 1023] + B[(i * 7) & 1023]; sink = double(s.to_int()); }, 2000000);
  auto bin_mul = ns_per([&](long n) { long long s = 0; for (long i = 0; i < n; ++i) s ^= a[i & 1023] * b[(i * 7) & 1023]; sink = double(s); }, 20000000);
  auto ter_mul = ns_per([&](long n) { bt::Word40 s; for (long i = 0; i < n; ++i) s = A[i & 1023] * B[(i * 7) & 1023]; sink = double(s.to_int()); }, 500000);
  auto bin_div = ns_per([&](long n) { long long s = 0; for (long i = 0; i < n; ++i) s ^= a[i & 1023] / (b[(i * 7) & 1023] | 1); sink = double(s); }, 20000000);
  auto ter_div = ns_per([&](long n) { bt::Word40 s; for (long i = 0; i < n; ++i) s = A[i & 1023] / B[(i * 7) & 1023]; sink = double(s.to_int()); }, 200000);
  std::printf("| 40-trit word add vs int64 add | %.2f | %.2f |\n", bin_add, ter_add);
  std::printf("| 40-trit word mul vs int64 mul | %.2f | %.2f |\n", bin_mul, ter_mul);
  std::printf("| 40-trit word div vs int64 div | %.2f | %.2f |\n", bin_div, ter_div);
#if defined(FSOT_HAVE_BOOST_MP)
  {
    const mp169 x = mp169(2) / 3, y = mp169(5) / 7;
    const bt::BT110 X = bt::BT110(2) / bt::BT110(3), Y = bt::BT110(5) / bt::BT110(7);
    auto bm = ns_per([&](long n) { mp169 s = x; for (long i = 0; i < n; ++i) s = s * y + x; sink = double(s); }, 200000);
    auto tm = ns_per([&](long n) { bt::BT110 s = X; for (long i = 0; i < n; ++i) s = s * Y + X; sink = double(s); }, 50000);
    auto bd = ns_per([&](long n) { mp169 s = x; for (long i = 0; i < n; ++i) s = y / (s + x); sink = double(s); }, 100000);
    auto td = ns_per([&](long n) { bt::BT110 s = X; for (long i = 0; i < n; ++i) s = Y / (s + X); sink = double(s); }, 20000);
    auto be = ns_per([&](long n) { mp169 s = x; for (long i = 0; i < n; ++i) s = exp(-s); sink = double(s); }, 5000);
    auto te = ns_per([&](long n) { bt::BT110 s = X; for (long i = 0; i < n; ++i) s = bt::exp(-s); sink = double(s); }, 1000);
    std::printf("| 169-bit vs 110-trit fused (x*y+z) | %.0f | %.0f |\n", bm, tm);
    std::printf("| 169-bit vs 110-trit y/(x+z) | %.0f | %.0f |\n", bd, td);
    std::printf("| 169-bit vs 110-trit exp(-x) | %.0f | %.0f |\n", be, te);
  }
#endif
  return 0;
}
