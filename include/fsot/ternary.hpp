// fsot/ternary.hpp — balanced-ternary arithmetic that does the actual math (header-only, freestanding).
//
// Every number here is a string of balanced trits {-1, 0, +1}. Arithmetic is done trit-parallel on two
// bit-planes per word (plane P marks +1 trits, plane N marks -1 trits; a trit is never in both), so a
// binary CPU executes ternary logic gates and ternary carry propagation; no binary integer or binary
// floating-point arithmetic is used for the values themselves. Binary integers appear only for indices,
// trit counts and exponents (the "address unit"), and at explicit I/O boundaries (from_binary/to_double).
//
//   BigT<W>      balanced-ternary integer of 64*W trits (fixed width, mod 3^(64W) wrap).
//   TWord<N>     N-trit machine word (N <= 64): Tryte = TWord<9>, Word27, Word40. add/sub/mul/div/cmp/shift.
//   BTFloat<P>   balanced-ternary floating point: P-trit mantissa, power-of-3 exponent.
//                + - * are correctly rounded (round-to-nearest == trit truncation in balanced ternary);
//                / is faithfully rounded; sqrt/exp/ln/sin/cos/pow run in P+16 trits and round to P.
//                Range reduction is ternary-native: exp/ln reduce by powers of 3 (exact exponent moves),
//                exp cubes back (y^3) and sin/cos use triple-angle formulas instead of halving/doubling.
//
// No heap, no exceptions, no iostream, no libm. Only <cstdint>, <bit>, <type_traits>. (Function-local statics cache
// constants; on bare metal build with -fno-threadsafe-statics.)
#pragma once
#include <bit>
#include <cstdint>
#include <type_traits>

