// fsot/trit.hpp — FSOT balanced-ternary (trinary) core.
//
// One C++ surface for the trit layers that exist across the FSOT repos:
//   * signed trit T = {-1, 0, +1}, ops neg/pair/sumSat/consensus/fromS
//       FSOT-Genetics zig/src/trit.zig == fsot-neuron-zig src/trit.zig
//   * T1 packing 2 bits/trit (00=0, 01=+1, 11=-1), TritWord of 32 trits in u64
//       same Zig files
//   * wire code {0=SpinDown, 1=Superposed, 2=SpinUp}, collapse at C_EFF*P_VAR,
//     pack 32 codes/u64, trit similarity (consensus attention)
//       FSOT-GPU fsot_lib/trinary.py == FSOT-Quantum fsot_lib/trinary.py, quantum.zig
//   * H/CX analogs, Bell analog          FSOT-Quantum zig/src/quantum.zig
//   * sign_trit(S) with eps 1e-12, PHASE_ROT, MIN3/MAX3, CONSENSUS
//       FSOT-Reality-OS reality_os_scalar / reality_os_trinary, hub fsot_quantum_trinary_syntax.py
//   * base/codon primary trits (A,G -> +1; C,T -> -1)   FSOT-Genetics
// New here (not in the repos yet): branch-free bit-sliced word ops on T1 words,
// and BalancedTernary27 (27-trit word = ISA word_width_trits) with carry add.
#pragma once
#include <array>
#include <bit>
#include <cstdint>
#include <optional>
#include <span>
#include <vector>

