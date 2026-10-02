// fsot_precision: per-prediction precision report under the z <= 1 gate (include/fsot/host/precision_gate.hpp).
//
//   fsot_precision --refs reference/published_2026-10-02.tsv --map reference/prediction_map_2026-10-02.tsv
//                  --lineage reference/pin_lineage_2026-10-02.tsv --tsv-out X.tsv --md-out X.md
//
// Values: hub seed leaves (include/fsot/host/seed_leaves.hpp, mp169; CKM in IEEE double) and the pinned
// AEB2AD closed forms (Engine sections, parity mode). References: one table, every entry verified against
// committed evidence by tools/check_references.py. "record" rows are the scored set (see the map header).
// The exploratory section evaluates the frozen-pending refinements of docs/freezes/REFINEMENTS_2026-10-02.md;
// they are printed separately and never counted. The refined_* columns carry the frozen-pending candidates of
// docs/freezes/REFINEMENTS_2026-10-02b.md (committed before scoring); they are never counted as confirmed.
// route "seed" = a committed hub vendor/fsot_seed_flavor.py function, evaluated here in mp169 (channel fix F2).
#define _USE_MATH_DEFINES  // M_PI on MSVC (must precede <cmath>)
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <functional>
#include <map>
#include <sstream>
#include <string>
#include <vector>

#include "fsot/engine.hpp"
#include "fsot/host/precision_gate.hpp"
#include "fsot/host/seed_leaves.hpp"

using namespace fsot;
using R = mp169;
// Printed numbers are computed in IEEE double on every platform; mp169 values are handed over through a
// 17-significant-digit decimal string (Boost's own formatting, platform independent) and strtod.
using LD = double;
static double to_d(const R& x) { return std::strtod(x.str(17, std::ios_base::scientific).c_str(), nullptr); }

static std::vector<std::string> split(const std::string& s, char d) {
  std::vector<std::string> out; std::string cur; std::istringstream ss(s);
  while (std::getline(ss, cur, d)) out.push_back(cur);
  if (!s.empty() && s.back() == d) out.push_back("");
  return out;
}
static std::vector<std::vector<std::string>> read_tsv(const std::string& p) {
  std::ifstream in(p); if (!in) { std::fprintf(stderr, "cannot open %s\n", p.c_str()); std::exit(2); }
  std::vector<std::vector<std::string>> rows; std::string line;
  while (std::getline(in, line)) { if (line.empty() || line[0] == '#') continue; rows.push_back(split(line, '\t')); }
  return rows;
}
static R num(const std::string& s) { return s.empty() ? R(0) : R(s.c_str()); }  // exact decimal -> mp169

struct RefRow { std::string key, kind, unit, source, evidence, note; R c = 0, sm = 0, sp = 0; bool ok = false; };

static std::string source_link(const RefRow& r, const std::map<std::string, RefRow>& refs) {
  if (r.source == "CODATA2022") return "CODATA 2022 \"" + r.evidence + "\" https://physics.nist.gov/cuu/Constants/Table/allascii.txt";
  if (r.source.rfind("ARXIV:", 0) == 0) return "arXiv:" + r.source.substr(6) + " https://arxiv.org/abs/" + r.source.substr(6) + " (" + r.evidence.substr(r.evidence.rfind(':') + 1) + ")";
  if (r.source == "AME2020") return "AME2020 mass excesses https://www-nds.iaea.org/amdc/ame2020/mass_1.mas20.txt";
  if (r.source.rfind("PDG2024:", 0) == 0) {
    std::string doc = r.source.substr(8);
    std::string kind = doc.rfind("sum-", 0) == 0 ? "tables" : "reviews";
    return "PDG 2024 https://pdg.lbl.gov/2024/" + kind + "/rpp2024-" + doc + ".pdf";
  }
  if (r.source == "derived") {
    auto parts = split(r.kind.substr(r.kind.find(':') + 1), '/');
    std::string s = "derived " + r.kind + " from";
    for (auto& p : parts) { auto it = refs.find(p); s += " [" + p + ": " + (it != refs.end() ? it->second.source : "?") + "]"; }
    return s;
  }
  return r.source;
}

