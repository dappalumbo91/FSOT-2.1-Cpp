// predict_closed_form — evaluate the FSOT closed forms with the freestanding balanced-ternary core
// (fsot::core::CoreEngine<BTFloat<P>>, sections generated from the authority, pin AEB2AD).
//
//   predict_closed_form [--section NAME] [--name TEXT] [--digits N] [--trits 40|72|110] [--corrected] [--tsv]
//   predict_closed_form --list-sections
//
// --section keeps one section; --name keeps rows whose displayed name contains TEXT; --corrected evaluates
// truncated 1/3 exponents as p/q (audit B-03), as Engine(Mode::corrected). Output columns: section, name,
// formula, value, target, error % (|v - t| / |t| * 100, empty when the row has no target or t = 0).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include "fsot/core.hpp"

namespace {
struct Opts {
  const char* section = nullptr;
  const char* name = nullptr;
  int digits = 20, trits = 110;
  bool corrected = false, tsv = false;
};

template <int P> struct Printer {
  using F = fsot::bt::BTFloat<P>;
  const Opts& o;
  int shown = 0;
  void operator()(const fsot::core::CfRow<F>& r) {
    if (o.section && std::strcmp(o.section, r.section) != 0) return;
    char nb[256], fb[512], vb[160], tb[160] = "", eb[64] = "";
    fsot::core::cf_name(r, nb, sizeof nb);
    if (o.name && !std::strstr(nb, o.name)) return;
    fsot::core::cf_formula(r, fb, sizeof fb);
    fsot::core::to_decimal(r.value, o.digits, vb, sizeof vb);
    if (r.has_target) {
      fsot::core::to_decimal(r.target, o.digits, tb, sizeof tb);
      if (!r.target.is_zero()) {
        const F err = fsot::bt::fabs(r.value - r.target) / fsot::bt::fabs(r.target) * F(100);
        fsot::core::to_decimal(err, 4, eb, sizeof eb);
      }
    }
    if (o.tsv) std::printf("%s\t%s\t%s\t%s\t%s\t%s\n", r.section, nb, fb, vb, tb, eb);
    else std::printf("%-28s %-34s = %s%s%s%s%s\n", r.section, nb, vb, *tb ? "  target " : "", tb, *eb ? "  err% " : "", eb);
    ++shown;
  }
};

template <int P> int run(const Opts& o) {
  fsot::core::CoreEngine<fsot::bt::BTFloat<P>> eng;
  eng.corrected = o.corrected;
  Printer<P> pr{o};
  if (o.tsv) std::printf("section\tname\tformula\tvalue\ttarget\terror_pct\n");
  eng.all_sections(pr);
  std::fprintf(stderr, "predict_closed_form: %d rows (BTFloat<%d>, %s mode, pin AEB2AD)\n", pr.shown, P,
               o.corrected ? "corrected" : "parity");
  return pr.shown ? 0 : 1;
}
}  // namespace

int main(int argc, char** argv) {
  Opts o;
  for (int i = 1; i < argc; ++i) {
    const std::string a = argv[i];
    auto next = [&]() -> const char* { if (i + 1 >= argc) { std::fprintf(stderr, "%s needs a value\n", a.c_str()); std::exit(2); } return argv[++i]; };
    if (a == "--section") o.section = next();
    else if (a == "--name") o.name = next();
    else if (a == "--digits") o.digits = std::atoi(next());
    else if (a == "--trits") o.trits = std::atoi(next());
    else if (a == "--corrected") o.corrected = true;
    else if (a == "--tsv") o.tsv = true;
    else if (a == "--list-sections") {
      for (const char* s : fsot::core::CoreEngine<fsot::bt::BT40>::SECTION_NAMES) std::printf("%s\n", s);
      return 0;
    } else { std::fprintf(stderr, "usage: predict_closed_form [--section S] [--name T] [--digits N] [--trits 40|72|110] [--corrected] [--tsv] | --list-sections\n"); return 2; }
  }
  if (o.digits < 1) o.digits = 1;
  if (o.digits > 100) o.digits = 100;
  switch (o.trits) {
    case 40: return run<40>(o);
    case 72: return run<72>(o);
    case 110: return run<110>(o);
    default: std::fprintf(stderr, "--trits must be 40, 72 or 110\n"); return 2;
  }
}
