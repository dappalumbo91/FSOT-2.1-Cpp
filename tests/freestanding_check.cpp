// Compiled with -ffreestanding -fno-exceptions -fno-rtti -fno-threadsafe-statics (no hosted headers):
// proves fsot/ternary.hpp needs no heap, exceptions, iostream or libm. CTest then checks `nm -u` of the
// object for forbidden symbols (malloc/new/throw/printf/libm).
#include "fsot/ternary.hpp"
#include "fsot/core.hpp"

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

// The freestanding closed forms (fsot/core.hpp + closed_forms_core.gen.inc): all 26 sections into a
// counting sink, at 40 trits.
struct CountSink {
  int n = 0;
  long long acc = 0;
  void operator()(const fsot::core::CfRow<BT40>& r) { ++n; acc += r.value.sign(); }
};
extern "C" int fsot_freestanding_closed_forms(long long* acc) {
  fsot::core::CoreEngine<BT40> eng;
  CountSink s;
  eng.all_sections(s);
  *acc = s.acc;
  return s.n;
}

