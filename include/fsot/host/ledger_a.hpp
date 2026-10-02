// fsot/host/ledger_a.hpp — Ledger A closed-form emit and property routing (C++ port of the hub's
// scripts/fsot_ledger_a_lib.py and scripts/fsot_api_predict_lib.py at AUTHORITY_PIN.json
// "ledger_b_data_commit"). Tables and emit expressions are generated (tools/gen_ledger_a_routing.py).
//
// Ledger A: fsot_predict(id) takes no measured value; compare_anchor(id) is the separate compare step.
// Routing:  route_property, formula_mass, predict_observable, make_fsot_record (Ledger B helper, takes m).
// All results are doubles bit-identical to the Python (constants enter as float(mpmath value), i.e. the
// correctly rounded double of the 169-bit engine value).
#pragma once
#include <cmath>
#include <optional>
#include <string>
#include <string_view>
#include <utility>

#include "fsot/engine.hpp"
#include "fsot/host/pyfloat.hpp"

namespace fsot::ledger_a {

struct LedgerASpec {
  const char* id;
  const char* units;
  const char* expression;
  const char* expression_id;
  const char* kind;  // FORECAST | CONSTANT_IDENTITY
  double anchor;
  const char* anchor_source;
  const char* kill_band;
  const char* section;  // closed-form section for _from_fn emitters ("" for translated ones)
  const char* row;
  int custom;           // index into ledger_a_custom, or -1
};
struct ExtensionFold { const char* name; int D_eff; double look; int hits; bool observed; };

#include "fsot/ledger_a.gen.inc"
#include "fsot/routing.gen.inc"

#if defined(FSOT_HAVE_BOOST_MP)
using Ref = mp169;
#elif defined(FSOT_HAVE_FLOAT128)
using Ref = f128;
#else
#error "Ledger A / routing needs a >=113-bit engine so float(value) is reproduced exactly"
#endif

inline const Engine<Ref>& engine() { static const Engine<Ref> e; return e; }

inline const LedgerASpec* find_spec(std::string_view id) {
  for (const auto& s : LEDGER_A) if (id == s.id) return &s;
  return nullptr;
}

struct Prediction { std::string observable_id; double value; const LedgerASpec* spec; std::string pin; };

inline std::optional<Prediction> fsot_predict(std::string_view id) {
  const LedgerASpec* s = find_spec(id);
  if (!s) return std::nullopt;
  const auto& e = engine();
  double v = 0;
  if (s->custom >= 0) {
    v = ledger_a_custom(e, s->custom);
  } else {
    bool found = false;
    for (auto& [name, fn] : e.sections())
      if (std::string_view(name) == s->section)
        for (auto& r : (e.*fn)())
          if (r.name == s->row) { v = static_cast<double>(r.computed); found = true; break; }
    if (!found) return std::nullopt;
  }
  return Prediction{std::string(id), v, s, std::string(AUTHORITY_PIN_PREFIX)};
}
// compare_anchor: |v - m| / max(|m|, 1e-30) * 100
inline std::optional<std::pair<Prediction, double>> compare_anchor(std::string_view id) {
  auto p = fsot_predict(id);
  if (!p) return std::nullopt;
  const double m = p->spec->anchor;
  const double err = std::fabs(p->value - m) / std::max(std::fabs(m), 1e-30) * 100.0;
  return std::make_pair(*p, err);
}

// ---------------- routing ----------------
inline double alpha() { static const double a = static_cast<double>(engine().ALPHA); return a; }

// canonical_domain_scalar: 35 core domains, else the derived extension fold (parent nest).
inline std::optional<double> domain_scalar(std::string_view name) {
  const auto& e = engine();
  for (auto& d : e.DOMAINS) if (d.name == name) return static_cast<double>(e.domain_scalar(name));
  for (const auto& f : EXTENSION_FOLDS)
    if (name == f.name) return static_cast<double>(e.scalar_from_fold(f.D_eff, Ref(f.look), f.hits, f.observed));
  return std::nullopt;
}

inline std::pair<std::string, double> route_property(std::string_view property, std::string_view default_domain) {
  for (const auto& [k, v] : PROPERTY_ROUTING) if (k == property) return {std::string(v), alpha()};
  return {std::string(default_domain), alpha()};
}

inline double err_pct(double c, double m) { return m == 0 ? std::fabs(c - m) * 100.0 : std::fabs(c - m) / std::fabs(m) * 100.0; }

// re.findall(r"([A-Z][a-z]?)(\d*)", formula); unknown element -> None; total > 0 else None
inline std::optional<double> formula_mass(std::string_view f) {
  if (f.empty()) return std::nullopt;
  double total = 0.0;
  std::size_t i = 0;
  while (i < f.size()) {
    if (!(f[i] >= 'A' && f[i] <= 'Z')) { ++i; continue; }
    std::size_t j = i + 1;
    if (j < f.size() && f[j] >= 'a' && f[j] <= 'z') ++j;
    const std::string_view elem = f.substr(i, j - i);
    std::size_t k = j;
    while (k < f.size() && f[k] >= '0' && f[k] <= '9') ++k;
    long long n = 1;
    if (k > j) { n = 0; for (std::size_t q = j; q < k; ++q) n = n * 10 + (f[q] - '0'); }
    const double* mass = nullptr;
    for (const auto& [sym, w] : ATOMIC_MASS) if (sym == elem) mass = &w;
    if (!mass) return std::nullopt;
    total += *mass * static_cast<double>(n);
    i = k;
  }
  if (total > 0) return total;
  return std::nullopt;
}

struct Record { double computed, error_pct; std::string eval_kind, fsot_domain; double fsot_scalar; };

// make_fsot_record(lab, property, name, measured, domain, formula) with factor=None, eval_kind default.
// corrected=false: parity (computed = round(c, 6) or round(c, 4) for |c| >= 1e6; error_pct = round(err, 6)).
// corrected=true:  significant-digit rounding (audit A-04): computed and error_pct = round_sig(x, 12), so the
//                  error recomputed from the emitted computed/measured pair reproduces error_pct.
inline std::optional<Record> make_fsot_record(std::string_view property, double measured, std::string_view domain,
                                              std::string_view formula, bool corrected = false) {
  auto [routed, f] = route_property(property, domain);
  double computed = 0, error = 0;
  std::string dom = routed;
  bool done = false;
  if (property == "molecular_weight" && !formula.empty())
    if (auto cm = formula_mass(formula)) { computed = *cm; error = err_pct(*cm, measured); done = true; }
  if (!done && property == "mol_weight" && !formula.empty())
    if (auto cm = formula_mass(formula)) { computed = *cm; error = err_pct(*cm, measured); dom = "Biochemistry"; done = true; }
  if (!done) {
    auto s = domain_scalar(routed);
    if (!s) return std::nullopt;  // Python raises KeyError
    computed = measured * (1.0 + std::fabs(*s) * f);
    error = err_pct(computed, measured);
  }
  const bool formula_hit = !formula.empty() && (property == "molecular_weight" || property == "mol_weight") &&
                           formula_mass(formula).has_value();
  auto s = domain_scalar(dom);
  if (!s) return std::nullopt;
  Record r;
  if (corrected) {
    r.computed = py::round_sig(computed, 12);
    r.error_pct = py::round_sig(error, 12);
  } else {
    r.computed = std::fabs(computed) < 1e6 ? py::round_nd(computed, 6) : py::round_nd(computed, 4);
    r.error_pct = py::round_nd(error, 6);
  }
  r.eval_kind = formula_hit ? "live_formula" : "fsot_correction";
  r.fsot_domain = dom;
  r.fsot_scalar = py::round_nd(*s, 6);
  return r;
}

}  // namespace fsot::ledger_a