static void resolve(std::map<std::string, RefRow>& refs) {
  for (int pass = 0; pass < 3; ++pass)
    for (auto& [k, r] : refs) {
      if (r.ok) continue;
      if (r.kind == "direct") { r.ok = true; continue; }
      const auto colon = r.kind.find(':');
      const std::string op = r.kind.substr(0, colon);
      auto parts = split(r.kind.substr(colon + 1), '/');
      auto& a = refs.at(parts[0]);
      if (!a.ok) continue;
      const R sa = a.sm > a.sp ? a.sm : a.sp;
      if (op == "ratio") {
        auto& b = refs.at(parts[1]); if (!b.ok) continue;
        const R sb = b.sm > b.sp ? b.sm : b.sp;
        r.c = a.c / b.c;
        r.sm = r.sp = m::fabs(r.c) * m::sqrt((sa / a.c) * (sa / a.c) + (sb / b.c) * (sb / b.c));
      } else if (op == "inv") {
        r.c = R(1) / a.c; r.sm = r.sp = sa / (a.c * a.c);
      } else if (op == "frac") {  // a/(a+b), exact propagation, uncorrelated (OD-1: Dm2_21/Dm2_31 = Dm2_21/(Dm2_32+Dm2_21))
        auto& b = refs.at(parts[1]); if (!b.ok) continue;
        const R sb = b.sm > b.sp ? b.sm : b.sp, t = a.c + b.c;
        r.c = a.c / t; r.sm = r.sp = m::sqrt((b.c * sa) * (b.c * sa) + (a.c * sb) * (a.c * sb)) / (t * t);
      } else if (op == "pi") {
        const R pi("3.14159265358979323846264338327950288419716939937510582097494459");
        r.c = a.c * pi; r.sm = a.sm * pi; r.sp = a.sp * pi;
      }
      r.ok = true;
    }
}

struct Out {
  std::string id, route, source, ref_key, unit, src_link, pin_target, hist, cause;
  bool record = false, od_superseded = false; LD value = 0; R vr = 0, rvr = 0; gate::Ref ref{}; gate::Score s{};
  std::string rid; LD rvalue = 0; gate::Score rs{};  // frozen-pending refinement (REFINEMENTS_2026-10-02b)
};

static std::string fmt(const char* f, double v) { char b[64]; std::snprintf(b, sizeof b, f, v); return b; }
// Gate arithmetic in mp169 (platform independent); only the printed results are rounded to double.
static gate::Score score_r(const R& v, const RefRow& r) {
  const R d = v - r.c, sig = d >= 0 ? r.sp : r.sm, z = m::fabs(d) / sig, rel = m::fabs(d) / m::fabs(r.c) * R(100);
  gate::Score s; s.z = to_d(z); s.rel_pct = to_d(rel); s.ppm = to_d(rel * R(10000));
  s.pass_z = z <= R(gate::Z_MAX); s.pass_old = rel <= R(gate::OLD_REL_PCT); return s;
}
static std::string fz(double z) { return z < 100 ? fmt("%.4f", z) : fmt("%.4g", z); }

