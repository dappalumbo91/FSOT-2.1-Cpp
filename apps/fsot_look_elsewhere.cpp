// fsot_look_elsewhere: how many alternative closed forms built from the same seeds land as close to each
// target as the FSOT expression does (look-elsewhere / trials-factor count).
//
// Seeds: pi, e, phi, gamma, G (Catalan) — the five seeds of the authority (AEB2AD §1).
// Grammar M (monomials):  (p/q) * s1^a * s2^b * s3^c   up to 3 distinct seeds, exponents in
//                          X = {-6..-1, 1..6, +-1/2, +-1/3}, p, q in 1..12 coprime, either sign.
// Grammar S (two-term):    u +- v with u, v unit monomials of up to 2 seeds, exponents in X.
// For each target t with an FSOT value c, tol = |c - t| / |t| (the FSOT expression's own relative error);
// the tool counts distinct grammar values v with |v - t| / |t| <= tol, and the expected count from the
// local density of M values (window |t|/1.05 .. |t|*1.05). For Ledger A rows it also counts values inside the
// published kill band. Values are doubles (tolerances below ~1e-13 are reported as "below double").
//
// The grammars are deliberately small. Typical FSOT expressions such as (a - b)/(c + d) are richer, so these
// counts are a LOWER BOUND on the effective number of alternatives.
//   fsot_look_elsewhere [--tsv out.tsv]
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <numeric>
#include <regex>
#include <string>
#include <vector>

#include "fsot/engine.hpp"
#include "fsot/host/ledger_a.hpp"

using namespace fsot;
using Ref = ledger_a::Ref;

struct Grammar {
  std::vector<double> M;      // sorted distinct positive monomial*rational values (sign handled by |t|)
  std::vector<double> unit2;  // sorted unit monomials, <= 2 seeds (for grammar S)
};

static Grammar build() {
  const double seeds[5] = {M_PI, M_E, (1 + std::sqrt(5.0)) / 2, 0.57721566490153286061, 0.91596559417721901505};
  std::vector<double> X;
  for (int k = -6; k <= 6; ++k) if (k) X.push_back(k);
  for (double f : {0.5, -0.5, 1.0 / 3, -1.0 / 3}) X.push_back(f);
  std::vector<double> mono{1.0}, u2{1.0};
  for (int i = 0; i < 5; ++i)
    for (double a : X) {
      const double va = std::pow(seeds[i], a);
      mono.push_back(va); u2.push_back(va);
      for (int j = i + 1; j < 5; ++j)
        for (double b : X) {
          const double vb = va * std::pow(seeds[j], b);
          mono.push_back(vb); u2.push_back(vb);
          for (int k = j + 1; k < 5; ++k)
            for (double c : X) mono.push_back(vb * std::pow(seeds[k], c));
        }
    }
  std::vector<double> rat;
  for (int p = 1; p <= 12; ++p)
    for (int q = 1; q <= 12; ++q)
      if (std::gcd(p, q) == 1) rat.push_back(double(p) / q);
  Grammar g;
  g.M.reserve(mono.size() * rat.size());
  for (double r : rat) for (double m : mono) g.M.push_back(r * m);
  auto dedupe = [](std::vector<double>& v) {
    std::sort(v.begin(), v.end());
    std::vector<double> o;
    for (double x : v) if (o.empty() || std::fabs(x - o.back()) > 1e-14 * x) o.push_back(x);
    v.swap(o);
  };
  dedupe(g.M);
  dedupe(u2);
  g.unit2 = u2;
  return g;
}

static long count_range(const std::vector<double>& v, double lo, double hi) {
  return long(std::upper_bound(v.begin(), v.end(), hi) - std::lower_bound(v.begin(), v.end(), lo));
}
// grammar S: values u + v or u - v (u, v in unit2, unordered for +), lying in [lo, hi] (lo > 0)
static long count_S(const std::vector<double>& u, double lo, double hi) {
  long n = 0;
  for (std::size_t i = 0; i < u.size(); ++i) {
    // u_i + u_j, j >= i
    auto b = std::lower_bound(u.begin() + i, u.end(), lo - u[i]);
    auto e = std::upper_bound(u.begin() + i, u.end(), hi - u[i]);
    if (e > b) n += long(e - b);
    // u_i - u_j  in [lo, hi]  <=>  u_j in [u_i - hi, u_i - lo]
    n += count_range(u, u[i] - hi, u[i] - lo);
  }
  return n;
}

struct Target { std::string source, name; double t, c; double band_lo = NAN, band_hi = NAN; };

