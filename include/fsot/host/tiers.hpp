// fsot/host/tiers.hpp — evidence tiers for gated records, domains, Ledger A and closed-form rows.
// Definitions (verbatim from the spec; docs/EVIDENCE_TIERS.md):
//   TIER 1 EXPLORATORY       mapping set or changed while looking at the scored data; DEFAULT when dated
//                            evidence is missing.
//   TIER 2 FROZEN-PENDING    mapping hashed and dated in a freeze/prereg file, not yet scored on data that
//                            postdates it.
//   TIER 3 CONFIRMED HELD-OUT  the freeze predates the data or its use.
//   STRUCTURAL/IDENTITY      Ledger B corrections and target-equals-computed rows (separate bucket).
// Operational rules (never promote without dated evidence):
//   * A freeze counts only if it carries an explicit hash, the hash is re-derived from the live mapping by
//     this code (or the freeze is about a different pin and therefore does not cover the live mapping), and
//     git shows the hash in the file. Freeze date = later of the claimed date and the first commit that
//     carries the hash (day granularity).
//   * Data use date = first commit that added the benchmark file (a lower bound for any record in it, so the
//     comparison "freeze < use" can only err toward NOT promoting).
//   * TIER 3 needs use date > freeze date (strictly later calendar day). Equal day or earlier -> TIER 2.
//   * Freezes written by apps/fsot_freeze_domain (this repo's freezes/*.json, "cpp_freezes" in the evidence
//     file) count per row: usable only at the live pin, with the hash in this repo's git, and with EVERY frozen
//     row_sha256 and the selection_sha256 re-derived from the live mapping (host/freeze.hpp). A domain's freeze
//     date is the earliest usable freeze that covers it.
#pragma once
#include <algorithm>
#include <cmath>
#include <map>
#include <regex>
#include <set>
#include <string>
#include <vector>

#include "fsot/engine.hpp"
#include "fsot/host/freeze.hpp"
#include "fsot/host/ledger_b.hpp"
#include "fsot/host/sha256.hpp"

namespace fsot::tiers {
using json = nlohmann::json;
enum class Tier { T1, T2, T3, STRUCT };
inline const char* tier_name(Tier t) {
  switch (t) {
    case Tier::T1: return "TIER1_EXPLORATORY";
    case Tier::T2: return "TIER2_FROZEN_PENDING";
    case Tier::T3: return "TIER3_CONFIRMED_HELD_OUT";
    default: return "STRUCTURAL_IDENTITY";
  }
}

// json.dumps(rows, sort_keys=True, separators=(",", ":")) of the 35-row table, as in the hub's
// scripts/audit_parameter_count.py::_domain_table_sha, from this engine's own DomainConfig values.
template <class R> std::string domain_table_sha256(const Engine<R>& e) {
  std::vector<std::pair<std::string, std::string>> rows;
  for (auto& d : e.DOMAINS) {
    std::string s = "{\"C\":" + py::repr(static_cast<double>(d.C)) + ",\"D_eff\":" + std::to_string(d.D_eff) +
                    ",\"delta_psi\":" + py::repr(static_cast<double>(d.delta_psi)) + ",\"delta_theta\":" +
                    py::repr(static_cast<double>(d.delta_theta)) + ",\"domain\":\"" + std::string(d.name) + "\",\"hits\":" +
                    std::to_string(d.hits) + ",\"observed\":" + (d.observed ? "true" : "false") + "}";
    rows.emplace_back(std::string(d.name), s);
  }
  std::sort(rows.begin(), rows.end());
  std::string blob = "[";
  for (std::size_t i = 0; i < rows.size(); ++i) blob += (i ? "," : "") + rows[i].second;
  blob += "]";
  return host::sha256_hex(blob);
}

inline std::string day(const json& v) { return v.is_string() ? v.get<std::string>().substr(0, 10) : std::string(); }

struct Freeze {
  std::string id, file, date, hash, pin, reason;
  std::vector<std::string> rows;  // cpp freezes: covered domains
  bool usable = false;  // hashed + dated + covers the live mapping
};

struct Counts {
  long t[4] = {0, 0, 0, 0};
  std::map<std::string, long> reasons;
  void add(Tier x, const std::string& why) { ++t[int(x)]; ++reasons[std::string(tier_name(x)) + ": " + why]; }
};

struct Report {
  Freeze domain_freeze, ledger_a_freeze, toe_freeze, prereg_manifest;
  std::vector<Freeze> cpp_freezes;
  std::map<std::string, const Freeze*> dom_freeze;  // domain -> earliest usable freeze covering its row
  std::map<std::string, std::string> file_first_added;  // benchmark file -> YYYY-MM-DD
  Counts records;
  std::map<std::string, Counts> by_domain;
  std::set<std::string> core;
  std::vector<std::string> lines;  // ledger A / closed-form rows