namespace fsot::bt {
using u64 = std::uint64_t;

// ============================================================ BigT<W>
template <int W> struct BigT {
  static_assert(W >= 1);
  static constexpr int TRITS = 64 * W;
  u64 p[W]{};
  u64 n[W]{};

  constexpr bool is_zero() const { for (int i = 0; i < W; ++i) if (p[i] | n[i]) return false; return true; }
  constexpr int trit(int i) const { return int((p[i >> 6] >> (i & 63)) & 1) - int((n[i >> 6] >> (i & 63)) & 1); }
  constexpr void set_trit(int i, int t) {
    const u64 b = u64(1) << (i & 63);
    p[i >> 6] &= ~b; n[i >> 6] &= ~b;
    if (t > 0) p[i >> 6] |= b; else if (t < 0) n[i >> 6] |= b;
  }
  // index of the most significant non-zero trit, -1 for zero
  constexpr int top() const {
    for (int i = W - 1; i >= 0; --i) if (u64 m = p[i] | n[i]) return 64 * i + 63 - std::countl_zero(m);
    return -1;
  }
  constexpr int sign() const { const int t = top(); return t < 0 ? 0 : trit(t); }
};

template <int W> constexpr BigT<W> neg(BigT<W> a) {
  for (int i = 0; i < W; ++i) { u64 t = a.p[i]; a.p[i] = a.n[i]; a.n[i] = t; }
  return a;
}

// a += b with ternary carry propagation. Returns the trit carried out of the top position (overflow).
// Per position: (+,+) -> digit -1 carry +1; (-,-) -> digit +1 carry -1; (+,-) -> 0; (x,0) -> x.
template <int W> constexpr int add_into(BigT<W>& a, BigT<W> b) {
  int carry_out = 0;
  for (;;) {
    u64 any = 0, cp_in = 0, cn_in = 0;
    BigT<W> c;
    for (int i = 0; i < W; ++i) {
      const u64 ap = a.p[i], an = a.n[i], bp = b.p[i], bn = b.n[i];
      const u64 a0 = ~(ap | an), b0 = ~(bp | bn);
      const u64 pp = ap & bp, nn = an & bn;
      a.p[i] = (ap & b0) | (bp & a0) | nn;
      a.n[i] = (an & b0) | (bn & a0) | pp;
      c.p[i] = (pp << 1) | cp_in;
      c.n[i] = (nn << 1) | cn_in;
      cp_in = pp >> 63; cn_in = nn >> 63;
      any |= pp | nn;
    }
    carry_out += int(cp_in) - int(cn_in);
    if (!any) return carry_out;
    b = c;
  }
}
template <int W> constexpr BigT<W> add(BigT<W> a, const BigT<W>& b) { add_into(a, b); return a; }
template <int W> constexpr BigT<W> sub(BigT<W> a, const BigT<W>& b) { add_into(a, neg(b)); return a; }

// Lexicographic compare from the most significant trit (valid in balanced ternary: a difference at trit k
// outweighs everything below it). Returns -1, 0, +1.
template <int W> constexpr int cmp(const BigT<W>& a, const BigT<W>& b) {
  for (int i = W - 1; i >= 0; --i) {
    const u64 d = (a.p[i] ^ b.p[i]) | (a.n[i] ^ b.n[i]);
    if (d) {
      const int h = 63 - std::countl_zero(d);
      const int ta = int((a.p[i] >> h) & 1) - int((a.n[i] >> h) & 1);
      const int tb = int((b.p[i] >> h) & 1) - int((b.n[i] >> h) & 1);
      return ta < tb ? -1 : 1;
    }
  }
  return 0;
}

// multiply by 3^k (trit shift left; trits shifted past the top are lost)
template <int W> constexpr BigT<W> shl(const BigT<W>& a, int k) {
  if (k <= 0) return a;
  BigT<W> r;
  const int ws = k >> 6, bs = k & 63;
  for (int i = W - 1; i >= ws; --i) {
    u64 vp = a.p[i - ws] << bs, vn = a.n[i - ws] << bs;
    if (bs && i - ws - 1 >= 0) { vp |= a.p[i - ws - 1] >> (64 - bs); vn |= a.n[i - ws - 1] >> (64 - bs); }
    r.p[i] = vp; r.n[i] = vn;
  }
  return r;
}
// divide by 3^k rounding to nearest: in balanced ternary, dropping trits IS round-to-nearest
template <int W> constexpr BigT<W> shr(const BigT<W>& a, int k) {
  if (k <= 0) return a;
  BigT<W> r;
  const int ws = k >> 6, bs = k & 63;
  for (int i = 0; i + ws < W; ++i) {
    u64 vp = a.p[i + ws] >> bs, vn = a.n[i + ws] >> bs;
    if (bs && i + ws + 1 < W) { vp |= a.p[i + ws + 1] << (64 - bs); vn |= a.n[i + ws + 1] << (64 - bs); }
    r.p[i] = vp; r.n[i] = vn;
  }
  return r;
}
template <int W2, int W1> constexpr BigT<W2> resize(const BigT<W1>& a) {  // caller guarantees it fits
  BigT<W2> r;
  for (int i = 0; i < W1 && i < W2; ++i) { r.p[i] = a.p[i]; r.n[i] = a.n[i]; }
  return r;
}

// Product (2W words wide). Radix-27 windows: 3 trits of b at a time select one of the precomputed
// multiples 0..13 of a (negated for digits -13..-1), so only ~1/3 as many ternary additions are needed.
template <int W> constexpr BigT<2 * W> mul(const BigT<W>& a, const BigT<W>& b) {
  BigT<2 * W> mult[14];
  mult[1] = resize<2 * W>(a);
  for (int k = 2; k <= 13; ++k) mult[k] = add(mult[k - 1], mult[1]);
  BigT<2 * W> acc;
  const int tb = b.top();
  for (int i = (tb < 0 ? -1 : tb / 3 * 3); i >= 0; i -= 3) {
    acc = shl(acc, 3);
    int d = b.trit(i) + 3 * (i + 1 < BigT<W>::TRITS ? b.trit(i + 1) : 0) + 9 * (i + 2 < BigT<W>::TRITS ? b.trit(i + 2) : 0);
    if (d > 0) add_into(acc, mult[d]);
    else if (d < 0) add_into(acc, neg(mult[-d]));
  }
  return acc;
}

// Rounded division q = round(N / D) by balanced-ternary long division: at each trit position choose
// q_i in {-1,0,+1} so that |R| <= |D| 3^i / 2. Only additions and comparisons. Requires top(N)+2 < 64W.
// Optionally returns 2R (sign/magnitude of the remainder, for sticky rounding).
template <int W> constexpr BigT<W> divround(BigT<W> N, BigT<W> D, BigT<W>* twice_rem = nullptr) {
  BigT<W> q;
  if (D.sign() < 0) { D = neg(D); N = neg(N); }
  const int tn = N.top(), td = D.top();
  BigT<W> R2 = add(N, N);
  if (tn < 0 || td < 0 || tn - td + 1 < 0) { if (twice_rem) *twice_rem = R2; return q; }
  const int i0 = tn - td + 1;
  BigT<W> T = shl(D, i0);
  BigT<W> T2 = add(T, T);
  for (int i = i0; i >= 0; --i) {
    if (cmp(R2, T) > 0) { q.set_trit(i, 1); add_into(R2, neg(T2)); }
    else if (cmp(neg(R2), T) > 0) { q.set_trit(i, -1); add_into(R2, T2); }
    if (i) { T = shr(T, 1); T2 = shr(T2, 1); }
  }
  if (twice_rem) *twice_rem = R2;
  return q;
}

// Binary -> ternary input boundary using only ternary additions (doubling and summing powers of two).
template <int W> constexpr BigT<W> from_binary(long long v) {
  BigT<W> r, pw;
  pw.set_trit(0, 1);
  const bool negative = v < 0;
  unsigned long long u = negative ? 0ull - static_cast<unsigned long long>(v) : static_cast<unsigned long long>(v);
  while (u) {
    if (u & 1) add_into(r, pw);
    add_into(pw, pw);
    u >>= 1;
  }
  return negative ? neg(r) : r;
}
// Ternary -> binary output boundary (Horner in binary integers; caller ensures it fits).
template <int W> constexpr long long to_binary(const BigT<W>& a) {
  long long v = 0;
  for (int i = a.top(); i >= 0; --i) v = v * 3 + a.trit(i);
  return v;
}

// ============================================================ TWord<N>: N-trit machine words
template <int N> struct TWord {
  static_assert(N >= 1 && N <= 64);
  static constexpr u64 MASK = N == 64 ? ~u64(0) : ((u64(1) << N) - 1);
  BigT<1> v;
  bool overflow = false;  // set when a result wrapped modulo 3^N

  static constexpr TWord from_int(long long x) { TWord w; w.v = from_binary<1>(x); w.overflow = w.v.top() >= N; w.v.p[0] &= MASK; w.v.n[0] &= MASK; return w; }
  constexpr long long to_int() const { return to_binary(v); }
  constexpr int trit(int i) const { return v.trit(i); }
  static constexpr TWord wrap(BigT<1> r, bool of) {
    TWord w; w.overflow = of || ((r.p[0] | r.n[0]) & ~MASK); w.v = r; w.v.p[0] &= MASK; w.v.n[0] &= MASK; return w;
  }
  friend constexpr TWord operator+(const TWord& a, const TWord& b) { BigT<1> r = a.v; int c = add_into(r, b.v); return wrap(r, c != 0); }
  friend constexpr TWord operator-(const TWord& a) { TWord w = a; w.v = neg(a.v); return w; }
  friend constexpr TWord operator-(const TWord& a, const TWord& b) { return a + (-b); }
  friend constexpr TWord operator*(const TWord& a, const TWord& b) {
    BigT<2> r = mul(a.v, b.v);
    return wrap(resize<1>(r), r.top() >= N);
  }
  // rounded quotient (balanced ternary rounds naturally); use divmod_floor for C-like truncation
  friend constexpr TWord operator/(const TWord& a, const TWord& b) {
    BigT<2> q = divround(resize<2>(a.v), resize<2>(b.v));
    return wrap(resize<1>(q), false);
  }
  friend constexpr int compare(const TWord& a, const TWord& b) { return cmp(a.v, b.v); }
  friend constexpr bool operator==(const TWord& a, const TWord& b) { return cmp(a.v, b.v) == 0; }
  friend constexpr bool operator<(const TWord& a, const TWord& b) { return cmp(a.v, b.v) < 0; }
  constexpr TWord shl(int k) const { return wrap(fsot::bt::shl(v, k), v.top() + k >= N); }
  constexpr TWord shr(int k) const { TWord w; w.v = fsot::bt::shr(v, k); return w; }
  constexpr int sign() const { return v.sign(); }
};
using Tryte = TWord<9>;    // 9 trits: 19,683 states (-9841..9841)
using Word27 = TWord<27>;  // matches Reality-OS BalancedTernary27
using Word40 = TWord<40>;  // largest word whose range fits int64: |x| <= (3^40-1)/2

// ============================================================ BTFloat<P>
template <int P> struct BTFloat {
  static_assert(P >= 4);
  static constexpr int W = (P + 2 + 63) / 64;  // mantissa words (one trit of headroom kept)
  static constexpr int WW = 2 * W;
  BigT<W> m;   // zero, or top() == P-1  (so |m| in [3^(P-1)/2, 3^P/2))
  int e = 0;   // value = m * 3^e

  constexpr BTFloat() = default;
  template <class I>
    requires std::is_integral_v<I>
  constexpr BTFloat(I v) { *this = from_wide(from_binary<WW>(static_cast<long long>(v)), 0); }
  constexpr bool is_zero() const { return m.is_zero(); }
  constexpr int sign() const { return m.sign(); }

  template <int WX> static constexpr BTFloat from_wide(const BigT<WX>& x, int ex) {
    BTFloat r;
    const int t = x.top();
    if (t < 0) return r;
    if (t > P - 1) { r.m = resize<W>(shr(x, t - (P - 1))); r.e = ex + t - (P - 1); }
    else { r.m = resize<W>(x); r.m = shl(r.m, (P - 1) - t); r.e = ex - ((P - 1) - t); }
    return r;
  }
  template <int Q> constexpr BTFloat<Q> to() const {  // change precision (rounds to nearest)
    if constexpr (BTFloat<Q>::W >= W) return BTFloat<Q>::from_wide(resize<BTFloat<Q>::W>(m), e);
    else return BTFloat<Q>::from_wide(m, e);
  }
  // exact multiplication by 3^k
  friend constexpr BTFloat scale3(BTFloat a, int k) { if (!a.is_zero()) a.e += k; return a; }

  friend constexpr BTFloat operator-(BTFloat a) { a.m = neg(a.m); return a; }
  friend constexpr BTFloat operator+(const BTFloat& x, const BTFloat& y) {
    if (x.is_zero()) return y;
    if (y.is_zero()) return x;
    const BTFloat& a = x.e >= y.e ? x : y;
    const BTFloat& b = x.e >= y.e ? y : x;
    const int d = a.e - b.e;
    if (d > P + 2) return a;  // |b| < ulp(a)/2: correctly rounded result is a
    BigT<WW> A = shl(resize<WW>(a.m), d);
    add_into(A, resize<WW>(b.m));
    return from_wide(A, b.e);
  }
  friend constexpr BTFloat operator-(const BTFloat& a, const BTFloat& b) { return a + (-b); }
  friend constexpr BTFloat operator*(const BTFloat& a, const BTFloat& b) {
    if (a.is_zero() || b.is_zero()) return BTFloat();
    return from_wide(mul(a.m, b.m), a.e + b.e);
  }
  friend constexpr BTFloat operator/(const BTFloat& a, const BTFloat& b) {
    if (a.is_zero() || b.is_zero()) return BTFloat();  // x/0 -> 0: no exceptions in the core (caller's contract)
    const BigT<WW> N = shl(resize<WW>(a.m), P + 2);
    return from_wide(divround(N, resize<WW>(b.m)), a.e - b.e - (P + 2));
  }
  BTFloat& operator+=(const BTFloat& o) { return *this = *this + o; }
  BTFloat& operator-=(const BTFloat& o) { return *this = *this - o; }
  BTFloat& operator*=(const BTFloat& o) { return *this = *this * o; }
  BTFloat& operator/=(const BTFloat& o) { return *this = *this / o; }

  friend constexpr int compare(const BTFloat& a, const BTFloat& b) { return (a - b).sign(); }
  friend constexpr bool operator==(const BTFloat& a, const BTFloat& b) { return compare(a, b) == 0; }
  friend constexpr bool operator!=(const BTFloat& a, const BTFloat& b) { return compare(a, b) != 0; }
  friend constexpr bool operator<(const BTFloat& a, const BTFloat& b) { return compare(a, b) < 0; }
  friend constexpr bool operator>(const BTFloat& a, const BTFloat& b) { return compare(a, b) > 0; }
  friend constexpr bool operator<=(const BTFloat& a, const BTFloat& b) { return compare(a, b) <= 0; }
  friend constexpr bool operator>=(const BTFloat& a, const BTFloat& b) { return compare(a, b) >= 0; }

  // nearest integer (drop the fractional trits); returns the integer as a BigT and as BTFloat
  constexpr BTFloat round_int() const {
    if (is_zero() || e >= 0) return *this;
    if (e < -(P + 1)) return BTFloat();
    return from_wide(shr(m, -e), 0);
  }
  constexpr long long to_int() const {  // integer-valued, small: output boundary
    const BTFloat r = round_int();
    if (r.is_zero()) return 0;
    long long v = to_binary(r.e < 0 ? shr(r.m, -r.e) : r.m);  // trailing trits are zero: exact
    for (int i = 0; i < r.e; ++i) v *= 3;
    return v;
  }
  // Output boundary: value as long double (Horner over trits). Not used inside any computation.
  constexpr long double to_ld() const {
    long double v = 0;
    for (int i = m.top(); i >= 0; --i) v = v * 3 + m.trit(i);
    long double s = 1, b = e >= 0 ? 3.0L : 1.0L / 3.0L;
    for (int k = e >= 0 ? e : -e; k; k >>= 1) { if (k & 1) s *= b; b *= b; }
    return v * s;
  }
  explicit constexpr operator double() const { return static_cast<double>(to_ld()); }
  explicit constexpr operator long double() const { return to_ld(); }
};

template <int P> constexpr BTFloat<P> fabs(const BTFloat<P>& x) { return x.sign() < 0 ? -x : x; }
template <int P> constexpr BTFloat<P> floor(const BTFloat<P>& x) {
  BTFloat<P> r = x.round_int();
  if (r > x) r = r - BTFloat<P>(1);
  return r;
}

// ------------------------------------------------------------ parsing decimal literals (ternary arithmetic)
// "123.456e-7": digits accumulate as a ternary integer (N*10 = N*9 + N = shl(N,2) + N), then one division by
// the ternary integer 10^k, all at P+16 trits, rounded to P.
template <int P> constexpr BTFloat<P> parse(const char* s) {
  constexpr int Q = P + 16;
  using F = BTFloat<Q>;
  using B = BigT<F::WW>;
  bool negative = false;
  if (*s == '-') { negative = true; ++s; } else if (*s == '+') ++s;
  B N, ten_k;
  ten_k.set_trit(0, 1);
  int frac = 0, exp10 = 0, digits = 0;
  bool dot = false;
  const B ten_digit[10] = {from_binary<F::WW>(0), from_binary<F::WW>(1), from_binary<F::WW>(2), from_binary<F::WW>(3),
                           from_binary<F::WW>(4), from_binary<F::WW>(5), from_binary<F::WW>(6), from_binary<F::WW>(7),
                           from_binary<F::WW>(8), from_binary<F::WW>(9)};
  for (; *s; ++s) {
    if (*s == '.') { dot = true; continue; }
    if (*s == 'e' || *s == 'E') {
      ++s; bool en = false;
      if (*s == '-') { en = true; ++s; } else if (*s == '+') ++s;
      for (; *s >= '0' && *s <= '9'; ++s) exp10 = exp10 * 10 + (*s - '0');
      if (en) exp10 = -exp10;
      break;
    }
    if (*s < '0' || *s > '9') break;
    if (N.top() + 4 >= B::TRITS - 2) { if (!dot) ++exp10; continue; }  // beyond capacity: drop digit
    N = add(shl(N, 2), N);
    add_into(N, ten_digit[*s - '0']);
    ++digits;
    if (dot) ++frac;
  }
  int k = frac - exp10;  // value = N * 10^-k
  F num = F::from_wide(N, 0);
  F p10 = F(1);
  const F ten = F(10);
  // 10^|k| by binary powering with ternary multiplications
  F base = ten;
  for (int kk = k < 0 ? -k : k; kk; kk >>= 1) { if (kk & 1) p10 = p10 * base; base = base * base; }
  F r = k >= 0 ? num / p10 : num * p10;
  if (negative) r = -r;
  return r.template to<P>();
}

// ------------------------------------------------------------ transcendental kernels (at working precision Q)
namespace detail {
template <class F> constexpr bool negligible(const F& term, const F& sum, int P) {
  return term.is_zero() || (!sum.is_zero() && term.e + P + 1 < sum.e);
}
// atanh(1/n) or atan(1/n) = sum (+-1)^k / ((2k+1) n^(2k+1)); n == 3 uses exact exponent shifts
template <int Q> constexpr BTFloat<Q> arc_inv(int n, bool alternate) {
  using F = BTFloat<Q>;
  const F one(1), nn(n), n2(n * n);
  F pw = n == 3 ? scale3(one, -1) : one / nn;
  F sum = pw;
  for (int k = 1;; ++k) {
    pw = n == 3 ? scale3(pw, -2) : pw / n2;
    F term = pw / F(2 * k + 1);
    if (negligible(term, sum, Q)) break;
    sum = (alternate && (k & 1)) ? sum - term : sum + term;
  }
  return sum;
}
template <int Q> const BTFloat<Q>& ln3() {  // ln 3 = 2 atanh(1/3) + 2 atanh(1/5)   (ln 2 + ln 3/2)
  static const BTFloat<Q> v = BTFloat<Q>(2) * (arc_inv<Q>(3, false) + arc_inv<Q>(5, false));
  return v;
}
template <int Q> const BTFloat<Q>& pi() {  // Machin: 16 atan(1/5) - 4 atan(1/239)
  static const BTFloat<Q> v = BTFloat<Q>(16) * arc_inv<Q>(5, true) - BTFloat<Q>(4) * arc_inv<Q>(239, true);
  return v;
}
template <int Q> BTFloat<Q> exp_k(const BTFloat<Q>& x) {
  using F = BTFloat<Q>;
  if (x.is_zero()) return F(1);
  const F kf = (x / ln3<Q>()).round_int();
  const long long k = kf.to_int();
  F r = x - kf * ln3<Q>();       // |r| <= ln3/2
  constexpr int J = 8;           // r / 3^8: exact exponent shift
  r = scale3(r, -J);
  F sum(1), term(1);
  for (int n = 1;; ++n) {
    term = term * r / F(n);
    if (negligible(term, sum, Q)) break;
    sum = sum + term;
  }
  for (int j = 0; j < J; ++j) sum = sum * sum * sum;  // e^(3t) = (e^t)^3
  return scale3(sum, int(k));
}
template <int Q> BTFloat<Q> ln_k(const BTFloat<Q>& x) {  // x > 0
  using F = BTFloat<Q>;
  const int k = x.e + (Q - 1);   // x = mant * 3^k, mant in [1/2, 3/2)
  const F mnt = scale3(x, -k);
  const F one(1);
  const F z = (mnt - one) / (mnt + one);  // |z| <= 1/3
  const F z2 = z * z;
  F pw = z, sum = z;
  for (int n = 1;; ++n) {
    pw = pw * z2;
    F term = pw / F(2 * n + 1);
    if (negligible(term, sum, Q)) break;
    sum = sum + term;
  }
  return F(2) * sum + F(k) * ln3<Q>();
}
// sin and versine via the triple-angle formulas:
//   sin 3t = s (3 - 4 s^2),  1 - cos 3t = u (3 - 2u)^2   (u = 1 - cos t keeps full relative precision)
template <int Q> void sincos_k(const BTFloat<Q>& x, BTFloat<Q>& s_out, BTFloat<Q>& c_out) {
  using F = BTFloat<Q>;
  const F two_pi = F(2) * pi<Q>();
  const F kf = (x / two_pi).round_int();
  F r = x - kf * two_pi;  // |r| <= pi
  constexpr int J = 6;
  const F t = scale3(r, -J);
  const F t2 = t * t;
  F s = t, term = t;
  for (int n = 1;; ++n) {  // sin t
    term = -(term * t2 / F((2 * n) * (2 * n + 1)));
    if (negligible(term, s, Q)) break;
    s = s + term;
  }
  F u = scale3(t2, 0) / F(2), uterm = u;
  for (int n = 2;; ++n) {  // 1 - cos t = t^2/2! - t^4/4! + ...
    uterm = -(uterm * t2 / F((2 * n - 1) * (2 * n)));
    if (negligible(uterm, u, Q)) break;
    u = u + uterm;
  }
  const F three(3), four(4), two(2);
  for (int j = 0; j < J; ++j) {
    s = s * (three - four * s * s);
    const F w = three - two * u;
    u = u * w * w;
  }
  s_out = s;
  c_out = F(1) - u;
}
template <int Q> BTFloat<Q> sqrt_k(const BTFloat<Q>& a) {  // a > 0, Newton x <- (x + a/x)/2
  using F = BTFloat<Q>;
  const int K = a.e + (Q - 1);
  const int h = K >= 0 ? K / 2 : -((-K + 1) / 2);
  F x = scale3(F((K - 2 * h) ? 2 : 1), h);
  const F half = F(1) / F(2);
  for (int it = 0; it < 64; ++it) {
    const F nx = (x + a / x) * half;
    const F d = nx - x;
    x = nx;
    if (d.is_zero() || d.e + Q + 2 < x.e) break;
  }
  return x;
}
}  // namespace detail

inline constexpr int GUARD = 16;
template <int P> BTFloat<P> exp(const BTFloat<P>& x) { return detail::exp_k<P + GUARD>(x.template to<P + GUARD>()).template to<P>(); }
template <int P> BTFloat<P> log(const BTFloat<P>& x) {
  if (x.sign() <= 0) return BTFloat<P>();  // domain error -> 0 (no exceptions in the core)
  return detail::ln_k<P + GUARD>(x.template to<P + GUARD>()).template to<P>();
}
template <int P> BTFloat<P> sqrt(const BTFloat<P>& x) {
  if (x.sign() <= 0) return BTFloat<P>();
  return detail::sqrt_k<P + GUARD>(x.template to<P + GUARD>()).template to<P>();
}
template <int P> BTFloat<P> sin(const BTFloat<P>& x) {
  BTFloat<P + GUARD> s, c; detail::sincos_k<P + GUARD>(x.template to<P + GUARD>(), s, c); return s.template to<P>();
}
template <int P> BTFloat<P> cos(const BTFloat<P>& x) {
  BTFloat<P + GUARD> s, c; detail::sincos_k<P + GUARD>(x.template to<P + GUARD>(), s, c); return c.template to<P>();
}
template <int P> BTFloat<P> pow(const BTFloat<P>& x, const BTFloat<P>& y) {
  if (x.sign() <= 0) return BTFloat<P>();
  return detail::exp_k<P + GUARD>(y.template to<P + GUARD>() * detail::ln_k<P + GUARD>(x.template to<P + GUARD>())).template to<P>();
}
template <int P> BTFloat<P> pi() { return detail::pi<P + GUARD>().template to<P>(); }
template <int P> BTFloat<P> e() { return detail::exp_k<P + GUARD>(BTFloat<P + GUARD>(1)).template to<P>(); }

// Precisions used by the FSOT ternary path (bits equivalent = P * log2(3) = 1.585 P)
using BT40 = BTFloat<40>;    // ~63.4 bits  (~ x87 long double)
using BT72 = BTFloat<72>;    // ~114 bits   (~ IEEE binary128)
using BT110 = BTFloat<110>;  // ~174 bits   (>= mpmath dps=50 / prec 169)

}  // namespace fsot::bt
