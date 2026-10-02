// fsot/real.hpp — numeric shim so the FSOT engine is written once and
// instantiated for double, long double, __float128 (GCC/Clang) and
// Boost.Multiprecision cpp_bin_float<169 bits> (= mpmath mp.dps=50, prec=169).
#pragma once
#include <cmath>
#include <cstdlib>
#include <numbers>
#include <string>
#include <type_traits>

#if defined(FSOT_HAVE_FLOAT128)
extern "C" {
#include <quadmath.h>
}
#endif

#if defined(FSOT_HAVE_BOOST_MP)
#include <boost/multiprecision/cpp_bin_float.hpp>
#include <boost/math/constants/constants.hpp>
#endif

namespace fsot {

#if defined(FSOT_HAVE_BOOST_MP)
// mpmath at mp.dps = 50 works at prec = 169 bits; match that exactly.
using mp169 = boost::multiprecision::number<
    boost::multiprecision::cpp_bin_float<169, boost::multiprecision::digit_base_2>,
    boost::multiprecision::et_off>;
#endif

#if defined(FSOT_HAVE_FLOAT128)
using f128 = __float128;
#endif

template <class R> struct real_traits;  // name(), pi(), e(), lit(), to_string()

template <> struct real_traits<double> {
  static const char* name() { return "double"; }
  static double pi() { return std::numbers::pi_v<double>; }
  static double e() { return std::numbers::e_v<double>; }
  static double lit(const char* s) { return std::strtod(s, nullptr); }
};
template <> struct real_traits<long double> {
  static const char* name() { return "long double"; }
  static long double pi() { return std::numbers::pi_v<long double>; }
  static long double e() { return std::numbers::e_v<long double>; }
  static long double lit(const char* s) { return std::strtold(s, nullptr); }
};
#if defined(FSOT_HAVE_FLOAT128)
template <> struct real_traits<f128> {
  static const char* name() { return "__float128"; }
  static f128 pi() { return M_PIq; }
  static f128 e() { return M_Eq; }
  static f128 lit(const char* s) { return strtoflt128(s, nullptr); }
};
#endif
#if defined(FSOT_HAVE_BOOST_MP)
template <> struct real_traits<mp169> {
  static const char* name() { return "cpp_bin_float<169>"; }
  static mp169 pi() { return boost::math::constants::pi<mp169>(); }
  static mp169 e() { return boost::math::constants::e<mp169>(); }
  static mp169 lit(const char* s) { return mp169(s); }
};
#endif

template <class R> inline R lit(const char* s) { return real_traits<R>::lit(s); }

// Math namespace: generic versions resolve via std:: or ADL (Boost); __float128
// gets explicit libquadmath overloads.
namespace m {
template <class R> inline R sqrt(const R& x) { using std::sqrt; return sqrt(x); }
template <class R> inline R ln(const R& x) { using std::log; return log(x); }
template <class R> inline R exp(const R& x) { using std::exp; return exp(x); }
template <class R> inline R sin(const R& x) { using std::sin; return sin(x); }
template <class R> inline R cos(const R& x) { using std::cos; return cos(x); }
template <class R> inline R acos(const R& x) { using std::acos; return acos(x); }
template <class R> inline R floor(const R& x) { using std::floor; return floor(x); }
template <class R> inline R fabs(const R& x) { using std::fabs; return fabs(x); }
template <class R> inline R pow(const R& x, const R& y) { using std::pow; return pow(x, y); }
#if defined(FSOT_HAVE_FLOAT128)
template <> inline f128 sqrt(const f128& x) { return sqrtq(x); }
template <> inline f128 ln(const f128& x) { return logq(x); }
template <> inline f128 exp(const f128& x) { return expq(x); }
template <> inline f128 sin(const f128& x) { return sinq(x); }
template <> inline f128 cos(const f128& x) { return cosq(x); }
template <> inline f128 acos(const f128& x) { return acosq(x); }
template <> inline f128 floor(const f128& x) { return floorq(x); }
template <> inline f128 fabs(const f128& x) { return fabsq(x); }
template <> inline f128 pow(const f128& x, const f128& y) { return powq(x, y); }
#endif
// Integer power by binary powering (mpmath evaluates x**n for integer n this way).
template <class R> inline R ipow(const R& x, int n) {
  if (n < 0) return R(1) / ipow(x, -n);
  R result(1), base(x);
  while (n) { if (n & 1) result *= base; base *= base; n >>= 1; }
  return result;
}
}  // namespace m

template <class R> inline std::string to_string(const R& x, int digits) {
#if defined(FSOT_HAVE_FLOAT128)
  if constexpr (std::is_same_v<R, f128>) {
    char buf[128];
    quadmath_snprintf(buf, sizeof buf, "%.*Qe", digits - 1, x);
    return buf;
  } else
#endif
#if defined(FSOT_HAVE_BOOST_MP)
  if constexpr (std::is_same_v<R, mp169>) {
    return x.str(digits, std::ios_base::scientific);
  } else
#endif
  {
    char buf[128];
    std::snprintf(buf, sizeof buf, "%.*Le", digits - 1, static_cast<long double>(x));
    return buf;
  }
}

}  // namespace fsot