  template <class R> void load(const json& ev, const Engine<R>& e, std::string_view live_pin) {
    for (auto& d : e.DOMAINS) core.insert(std::string(d.name));
    for (const auto& f : ev.at("freezes")) {
      Freeze z;
      z.id = f.at("id").get<std::string>();
      z.file = f.at("file").get<std::string>();
      z.pin = f.value("pin_prefix", json()).is_string() ? f["pin_prefix"].get<std::string>() : "";
      z.hash = f.value("hash", json()).is_string() ? f["hash"].get<std::string>() : "";
      const std::string claimed = day(f.value("claimed_date", json())), git_day = day(f.value("hash_first_commit_date", json()));
      z.date = std::max(claimed, git_day);
      if (z.hash.empty()) {
        z.reason = z.file + " is dated (" + claimed + ") but carries no hash";
      } else if (git_day.empty()) {
        z.reason = z.file + ": hash not found in git history";
      } else if (z.id == "domain_table_freeze") {
        const std::string live = domain_table_sha256(e);
        if (live != z.hash) z.reason = z.file + ": frozen hash " + z.hash.substr(0, 12) + " != live table " + live.substr(0, 12);
        else if (z.pin != live_pin) z.reason = z.file + ": frozen at pin " + z.pin + ", live pin " + std::string(live_pin);
        else { z.usable = true; z.reason = z.file + " sha256 " + z.hash.substr(0, 12) + " re-derived; frozen " + z.date + " (hash in git since " + git_day + ")"; }
      } else {
        z.reason = z.file + ": hashed at pin " + z.pin + ", not the live pin " + std::string(live_pin) + " (does not cover the live mapping)";
      }
      if (z.id == "domain_table_freeze") domain_freeze = z;
      else if (z.id == "ledger_a_freeze") ledger_a_freeze = z;
      else if (z.id == "toe_prereg_freeze") toe_freeze = z;
      else if (z.id == "preregistered_predictions_manifest") prereg_manifest = z;
    }
    if (ev.contains("cpp_freezes"))
      for (const auto& f : ev.at("cpp_freezes")) {
        Freeze z;
        z.id = f.at("id").get<std::string>();
        z.file = f.at("file").get<std::string>();
        z.pin = f.value("pin_prefix", "");
        z.hash = f.value("hash", "");
        const std::string claimed = day(f.value("claimed_date", json())), git_day = day(f.value("hash_first_commit_date", json()));
        z.date = std::max(claimed, git_day);
        std::vector<const freeze::Row*> rows;
        std::string bad;
        for (auto& [name, sha] : f.at("rows").items()) {
          const auto* L = freeze::live_row(name);
          if (!L) { bad = name + " not in the live mapping"; break; }
          if (L->sha != sha.get<std::string>()) { bad = name + " row hash != live row"; break; }
          rows.push_back(L);
        }
        if (z.pin != live_pin) z.reason = z.file + ": frozen at pin " + z.pin + ", live pin " + std::string(live_pin);
        else if (git_day.empty()) z.reason = z.file + ": hash not found in git history";
        else if (!bad.empty()) z.reason = z.file + ": " + bad;
        else if (freeze::table_sha(rows) != z.hash) z.reason = z.file + ": selection_sha256 != live rows";
        else {
          z.usable = true;
          z.reason = z.file + " selection_sha256 " + z.hash.substr(0, 12) + " re-derived (" + std::to_string(rows.size()) +
                     " rows); frozen " + z.date + " (hash in git since " + git_day + ")";
        }
        z.rows.reserve(rows.size());
        for (auto* r : rows) z.rows.push_back(r->domain);
        cpp_freezes.push_back(z);
      }
    if (domain_freeze.usable)
      for (auto& d : core) dom_freeze[d] = &domain_freeze;
    for (auto& z : cpp_freezes)
      if (z.usable)
        for (auto& d : z.rows) {
          auto it = dom_freeze.find(d);
          if (it == dom_freeze.end() || z.date < it->second->date) dom_freeze[d] = &z;
        }
    for (auto& [k, v] : ev.at("benchmark_files").items()) file_first_added[k] = day(v.at("first_added_date"));
  }

