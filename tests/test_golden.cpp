// Golden-value harness: every constant, domain fold, domain S, Ledger-B
// correction and closed-form row of vendor/fsot_compute.py (pin AEB2AD)
// compared to the C++ port at each precision.
#include <cfloat>
#include <cstdio>
#include <fstream>
#include <map>
#include <sstream>
#include <string>
#include <vector>

#include "fsot/engine.hpp"
#include "fsot/trit.hpp"

using namespace fsot;
#if defined(FSOT_HAVE_BOOST_MP)
using Ref = mp169;
#else
using Ref = long double;
#endif

struct Row { std::string key, name, value; };

static std::vector<Row> load(const char* path) {
  std::ifstream in(path);
  std::vector<Row> rows;
  std::string line;
  while (std::getline(in, line)) {
    if (line.empty() || line[0] == '#') continue;
    std::istringstream ss(line);
    Row r;
    std::getline(ss, r.key, '\t'); std::getline(ss, r.name, '\t'); std::getline(ss, r.value, '\t');
    rows.push_back(r);
  }
  return rows;
}

template <class R> Ref to_ref(const R& x) {
#if defined(FSOT_HAVE_BOOST_MP)
  if constexpr (std::is_same_v<R, mp169>) return x;
  else return Ref(to_string(x, 45));
#else
  return static_cast<Ref>(x);
#endif
}

struct Stats {
  int checked = 0, failed = 0, exact_fail = 0, bit_identical = 0, float_checked = 0;
  double max_rel = 0; std::string worst;
  double max_mixed = 0; std::string worst_mixed;
  double max_rel_wo_cancel = 0; std::string worst_wo_cancel;  // excludes Chain_consistency_% (difference of near-equal values)  // |d| / max(|g|,1): robust to cancellation rows
};

template <class R> Stats run(const std::vector<Row>& rows, double tol, bool verbose) {
  Engine<R> eng;
  std::map<std::string, R> consts = {
      {"PI", eng.PI}, {"E", eng.E}, {"PHI", eng.PHI}, {"GAMMA", eng.GAMMA}, {"G_CAT", eng.G_CAT},
      {"ALPHA", eng.ALPHA}, {"PSI_CON", eng.PSI_CON}, {"ETA_EFF", eng.ETA_EFF}, {"BETA", eng.BETA},
      {"GAMMA_C", eng.GAMMA_C}, {"OMEGA", eng.OMEGA}, {"THETA_S", eng.THETA_S}, {"POOF", eng.POOF},
      {"C_EFF", eng.C_EFF}, {"A_BLEED", eng.A_BLEED}, {"P_VAR", eng.P_VAR}, {"B_IN", eng.B_IN},
      {"A_IN", eng.A_IN}, {"SUCTION", eng.SUCTION}, {"CHAOS", eng.CHAOS}, {"P_BASE", eng.P_BASE},
      {"P_NEW", eng.P_NEW}, {"C_FACTOR", eng.C_FACTOR}, {"K", eng.K}, {"C_COSM", eng.C_COSM},
      {"S_COSM", eng.S_COSM}, {"S_QUANT", eng.S_QUANT}, {"S_CHEM", eng.S_CHEM}};
  std::map<std::string, std::vector<Result<R>>> secs;
  for (auto& [name, fn] : eng.sections()) secs[name] = (eng.*fn)();
  int total = 0, pass5 = 0;
  for (auto& [n, rs] : secs)
    for (auto& r : rs)
      if (r.measured && *r.measured != R(0)) {
        ++total;
        if (static_cast<double>(m::fabs(r.computed - *r.measured) / m::fabs(*r.measured) * R(100)) < 5.0) ++pass5;
      }

  Stats st;
  auto cmp = [&](const std::string& label, const R& c, const std::string& gs) {
    const Ref g(gs.c_str());
    const Ref d = m::fabs(to_ref(c) - g);
    const Ref ag = m::fabs(g);
    const double rel = ag == 0 ? static_cast<double>(d) : static_cast<double>(d / ag);
    const double mixed = static_cast<double>(d / (ag > Ref(1) ? ag : Ref(1)));
    ++st.checked; ++st.float_checked;
    if constexpr (std::is_same_v<R, double> || std::is_same_v<R, long double>) {
      if (c == static_cast<R>(Ref(gs.c_str()))) ++st.bit_identical;
    } else {
      // rounded to double, does the high-precision result equal float(mpmath)?
      if (static_cast<double>(to_ref(c)) == static_cast<double>(Ref(gs.c_str()))) ++st.bit_identical;
    }
    if (rel > st.max_rel) { st.max_rel = rel; st.worst = label; }
    if (label.find("Chain_consistency") == std::string::npos && rel > st.max_rel_wo_cancel) { st.max_rel_wo_cancel = rel; st.worst_wo_cancel = label; }
    if (mixed > st.max_mixed) { st.max_mixed = mixed; st.worst_mixed = label; }
    if (mixed > tol) { ++st.failed; if (verbose) std::printf("  FAIL %s rel=%.3e\n", label.c_str(), rel); }
  };
  auto exact = [&](const std::string& label, long long c, const std::string& gs) {
    ++st.checked;
    if (std::to_string(c) != gs) { ++st.failed; ++st.exact_fail; std::printf("  EXACT FAIL %s: %lld vs %s\n", label.c_str(), c, gs.c_str()); }
  };
  for (auto& row : rows) {
    const std::string& k = row.key;
    if (k == "const") cmp("const." + row.name, consts.at(row.name), row.value);
    else if (k == "domain.D_eff") exact(k + "." + row.name, eng.domain(row.name).D_eff, row.value);
    else if (k == "domain.hits") exact(k + "." + row.name, eng.domain(row.name).hits, row.value);
    else if (k == "domain.observed") exact(k + "." + row.name, eng.domain(row.name).observed, row.value);
    else if (k == "domain.look") cmp(k + "." + row.name, eng.domain(row.name).delta_psi, row.value);
    else if (k == "domain.C") cmp(k + "." + row.name, eng.domain(row.name).C, row.value);
    else if (k == "domain.S") cmp(k + "." + row.name, eng.domain_scalar(row.name), row.value);
    else if (k == "correct72") cmp(k + "." + row.name, eng.fsot_correct(R(72), row.name), row.value);
    else if (k.rfind("sec.", 0) == 0) {
      const auto dot = k.rfind('.');
      const std::string sec = k.substr(4, dot - 4);
      const std::size_t idx = std::stoul(k.substr(dot + 1));
      const auto& rs = secs.at(sec);
      if (idx >= rs.size()) { ++st.failed; std::printf("  MISSING %s\n", k.c_str()); continue; }
      if (rs[idx].name != row.name) { ++st.failed; std::printf("  NAME MISMATCH %s: %s vs %s\n", k.c_str(), rs[idx].name.c_str(), row.name.c_str()); }
      cmp(k + "(" + row.name + ")", rs[idx].computed, row.value);
    } else if (k == "summary.total") exact(k, total, row.value);
    else if (k == "summary.pass5") exact(k, pass5, row.value);
  }
  // section sizes must match exactly (no extra rows on the C++ side)
  std::map<std::string, std::size_t> gold_count;
  for (auto& row : rows) if (row.key.rfind("sec.", 0) == 0) gold_count[row.key.substr(4, row.key.rfind('.') - 4)]++;
  for (auto& [n, rs] : secs) if (rs.size() != gold_count[n]) { ++st.failed; std::printf("  COUNT MISMATCH %s: %zu vs %zu\n", n.c_str(), rs.size(), gold_count[n]); }
  return st;
}

