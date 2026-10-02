// Freestanding closed forms (fsot::core::CoreEngine<BTFloat<110>>, closed_forms_core.gen.inc) against the
// mpmath golden (golden/golden_AEB2AD.tsv, sec.* rows, dps 50): same 368 rows, same names, same order,
// and every value within a relative 1e-45 (or absolute 1e-45 for a zero target).
#include <cmath>
#include <cstdio>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include "fsot/core.hpp"

using F = fsot::bt::BTFloat<110>;
using G = fsot::bt::BTFloat<120>;

struct Collect {
  std::vector<std::pair<std::string, F>> rows;
  void operator()(const fsot::core::CfRow<F>& r) {
    char nb[256];
    fsot::core::cf_name(r, nb, sizeof nb);
    rows.emplace_back(nb, r.value);
  }
};

int main() {
  std::ifstream in(FSOT_GOLDEN_TSV);
  std::vector<std::pair<std::string, std::string>> gold;
  for (std::string line; std::getline(in, line);) {
    if (line.rfind("sec.", 0) != 0) continue;
    std::stringstream ss(line);
    std::string key, name, val;
    std::getline(ss, key, '\t'); std::getline(ss, name, '\t'); std::getline(ss, val, '\t');
    gold.emplace_back(name, val);
  }
  fsot::core::CoreEngine<F> c;
  Collect col;
  c.all_sections(col);
  int bad = 0;
  if (col.rows.size() != gold.size()) { std::printf("row count %zu vs golden %zu\n", col.rows.size(), gold.size()); ++bad; }
  const G tol = fsot::bt::parse<120>("1e-45");
  double worst = 0; std::string worst_name;
  for (size_t i = 0; i < std::min(col.rows.size(), gold.size()); ++i) {
    if (col.rows[i].first != gold[i].first) { std::printf("name %zu: %s vs %s\n", i, col.rows[i].first.c_str(), gold[i].first.c_str()); ++bad; continue; }
    const G v = col.rows[i].second.to<120>(), g = fsot::bt::parse<120>(gold[i].second.c_str());
    const G d = fsot::bt::fabs(v - g);
    const G scale = g.is_zero() ? G(1) : fsot::bt::fabs(g);
    const G rel = d / scale;
    char rb[64]; fsot::core::to_decimal(rel, 3, rb, sizeof rb);
    const double rd = std::strtod(rb, nullptr);
    if (rd > worst) { worst = rd; worst_name = gold[i].first; }
    if (tol < rel) { std::printf("value %s: rel %s\n", gold[i].first.c_str(), rb); ++bad; }
  }
  std::printf("core closed forms: %zu rows, worst rel %.3g (%s), %d mismatches\n", col.rows.size(), worst, worst_name.c_str(), bad);
  return bad ? 1 : 0;
}
