// fsot/host/ledger_b.hpp — C++ port of the FSOT-2.1-Lean benchmark margin audit and Ledger B re-scorer.
//
// Ports, statement by statement (hub commit pinned in AUTHORITY_PIN.json "ledger_b_data_commit"):
//   scripts/benchmark_margin_lib.py       classify_record, classifier_metrics, scalar_metrics, analyze_benchmark
//   scripts/scientific_measurement_lib.py literature_aware_error_pct and helpers
//   scripts/literature_uncertainty_lib.py is_contested_record, resolve_reference_uncertainty_pct
//   scripts/fsot_precision_constants.py   gate values
//   scripts/fsot_api_predict_lib.py       fsot_correct  (c = m (1 + |S| ALPHA), stored round(c, 6|4))
// Host-only (heap, std::string, nlohmann::json); the freestanding core never includes this file.
// Python exceptions that the original catches are modelled as std::nullopt.
#pragma once
#include <array>
#include <cmath>
#include <initializer_list>
#include <map>
#include <optional>
#include <set>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>

#include "fsot/host/pyjson.hpp"

namespace fsot::ledger_b {
using json = nlohmann::json;
using namespace fsot::py;

// fsot_precision_constants.py
inline constexpr double MAX_MEDIAN_ERROR_PCT = 0.5;
inline constexpr double MAX_SCALAR_ERROR_PCT = 0.5;
inline constexpr double TIER_SCALAR_MAX_ERROR_PCT = 0.05;
inline constexpr double MIN_CLASSIFIER_ACCURACY_PCT = 99.5;
inline const std::set<std::string> AUDIT_EXCLUDED_BENCHMARKS = {"structure_calibration_benchmark.json"};

inline const std::set<std::string> STRUCTURAL_EVAL_KINDS = {
    "catalog_consistency", "public_catalog_anchor", "crosswalk_bridge", "scalar_bridge", "structural",
    "meta_inventory", "inventory", "rollup", "prereg_scaffold", "gap_detection", "classifier_match",
    "panel_relay", "cross_panel_relay", "stability_index", "skipped", "jpl_physical", "jpl_orbital",
    "jpl_kepler", "reference_anchor", "jpl_elements", "panel_anchor", "contested_observable",
    "cross_domain_bridge", "bridge_observable", "fsot_compute", "certificate_gate", "fic_valve",
    "resonance_crosswalk", "summary_crosscheck", "artifact_present", "anomaly_anchor", "literature_monitor",
    "panel_bridge", "reference_gate", "count_anchor", "time_anchor", "time_relay", "timing_gate",
    "crosswalk_relay", "wave1_crosscheck", "fi_hero_relay", "hero_relay", "channel_rollup", "h0_anchor",
    "h0_gate", "dark_sector_anchor", "fluid_spacetime_bridge", "fluid_spacetime_relay",
    "preregistered_certificate", "simbad_anchor", "gaia_anchor", "gaia_literature_anchor", "mp_anchor",
    "pubchem_live_anchor", "gwosc_live_anchor", "gwosc_public_anchor", "mast_anchor", "wds_live_anchor",
    "wds_anchor", "bundled_anchor", "bundled_only_anchor", "catalog_anchor", "dataset_anchor", "ingest_meta",
    "domain_panel_bridge", "category_panel_bridge", "pharmacology_bridge", "uniprot_bridge",
    "culinary_arts_bridge", "maillard_chemistry_bridge", "food_microbiology_bridge", "simbad_bridge",
    "tier60_bridge", "tier62_bridge", "tier68_bridge", "tier53_bridge", "ingest_consistency",
    "astrometry_consistency", "formula_mass_relay", "ingest_relay", "literature_fit_band"};
inline const std::set<std::string> STRUCTURAL_PROPERTIES = {  // lower-cased, as compared by the original
    "detected_hole_count", "domain_benchmark_records", "positive_s_verse_count", "codon_weight_count",
    "gauntlet_pass_rate_pct", "domain_pooled_median", "child_domain_pooled_median",
    "strict_empirical_max_error_pct", "mean_codon_stability", "codon_unit_coverage", "pooled_igem_median",
    "schema_pass_rate_pct", "stabilization_margin", "kepler_mass_closure", "prediction_gap_fill",
    "info_uplift_fraction", "vib_avg_s", "archetype_mean_s", "discriminant_pass", "codon_stability",
    "mt_genome_bp"};
inline const std::set<std::string> CLASSIFIER_PROPERTIES = {
    "nebula_lensing_coupling", "nebula_framework_fit", "fic_fertile_classifier", "storm_classifier",
    "classifier_match", "kp_storm_classifier", "freezing_month_classifier", "dst_storm_classifier",
    "goes_storm_classifier", "shallow_depth_classifier", "mass_decline_classifier"};
inline const std::array<std::pair<const char*, const char*>, 12> CLASSIFIER_FIELD_PAIRS = {{
    {"computed", "measured"}, {"computed_coupled", "measured_coupled"}, {"computed_freezing", "measured_freezing"},
    {"computed_quiet", "measured_quiet"}, {"computed_repeater", "measured_repeater"},
    {"computed_shallow", "measured_shallow"}, {"computed_loss", "measured_loss"},
    {"computed_decline", "measured_decline"}, {"computed_crustal", "measured_crustal"},
    {"computed_quality", "measured_quality"}, {"computed_mt", "measured_mt"}, {"computed_margin", "measured_margin"}}};
inline const std::set<std::string> CATALOG_SPEC_PROPERTIES = {
    "symmetric_key_bits", "block_cipher_rounds", "asymmetric_modulus_bits", "public_exponent",
    "pqc_security_level", "hash_output_bits", "key_schedule_words", "iv_bits", "tag_bits", "protocol_version",
    "curve_order_bits", "ecc_key_bits", "collision_work_exponent", "pqc_signature_level"};
inline const std::set<std::string> GAP_FILL_STRUCTURAL_PROPERTIES = {
    "panel_dispersion", "decision_observables", "maillard_roast", "hvac_thermal", "envelope_climate",
    "kepler_third_law_ratio", "fi_proxy_hero_certified"};

inline std::optional<std::pair<const char*, const char*>> classifier_field_pair(const json& r) {
  for (auto& p : CLASSIFIER_FIELD_PAIRS)
    if (r.contains(p.first) && r.contains(p.second)) return p;
  return std::nullopt;
}

inline std::string classify_record(const json& r, std::string_view file_name = "") {
  const std::string eval_kind = lower_ascii(str_or_empty(r, "eval_kind"));
  if (eval_kind == "fsot_correction") return "structural";
  if (auto e = get(r, "record_kind"); e && e->is_string()) {
    const auto& s = e->get_ref<const std::string&>();
    if (s == "scalar" || s == "classifier" || s == "structural") return s;
  }
  if (!file_name.empty() && contains(lower_ascii(std::string(file_name)), "gap_fill")) return "structural";
  const std::string prop = lower_ascii(str_or_empty(r, "property"));
  if (STRUCTURAL_EVAL_KINDS.count(eval_kind)) return "structural";
  if (eval_kind == "w0_live" || eval_kind == "wa_preregistered" || eval_kind == "h0_live" ||
      eval_kind == "preregistered_falsifiable" || eval_kind == "preregistered_certificate")
    return "structural";
  if (STRUCTURAL_PROPERTIES.count(prop)) return "structural";
  if (starts_with(prop, "section_median_")) return "structural";
  if (GAP_FILL_STRUCTURAL_PROPERTIES.count(prop)) return "structural";
  if (CATALOG_SPEC_PROPERTIES.count(prop)) return "structural";
  if (prop == "pooled_median" || prop == "hybrid_fi" || prop == "fi_proxy_hero_certification" || prop == "headline_median")
    return "structural";
  if (ends_with(prop, "_panel_cv_pct") || ends_with(prop, "_yoy_growth_pct") || contains(prop, "rollup")) return "structural";
  if (ends_with(prop, "_pct") && contains(prop, "panel")) return "structural";
  if (prop == "median_error_pct" || prop == "pooled_median_error_pct" || prop == "headline_median_error_pct") return "structural";
  if (eval_kind == "gap_fill_channel" || eval_kind == "tier_gap_fill" || contains(str_or_empty(r, "lab"), "gap_fill"))
    return "structural";
  if (classifier_field_pair(r) && (CLASSIFIER_PROPERTIES.count(prop) || ends_with(prop, "_classifier") ||
                                   contains(prop, "classifier") || eval_kind == "classifier_match"))
    return "classifier";
  if (contains(prop, "gate") || prop == "exit_code_zero" || ends_with(prop, "_zero") || ends_with(prop, "_resolved"))
    return "structural";
  if (ends_with(prop, "_count") || ends_with(prop, "_records")) return "structural";
  if (auto m = get(r, "measured"); m && eq_zero(*m) && ends_with(prop, "_median") && eval_kind != "scalar_prediction")
    return "structural";
  return "scalar";
}

// ---------------- literature_uncertainty_lib ----------------
struct Literature {
  std::unordered_map<std::string, json> anchors;  // data/literature_uncertainty_anchors.json ["anchors"]
  std::unordered_map<std::string, json> stumped;  // data/stumped_observables_reference.json by property / id

