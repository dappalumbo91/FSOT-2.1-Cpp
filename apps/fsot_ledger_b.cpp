// fsot_ledger_b: C++ re-run of the FSOT-2.1-Lean benchmark margin audit + Ledger B re-score.
// Output format is identical to tools/dump_ledger_b_golden.py (every line after the header).
//   fsot_ledger_b --hub /path/to/FSOT-2.1-Lean [--out out.tsv] [--golden golden/ledger_b_XXXXXXXX.tsv]
//                 [--corrected-out corrected.tsv]
// --corrected-out writes the corrected-mode report (docs/AUDIT_LOG.md "Fixed in C++"): gate errors recomputed
// from computed/measured (old vs new counts), Ledger B structural corrections vs genuine predictions,
// round(c,6) vs significant-digit emitter reproducibility, and NaN/Infinity tokens read per file.
// Exit 0 iff --golden is absent or every line after the header matches byte-for-byte.
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <map>
#include <sstream>

#include "fsot/engine.hpp"
#include "fsot/host/ledger_b.hpp"

namespace fs = std::filesystem;
using namespace fsot;
using fsot::ledger_b::json;

#if defined(FSOT_HAVE_BOOST_MP)
using RS = mp169;
#elif defined(FSOT_HAVE_FLOAT128)
using RS = f128;
#else
#error "fsot_ledger_b needs a >=113-bit type so double(S) is correctly rounded"
#endif

static std::string fmt(const json& v) {
  if (v.is_null()) return "None";
  if (v.is_boolean()) return v.get<bool>() ? "True" : "False";
  std::string s = fsot::py::str(v);
  std::replace(s.begin(), s.end(), '\t', ' ');
  std::replace(s.begin(), s.end(), '\n', ' ');
  return s;
}
static std::string fmt(const std::optional<double>& v) { return v ? fsot::py::repr(*v) : "None"; }
static std::string fmt(bool b) { return b ? "True" : "False"; }
static std::string fmt(long n) { return std::to_string(n); }

static std::optional<json> load(const fs::path& p, fsot::py::NonFiniteLog* log = nullptr) {
  std::ifstream f(p, std::ios::binary);
  if (!f) return std::nullopt;
  std::stringstream ss;
  ss << f.rdbuf();
  return fsot::py::loads(ss.str(), log);
}