int main(int argc, char** argv) {
  const char* tsv = nullptr;
  for (int i = 1; i + 1 < argc; ++i) if (!std::strcmp(argv[i], "--tsv")) tsv = argv[i + 1];
  const Grammar g = build();
  std::printf("grammar M: %zu distinct values in [%.3g, %.3g]; grammar S unit set: %zu (S size ~%zu)\n", g.M.size(), g.M.front(),
              g.M.back(), g.unit2.size(), g.unit2.size() * g.unit2.size() * 3 / 2);

  std::vector<Target> targets;
  const auto& e = ledger_a::engine();
  std::vector<std::string> literal_rows;
  for (auto& li : Engine<Ref>::LITERAL_INPUT_ROWS) literal_rows.push_back(li.row);
  for (auto& [sec, fn] : e.sections())
    for (auto& r : (e.*fn)()) {
      if (!r.measured || *r.measured == Ref(0)) continue;
      if (r.computed == *r.measured) continue;  // non-prediction (computed = target)
      if (std::find(literal_rows.begin(), literal_rows.end(), r.name) != literal_rows.end()) continue;
      targets.push_back({std::string("closed_form:") + sec, r.name, static_cast<double>(*r.measured), static_cast<double>(r.computed)});
    }
  const std::regex band(R"(\[\s*(-?[0-9.]+)\s*,\s*(-?[0-9.]+)\s*\])");
  for (const auto& s : ledger_a::LEDGER_A) {
    auto p = ledger_a::fsot_predict(s.id);
    if (!p) continue;
    Target t{std::string("ledger_a:") + s.kind, s.id, s.anchor, p->value};
    std::cmatch mm;
    if (std::regex_search(s.kill_band, mm, band)) { t.band_lo = std::stod(mm[1]); t.band_hi = std::stod(mm[2]); }
    targets.push_back(t);
  }

  FILE* out = tsv ? std::fopen(tsv, "w") : nullptr;
  if (out) std::fprintf(out, "#source\tname\ttarget\tfsot_value\tfsot_rel_err\tM_within\tM_expected\tS_within\tband\tM_in_band\tS_in_band\n");
  long n = 0, n_beaten = 0, n_tiny = 0;
  std::vector<double> mcounts;
  for (const auto& t : targets) {
    const double at = std::fabs(t.t);
    const double tol = std::fabs(t.c - t.t) / at;
    const double lo = at * (1 - tol), hi = at * (1 + tol);
    const long mw = count_range(g.M, lo, hi);
    // expected count from the LOCAL density of M values (window x/1.05 .. x*1.05 around |t|)
    const double local = double(count_range(g.M, at / 1.05, at * 1.05)) / (2 * std::log(1.05));
    const double mexp = local * std::log((1 + tol) / (1 - tol));
    const long sw = count_S(g.unit2, lo, hi);
    std::string bandtxt = "-";
    long mb = -1, sb = -1;
    if (!std::isnan(t.band_lo)) {
      double blo = std::fabs(t.band_lo), bhi = std::fabs(t.band_hi);
      if (blo > bhi) std::swap(blo, bhi);
      mb = count_range(g.M, blo, bhi);
      sb = count_S(g.unit2, blo, bhi);
      char b[64]; std::snprintf(b, sizeof b, "[%g,%g]", t.band_lo, t.band_hi); bandtxt = b;
    }
    ++n; n_beaten += mw >= 1; n_tiny += tol < 1e-13;
    mcounts.push_back(double(mw));
    if (out)
      std::fprintf(out, "%s\t%s\t%.17g\t%.17g\t%.3e\t%ld\t%.3g\t%ld\t%s\t%ld\t%ld\n", t.source.c_str(), t.name.c_str(), t.t, t.c, tol, mw, mexp, sw,
                   bandtxt.c_str(), mb, sb);
    if (t.source.rfind("ledger_a", 0) == 0)
      std::printf("  %-20s tol=%.2e  M_within=%-6ld (expected %.3g)  S_within=%-6ld  band %-16s M=%ld S=%ld\n", t.name.c_str(), tol, mw, mexp, sw,
                  bandtxt.c_str(), mb, sb);
  }
  std::sort(mcounts.begin(), mcounts.end());
  std::printf("%ld targets; %ld have at least one M-grammar value at least as close as the FSOT expression; median M_within %.0f\n",
              n, n_beaten, mcounts.empty() ? 0.0 : mcounts[mcounts.size() / 2]);
  if (n_tiny) std::printf("%ld targets have tol < 1e-13 (below double resolution of the count)\n", n_tiny);
  if (out) std::fclose(out);
}