  static std::string attributed_domain(const json& r) {
    for (const char* k : {"fsot_domain", "domain"})
      if (auto v = ledger_b::get(r, k); v && v->is_string() && !v->get_ref<const std::string&>().empty()) return v->get<std::string>();
    return "(unattributed)";
  }
  static bool has_pred_id(const json& r) {
    static const std::regex re("^PRED-[0-9]+$");
    for (auto& [k, v] : r.items()) if (v.is_string() && std::regex_match(v.get_ref<const std::string&>(), re)) return true;
    return false;
  }

  // classify one gated scalar record (same selection as the strict gate)
  void record(const json& r, const std::string& file, const std::map<std::string, double>& S) {
    const std::string dom = attributed_domain(r);
    auto put = [&](Tier t, const std::string& why) { records.add(t, why); by_domain[dom].add(t, why); };
    const std::string ek = ledger_b::str_or_empty(r, "eval_kind");
    if (ek == "fsot_prediction" || ek == "fsot_correction") return put(Tier::STRUCT, "Ledger B correction c = m(1+|S|ALPHA)");
    {
      auto c = ledger_b::get(r, "computed"), m = ledger_b::get(r, "measured");
      if (c && m && c->is_number() && m->is_number() && c->get<double>() == m->get<double>())
        return put(Tier::STRUCT, "target equals computed");
    }
    // covered by a freeze only if the record was scored with the frozen row (fsot_scalar == round(live S, 6))
    if (auto fz = dom_freeze.find(dom); fz != dom_freeze.end()) {
      const Freeze& z = *fz->second;
      auto fs = ledger_b::get(r, "fsot_scalar");
      std::optional<double> f, live;
      if (!ledger_b::is_none(fs)) f = ledger_b::to_float(*fs);
      if (auto it = S.find(dom); it != S.end()) live = it->second;
      else if (const auto* L = freeze::live_row(dom)) live = L->scalar;
      if (f && live && *f == py::round_nd(*live, 6)) {
        const std::string use = file_first_added.count(file) ? file_first_added.at(file) : "";
        const std::string what = &z == &domain_freeze ? std::string("domain-table freeze ") : z.id + " ";
        if (use.empty()) return put(Tier::T1, "frozen domain table, but no dated first use of " + file);
        if (use > z.date) return put(Tier::T3, what + z.date + " predates first use " + use);
        if (&z == &domain_freeze) return put(Tier::T2, "scored with frozen domain table; data first used " + use.substr(0, 7) + " <= freeze " + z.date);
        return put(Tier::T2, "scored with row frozen in " + z.id + "; data first used " + use.substr(0, 7) + " <= freeze " + z.date);
      }
    }
    if (has_pred_id(r)) return put(Tier::T1, "PRED id: " + prereg_manifest.reason);
    return put(Tier::T1, "no hashed+dated freeze covers this record's mapping");
  }

  Tier domain_tier(const std::string& d, std::string& why) const {
    auto fz = dom_freeze.find(d);
    if (fz == dom_freeze.end()) {
      if (core.count(d)) { why = domain_freeze.reason; return Tier::T1; }
      why = "not in a hashed freeze (domain_table_freeze covers the 35 core domains; no usable freezes/*.json row)";
      return Tier::T1;
    }
    const Freeze& z = *fz->second;
    auto it = by_domain.find(d);
    if (it != by_domain.end() && it->second.t[int(Tier::T3)] > 0) { why = "frozen " + (&z == &domain_freeze ? std::string("table") : z.id) + "; scored on data first used after " + z.date; return Tier::T3; }
    why = "row hashed in " + z.reason + "; no non-structural record scored with it on data first used after the freeze";
    return Tier::T2;
  }
};

}  // namespace fsot::tiers