namespace fsot::trit {

using Trit = std::int8_t;  // -1 | 0 | +1

constexpr Trit as_trit(int x) { return x > 0 ? 1 : (x < 0 ? -1 : 0); }
constexpr Trit neg(Trit t) { return as_trit(-int(t)); }
constexpr Trit pair(Trit a, Trit b) { return as_trit(int(a) * int(b)); }      // product
constexpr Trit sum_sat(Trit a, Trit b) { return as_trit(int(a) + int(b)); }   // saturating sum
constexpr Trit consensus(Trit a, Trit b) { return a == b ? a : 0; }
constexpr Trit min3(Trit a, Trit b) { return a < b ? a : b; }                 // Kleene AND
constexpr Trit max3(Trit a, Trit b) { return a > b ? a : b; }                 // Kleene OR
constexpr Trit phase_rot(Trit v) { return v < 0 ? 0 : (v == 0 ? 1 : -1); }    // Reality-OS PHASE_ROT
template <class F> constexpr Trit from_s(F s, F lo, F hi) { return s < lo ? -1 : (s > hi ? 1 : 0); }
// Hub trit_from_S / Reality-OS sign_trit: +1 emerge, 0 null, -1 damp.
template <class F> constexpr Trit sign_trit(F s) { return s > F(1e-12) ? 1 : (s < F(-1e-12) ? -1 : 0); }

// ---- wire code {0,1,2} (FSOT-GPU / FSOT-Quantum) ----
// Live collapse threshold C_EFF*P_VAR under pin AEB2AD (float64 of the mp value).
// Note: FSOT-GPU/Quantum seeds.py and quantum.zig still carry the pre-π-identity
// C_EFF (0.9577022...) -> threshold 0.9174663774653723. See docs/INVENTORY.md.
inline constexpr double COLLAPSE_THRESHOLD_AEB2AD = 0.9175102712064876;  // float(C_EFF*P_VAR) at AEB2AD; checked by golden test
template <class F> constexpr std::uint8_t collapse_code(F v, F threshold) {
  return v > threshold ? 2 : (v < -threshold ? 0 : 1);
}
constexpr Trit code_to_signed(std::uint8_t c) { return c == 0 ? -1 : (c == 2 ? 1 : 0); }
constexpr std::uint8_t signed_to_code(Trit s) { return s < 0 ? 0 : (s > 0 ? 2 : 1); }

inline std::uint64_t pack_codes_u64(std::span<const std::uint8_t, 32> codes) {
  std::uint64_t w = 0;
  for (int i = 0; i < 32; ++i) w |= std::uint64_t(codes[i] & 3u) << (2 * i);
  return w;
}
inline std::array<std::uint8_t, 32> unpack_codes_u64(std::uint64_t w) {
  std::array<std::uint8_t, 32> c{};
  for (int i = 0; i < 32; ++i) c[i] = std::uint8_t((w >> (2 * i)) & 3u);
  return c;
}
// Mean consensus: match +1, opposite -1, either superposed (code 1) contributes 0.
inline double trit_similarity_codes(std::span<const std::uint8_t> a, std::span<const std::uint8_t> b) {
  const std::size_t n = a.size() < b.size() ? a.size() : b.size();
  if (n == 0) return 0.0;
  long acc = 0;
  for (std::size_t i = 0; i < n; ++i) {
    if (a[i] == 1 || b[i] == 1) continue;
    acc += a[i] == b[i] ? 1 : -1;
  }
  return double(acc) / double(n);
}
// Bit-parallel similarity for 32 codes per word (same result as above when n=32).
// Code bits: 0=00, 1=01, 2=10. "Definite" lanes have exactly bit1 xor bit0 ... use masks.
inline int trit_similarity_words_acc(std::uint64_t a, std::uint64_t b) {
  constexpr std::uint64_t LO = 0x5555555555555555ull;
  const std::uint64_t a_sup = a & LO, b_sup = b & LO;             // low bit set => code 1 (superposed)
  const std::uint64_t def = ~(a_sup | b_sup) & LO;                 // lanes where both definite
  const std::uint64_t a_up = (a >> 1) & LO, b_up = (b >> 1) & LO;  // high bit => code 2
  const std::uint64_t same = ~(a_up ^ b_up) & def;
  const std::uint64_t opp = (a_up ^ b_up) & def;
  return std::popcount(same) - std::popcount(opp);
}

// ---- T1 packing (FSOT-Genetics / fsot-neuron-zig): 00=0, 01=+1, 11=-1 ----
constexpr std::uint8_t pack_t1(Trit t) { return t > 0 ? 0b01 : (t < 0 ? 0b11 : 0b00); }
constexpr std::optional<Trit> unpack_t1(std::uint8_t bits) {
  switch (bits & 0b11) {
    case 0b01: return Trit{1};
    case 0b11: return Trit{-1};
    case 0b00: return Trit{0};
    default: return std::nullopt;  // 0b10 is invalid in T1
  }
}

struct TritWord {  // up to 32 trits in a u64 carrier
  std::uint8_t n = 0;
  std::uint64_t pack = 0;
  static TritWord from_trits(std::span<const Trit> ts) {
    TritWord w;
    w.n = std::uint8_t(ts.size() < 32 ? ts.size() : 32);
    for (std::uint8_t i = 0; i < w.n; ++i) w.pack |= std::uint64_t(pack_t1(ts[i])) << (2 * i);
    return w;
  }
  std::optional<Trit> get(std::uint8_t i) const {
    if (i >= n) return std::nullopt;
    return unpack_t1(std::uint8_t(pack >> (2 * i)));
  }
};
// Reference (lane loop) pairwise product, as in trit.zig pairWords.
inline TritWord pair_words(const TritWord& a, const TritWord& b) {
  const std::uint8_t n = a.n < b.n ? a.n : b.n;
  std::array<Trit, 32> out{};
  for (std::uint8_t i = 0; i < n; ++i) out[i] = pair(a.get(i).value_or(0), b.get(i).value_or(0));
  return TritWord::from_trits(std::span<const Trit>(out.data(), n));
}
// Bit-sliced pairwise product on T1 words: lane = (nz, sign) with nz=bit0, sign=bit1.
// product nz = nzA & nzB ; product sign = (sA ^ sB) & nz.  32 lanes in ~6 ops.
inline TritWord pair_words_fast(const TritWord& a, const TritWord& b) {
  constexpr std::uint64_t LO = 0x5555555555555555ull;
  const std::uint8_t n = a.n < b.n ? a.n : b.n;
  const std::uint64_t lane_mask = n >= 32 ? ~0ull : ((1ull << (2 * n)) - 1);
  const std::uint64_t nz = a.pack & b.pack & LO;
  const std::uint64_t sg = ((a.pack ^ b.pack) >> 1) & nz;
  return TritWord{n, (nz | (sg << 1)) & lane_mask};
}
// Bit-sliced Kleene ops on T1 words.
inline std::uint64_t neg_word(std::uint64_t p) {  // flip sign bit where nonzero
  constexpr std::uint64_t LO = 0x5555555555555555ull;
  return p ^ ((p & LO) << 1);
}
inline std::uint64_t consensus_word(std::uint64_t a, std::uint64_t b) {  // equal lanes keep, else 0
  constexpr std::uint64_t LO = 0x5555555555555555ull;
  const std::uint64_t diff = a ^ b;
  const std::uint64_t lane_diff = (diff | (diff >> 1)) & LO;
  const std::uint64_t keep = ~(lane_diff | (lane_diff << 1));
  return a & keep;
}

// ---- genetics: A,G -> +1 ; C,T -> -1 ----
constexpr Trit base_primary(char b) {
  switch (b) {
    case 'A': case 'a': case 'G': case 'g': return 1;
    case 'C': case 'c': case 'T': case 't': return -1;
    default: return 0;
  }
}
constexpr std::array<Trit, 3> codon_primary(char c0, char c1, char c2) {
  return {base_primary(c0), base_primary(c1), base_primary(c2)};
}

// FSOT-Genetics crates/codon_core (Rust): RNA-aware primary (U -> -1; trit.zig maps U -> 0),
// secondary A-T axis (A=+1, T/U=-1, G/C=0), and positional base-3 codon pack (trit+1, 0..728).
constexpr Trit nt_primary(char b) { return (b == 'U' || b == 'u') ? Trit{-1} : base_primary(b); }
constexpr Trit nt_secondary(char b) {
  switch (b) {
    case 'A': case 'a': return 1;
    case 'T': case 't': case 'U': case 'u': return -1;
    default: return 0;
  }
}
struct CodonTrinary { std::array<Trit, 3> primary, secondary; };
constexpr CodonTrinary encode_codon(char c0, char c1, char c2) {
  return {{nt_primary(c0), nt_primary(c1), nt_primary(c2)}, {nt_secondary(c0), nt_secondary(c1), nt_secondary(c2)}};
}
constexpr std::uint16_t pack_codon(const CodonTrinary& t) {
  auto u = [](Trit x) { return std::uint16_t(x + 1); };
  const std::uint16_t p = u(t.primary[0]) + u(t.primary[1]) * 3 + u(t.primary[2]) * 9;
  const std::uint16_t s = u(t.secondary[0]) + u(t.secondary[1]) * 3 + u(t.secondary[2]) * 9;
  return std::uint16_t(p + s * 27);
}

// ---- quantum analogs (FSOT-Quantum quantum.zig) ----
constexpr Trit h_analog(Trit t, Trit resolve) { return t != 0 ? 0 : resolve; }
constexpr Trit cx_target(Trit c, Trit t) { return c == 0 ? 0 : (c > 0 ? neg(t) : t); }
constexpr std::array<Trit, 2> bell_analog(Trit resolve) {
  Trit s0 = -1, s1 = -1;
  s0 = h_analog(s0, resolve);
  s1 = cx_target(s0, s1);
  if (s0 == 0) s0 = resolve;
  if (s1 == 0) s1 = resolve;
  return {s0, s1};
}

// ---- BalancedTernary27: 27-trit word (ISA word_width_trits = 27 = 3^3) ----
struct BalancedTernary27 {
  static constexpr int N = 27;
  std::array<Trit, N> t{};  // little-endian trits
  static constexpr std::int64_t MAX = (7625597484987LL - 1) / 2;  // (3^27-1)/2
  static BalancedTernary27 from_int(std::int64_t v) {
    BalancedTernary27 b;
    for (int i = 0; i < N && v != 0; ++i) {
      int r = int(((v % 3) + 3) % 3);
      if (r == 2) { b.t[i] = -1; v = (v + 1) / 3; }
      else { b.t[i] = Trit(r); v = (v - r) / 3; }
    }
    return b;
  }
  std::int64_t to_int() const {
    std::int64_t v = 0;
    for (int i = N - 1; i >= 0; --i) v = v * 3 + t[i];
    return v;
  }
  BalancedTernary27 operator-() const { BalancedTernary27 r; for (int i = 0; i < N; ++i) r.t[i] = neg(t[i]); return r; }
  // ripple-carry add, wraps modulo 3^27 like a hardware word
  friend BalancedTernary27 operator+(const BalancedTernary27& a, const BalancedTernary27& b) {
    BalancedTernary27 r; int carry = 0;
    for (int i = 0; i < N; ++i) {
      int s = a.t[i] + b.t[i] + carry;
      carry = 0;
      if (s > 1) { s -= 3; carry = 1; } else if (s < -1) { s += 3; carry = -1; }
      r.t[i] = Trit(s);
    }
    return r;
  }
  friend BalancedTernary27 operator-(const BalancedTernary27& a, const BalancedTernary27& b) { return a + (-b); }
};

}  // namespace fsot::trit
