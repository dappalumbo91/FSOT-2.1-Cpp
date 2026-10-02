// Compiled with -ffreestanding -fno-exceptions -fno-rtti -fno-threadsafe-statics (no hosted headers):
// proves fsot/ternary.hpp needs no heap, exceptions, iostream or libm. CTest then checks `nm -u` of the
// object for forbidden symbols (malloc/new/throw/printf/libm).
#include "fsot/ternary.hpp"

using namespace fsot::bt;

extern "C" int fsot_freestanding_demo(long long* out) {
  // ALPHA = ln(pi) / (e * phi^13), evaluated entirely in balanced ternary at 40 trits
  const BT40 one(1), two(2), five(5);
  const BT40 phi = (one + sqrt(five)) / two;
  BT40 phi13 = one;
  for (int i = 0; i < 13; ++i) phi13 = phi13 * phi;
  const BT40 alpha = log(pi<40>()) / (e<40>() * phi13);
  // 1e12 * alpha as an integer through ternary rounding (no binary float involved)
  BT40 scaled = alpha;
  for (int i = 0; i < 12; ++i) scaled = scaled * BT40(10);
  *out = scaled.to_int();
  const Word27 a = Word27::from_int(123456), b = Word27::from_int(-789);
  return int((a * b + a / b).to_int() & 0x7fffffff);
}