int main(int argc, char** argv) {
#if !defined(FSOT_HAVE_BOOST_MP)
  std::puts("fsot_precision: needs Boost.Multiprecision"); return 0;
#else
  std::string refs_p, map_p, lin_p, tsv_p, md_p;
  for (int i = 1; i + 1 < argc; i += 2) {
    std::string a = argv[i];
    if (a == "--refs") refs_p = argv[i + 1]; else if (a == "--map") map_p = argv[i + 1];
    else if (a == "--lineage") lin_p = argv[i + 1]; else if (a == "--tsv-out") tsv_p = argv[i + 1];
    else if (a == "--md-out") md_p = argv[i + 1];
  }
  if (refs_p.empty() || map_p.empty() || lin_p.empty()) { std::fprintf(stderr, "usage: see header\n"); return 2; }

  std::map<std::string, RefRow> refs;
  for (auto& f : read_tsv(refs_p)) {
    RefRow r; r.key = f.at(0); r.kind = f.at(1); r.unit = f.at(5); r.source = f.at(6); r.evidence = f.size() > 7 ? f[7] : "";
    r.note = f.size() > 8 ? f[8] : "";
    if (r.kind == "direct") { r.c = num(f.at(2)); r.sm = num(f.at(3)); r.sp = num(f.at(4)); }
    refs[r.key] = r;
  }
  resolve(refs);

  // lineage: "sec|row" -> pin values
  std::vector<std::string> pins = {"D1D38A", "3090BC", "FE23A2", "3FBCE5", "AEB2AD"};
  std::map<std::string, std::string> pin_commit = {{"D1D38A", "012e5c64 2026-08-04"}, {"3090BC", "ba6a8288 2026-09-11"},
      {"FE23A2", "3c74a180 2026-09-11"}, {"3FBCE5", "ebd48320 2026-09-14"}, {"AEB2AD", "d127c07e 2026-09-14"}};
  std::map<std::string, std::vector<std::string>> lineage;
  for (auto& f : read_tsv(lin_p)) lineage[f[0]] = std::vector<std::string>(f.begin() + 1, f.end());

  Engine<R> eng;
  leaves::SeedLeaves<R> L(eng);
  std::map<std::string, R> leafv;
  for (auto& [id, v] : L.mp_values()) leafv[id] = v;
  const auto ckm = leaves::ckm_double(eng);
  for (auto& [k, v] : ckm.mags) leafv["CKM_" + k] = R(v);
  // seed route (hub vendor/fsot_seed_flavor.py seed_alpha_s_MZ, 8760d403 2026-08-03): 2 (POOF/psi_con)^2
  std::map<std::string, R> seedv = {{"seed_alpha_s_MZ", R(2) * (eng.POOF / eng.PSI_CON) * (eng.POOF / eng.PSI_CON)}};
  // frozen-pending candidates of docs/freezes/REFINEMENTS_2026-10-02b.json (row id -> candidate id, value)
  const R yy = L.yy();
  std::map<std::string, std::pair<std::string, std::function<R(const R&)>>> refined = {
      {"pin:wave3|m_H/m_W", {"C-MHW-1", [&](const R&) { return R(leafv.at("m_H_MeV") / leafv.at("m_W_MeV")); }}},
      {"pin:wave4|Dm2_21/Dm2_32", {"C-DM-1", [&](const R&) { return R(m::ipow(eng.POOF * eng.G_CAT * eng.P_NEW, 3) / leafv.at("dm2_32")); }}},
      {"pin:wave1|T_CMB", {"C-TCMB", [&](const R& b) { return R(b * (R(1) + yy)); }}},
      {"pin:wave5|Gamma_Z/M_Z", {"C-GZ", [&](const R& b) { return R(b * (R(1) + yy)); }}},
      {"pin:wave3|Deuteron_binding_MeV", {"C-BD", [&](const R& b) { return R(b * (R(1) + yy * eng.GAMMA * eng.PSI_CON * eng.PSI_CON)); }}},
      {"pin:wave8|Deuteron_mu_muN", {"C-MUD", [&](const R& b) { return R(b * (R(1) + yy)); }}}};
  std::map<std::string, std::pair<R, R>> pinv;  // value, target
  for (auto& [name, fn] : eng.sections())
    for (auto& r : (eng.*fn)())
      pinv[std::string(name) + "|" + r.name] = {R(r.computed), r.measured ? R(*r.measured) : R(0)};

  // owner decision OD-2 (audit/OWNER_DECISIONS_2026-10-02i.md): same Engine, Quantum_Mechanics D_eff = 6 (pre-FE23A2).
  // The pinned Engine `eng` above is unchanged and is the one the pin-parity checks use.
  Engine<R> eng6;
  for (auto& d : eng6.DOMAINS) if (d.name == "Quantum_Mechanics") d.D_eff = 6;
  eng6.S_QUANT = eng6.domain_scalar("Quantum_Mechanics");
  std::map<std::string, R> ownerv;
  for (auto& [name, fn] : eng6.sections())
    for (auto& r : (eng6.*fn)()) ownerv[std::string(name) + "|" + r.name] = R(r.computed);

  std::vector<Out> outs;
  for (auto& f : read_tsv(map_p)) {
    Out o; o.id = f.at(0); o.route = f.at(1); o.source = f.at(2); o.ref_key = f.at(3);
    const R scale = num(f.at(4)); o.record = f.at(5) == "1"; const std::string note = f.size() > 6 ? f[6] : "";
    auto rit = refs.find(o.ref_key);
    if (rit == refs.end()) { std::fprintf(stderr, "unknown ref %s\n", o.ref_key.c_str()); return 2; }
    const RefRow& rr = rit->second;
    o.ref = {to_d(rr.c), to_d(rr.sm), to_d(rr.sp)}; o.unit = rr.unit; o.src_link = source_link(rr, refs);
    if (o.route == "leaf") {
      auto it = leafv.find(o.source); if (it == leafv.end()) { std::fprintf(stderr, "no leaf %s\n", o.source.c_str()); return 2; }
      o.vr = it->second * scale;
    } else if (o.route == "owner") {
      auto it = ownerv.find(o.source); if (it == ownerv.end()) { std::fprintf(stderr, "no owner row %s\n", o.source.c_str()); return 2; }
      o.vr = it->second * scale;
    } else if (o.route == "seed") {
      auto it = seedv.find(o.source); if (it == seedv.end()) { std::fprintf(stderr, "no seed %s\n", o.source.c_str()); return 2; }
      o.vr = it->second * scale;
    } else {
      auto it = pinv.find(o.source); if (it == pinv.end()) { std::fprintf(stderr, "no pin row %s\n", o.source.c_str()); return 2; }
      o.vr = it->second.first * scale; o.pin_target = fmt("%.10g", to_d(it->second.second * scale));
    }
    o.value = to_d(o.vr);
    o.s = score_r(o.vr, rr);
    o.od_superseded = note.rfind("[OD-superseded]", 0) == 0;
    if (auto ri = refined.find(o.id); ri != refined.end()) {
      o.rid = ri->second.first; o.rvr = ri->second.second(o.vr); o.rvalue = to_d(o.rvr); o.rs = score_r(o.rvr, rr);
    }
    if (o.route == "owner") {
      o.hist = "pinned AEB2AD value " + fmt("%.15g", to_d(pinv.at(o.source).first * scale)) + " z=" + fz(score_r(pinv.at(o.source).first * scale, rr).z);
      o.cause = note;
    } else if (o.route == "seed") {
      o.hist = note;
      o.cause = o.s.pass_z ? "channel fix: committed hub seed route (REFINEMENTS_2026-10-02b F2)" : "seed outside the PDG 2024 sigma";
    } else if (o.route == "leaf") {
      o.hist = note;
      o.cause = o.s.pass_z ? "restored: hub seed leaf (2026-09-29) absent from the C++ port (H-01)"
                           : "leaf outside the PDG 2024/CODATA 2022 sigma";
    } else {
      // historical best over the five hub pins, scored against the same reference
      auto lit = lineage.find(o.source);
      int best = -1; double bestz = 1e300; std::vector<double> zs(pins.size(), -1); std::vector<R> vs(pins.size(), R(0));
      if (lit != lineage.end())
        for (size_t i = 0; i < pins.size() && i < lit->second.size(); ++i) {
          if (lit->second[i].empty()) continue;
          vs[i] = num(lit->second[i]) * scale; zs[i] = score_r(vs[i], rr).z;
          if (zs[i] <= bestz) { bestz = zs[i]; best = (int)i; }  // ties -> latest pin
        }
      if (best >= 0) o.hist = pins[best] + " (" + pin_commit[pins[best]] + ") " + fmt("%.10g", to_d(vs[best])) + " z=" + fz(bestz);
      std::string changed;  // first in-window pin where the value moved and z got worse
      for (size_t i = 1; i < pins.size(); ++i)
        if (zs[i] >= 0 && zs[i - 1] >= 0 && vs[i] != vs[i - 1] && zs[i] > zs[i - 1] * 1.0000001 && zs[i] > gate::Z_MAX)
          changed += (changed.empty() ? "" : "; ") + pins[i - 1] + "->" + pins[i] + " (" + pin_commit[pins[i]] + ") z " +
                     fz(zs[i - 1]) + "->" + fz(zs[i]);
      if (o.s.pass_z) o.cause = "";
      else if (!changed.empty() && bestz <= gate::Z_MAX) o.cause = "re-pin regression (frozen pin; theory decision): " + changed;
      else if (!changed.empty()) o.cause = "formula miss; also worsened by re-pin: " + changed;
      else o.cause = "formula miss: outside sigma under every pin (best z=" + fz(bestz) + ")";
      const R tgt = num(o.pin_target);
      const R sig = tgt >= rr.c ? rr.sp : rr.sm;
      if (tgt != 0 && m::fabs(tgt - rr.c) > sig)
        o.cause += std::string(o.cause.empty() ? "" : "; ") + "pin target " + o.pin_target + " is " +
                   fmt("%.3g", to_d(m::fabs(tgt - rr.c) / sig)) + " sigma off the current reference";
      if (!note.empty()) o.cause += std::string(o.cause.empty() ? "" : "; ") + note;
    }
    outs.push_back(o);
  }

  // summary
  auto summarize = [&](bool record_only, FILE* fp, const char* label, bool with_refined = false, bool pinned_only = false) {
    std::vector<LD> ppm; int n = 0, pz = 0, p2 = 0; LD worst = -1; std::string worst_id;
    for (auto& o : outs) {
      const bool is_od = o.id.rfind("od", 0) == 0;
      if (pinned_only) { if (!((o.record && !is_od) || o.od_superseded)) continue; }
      else if (record_only && !o.record) continue;
      const gate::Score& sc = (with_refined && !o.rid.empty() && o.rs.pass_z) ? o.rs : o.s;  // failing candidates are not adopted
      ++n; pz += sc.pass_z; p2 += sc.pass_old; ppm.push_back(sc.ppm);
      if (sc.ppm > worst) { worst = sc.ppm; worst_id = o.id; }
    }
    std::sort(ppm.begin(), ppm.end());
    const LD med = ppm.empty() ? 0 : (ppm.size() % 2 ? ppm[ppm.size() / 2] : 0.5 * (ppm[ppm.size() / 2 - 1] + ppm[ppm.size() / 2]));
    std::fprintf(fp, "%s: n=%d  pass z<=%.0f: %d/%d  pass |rel|<=%.0f%%: %d/%d  median ppm=%.4g  worst ppm=%.6g (%s)\n", label, n,
                 gate::Z_MAX, pz, n, gate::OLD_REL_PCT, p2, n, med, worst, worst_id.c_str());
  };

  FILE* tsv = tsv_p.empty() ? stdout : std::fopen(tsv_p.c_str(), "wb");
  std::fprintf(tsv, "#id\troute\trecord\tvalue\tunit\tref_key\tcentral\tsigma_minus\tsigma_plus\tppm\tz\tpass_z<=1\trel_pct\tpass_2pct\tpin_target\thistorical_best\tcause\tsource\trefined_id\trefined_value\trefined_z\trefined_pass_z<=1\n");
  for (auto& o : outs) {
    std::fprintf(tsv, "%s\t%s\t%d\t%.15g\t%s\t%s\t%.15g\t%.6g\t%.6g\t%.6g\t%.4g\t%s\t%.6g\t%s\t%s\t%s\t%s\t%s", o.id.c_str(), o.route.c_str(),
                 o.record, o.value, o.unit.c_str(), o.ref_key.c_str(), o.ref.central, o.ref.sigma_minus, o.ref.sigma_plus, o.s.ppm, o.s.z,
                 o.s.pass_z ? "PASS" : "FAIL", o.s.rel_pct, o.s.pass_old ? "PASS" : "FAIL", o.pin_target.c_str(), o.hist.c_str(),
                 o.cause.c_str(), o.src_link.c_str());
    if (o.rid.empty()) std::fprintf(tsv, "\t\t\t\t\n");
    else std::fprintf(tsv, "\t%s\t%.15g\t%.4g\t%s\n", o.rid.c_str(), o.rvalue, o.rs.z, o.rs.pass_z ? "PASS (frozen-pending)" : "FAIL (open)");
  }
  if (tsv != stdout) std::fclose(tsv);

  // exploratory: frozen-pending refinements (docs/freezes/REFINEMENTS_2026-10-02.md), NOT scored
  auto f = [](const R& x) { return to_d(x); };
  const auto& vus_fit = refs.at("CKM_V_us"); const auto& vus_dir = refs.at("CKM_V_us_direct");
  const auto& vud_fit = refs.at("CKM_V_ud"); const auto& vud_dir = refs.at("CKM_V_ud_direct");
  const double chem = f(eng.THETA_S / eng.PHI + (R(1) - eng.domain_scalar("Chemistry")));
  const double qm = f(eng.THETA_S / eng.PHI + (R(1) - eng.domain_scalar("Quantum_Mechanics")));
  const double lam = ckm.lam;
  auto zfit = [&](double v, const RefRow& r) { return gate::score(v, {to_d(r.c), to_d(r.sm), to_d(r.sp)}).z; };
  const double alpha_inv_seed = std::pow(f(eng.PHI) * f(eng.G_CAT) / f(eng.C_FACTOR), 3.0);
  const double deficit_pred = (1.0 / alpha_inv_seed) / (M_PI * std::sqrt(2.0));
  const double vud_c = to_d(vud_dir.c), vud_s = to_d(vud_dir.sm), vus_c = to_d(vus_dir.c), vus_s = to_d(vus_dir.sm);
  const double vub = ckm.mags.at("V_ub");
  const double deficit_meas = 1.0 - (vud_c * vud_c + vus_c * vus_c + vub * vub);
  const double deficit_sig = std::sqrt(std::pow(2.0 * vud_c * vud_s, 2) + std::pow(2.0 * vus_c * vus_s, 2));
  const double vud = ckm.mags.at("V_ud");
  const double z_vud_fit = zfit(vud, vud_fit), z_vud_dir = zfit(vud, vud_dir);
  const double published_z = std::fabs(to_d(vud_fit.c) - vud_c) / vud_s;
  const bool channel_mismatch = z_vud_fit <= 1 && z_vud_dir > 1 && published_z + 1e-9 >= z_vud_dir;
  struct Br { const char* name; const char* formula; double v; double z; };
  std::vector<Br> br = {{"pin_qm_floor", "theta_S/phi + (1 - S_Quantum_Mechanics)", qm, zfit(qm, vus_fit)},
                        {"condensation_chemistry", "theta_S/phi + (1 - S_Chemistry)", chem, zfit(chem, vus_fit)},
                        {"seed_lambda", "POOF*(1+ETA_EFF)", lam, zfit(lam, vus_fit)}};
  const Br* go = nullptr;
  for (auto& b : br) if (b.z <= 1 && (!go || b.z < go->z)) go = &b;

  FILE* md = md_p.empty() ? stdout : std::fopen(md_p.c_str(), "wb");
  std::fprintf(md, "<!-- generated by apps/fsot_precision.cpp; do not edit by hand -->\n");
  std::fprintf(md, "Gate: z = |value - central| / sigma <= %.0f (include/fsot/host/precision_gate.hpp); legacy check |rel| <= %.0f%% reported alongside.\n\n",
               gate::Z_MAX, gate::OLD_REL_PCT);
  std::fprintf(md, "```\n"); summarize(true, md, "record set (scored)"); summarize(false, md, "all rows (incl. superseded/alternate)");
  summarize(true, md, "record set if the passing frozen-pending refinements were adopted (NOT confirmed)", true);
  summarize(true, md, "record set without the owner decisions OD-1/OD-2 (pinned rows only; audit/OWNER_DECISIONS_2026-10-02i.md)", false, true);
  std::fprintf(md, "```\n\n");
  std::fprintf(md, "| id | route | rec | confirmed value | unit | central | sigma (-/+) | ppm | z | z<=1 | 2%% | frozen-pending refined (id: value, z) | historical best | cause / note | source |\n");
  std::fprintf(md, "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n");
  for (auto& o : outs) {
    std::string sig = o.ref.sigma_minus == o.ref.sigma_plus ? fmt("%.4g", o.ref.sigma_plus) : fmt("-%.4g", o.ref.sigma_minus) + "/+" + fmt("%.4g", o.ref.sigma_plus);
    std::string cause = o.cause; std::replace(cause.begin(), cause.end(), '|', '/');
    std::string id = o.id; std::replace(id.begin(), id.end(), '|', '/');
    std::string rcol = o.rid.empty() ? "" : o.rid + ": " + fmt("%.15g", o.rvalue) + ", z=" + fz(o.rs.z) + (o.rs.pass_z ? " (frozen-pending)" : " (fails; open)");
    std::fprintf(md, "| %s | %s | %s | %.15g | %s | %.15g | %s | %.4g | %s | %s | %s | %s | %s | %s | %s |\n", id.c_str(), o.route.c_str(), o.record ? "Y" : "-",
                 o.value, o.unit.c_str(), o.ref.central, sig.c_str(), o.s.ppm, fz(o.s.z).c_str(), o.s.pass_z ? "PASS" : "**FAIL**", o.s.pass_old ? "PASS" : "FAIL",
                 rcol.c_str(), o.hist.c_str(), cause.c_str(), o.src_link.c_str());
  }
  std::fprintf(md, "\n### EXPLORATORY (tier frozen-pending; not counted above; docs/freezes/REFINEMENTS_2026-10-02.md)\n\n```\n");
  std::fprintf(md, "R1 |V_us| Chemistry route theta_S/phi+(1-S_Chemistry) = %.12g  z_fit=%.4f  z_direct=%.4f\n", chem, zfit(chem, vus_fit), zfit(chem, vus_dir));
  std::fprintf(md, "R2 first-row deficit alpha_seed/(pi*sqrt2) = %.6e  measured(direct Vud,Vus; seed Vub) = %.6e +- %.2e  z=%.4f\n", deficit_pred, deficit_meas, deficit_sig,
               std::fabs(deficit_pred - deficit_meas) / deficit_sig);
  std::fprintf(md, "R3 V_ud exemption: seed V_ud=%.12g z_fit=%.4f z_direct=%.4f published fit-vs-direct=%.4f sigma_direct -> %s\n", vud, z_vud_fit, z_vud_dir, published_z,
               channel_mismatch ? "channel_mismatch (exempt under R3)" : "no exemption");
  for (auto& b : br) std::fprintf(md, "R4 branch %-24s %-42s value=%.12g z_fit=%.4f\n", b.name, b.formula, b.v, b.z);
  std::fprintf(md, "R4 min-z route selection -> %s (z_fit=%.4f)\n", go ? go->name : "none", go ? go->z : -1.0);
  std::fprintf(md, "```\n");
  if (md != stdout) std::fclose(md);
  summarize(true, stdout, "record set (scored)");
  summarize(false, stdout, "all rows");
  summarize(true, stdout, "record set with passing frozen-pending refinements (NOT confirmed)", true);
  summarize(true, stdout, "record set without owner decisions (pinned only)", false, true);
  return 0;
#endif
}
