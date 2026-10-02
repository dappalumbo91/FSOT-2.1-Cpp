// fsot/ternary_real.hpp — plugs fsot::bt::BTFloat<P> into the engine's numeric shim so that
// Engine<BTFloat<P>> evaluates the whole FSOT core (seeds, layers, folds, S) in balanced ternary.
// Host-side glue only (the engine itself still uses std::vector/std::string).
#pragma once
#include <cstdio>
#include <string>

#include "fsot/real.hpp"
#include "fsot/ternary.hpp"

namespace fsot {
template <int P> struct real_traits<bt::BTFloat<P>> {
  static const char* name() {
    static char buf[32];
    std::snprintf(buf, sizeof buf, "BTFloat<%d trits>", P);
    return buf;
  }
  static bt::BTFloat<P> pi() { return bt::pi<P>(); }
  static bt::BTFloat<P> e() { return bt::e<P>(); }
  static bt::BTFloat<P> lit(const char* s) { return bt::parse<P>(s); }
};

namespace bt {
// Decimal output computed with ternary arithmetic: scale into [1,10) by ternary multiplications/divisions
// by 10, then peel digits with floor (sig digits, scientific notation).
template <int P> std::string to_decimal(const BTFloat<P>& x, int sig) {
  if (x.is_zero()) return "0";
  using F = BTFloat<P + 8>;
  F v = x.template to<P + 8>();
  std::string out;
  if (v.sign() < 0) { out = "-"; v = -v; }
  const F ten(10), one(1);
  int e10 = 0;
  while (v >= ten) { v = v / ten; ++e10; }
  while (v < one) { v = v * ten; --e10; }
  std::string digits;
  for (int i = 0; i < sig; ++i) {
    const F d = floor(v);
    digits += char('0' + d.to_int());
    v = (v - d) * ten;
  }
  out += digits.substr(0, 1) + "." + digits.substr(1) + "e" + std::to_string(e10);
  return out;
}
}  // namespace bt

template <int P> inline std::string to_string(const bt::BTFloat<P>& x, int digits) { return bt::to_decimal(x, digits); }
}  // namespace fsot
