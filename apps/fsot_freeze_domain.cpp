// fsot_freeze_domain — write or verify a dated SHA-256 freeze of the live domain mapping against the pinned
// authority (AEB2AD). A freeze written here and committed to git counts for TIER 2/3 in the evidence-tier
// report (tools/gen_tier_evidence.py collects freezes/*.json with their first git commit; include/fsot/host/
// tiers.hpp re-derives every row hash from the live mapping before it lets the freeze count).
//
//   fsot_freeze_domain --authority PATH/vendor/fsot_compute.py --out freezes/domain_freeze_<date>_AEB2AD.json
//                      [--scope all|core|extension|closed_form|ledger_a] [--domains A,B,cf:wave1/H0,la:ID,...] [--date YYYY-MM-DD] [--note TEXT]
//   fsot_freeze_domain --verify freezes/X.json        (exit 0 iff every frozen hash equals the live mapping)
//   fsot_freeze_domain --print-core-sha               (hub-scheme domain_table_sha256 of the 35 core rows)
//
// --date defaults to the later of today's local and UTC calendar dates (a freeze can only be dated later than
// it was made, never earlier). The authority file is hashed and must equal AUTHORITY_SHA256; the K line is
// checked as in the hub's data/domain_table_freeze.json. Nothing is tuned: the rows are the engine's values.
#include <cstdio>
#include <ctime>
#include <fstream>
#include <iterator>
#include <sstream>
#include <string>
#include <vector>

#include <nlohmann/json.hpp>

#include "fsot/host/freeze.hpp"

namespace fz = fsot::freeze;
using ojson = nlohmann::ordered_json;

static std::string upper(std::string s) { for (auto& c : s) c = (char)std::toupper((unsigned char)c); return s; }
static std::string today() {
  std::time_t t = std::time(nullptr);
  char a[16], b[16];
  std::tm lt{}, ut{};
  localtime_r(&t, &lt);
  gmtime_r(&t, &ut);
  std::strftime(a, sizeof a, "%Y-%m-%d", &lt);
  std::strftime(b, sizeof b, "%Y-%m-%d", &ut);
  return std::max(std::string(a), std::string(b));
}
static bool valid_date(const std::string& d) {
  if (d.size() != 10 || d[4] != '-' || d[7] != '-') return false;
  for (int i : {0, 1, 2, 3, 5, 6, 8, 9}) if (!std::isdigit((unsigned char)d[i])) return false;
  return true;
}

static int verify(const std::string& path) {
  std::ifstream f(path);
  if (!f) { std::fprintf(stderr, "cannot open %s\n", path.c_str()); return 2; }
  auto j = nlohmann::json::parse(f);
  int bad = 0;
  if (j.value("pin_prefix", "") != std::string(fsot::AUTHORITY_PIN_PREFIX)) { std::printf("FAIL pin_prefix %s\n", j.value("pin_prefix", "").c_str()); ++bad; }
  if (upper(j.value("authority_sha256", "")) != std::string(fsot::AUTHORITY_SHA256)) { std::printf("FAIL authority_sha256\n"); ++bad; }
  std::vector<const fz::Row*> sel;
  for (auto& r : j.at("domains")) {
    const auto* L = fz::live_row(r.at("domain").get<std::string>());
    if (!L) { std::printf("FAIL %s: not in the live mapping\n", r["domain"].get<std::string>().c_str()); ++bad; continue; }
    if (L->sha != r.at("row_sha256").get<std::string>()) { std::printf("FAIL %s: row hash changed\n", L->domain.c_str()); ++bad; }
    sel.push_back(L);
  }
  const std::string s = fz::table_sha(sel);
  if (s != j.at("selection_sha256").get<std::string>()) { std::printf("FAIL selection_sha256 %s != live %s\n", j["selection_sha256"].get<std::string>().c_str(), s.c_str()); ++bad; }
  if (j.contains("domain_table_sha256") && j["domain_table_sha256"].is_string() && j["domain_table_sha256"] != fz::core_table_sha()) {
    std::printf("FAIL domain_table_sha256 != live core table %s\n", fz::core_table_sha().c_str()); ++bad;
  }
  std::printf("%s %s: %zu rows, freeze_date %s, selection_sha256 %s\n", bad ? "FAIL" : "OK", path.c_str(), sel.size(),
              j.value("freeze_date", "").c_str(), s.c_str());
  return bad ? 1 : 0;
}

