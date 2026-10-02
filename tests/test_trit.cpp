// Ternary core tests: mirrors trit.zig selfTest (Genetics / neuron-zig),
// quantum.zig selftest (FSOT-Quantum), trinary.py (GPU/Quantum), and the
// Reality-OS boot self-test; plus fast-path == reference fuzz.
#include <cstdio>
#include <random>
#include <string_view>

#include "fsot/engine.hpp"
#include "fsot/fsotb_vm.hpp"
#include "fsot/trit.hpp"

using namespace fsot::trit;
static int fails = 0;
#define CHECK(x) do { if (!(x)) { ++fails; std::printf("FAIL line %d: %s\n", __LINE__, #x); } } while (0)

int main() {
  // --- trit.zig selfTest, verbatim cases ---
  CHECK(pair(1, -1) == -1); CHECK(pair(1, 1) == 1);
  CHECK(sum_sat(1, 1) == 1); CHECK(sum_sat(1, -1) == 0);
  CHECK(consensus(1, 1) == 1); CHECK(consensus(1, -1) == 0);
  CHECK(neg(1) == -1);
  CHECK(from_s(-0.5f, -0.4f, 0.4f) == -1); CHECK(from_s(0.0f, -0.4f, 0.4f) == 0); CHECK(from_s(0.9f, -0.4f, 0.4f) == 1);
  auto atg = codon_primary('A', 'T', 'G'); CHECK(atg[0] == 1 && atg[1] == -1 && atg[2] == 1);
  { Trit ts[] = {1, -1, 0, 1}; auto w = TritWord::from_trits(ts); for (int i = 0; i < 4; ++i) CHECK(w.get(i) == ts[i]); }
  { Trit a[] = {1, 1, -1}, b[] = {1, -1, -1};
    auto wp = pair_words(TritWord::from_trits(a), TritWord::from_trits(b));
    CHECK(wp.get(0) == 1); CHECK(wp.get(1) == -1); CHECK(wp.get(2) == 1); }
  CHECK(!unpack_t1(0b10).has_value());
  // codon_core (Rust) parity: ATG -> primary (+1,-1,+1), secondary (+1,-1,0); pack = p + 27 s
  { auto c = encode_codon('A', 'T', 'G');
    CHECK(c.primary == (std::array<Trit, 3>{1, -1, 1})); CHECK(c.secondary == (std::array<Trit, 3>{1, -1, 0}));
    CHECK(pack_codon(c) == (2 + 0 * 3 + 2 * 9) + 27 * (2 + 0 * 3 + 1 * 9));
    CHECK(nt_primary('U') == -1); CHECK(base_primary('U') == 0);
    // all 64 codons pack uniquely
    const char B[] = "ACGT"; bool seen[729] = {}; int dup = 0;
    for (char a : std::string_view(B, 4)) for (char b : std::string_view(B, 4)) for (char d : std::string_view(B, 4)) {
      auto k = pack_codon(encode_codon(a, b, d)); if (seen[k]) ++dup; seen[k] = true; }
    CHECK(dup == 0); }
  // --- quantum.zig selftest ---
  { std::array<std::uint8_t, 32> c{}; for (int i = 0; i < 32; ++i) c[i] = i % 3;
    CHECK(unpack_codes_u64(pack_codes_u64(c)) == c); }
  { const double thr = COLLAPSE_THRESHOLD_AEB2AD;
    CHECK(collapse_code(1.0, thr) == 2); CHECK(collapse_code(-1.0, thr) == 0); CHECK(collapse_code(0.0, thr) == 1);
    CHECK(collapse_code(thr + 0.02, thr) == 2); CHECK(collapse_code(-(thr + 0.02), thr) == 0); }
  { auto b = bell_analog(1); CHECK(b[0] == 1 && b[1] == 1); auto d = bell_analog(-1); CHECK(d[0] == -1 && d[1] == -1); }
  for (int s = -1; s <= 1; ++s) CHECK(code_to_signed(signed_to_code(Trit(s))) == s);
  // --- Reality-OS boot self-test (r0==7, emit 42, one eval) on the live nest table ---
  { fsot::Engine<double> eng; std::vector<double> S; for (auto& d : eng.DOMAINS) S.push_back(eng.domain_scalar(d.name));
    fsot::fsotb::Vm vm; vm.panel_S = S; auto prog = fsot::fsotb::boot_selftest_program();
    auto st = vm.run(prog, 32);
    CHECK(st == fsot::fsotb::Status::Halted); CHECK(vm.regs[0] == 7); CHECK(vm.last_emit_tag == 42); CHECK(vm.eval_count == 1);
    CHECK(vm.regs[3] == static_cast<std::int32_t>(S[0] * 1e6)); }
  // --- BalancedTernary27 round-trip / add ---
  { std::mt19937_64 rng(3); std::uniform_int_distribution<std::int64_t> U(-BalancedTernary27::MAX / 2, BalancedTernary27::MAX / 2);
    for (int i = 0; i < 20000; ++i) { auto a = U(rng), b = U(rng);
      CHECK(BalancedTernary27::from_int(a).to_int() == a);
      CHECK((BalancedTernary27::from_int(a) + BalancedTernary27::from_int(b)).to_int() == a + b);
      CHECK((BalancedTernary27::from_int(a) - BalancedTernary27::from_int(b)).to_int() == a - b); } }
  // --- fuzz: bit-sliced fast paths == lane-by-lane reference ---
  { std::mt19937_64 rng(7); std::uniform_int_distribution<int> T(-1, 1), C(0, 2), Nn(0, 32);
    for (int it = 0; it < 100000; ++it) {
      int n = Nn(rng); std::array<Trit, 32> a{}, b{};
      for (int i = 0; i < 32; ++i) { a[i] = Trit(T(rng)); b[i] = Trit(T(rng)); }
      auto wa = TritWord::from_trits(std::span<const Trit>(a.data(), n)), wb = TritWord::from_trits(std::span<const Trit>(b.data(), n));
      auto ref = pair_words(wa, wb), fast = pair_words_fast(wa, wb);
      if (ref.pack != fast.pack || ref.n != fast.n) { ++fails; break; }
      auto full_a = TritWord::from_trits(a), full_b = TritWord::from_trits(b);
      auto cw = consensus_word(full_a.pack, full_b.pack), nw = neg_word(full_a.pack);
      for (std::uint8_t i = 0; i < 32; ++i) {
        if (unpack_t1(std::uint8_t(cw >> (2 * i))) != consensus(a[i], b[i])) { ++fails; break; }
        if (unpack_t1(std::uint8_t(nw >> (2 * i))) != neg(a[i])) { ++fails; break; }
      }
      std::array<std::uint8_t, 32> ca{}, cb{};
      for (int i = 0; i < 32; ++i) { ca[i] = std::uint8_t(C(rng)); cb[i] = std::uint8_t(C(rng)); }
      double ref_sim = trit_similarity_codes(ca, cb);
      double fast_sim = trit_similarity_words_acc(pack_codes_u64(ca), pack_codes_u64(cb)) / 32.0;
      if (ref_sim != fast_sim) { ++fails; std::printf("sim mismatch %f %f\n", ref_sim, fast_sim); break; }
    } }
  std::printf("%s (%d failures)\n", fails ? "TRIT: FAIL" : "TRIT: ALL PASS", fails);
  return fails ? 1 : 0;
}
