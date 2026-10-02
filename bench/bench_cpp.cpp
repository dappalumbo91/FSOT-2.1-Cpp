// C++ benchmark: same workloads as bench/bench_py.py. Prints JSON lines.
#include <chrono>
#include <cstdio>
#include <random>
#include <vector>

#include "fsot/engine.hpp"
#include "fsot/trit.hpp"

using namespace fsot;
using clk = std::chrono::steady_clock;
static volatile double sink;

template <class F> double time_per_call(F&& f, double min_seconds = 0.3) {
  std::size_t n = 1;
  for (;;) {
    auto t0 = clk::now();
    for (std::size_t i = 0; i < n; ++i) f();
    double dt = std::chrono::duration<double>(clk::now() - t0).count();
    if (dt >= min_seconds) return dt / double(n);
    n *= 2;
  }
}

template <class R> void bench_engine() {
  const char* nm = real_traits<R>::name();
  double t_init = time_per_call([] { Engine<R> e; sink = static_cast<double>(e.S_COSM); });
  Engine<R> e;
  double t_dom = time_per_call([&] { R acc(0); for (auto& d : e.DOMAINS) acc += e.domain_scalar(d.name); sink = static_cast<double>(acc); });
  double t_sec = time_per_call([&] { std::size_t c = 0; for (auto& [n, fn] : e.sections()) c += (e.*fn)().size(); sink = double(c); });
  // hot path: raw scalar law (one S evaluation)
  auto si = e.default_input(); si.D_eff = R(12); si.observed = true;
  double t_one = time_per_call([&] { si.delta_psi += R(0); sink = static_cast<double>(e.compute_scalar(si)); });
  std::printf("{\"type\":\"%s\",\"engine_init_s\":%.6e,\"domains35_s\":%.6e,\"sections_all_s\":%.6e,\"one_scalar_s\":%.6e}\n",
              nm, t_init, t_dom, t_sec, t_one);
}

int main() {
  bench_engine<double>();
  bench_engine<long double>();
#if defined(FSOT_HAVE_FLOAT128)
  bench_engine<f128>();
#endif
#if defined(FSOT_HAVE_BOOST_MP)
  bench_engine<mp169>();
#endif
  // ternary: similarity over 4096 x 256-trit vectors (codes), reference vs bit-packed
  const int NV = 4096, DIM = 256;
  std::mt19937_64 rng(1);
  std::uniform_int_distribution<int> C(0, 2);
  std::vector<std::uint8_t> a(NV * DIM), b(NV * DIM);
  for (auto& x : a) x = std::uint8_t(C(rng));
  for (auto& x : b) x = std::uint8_t(C(rng));
  double t_ref = time_per_call([&] {
    double acc = 0;
    for (int v = 0; v < NV; ++v)
      acc += trit::trit_similarity_codes(std::span(a.data() + v * DIM, DIM), std::span(b.data() + v * DIM, DIM));
    sink = acc;
  });
  std::vector<std::uint64_t> pa(NV * DIM / 32), pb(NV * DIM / 32);
  for (std::size_t w = 0; w < pa.size(); ++w) {
    pa[w] = trit::pack_codes_u64(std::span<const std::uint8_t, 32>(a.data() + w * 32, 32));
    pb[w] = trit::pack_codes_u64(std::span<const std::uint8_t, 32>(b.data() + w * 32, 32));
  }
  double t_fast = time_per_call([&] {
    double acc = 0;
    const int WPV = DIM / 32;
    for (int v = 0; v < NV; ++v) {
      int s = 0;
      for (int w = 0; w < WPV; ++w) s += trit::trit_similarity_words_acc(pa[v * WPV + w], pb[v * WPV + w]);
      acc += double(s) / DIM;
    }
    sink = acc;
  });
  std::printf("{\"type\":\"trit\",\"similarity_4096x256_ref_s\":%.6e,\"similarity_4096x256_packed_s\":%.6e}\n", t_ref, t_fast);
}