  void load(const json& anchors_doc, const json& stumped_doc) {
    if (auto a = get(anchors_doc, "anchors"); a && truthy(*a))
      for (auto it = a->begin(); it != a->end(); ++it) anchors[it.key()] = it.value();
    if (auto obs = get(stumped_doc, "observables"); obs && truthy(*obs))
      for (const auto& row : *obs) {
        const std::string prop = str_or_empty(row, "property");
        if (!prop.empty()) stumped[prop] = row;
        const std::string oid = str_or_empty(row, "id");
        if (!oid.empty()) stumped[oid] = row;
      }
  }
  const json* anchor(const std::string& k) const { auto it = anchors.find(k); return it == anchors.end() ? nullptr : &it->second; }
  const json* stump(const std::string& k) const { auto it = stumped.find(k); return it == stumped.end() ? nullptr : &it->second; }
};

inline bool is_contested_record(const json& r) {
  static const std::set<std::string> kinds = {"contested_observable", "w0_live", "wa_live", "wa_preregistered",
                                              "preregistered_falsifiable", "h0_live"};
  static const std::set<std::string> props = {"hubble_constant", "sector_h0_overlay", "frb_p34_periodicity",
                                              "host_h0_median", "host_h0_weighted_mean", "dark_energy_eos",
                                              "dark_energy_eos_evolution", "reionization_optical_depth"};
  static const std::set<std::string> classes = {"tension_sector_prediction", "preregistered_falsifiable",
                                                "literature_monitor", "bao_sector_prediction", "cmb_sector_prediction"};
  if (kinds.count(lower_ascii(str_or_empty(r, "eval_kind")))) return true;
  const std::string prop = str_or_empty(r, "property");
  if (props.count(prop)) return true;
  if (classes.count(str_or_empty(r, "comparison_class"))) return true;
  if (auto s = get(r, "sector"); s && truthy(*s) && prop == "hubble_constant") return true;
  return false;
}

// text.lower() then δ/Δ/γ → ascii. Lower-casing is ASCII plus Greek Δ/Γ, the only non-ASCII case
// mappings that can change the token test below (documented approximation of str.lower()).
inline std::string normalize_biochem_text(const std::string& text) {
  std::string p;
  for (std::size_t i = 0; i < text.size(); ++i) {
    unsigned char c = (unsigned char)text[i];
    if (c == 0xCE && i + 1 < text.size() && ((unsigned char)text[i + 1] == 0x94 || (unsigned char)text[i + 1] == 0x93)) {
      p += char(0xCE); p += char((unsigned char)text[i + 1] + 0x20); ++i; continue;  // Δ→δ, Γ→γ
    }
    p += (c >= 'A' && c <= 'Z') ? char(c - 'A' + 'a') : char(c);
  }
  auto repl = [](std::string& s, const std::string& a, const std::string& b) {
    for (std::size_t pos = 0; (pos = s.find(a, pos)) != std::string::npos; pos += b.size()) s.replace(pos, a.size(), b);
  };
  repl(p, "\xCE\xB4", "delta");
  repl(p, "\xCE\xB3", "gamma");
  repl(p, "delta g", "deltag");
  repl(p, "delta_g", "deltag");
  return p;
}
inline bool biochem_property(std::initializer_list<std::string> fields) {
  static const char* tokens[] = {"pka", "pkd", "pki", "deltag", "km", "kcat", "ki", "ic50", "ec50", "kd",
                                 "stacking", "activation_ea", "youngs_modulus"};
  for (const auto& f : fields) {
    if (f.empty()) continue;
    const std::string p = normalize_biochem_text(f);
    for (auto t : tokens) if (contains(p, t)) return true;
  }
  return false;
}

inline std::string stumped_canonical_property(const json& r, const Literature& lit) {
  const std::string prop = str_or_empty(r, "property");
  for (const std::string& key : {prop, str_or_empty(r, "name"), str_or_empty(r, "id")}) {
    if (key.empty()) continue;
    const json* s = lit.stump(key);
    if (s && truthy(*s)) if (auto p = get(*s, "property"); p && truthy(*p)) return str(*p);
  }
  return prop;
}

// Returns value or nullopt (None). Sets `raised` when Python would raise TypeError/ValueError out of it.
inline std::optional<double> resolve_reference_uncertainty_pct(const json& row, const Literature& lit, bool& raised) {
  if (auto v = get(row, "reference_uncertainty_pct"); !is_none(v)) if (auto f = to_float(*v)) return *f;
  if (auto sci = get(row, "scientific_measurement"); sci && truthy(*sci) && sci->is_object())
    if (auto v = get(*sci, "reference_uncertainty_pct"); !is_none(v)) if (auto f = to_float(*v)) return *f;
  if (auto v = get(row, "measured_uncertainty_rel"); !is_none(v)) if (auto f = to_float(*v)) return *f * 100.0;
  const json* measured = get(row, "measured");
  if (auto v = get(row, "measured_uncertainty"); !is_none(v) && !is_none(measured) && !eq_zero(*measured)) {
    auto a = to_float(*v);
    auto b = to_float(*measured);
    if (a && b && *b != 0.0) return std::fabs(*a / *b) * 100.0;
  }
  if (!is_none(get(row, "sigma")) && !is_none(get(row, "sigma_distance"))) {
    auto e = get(row, "error_pct");
    if (!e || !truthy(*e)) return 0.0;
    if (auto f = to_float(*e)) return *f;
  }
  static const std::map<std::string, std::string> PROPERTY_ANCHOR_ALIASES = {
      {"H0_planck_km_s_Mpc", "hubble_constant"}, {"h0_planck_km_s_mpc", "hubble_constant"},
      {"w0_bao_readout", "w0_constraint"}, {"wa_bao_readout", "dark_energy_eos"},
      {"w0_cmb_readout", "w0_constraint"}, {"wa_cmb_readout", "dark_energy_eos"}};
  static const std::map<std::string, std::string> RECORD_NAME_ANCHOR_ALIASES = {
      {"Mean_dependency_length_EN", "mean_dependency_length"}, {"FRB20200929C", "frb_p34_periodicity"}};
  const std::string prop = stumped_canonical_property(row, lit);
  const json* anchor = lit.anchor(prop);
  if (!anchor) {
    auto it = PROPERTY_ANCHOR_ALIASES.find(prop);
    anchor = lit.anchor(it == PROPERTY_ANCHOR_ALIASES.end() ? std::string() : it->second);
  }
  if (!anchor && biochem_property({prop, str_or_empty(row, "name"), str_or_empty(row, "display_name"),
                                   str_or_empty(row, "section_display_name")}))
    return 0.2;  // BIOCHEM_UNCERTAINTY_PCT
  if (!anchor && (contains(lower_ascii(str_or_empty(row, "lab")), "neuroeconomics") || ends_with(prop, "_alpha") ||
                  contains(prop, "transfer_pct")))
    return 0.15;  // BEHAVIORAL_UNCERTAINTY_PCT
  if (!anchor) {
    auto it = RECORD_NAME_ANCHOR_ALIASES.find(str_or_empty(row, "name"));
    if (it != RECORD_NAME_ANCHOR_ALIASES.end()) anchor = lit.anchor(it->second);
  }
  if (anchor && truthy(*anchor))
    if (auto v = get(*anchor, "measured_uncertainty_pct"); !is_none(v)) {
      if (auto f = to_float(*v)) return *f;
      raised = true; return std::nullopt;
    }
  const json* st = lit.stump(prop);
  if (st && truthy(*st))
    if (auto v = get(*st, "measured_uncertainty_pct"); !is_none(v)) {
      if (auto f = to_float(*v)) return *f;
      raised = true; return std::nullopt;
    }
  return std::nullopt;
}

// ---------------- scientific_measurement_lib ----------------
inline double relative_error_pct(double c, double m) {
  if (m == 0) return c == 0 ? 0.0 : 100.0;
  return std::fabs(c - m) / std::fabs(m) * 100.0;
}
inline int decimals_from_float(double v) {
  if (v == 0) return 0;
  const double tol = std::max(1e-12, std::fabs(v) * 1e-12);
  for (int d = 6; d >= 0; --d)
    if (std::fabs(v - round_nd(v, d)) <= tol) return d;
  return 6;
}
inline int display_precision_decimals(double measured, const json& row) {
  if (auto ex = get(row, "measured_display_decimals"); !is_none(ex))
    if (auto i = to_int(*ex)) return int(std::max<long long>(0, *i));
  if (auto t = get(row, "target_value"); !is_none(t)) {
    std::string text = str(*t);
    auto ws = [](char c) { return c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\f' || c == '\v'; };
    while (!text.empty() && ws(text.front())) text.erase(0, 1);
    while (!text.empty() && ws(text.back())) text.pop_back();
    auto dot = text.find('.');
    if (dot == std::string::npos) return 0;
    std::string frac = text.substr(dot + 1);
    while (!frac.empty() && frac.back() == '0') frac.pop_back();
    int n = 0;
    for (unsigned char c : frac) if ((c & 0xC0) != 0x80) ++n;  // len() counts code points
    return n;
  }
  return decimals_from_float(measured);
}

struct Aware {
  double effective;
  std::string kind;
  bool within_display = false, within_literature = false;
};

inline std::optional<Aware> literature_aware_error_pct(double computed, double measured, const json& row, const Literature& lit) {
  double raw = relative_error_pct(computed, measured);
  const double delta = computed - measured;
  const std::string ek = lower_ascii(str_or_empty(row, "eval_kind"));
  const std::string prop = str_or_empty(row, "property");
  if ((!is_none(get(row, "expected_holes")) && !is_none(get(row, "match"))) || prop == "adversarial_hole_detected") {
    auto mt = get(row, "match");
    bool matched = mt && truthy(*mt);
    return Aware{matched ? 0.0 : 100.0, "adversarial_match", matched, matched};
  }
  static const std::set<std::string> lm = {"anomaly_anchor", "literature_monitor", "panel_bridge", "reference_gate", "count_anchor"};
  static const std::set<std::string> sg = {"certificate_gate", "h0_gate", "crosswalk_bridge", "dark_sector_anchor"};
  if (lm.count(ek) || str_or_empty(row, "comparison_class") == "literature_monitor" || sg.count(ek) ||
      ends_with(prop, "_ready") || ends_with(prop, "_gate")) {
    bool w = raw <= MAX_SCALAR_ERROR_PCT;
    return Aware{raw, "structural_gate", w, w};
  }
  {
    auto lab = get(row, "lab");
    auto sp = get(row, "species_property");
    if ((lab && lab->is_string() && lab->get_ref<const std::string&>() == "materials_species_bridge") ||
        (sp && truthy(*sp)) || prop == "biology_strict_operon_replication" || prop == "coding_bp_sum_bridge")
      return Aware{raw, "catalog_crosswalk", false, false};
  }
  if (ek == "simulation_aggregate")
    if (auto s = get(row, "error_pct"); !is_none(s)) if (auto f = to_float(*s)) raw = *f;
  if (ek == "preregistered_falsifiable" || ek == "wa_preregistered") {
    auto sd = get(row, "sigma_distance");
    if (!is_none(get(row, "sigma")) && !is_none(sd))
      if (auto z = to_float(*sd)) return Aware{std::min(*z, 3.0) * 0.05, "preregistered_falsifiable", false, *z <= 2.0};
  }
  if (auto sd = get(row, "sigma_distance"); !is_none(sd) && !is_none(get(row, "sigma"))) {
    double sigma_eff = raw;
    if (auto e = get(row, "error_pct"); e && truthy(*e)) { if (auto f = to_float(*e)) sigma_eff = *f; }
    auto z = to_float(*sd);
    if (!z) return std::nullopt;  // float(row["sigma_distance"]) raises -> caller's except
    return Aware{sigma_eff, "sigma_distance", false, *z <= 2.0};
  }
  bool raised = false;
  std::optional<double> unc = resolve_reference_uncertainty_pct(row, lit, raised);
  if (raised) return std::nullopt;
  if (!unc) if (auto v = get(row, "reference_uncertainty_pct"); !is_none(v)) unc = to_float(*v);
  if (!unc) if (auto v = get(row, "measured_uncertainty_rel"); !is_none(v)) if (auto f = to_float(*v)) unc = *f * 100.0;
  if (!unc) if (auto v = get(row, "measured_uncertainty"); !is_none(v) && measured != 0) if (auto f = to_float(*v)) unc = std::fabs(*f / measured) * 100.0;
  if (unc && *unc > 0) {
    bool within = raw <= *unc;
    return Aware{within ? 0.0 : raw, "uncertainty_band", false, within};
  }
  const int dec = display_precision_decimals(measured, row);
  const double band = dec <= 0 ? 0.5 : 0.5 * std::pow(10.0, -dec);
  const bool within = std::fabs(delta) <= band + std::max(1e-12, std::fabs(measured) * 1e-12);
  return Aware{within ? 0.0 : raw, "display_precision", within, within};
}

// ---------------- benchmark_margin_lib ----------------
struct Margin {
  bool excluded = false;
  json records;
  std::optional<double> pooled_headline;
  long scalar_count = 0;
  std::optional<double> scalar_median, max_scalar, effective_median, max_effective, worst_effective, max_gate, tier_median;
  long rounding_ghost = 0, catalog_crosswalk = 0;
  bool strict_pass = true, effective_pass = true, tier_pass = true, tier_max_pass = true, median_pass = true;
  long classifier_count = 0, classifier_correct = 0;
  std::optional<double> classifier_accuracy;
  bool classifier_pass = true;
  std::optional<double> official_pooled;
  bool green = false;
  json max_scalar_name, max_scalar_property, max_gate_name, worst_effective_name;
};

inline const json& material_records(const json& doc) {
  static const json empty_list = json::array();
  if (auto m = get(doc, "material_records"); m && truthy(*m)) return *m;
  if (auto r = get(doc, "records"); r && truthy(*r)) return *r;
  return empty_list;
}

inline Margin analyze_benchmark(const json& doc, const std::string& file_name, const Literature& lit) {
  Margin out;
  if (AUDIT_EXCLUDED_BENCHMARKS.count(file_name)) { out.excluded = true; return out; }
  const json& mat = material_records(doc);
  for (const char* k : {"pooled_median_error_pct", "median_error_pct", "headline_median_error_pct"})
    if (auto v = get(doc, k); !is_none(v)) { out.pooled_headline = to_float(*v); break; }

  // scalar_metrics
  std::vector<double> errs, eff_errs, gate_errs;
  double max_err = 0, max_gate = 0, max_eff_any = 0;
  const json *max_row = nullptr, *max_gate_row = nullptr, *max_eff_row = nullptr;
  auto aware_for = [&](const json& r, double ef) -> Aware {
    auto c = get(r, "computed");
    auto m = get(r, "measured");
    if (!is_none(c) && !is_none(m)) {
      auto cf = to_float(*c), mf = to_float(*m);
      if (cf && mf) if (auto a = literature_aware_error_pct(*cf, *mf, r, lit)) return *a;
    }
    return Aware{ef, "raw"};
  };
  for (const auto& r : mat) {
    if (classify_record(r, file_name) != "scalar") continue;
    auto e = get(r, "error_pct");
    if (is_none(e)) continue;
    auto efo = to_float(*e);
    if (!efo) continue;
    const double ef = *efo;
    errs.push_back(ef);
    if (ef > max_err) { max_err = ef; max_row = &r; }
    Aware aw = aware_for(r, ef);
    const double eff = aw.effective;
    eff_errs.push_back(eff);
    const double gate = is_contested_record(r) ? eff : ef;
    gate_errs.push_back(gate);
    if (gate > max_gate) { max_gate = gate; max_gate_row = &r; }
    if (eff > max_eff_any) { max_eff_any = eff; max_eff_row = &r; }
    if (aw.kind == "catalog_crosswalk") ++out.catalog_crosswalk;
    else if ((aw.within_display || aw.within_literature) && ef > MAX_SCALAR_ERROR_PCT) ++out.rounding_ghost;
  }
  double max_raw_eff = max_err;
  if (max_row) {
    auto c = get(*max_row, "computed");
    auto m = get(*max_row, "measured");
    if (!is_none(c) && !is_none(m)) {
      auto cf = to_float(*c), mf = to_float(*m);
      std::optional<Aware> a;
      if (cf && mf) a = literature_aware_error_pct(*cf, *mf, *max_row, lit);
      max_raw_eff = (a && a->effective != 0.0) ? a->effective : max_err;  // float(eff or max_err)
    }
  }
  auto field = [](const json* r, const char* k) -> json { if (!r) return nullptr; auto v = get(*r, k); return v ? *v : json(nullptr); };
  out.scalar_count = long(errs.size());
  out.scalar_median = median(errs);
  out.effective_median = median(eff_errs);
  auto gate_med = median(gate_errs);
  if (!errs.empty()) out.max_scalar = max_err;
  if (!eff_errs.empty()) { out.max_effective = max_raw_eff; out.worst_effective = max_eff_any; }
  if (!gate_errs.empty()) out.max_gate = max_gate;
  out.tier_median = out.effective_median ? out.effective_median : (gate_med ? gate_med : out.scalar_median);
  out.strict_pass = gate_errs.empty() || max_gate <= MAX_SCALAR_ERROR_PCT;
  out.effective_pass = eff_errs.empty() || max_raw_eff <= MAX_SCALAR_ERROR_PCT;
  out.tier_pass = errs.empty() || (out.tier_median && *out.tier_median <= TIER_SCALAR_MAX_ERROR_PCT);
  out.tier_max_pass = errs.empty() || max_err <= TIER_SCALAR_MAX_ERROR_PCT;
  out.median_pass = !out.scalar_median || *out.scalar_median <= MAX_MEDIAN_ERROR_PCT;
  out.max_scalar_name = field(max_row, "name");
  out.max_scalar_property = field(max_row, "property");
  out.max_gate_name = field(max_gate_row, "name");
  out.worst_effective_name = field(max_eff_row, "name");

  // classifier_metrics (the original calls classify_record without file_name here)
  long n = 0, correct = 0;
  for (const auto& r : mat) {
    if (classify_record(r) != "classifier") continue;
    ++n;
    auto pair = classifier_field_pair(r);
    if (!pair) continue;
    auto a = to_float(r.at(pair->first)), b = to_float(r.at(pair->second));
    // int(round(x)) == int(round(y)); round() is half-even like nearbyint in the default mode
    if (a && b && std::isfinite(*a) && std::isfinite(*b) && std::nearbyint(*a) == std::nearbyint(*b)) ++correct;
  }
  out.classifier_count = n;
  out.classifier_correct = correct;
  if (n) {
    const double acc = 100.0 * double(correct) / double(n);
    out.classifier_accuracy = round_nd(acc, 6);
    out.classifier_pass = acc >= MIN_CLASSIFIER_ACCURACY_PCT;
  }
  if (out.scalar_count > 0) out.official_pooled = out.scalar_median;
  out.green = (!out.official_pooled || *out.official_pooled <= MAX_MEDIAN_ERROR_PCT) && out.classifier_pass &&
              (out.scalar_count == 0 || out.strict_pass);
  if (auto v = get(doc, "record_count"); v && truthy(*v)) out.records = *v;
  else if (auto w = get(doc, "observable_count"); w && truthy(*w)) out.records = *w;
  else out.records = mat.size();
  return out;
}

// ---------------- Ledger B re-score with the live law ----------------
struct LedgerBStats {
  long lb = 0, unrouted = 0, c_match = 0, s_match = 0, e_match = 0;
  double max_rel_dev = 0.0;
};
// S: domain name -> double(S) rounded from a >=113-bit evaluation; alpha = double(ALPHA).
template <class SMap>
LedgerBStats rescore(const json& doc, const SMap& S, double alpha) {
  LedgerBStats st;
  for (const auto& r : material_records(doc)) {
    if (!r.is_object()) continue;
    auto ek = get(r, "eval_kind");
    if (!ek || !ek->is_string()) continue;
    const auto& eks = ek->get_ref<const std::string&>();
    if (eks != "fsot_prediction" && eks != "fsot_correction") continue;
    auto dom = get(r, "fsot_domain");
    auto m = get(r, "measured");
    auto sit = (dom && dom->is_string()) ? S.find(dom->get<std::string>()) : S.end();
    if (sit == S.end() || !m || !m->is_number()) { ++st.unrouted; continue; }
    ++st.lb;
    const double mv = m->get<double>();
    const double s = sit->second;
    const double c = mv * (1.0 + std::fabs(s) * alpha);
    const double cr = std::fabs(c) < 1e6 ? round_nd(c, 6) : round_nd(c, 4);
    const double err = mv != 0 ? std::fabs(c - mv) / std::fabs(mv) * 100.0 : std::fabs(c - mv) * 100.0;
    if (auto sc = get(r, "computed"); sc && sc->is_number()) {
      const double scv = sc->get<double>();
      if (scv == cr) ++st.c_match;
      if (cr != 0) st.max_rel_dev = std::max(st.max_rel_dev, std::fabs(scv - cr) / std::fabs(cr));
    }
    if (auto fs = get(r, "fsot_scalar"); !is_none(fs)) if (auto f = to_float(*fs); f && *f == round_nd(s, 6)) ++st.s_match;
    if (auto ep = get(r, "error_pct"); !is_none(ep)) if (auto f = to_float(*ep); f && *f == round_nd(err, 6)) ++st.e_match;
  }
  return st;
}

}  // namespace fsot::ledger_b