int main(int argc, char** argv) {
  std::string hub, out, golden, corrected_out;
  for (int i = 1; i + 1 < argc; i += 2) {
    std::string a = argv[i];
    if (a == "--hub") hub = argv[i + 1];
    else if (a == "--out") out = argv[i + 1];
    else if (a == "--golden") golden = argv[i + 1];
    else if (a == "--corrected-out") corrected_out = argv[i + 1];
  }
  if (hub.empty()) { std::fprintf(stderr, "usage: fsot_ledger_b --hub DIR [--out F] [--golden F]\n"); return 2; }
  const auto t0 = std::chrono::steady_clock::now();
  Engine<RS> eng;
  std::map<std::string, double> S;
  for (auto& d : eng.DOMAINS) S[std::string(d.name)] = static_cast<double>(eng.domain_scalar(d.name));
  const double alpha = static_cast<double>(eng.ALPHA);

  fsot::ledger_b::Literature lit;
  {
    auto a = load(fs::path(hub) / "data" / "literature_uncertainty_anchors.json");
    auto s = load(fs::path(hub) / "data" / "stumped_observables_reference.json");
    lit.load(a ? *a : json::object(), s ? *s : json::object());
  }
  std::vector<fs::path> files;
  for (auto& e : fs::directory_iterator(fs::path(hub) / "data")) {
    const std::string n = e.path().filename().string();
    if (e.is_regular_file() && n.size() > 15 && n.compare(n.size() - 15, 15, "_benchmark.json") == 0) files.push_back(e.path());
  }
  std::sort(files.begin(), files.end(), [](const fs::path& a, const fs::path& b) { return a.filename().string() < b.filename().string(); });

  std::vector<std::string> lines{"#hub_commit\t(cpp)\t" + std::string(AUTHORITY_PIN_PREFIX)};
  long active = 0, green = 0;
  fsot::ledger_b::LedgerBStats tot;
  auto add = [&](const std::string& f, const std::string& k, const std::string& v) { lines.push_back(f + "\t" + k + "\t" + v); };
  std::vector<std::string> corr{"#file\tkey\tvalue  (corrected mode; pin " + std::string(AUTHORITY_PIN_PREFIX) + ")"};
  auto cadd = [&](const std::string& f, const std::string& k, const std::string& v) { corr.push_back(f + "\t" + k + "\t" + v); };
  struct { long files_nonfinite = 0, nan = 0, inf = 0, scalars = 0, stored_over = 0, gate_over = 0, disagree = 0, stored_only = 0,
           green_old = 0, green_new = 0, lb_scalars = 0, genuine = 0, genuine_over = 0, emit_dp = 0, emit_sig = 0; } C;
  for (auto& p : files) {
    const std::string name = p.filename().string();
    fsot::py::NonFiniteLog nf;
    auto doc = load(p, &nf);
    if (nf.total()) {
      ++C.files_nonfinite; C.nan += nf.nan; C.inf += nf.pos_inf + nf.neg_inf;
      std::string ls;
      for (long l : nf.first_lines) ls += (ls.empty() ? "" : ",") + std::to_string(l);
      cadd(name, "nonfinite_tokens", "NaN=" + std::to_string(nf.nan) + " Infinity=" + std::to_string(nf.pos_inf) +
                                         " -Infinity=" + std::to_string(nf.neg_inf) + " first_lines=" + ls);
      std::fprintf(stderr, "note: %s: read %ld non-standard JSON tokens (NaN/Infinity) tolerantly, first at line %ld\n",
                   name.c_str(), nf.total(), nf.first_lines.empty() ? 0L : nf.first_lines[0]);
    }
    if (!doc) { add(name, "load_error", "True"); continue; }
    auto m = fsot::ledger_b::analyze_benchmark(*doc, name, lit);
    if (m.excluded) add(name, "excluded", "True");
    else {
      ++active; green += m.green;
      add(name, "records", fmt(m.records));
      add(name, "pooled_median_error_pct", fmt(m.pooled_headline));
      add(name, "scalar_count", fmt(m.scalar_count));
      add(name, "scalar_median_error_pct", fmt(m.scalar_median));
      add(name, "max_scalar_error_pct", fmt(m.max_scalar));
      add(name, "effective_scalar_median_error_pct", fmt(m.effective_median));
      add(name, "max_effective_scalar_error_pct", fmt(m.max_effective));
      add(name, "worst_effective_scalar_error_pct", fmt(m.worst_effective));
      add(name, "rounding_ghost_scalar_count", fmt(m.rounding_ghost));
      add(name, "catalog_crosswalk_scalar_count", fmt(m.catalog_crosswalk));
      add(name, "strict_scalar_pass", fmt(m.strict_pass));
      add(name, "effective_scalar_pass", fmt(m.effective_pass));
      add(name, "max_gate_scalar_error_pct", fmt(m.max_gate));
      add(name, "tier_scalar_median_error_pct", fmt(m.tier_median));
      add(name, "tier_scalar_pass", fmt(m.tier_pass));
      add(name, "tier_scalar_max_pass", fmt(m.tier_max_pass));
      add(name, "scalar_median_pass", fmt(m.median_pass));
      add(name, "classifier_count", fmt(m.classifier_count));
      add(name, "classifier_correct", fmt(m.classifier_correct));
      add(name, "classifier_accuracy_pct", fmt(m.classifier_accuracy));
      add(name, "classifier_pass", fmt(m.classifier_pass));
      add(name, "official_pooled_median_error_pct", fmt(m.official_pooled));
      add(name, "green_gate_pass", fmt(m.green));
      add(name, "max_scalar_name", fmt(m.max_scalar_name));
      add(name, "max_scalar_property", fmt(m.max_scalar_property));
      add(name, "max_gate_scalar_name", fmt(m.max_gate_name));
      add(name, "worst_effective_scalar_name", fmt(m.worst_effective_name));
    }
    if (!corrected_out.empty() && !m.excluded) {
      auto mc = fsot::ledger_b::analyze_benchmark(*doc, name, lit, /*recompute=*/true);
      C.scalars += mc.scalar_count; C.stored_over += mc.stored_over; C.gate_over += mc.gate_over; C.disagree += mc.disagree;
      C.stored_only += mc.stored_only; C.green_old += m.green; C.green_new += mc.green;
      C.lb_scalars += mc.ledger_b_scalars; C.genuine += mc.genuine_scalars; C.genuine_over += mc.genuine_over;
      if (mc.scalar_count) {
        cadd(name, "scalars", fmt(mc.scalar_count));
        cadd(name, "over_0.5pct_stored_vs_recomputed", fmt(mc.stored_over) + " -> " + fmt(mc.gate_over));
        cadd(name, "stored_error_disagrees_with_fields", fmt(mc.disagree));
        cadd(name, "stored_only_not_recomputable", fmt(mc.stored_only));
        cadd(name, "ledger_b_structural_corrections", fmt(mc.ledger_b_scalars));
        cadd(name, "genuine_predictions", fmt(mc.genuine_scalars));
        cadd(name, "genuine_over_0.5pct", fmt(mc.genuine_over));
        cadd(name, "genuine_median_error_pct", fmt(fsot::py::median(mc.genuine_errs)));
      }
      cadd(name, "green_parity_vs_corrected", fmt(m.green) + " -> " + fmt(mc.green));
    }
    auto st = fsot::ledger_b::rescore(*doc, S, alpha);
    C.emit_dp += st.emit_dp_irreproducible; C.emit_sig += st.emit_sig_irreproducible;
    if (st.lb || st.unrouted) {
      add(name, "lb_records", fmt(st.lb));
      add(name, "lb_unrouted", fmt(st.unrouted));
      add(name, "lb_computed_match", fmt(st.c_match));
      add(name, "lb_scalar_match", fmt(st.s_match));
      add(name, "lb_error_match", fmt(st.e_match));
      add(name, "lb_max_rel_dev", fsot::py::repr(st.max_rel_dev));
    }
    tot.lb += st.lb; tot.unrouted += st.unrouted; tot.c_match += st.c_match; tot.s_match += st.s_match; tot.e_match += st.e_match;
  }
  add("#summary", "active", fmt(active));
  add("#summary", "green", fmt(green));
  add("#summary", "lb", fmt(tot.lb));
  add("#summary", "unrouted", fmt(tot.unrouted));
  add("#summary", "c_match", fmt(tot.c_match));
  add("#summary", "s_match", fmt(tot.s_match));
  add("#summary", "e_match", fmt(tot.e_match));
  const double secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
  std::printf("fsot_ledger_b: %zu files, active=%ld green=%ld ledgerB=%ld unrouted=%ld c_match=%ld s_match=%ld e_match=%ld (%.2f s)\n",
              files.size(), active, green, tot.lb, tot.unrouted, tot.c_match, tot.s_match, tot.e_match, secs);
  if (!out.empty()) { std::ofstream o(out, std::ios::binary); for (auto& l : lines) o << l << "\n"; }
  if (!corrected_out.empty()) {
    cadd("#summary", "files_with_nonfinite_tokens", fmt(C.files_nonfinite) + " (NaN=" + fmt(C.nan) + ", Infinity=" + fmt(C.inf) + ")");
    cadd("#summary", "gated_scalars", fmt(C.scalars));
    cadd("#summary", "over_0.5pct_stored_vs_recomputed", fmt(C.stored_over) + " -> " + fmt(C.gate_over));
    cadd("#summary", "stored_error_disagrees_with_fields", fmt(C.disagree));
    cadd("#summary", "stored_only_not_recomputable", fmt(C.stored_only));
    cadd("#summary", "green_files_parity_vs_corrected", fmt(C.green_old) + " -> " + fmt(C.green_new) + " of " + fmt(active));
    cadd("#summary", "ledger_b_structural_corrections", fmt(C.lb_scalars));
    cadd("#summary", "genuine_predictions", fmt(C.genuine));
    cadd("#summary", "genuine_over_0.5pct", fmt(C.genuine_over));
    cadd("#summary", "lb_emit_irreproducible_round6_vs_sig12", fmt(C.emit_dp) + " -> " + fmt(C.emit_sig) + " of " + fmt(tot.lb));
    std::ofstream o(corrected_out, std::ios::binary);
    for (auto& l : corr) o << l << "\n";
  }
  if (golden.empty()) return 0;
  std::ifstream g(golden);
  if (!g) { std::fprintf(stderr, "cannot open golden %s\n", golden.c_str()); return 2; }
  std::vector<std::string> want;
  for (std::string l; std::getline(g, l);) want.push_back(l);
  long bad = 0;
  const std::size_t n = std::max(want.size(), lines.size());
  for (std::size_t i = 1; i < n; ++i) {
    const std::string a = i < lines.size() ? lines[i] : "<missing>";
    const std::string b = i < want.size() ? want[i] : "<missing>";
    if (a != b) { if (bad < 20) std::fprintf(stderr, "line %zu\n  cpp:    %s\n  python: %s\n", i + 1, a.c_str(), b.c_str()); ++bad; }
  }
  std::printf("golden compare: %zu lines, %ld mismatches\n", want.size(), bad);
  return bad ? 1 : 0;
}
