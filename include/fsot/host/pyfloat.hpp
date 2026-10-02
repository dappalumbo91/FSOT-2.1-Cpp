// fsot/host/pyfloat.hpp — CPython float semantics needed for bit-exact golden comparison (host only):
// repr(float) and round(x, ndigits).
#pragma once
#include <charconv>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <string>

namespace fsot::py {
// repr(float) — CPython 'r' format: shortest round-trip digits; fixed if -4 <= exp < 16.
inline std::string repr(double x) {
  if (std::isnan(x)) return "nan";
  if (std::isinf(x)) return x > 0 ? "inf" : "-inf";
  if (x == 0) return std::signbit(x) ? "-0.0" : "0.0";
  char buf[64];
  auto res = std::to_chars(buf, buf + sizeof buf, x, std::chars_format::scientific);
  std::string s(buf, res.ptr);
  bool neg = s[0] == '-';
  if (neg) s.erase(0, 1);
  const auto epos = s.find('e');
  std::string mant = s.substr(0, epos);
  int exp10 = std::atoi(s.c_str() + epos + 1);
  std::string digits;
  for (char c : mant) if (c != '.') digits += c;
  std::string out;
  if (exp10 >= -4 && exp10 < 16) {
    const int nd = static_cast<int>(digits.size());
    if (exp10 >= 0) {
      if (nd <= exp10 + 1) out = digits + std::string(exp10 + 1 - nd, '0') + ".0";
      else out = digits.substr(0, exp10 + 1) + "." + digits.substr(exp10 + 1);
    } else {
      out = "0." + std::string(-exp10 - 1, '0') + digits;
    }
  } else {
    out = digits.substr(0, 1);
    if (digits.size() > 1) out += "." + digits.substr(1);
    char eb[16];
    std::snprintf(eb, sizeof eb, "e%c%02d", exp10 < 0 ? '-' : '+', std::abs(exp10));
    out += eb;
  }
  return neg ? "-" + out : out;
}

// round(x, nd) for floats: exact decimal rounding (half-even on the exact binary value), back to double.
inline double round_nd(double x, int nd) {
  if (!std::isfinite(x)) return x;
  char buf[512];
  std::snprintf(buf, sizeof buf, "%.*f", nd, x);
  return std::strtod(buf, nullptr);
}

}  // namespace fsot::py