int main(int argc, char** argv) {
  std::string authority, out, scope = "all", domains, date, note, ver;
  bool print_core = false;
  for (int i = 1; i < argc; ++i) {
    std::string a = argv[i];
    auto next = [&]() -> std::string { if (i + 1 >= argc) { std::fprintf(stderr, "%s needs a value\n", a.c_str()); std::exit(2); } return argv[++i]; };
    if (a == "--authority") authority = next();
    else if (a == "--out") out = next();
    else if (a == "--scope") scope = next();
    else if (a == "--domains") domains = next();
    else if (a == "--date") date = next();
    else if (a == "--note") note = next();
    else if (a == "--verify") ver = next();
    else if (a == "--print-core-sha") print_core = true;
    else { std::fprintf(stderr, "unknown option %s (see header of apps/fsot_freeze_domain.cpp)\n", a.c_str()); return 2; }
  }
  if (print_core) { std::printf("%s\n", fz::core_table_sha().c_str()); return 0; }
  if (!ver.empty()) return verify(ver);
  if (authority.empty() || out.empty()) { std::fprintf(stderr, "need --authority and --out (or --verify FILE)\n"); return 2; }
  std::ifstream af(authority, std::ios::binary);
  if (!af) { std::fprintf(stderr, "cannot open %s\n", authority.c_str()); return 2; }
  const std::string src((std::istreambuf_iterator<char>(af)), std::istreambuf_iterator<char>());
  const std::string asha = upper(fsot::host::sha256_hex(src));
  if (asha != std::string(fsot::AUTHORITY_SHA256)) {
    std::fprintf(stderr, "authority sha256 %s != pinned %s; refusing to freeze\n", asha.c_str(), std::string(fsot::AUTHORITY_SHA256).c_str());
    return 3;
  }
  if (date.empty()) date = today();
  if (!valid_date(date) || date < today()) { std::fprintf(stderr, "--date must be YYYY-MM-DD and not earlier than %s\n", today().c_str()); return 2; }
  if (scope != "all" && scope != "core" && scope != "extension" && scope != "closed_form" && scope != "ledger_a") {
    std::fprintf(stderr, "--scope all|core|extension|closed_form|ledger_a\n");
    return 2;
  }

  std::vector<const fz::Row*> sel;
  if (!domains.empty()) {
    std::stringstream ss(domains);
    for (std::string d; std::getline(ss, d, ',');) {
      const auto* r = fz::live_row(d);
      if (!r) { std::fprintf(stderr, "unknown domain %s (not core and not a reachable extension fold)\n", d.c_str()); return 2; }
      sel.push_back(r);
    }
    scope = "domains";
  } else {
    for (auto& r : fz::live_rows())
      if (scope == "all" || r.kind == scope || (scope == "extension" && r.kind == "extension_fold")) sel.push_back(&r);
  }
  std::sort(sel.begin(), sel.end(), [](const fz::Row* a, const fz::Row* b) { return a->domain < b->domain; });
  sel.erase(std::unique(sel.begin(), sel.end()), sel.end());
  long ncore = 0, next = 0, ncf = 0, nla = 0;
  for (auto* r : sel) { ncore += r->kind == "core"; next += r->kind == "extension_fold"; ncf += r->kind == "closed_form"; nla += r->kind == "ledger_a"; }

  const bool k_present = src.find(fz::K_LINE_NEEDLE) != std::string::npos;
  ojson j;
  j["freeze_date"] = date;
  j["pin_prefix"] = std::string(fsot::AUTHORITY_PIN_PREFIX);
  j["authority_sha256"] = asha;
  j["k_line_present"] = k_present;
  j["k_line_sha256"] = fsot::host::sha256_hex(fz::K_LINE_NEEDLE);
  j["scope"] = scope;
  j["domain_count"] = sel.size();
  j["core_rows"] = ncore;
  j["extension_rows"] = next;
  j["closed_form_rows"] = ncf;
  j["ledger_a_rows"] = nla;
  j["domain_table_sha256"] = ncore == 35 ? ojson(fz::core_table_sha()) : ojson(nullptr);
  j["selection_sha256"] = fz::table_sha(sel);
  j["generator"] = "FSOT-2.1-Cpp apps/fsot_freeze_domain.cpp (rows from the C++ engine; hub _domain_table_sha row scheme)";
  j["counts_for_tiers_when"] = "committed to git; freeze date = later of freeze_date and the first commit carrying selection_sha256; "
                               "every row_sha256 must equal the live mapping (tools/gen_tier_evidence.py + include/fsot/host/tiers.hpp)";
  j["note"] = note.empty() ? "Dated SHA-256 freeze of the live AEB2AD domain mapping; no constant, f or domain parameter chosen here." : note;
  ojson rows = ojson::array();
  for (auto* r : sel) {
    ojson x = ojson::parse(r->json);
    if (r->kind == "closed_form" || r->kind == "ledger_a") x = ojson{{"domain", r->domain}, {"row", ojson::parse(r->json)}};
    x["kind"] = r->kind;
    x["row_sha256"] = r->sha;
    x["live_scalar"] = nlohmann::json::parse(fsot::py::repr(r->scalar));
    rows.push_back(x);
  }
  j["domains"] = rows;
  std::ofstream o(out, std::ios::binary);
  if (!o) { std::fprintf(stderr, "cannot write %s\n", out.c_str()); return 2; }
  o << j.dump(1) << "\n";
  std::printf("wrote %s: %zu rows (%ld core, %ld extension, %ld closed-form, %ld Ledger A), selection_sha256 %s%s\n", out.c_str(),
              sel.size(), ncore, next, ncf, nla, j["selection_sha256"].get<std::string>().c_str(),
              ncore == 35 ? (", domain_table_sha256 " + fz::core_table_sha()).c_str() : "");
  return k_present ? 0 : 4;
}