template <class R> bool report(const std::vector<Row>& rows, double tol) {
  Stats st = run<R>(rows, tol, true);
  std::printf("  %s: max_rel excluding cancellation row = %.3e [%s]\n", real_traits<R>::name(), st.max_rel_wo_cancel, st.worst_wo_cancel.c_str());
  if (st.bit_identical) std::printf("  %s: %d/%d values bit-identical to golden after rounding to this type (hi-prec types: rounded to double vs float(mpmath))\n", real_traits<R>::name(), st.bit_identical, st.float_checked);
  std::printf("%-20s checked=%4d failed=%d  max_rel=%.3e [%s]  max_mixed=%.3e [%s]  tol=%.0e  %s\n",
              real_traits<R>::name(), st.checked, st.failed, st.max_rel, st.worst.c_str(), st.max_mixed,
              st.worst_mixed.c_str(), tol, st.failed ? "FAIL" : "PASS");
  return st.failed == 0;
}

int main(int argc, char** argv) {
  const char* path = argc > 1 ? argv[1] : FSOT_GOLDEN_TSV;
  auto rows = load(path);
  if (rows.empty()) { std::printf("no golden rows in %s\n", path); return 2; }
  bool ok = true;
  ok &= report<double>(rows, 1e-12);
#if LDBL_MANT_DIG > DBL_MANT_DIG
  ok &= report<long double>(rows, 1e-15);
#else
  std::printf("long double: skipped (LDBL_MANT_DIG %d <= DBL_MANT_DIG %d on this platform; the 1e-15 bar needs 80-bit long double)\n", LDBL_MANT_DIG, DBL_MANT_DIG);
#endif
#if defined(FSOT_HAVE_FLOAT128)
  ok &= report<f128>(rows, 1e-28);
#endif
#if defined(FSOT_HAVE_BOOST_MP)
  ok &= report<mp169>(rows, 1e-45);
#endif
  // Ternary collapse constant must equal float(C_EFF*P_VAR) at this pin.
#if defined(FSOT_HAVE_BOOST_MP)
  { Engine<mp169> e; const double thr = static_cast<double>(e.C_EFF * e.P_VAR);
    if (thr != trit::COLLAPSE_THRESHOLD_AEB2AD) { std::printf("collapse threshold drift %.17g\n", thr); ok = false; } }
#endif
  { Engine<double> d; const double st = d.domain_scalar("Thermodynamics");
    std::printf("S_thermo(double) = %.17g (expected 0.9363875640629747 from float(mpmath)) %s\n", st,
                st == 0.9363875640629747 ? "bit-identical" : "differs by a few ulp");
    if (std::fabs(st - 0.9363875640629747) > 1e-15) ok = false; }
#if defined(FSOT_HAVE_BOOST_MP)
  { Engine<mp169> e; const double st = static_cast<double>(e.domain_scalar("Thermodynamics"));
    std::printf("S_thermo(mp169 -> double) = %.17g %s\n", st, st == 0.9363875640629747 ? "bit-identical to float(mpmath)" : "MISMATCH");
    if (st != 0.9363875640629747) ok = false; }
#endif
  std::printf("%s\n", ok ? "GOLDEN: ALL PASS" : "GOLDEN: FAILURES");
  return ok ? 0 : 1;
}
