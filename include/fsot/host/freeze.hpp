// fsot/host/freeze.hpp — dated SHA-256 freezes of the live domain mapping (core DomainConfig table and the
// derived extension folds), shared by apps/fsot_freeze_domain.cpp (writer/verifier) and host/tiers.hpp
// (which only lets a freeze count for TIER 2/3 when every frozen row hash is re-derived from the live mapping).
//
// Row JSON = json.dumps(row, sort_keys=True, separators=(",", ":")) with Python float repr, exactly the hub's
// scripts/audit_parameter_count.py::_domain_table_sha row scheme:
//   core row      {"C","D_eff","delta_psi","delta_theta","domain","hits","observed"}
//   extension row {"D_eff","delta_psi","domain","hits","kind":"extension_fold","observed"}  (delta_psi = look;
//                 extension folds carry no C/delta_theta, see routing.gen.inc / scalar_from_fold)
//   closed_form   {"computed","formula","kind":"closed_form","name","section"}   key "cf:<section>/<name>"
//   ledger_a      {"expression","expression_id","id","kind":"ledger_a","units","value"}   key "la:<id>"
//                 (these two are nlohmann compact dumps: sorted keys, UTF-8, Python repr floats as strings so
//                 the hash is exact; json.dumps(..., sort_keys=True, separators=(",",":"), ensure_ascii=False))
// Table hash = sha256("[" + rows sorted by domain name joined with "," + "]"). For the 35 core rows this is
// the hub's domain_table_sha256 (data/domain_table_freeze.json).
#pragma once
#include <algorithm>
#include <set>
#include <string>
#include <vector>

#include <nlohmann/json.hpp>

#include "fsot/engine.hpp"
#include "fsot/host/ledger_a.hpp"
#include "fsot/host/pyfloat.hpp"
#include "fsot/host/sha256.hpp"

namespace fsot::freeze {

// hub scripts/audit_parameter_count.py K_LINE_NEEDLE (the K definition line in the authority)
inline constexpr std::string_view K_LINE_NEEDLE = "K        = PHI * (GAMMA / E) * sqrt(2) / ln(PI) * (1 - 1 / PI**4)";

struct Row {
  std::string domain, kind, json, sha;
  double scalar = 0;  // live domain scalar (float of the 169-bit value); informative, not hashed
};

template <class R> std::string core_row_json(const DomainConfig<R>& d) {
  return "{\"C\":" + py::repr(static_cast<double>(d.C)) + ",\"D_eff\":" + std::to_string(d.D_eff) +
         ",\"delta_psi\":" + py::repr(static_cast<double>(d.delta_psi)) + ",\"delta_theta\":" +
         py::repr(static_cast<double>(d.delta_theta)) + ",\"domain\":\"" + std::string(d.name) + "\",\"hits\":" +
         std::to_string(d.hits) + ",\"observed\":" + (d.observed ? "true" : "false") + "}";
}
inline std::string ext_row_json(const ledger_a::ExtensionFold& f) {
  return "{\"D_eff\":" + std::to_string(f.D_eff) + ",\"delta_psi\":" + py::repr(f.look) + ",\"domain\":\"" + f.name +
         "\",\"hits\":" + std::to_string(f.hits) + ",\"kind\":\"extension_fold\",\"observed\":" + (f.observed ? "true" : "false") + "}";
}

// Live rows: 35 core domains, then extension folds that routing can actually reach (a fold whose name is a
// core domain, or repeats an earlier fold, is shadowed in ledger_a::domain_scalar and therefore not frozen).
inline const std::vector<Row>& live_rows() {
  static const std::vector<Row> rows = [] {
    std::vector<Row> v;
    std::set<std::string> seen;
    const auto& e = ledger_a::engine();
    for (auto& d : e.DOMAINS) {
      Row r{std::string(d.name), "core", core_row_json(d), "", static_cast<double>(e.domain_scalar(d.name))};
      r.sha = host::sha256_hex(r.json);
      seen.insert(r.domain);
      v.push_back(r);
    }
    for (const auto& f : ledger_a::EXTENSION_FOLDS) {
      if (!seen.insert(f.name).second) continue;
      Row r{f.name, "extension_fold", ext_row_json(f), "",
            static_cast<double>(e.scalar_from_fold(f.D_eff, ledger_a::Ref(f.look), f.hits, f.observed))};
      r.sha = host::sha256_hex(r.json);
      v.push_back(r);
    }
    // closed-form section rows (formula text + value), then Ledger A forecast expressions
    for (auto& [sec, fn] : e.sections())
      for (auto& r : (e.*fn)()) {
        const std::string key = "cf:" + std::string(sec) + "/" + r.name;
        if (!seen.insert(key).second) continue;
        nlohmann::json j = {{"computed", py::repr(static_cast<double>(r.computed))}, {"formula", r.formula},
                            {"kind", "closed_form"}, {"name", r.name}, {"section", sec}};
        Row x{key, "closed_form", j.dump(), "", static_cast<double>(r.computed)};
        x.sha = host::sha256_hex(x.json);
        v.push_back(x);
      }
    for (const auto& sp : ledger_a::LEDGER_A) {
      auto pr = ledger_a::fsot_predict(sp.id);
      if (!pr) continue;
      const std::string key = std::string("la:") + sp.id;
      if (!seen.insert(key).second) continue;
      nlohmann::json j = {{"expression", sp.expression}, {"expression_id", sp.expression_id}, {"id", sp.id},
                          {"kind", "ledger_a"}, {"units", sp.units}, {"value", py::repr(pr->value)}};
      Row x{key, "ledger_a", j.dump(), "", pr->value};
      x.sha = host::sha256_hex(x.json);
      v.push_back(x);
    }
    return v;
  }();
  return rows;
}
inline const Row* live_row(const std::string& name) {
  for (auto& r : live_rows()) if (r.domain == name) return &r;
  return nullptr;
}
inline std::string table_sha(std::vector<const Row*> rows) {
  std::sort(rows.begin(), rows.end(), [](const Row* a, const Row* b) { return a->domain < b->domain; });
  std::string blob = "[";
  for (std::size_t i = 0; i < rows.size(); ++i) blob += (i ? "," : "") + rows[i]->json;
  return host::sha256_hex(blob + "]");
}
inline std::string core_table_sha() {
  std::vector<const Row*> c;
  for (auto& r : live_rows()) if (r.kind == "core") c.push_back(&r);
  return table_sha(c);
}

}  // namespace fsot::freeze
