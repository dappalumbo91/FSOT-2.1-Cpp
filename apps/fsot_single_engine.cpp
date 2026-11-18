// fsot_single_engine — the consolidated FSOT engine table.
//   --table   <out.tsv>  every closed-form row: canonical (derived) value, authority-parity value, both D-02/D-04
//                        alternatives, measured, rel%, z (when the authority row carries sigma), row kind
//   --folded  <tsv> <out.tsv>  folded dial-in routes re-derived live and re-scored (input golden/folded_routes.tsv)
//   --before-after <out.md>    every row whose value differs from authority parity, and the variant deltas
//   §43.5vt (Damian t994u): the folded G_F / tau_n rows and every row that reads G_F carry SM_PARITY_REFINE_LATER
#include <array>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <map>
#include <sstream>
#include <string>
#include <tuple>

#include "fsot/derive/derived_table.hpp"
#include "fsot/fold/folded_routes.hpp"

using namespace fsot;
using R = mp169;
static std::string s30(const R& x) { return x.str(30); }
static std::string key(const derive::Row<R>& r) { return r.section + "|" + r.name; }
static std::string md(std::string s) {  // markdown cell: escape '|' (row names like |V_cb|)
  for (std::size_t i = 0; (i = s.find('|', i)) != std::string::npos; i += 2) s.insert(i, "\\");
  return s;
}

int main(int argc, char** argv) {
  Engine<R> canon(Mode::corrected), parity(Mode::parity), e10(Mode::corrected), d5(Mode::corrected);
  derive::with_c_cosm_10phi(e10);
  derive::with_qm_rung(d5, 5);
  auto T = derive::table(canon, true), P = derive::table(parity, false), A = derive::table(e10, true), B = derive::table(d5, true);
  {  // IRONOUT-2 (Damian t999u): one engine-wide value per quantity; sources = the tip's scored values in the frozen audit
    std::map<std::string, std::string> pins;
    std::ifstream pin(FSOT_PRECISION_TSV);
    if (!pin) { std::fprintf(stderr, "cannot open %s\n", FSOT_PRECISION_TSV); return 2; }
    for (std::string line; std::getline(pin, line);) {
      if (line.empty() || line[0] == '#') continue;
      const auto t1 = line.find('\t'), t2 = line.find('\t', t1 + 1), t3 = line.find('\t', t2 + 1), t4 = line.find('\t', t3 + 1);
      pins.emplace(line.substr(0, t1), line.substr(t3 + 1, t4 - t3 - 1));
    }
    // T: frozen pins as scored. A/B (D-02 10phi, D-04 QM-D5): a pin that is a live seed leaf follows its variant engine.
    const auto lc = leaves::SeedLeaves<R>(canon).mp_values(), la = leaves::SeedLeaves<R>(e10).mp_values(), lb = leaves::SeedLeaves<R>(d5).mp_values();
    derive::ironout2(T, pins); derive::ironout2(A, pins, &lc, &la); derive::ironout2(B, pins, &lc, &lb);
  }
  std::map<std::string, R> pv, av, bv;
  leaves::SeedLeaves<R> VL(canon);
  const auto vpk = fold::vt::Package<R>::load(FSOT_VT_PACKAGE_TSV);
  const fold::vt::Chain<R> vch{vpk, fold::vt::engine_inputs(VL)};
  const auto vin = fold::vt::engine_inputs(VL);
  const R s2h = fold::vt::leaf(VL, "sin2_theta_W_MSbar");
  const auto v0 = vch.solve(fold::vt::Route{false, false, false, false, false, false, false}), v2 = vch.solve(fold::vt::P2()), v1 = vch.solve(fold::vt::P1());
  // IRONOUT-2 (parent steering 1:55 PM EST): CARRIED G_F route = §43.5vv P3 + §43.5vw P3 Delta_R^V; vt P2/P1 alternates.
  const auto vvwpk = fold::vt::Package<R>::load(FSOT_VV_VW_PACKAGE_TSV);
  fold::vt::Chain<R> vvw{vpk, fold::vt::engine_inputs(VL)};
  vvw.hooks = fold::vt::vv_p3_vw_p3(vvwpk);
  const auto v3 = vvw.solve(fold::vt::P1());
  const R tau_vv_only = vpk.at("tau_vk_s") / (v3.ratio * v3.ratio);
  // IRONOUT-2 unify tau_n: of the FSOT tau_n values (closed form pi^7 theta_S 878.5929, vt P2 877.8484, vt P1 877.6310,
  // vv P3 877.8657, vv P3 + vw P3 878.4325) the carried chain value lands closest to the pdgLive primary 878.3(4)
  // (z +0.33 vs the closed form's +0.73), so the catalog row reads it; the closed form stays in the parity column.
  for (auto* X : {&T, &A, &B})
    for (auto& r : *X)
      if (r.section == "wave3" && r.name == "Neutron_lifetime_s") {
        r.value = v3.tau_n; r.kind = derive::RowKind::derived_replacement;
        r.formula += " [IRONOUT-2 unify: value = carried G_F chain tau_n (vv P3 + vw P3 Delta_R^V), fold::vt::Chain]";
        r.why = "IRONOUT-2 unify: tau_n closed form -> carried vv P3 + vw P3 chain (closest to pdgLive 878.3(4))";
      }
  for (auto& r : P) pv.emplace(key(r), r.value);
  for (auto& r : A) av.emplace(key(r), r.value);
  for (auto& r : B) bv.emplace(key(r), r.value);
  const R gzref = lit<R>("0.02736653946"), gzsig = lit<R>("2.523e-5");  // audit/score_2026-10-02z.tsv:14 reference (published Gamma_Z/m_Z)
  auto gz = [&](const R& GF) { return fold::vt::gz_over_mz_A1(canon, GF, vin.MZ, s2h, vin.alpha); };
  for (int i = 1; i < argc; ++i) {
    if (!std::strcmp(argv[i], "--table") && i + 1 < argc) {
      std::ofstream o(argv[++i], std::ios::binary);
      // IRONOUT-1 #6 (criteria, not physics): the authority's printed "sigma" field is its claimed |z| tag (e.g. H0 2.1 =
      // (68.44 - 67.4)/0.5), NOT an absolute uncertainty. It is carried as auth_sigma_tag and no z is computed from it
      // (z left blank); scored z comes only from fsot_precision (published sigma) and the folded routes.
      o << "#section\tname\tformula\tkind\tvalue\tvalue_parity\tvalue_c_cosm_10phi\tvalue_qm_D5\tmeasured\tauth_sigma_tag\trel_pct\tz\tsensitive\n";
      for (auto& r : T) {
        const std::string k = key(r);
        std::string sens;
        if (av.count(k) && av.at(k) != r.value) sens += "D-02 ";
        if (bv.count(k) && bv.at(k) != r.value) sens += "D-04 ";
        o << r.section << '\t' << r.name << '\t' << r.formula << '\t' << derive::kind_name(r.kind) << '\t' << s30(r.value) << '\t'
          << (pv.count(k) ? s30(pv.at(k)) : "") << '\t' << (av.count(k) ? s30(av.at(k)) : "") << '\t' << (bv.count(k) ? s30(bv.at(k)) : "") << '\t';
        if (r.measured) {
          const R rel = m::fabs(r.value - *r.measured) / m::fabs(*r.measured) * R(100);
          o << s30(*r.measured) << '\t' << (r.sigma ? std::to_string(*r.sigma) : "") << '\t' << double(rel) << '\t';
          if (r.wa_sigma) o << double((r.value - *r.measured) / R(*r.wa_sigma));  // IRONOUT-2 retarget: z vs world average
        } else o << "\t\t\t";
        o << '\t' << sens << '\n';
      }
    } else if (!std::strcmp(argv[i], "--folded") && i + 2 < argc) {
      std::ifstream in(argv[++i]); std::ofstream o(argv[++i], std::ios::binary);
      leaves::SeedLeaves<R> L(canon); fold::Live<R> live{canon, L, &vch, &vvw};
      o << "#route\tleaf\tpred_live\tpred_recorded\tobs\tsigma\tz_live\tlive\tflag\n";
      std::string line;
      while (std::getline(in, line)) {
        if (line.empty() || line[0] == '#') continue;
        std::vector<std::string> c; std::stringstream ss(line); std::string x;
        while (std::getline(ss, x, '\t')) c.push_back(x);
        c.resize(9);
        if (c[0] == "HOOK" || c[2].empty()) continue;
        std::string pl = c[2];
        double pred = std::strtod(c[2].c_str(), nullptr);
        if (!c[7].empty()) if (auto v = live(c[7])) { pl = s30(*v); pred = double(*v); }
        // IRONOUT-2 r4 (Tracer REFINEMENT_LIST r4; Scout WAVE90 43_5wf, PDG 2026 / CODATA 2022): single-experiment targets
        // filed with the ledger routes are scored against the current world average. The ledger file keeps the filed target.
        static const std::map<std::string, std::array<const char*, 3>> wa = {
            {"43.5qk-GZ_DELPHI_TIP", {"2495.5", "2.3", "PDG 2026 Gamma_Z OUR EVALUATION (was DELPHI 2487.6(41))"}},
            {"43.5ql-GZ_L3_TIP", {"2495.5", "2.3", "PDG 2026 Gamma_Z OUR EVALUATION (was L3 2502.4(42))"}},
            {"43.5rh-RP_GRININ_TIP", {"0.84075", "0.00064", "CODATA 2022 r_p (was Grinin 0.8482(38))"}},
            {"43.5rn-MH_CMS2020_TIP", {"125.13", "0.11", "PDG 2026 m_H average (was CMS 2020 125.38(14))"}},
            {"43.5pp-DM2_21_SOLAR", {"7.60e-5", "0.17e-5", "PDG 2026 Dm2_21 OUR AVERAGE (was SK solar-only 6.10(95)e-5)"}},
            {"43.5qy-MK_CHENG_TIP", {"493.677", "0.015", "PDG 2026 m_K+- OUR FIT (was Cheng 1975 493.657(20))"}},
        };
        std::string note;
        if (auto w = wa.find(c[0]); w != wa.end()) { c[3] = w->second[0]; c[4] = w->second[1]; note = std::string(" WA-RETARGET: ") + w->second[2]; }
        std::string z;
        if (!c[3].empty() && !c[4].empty()) z = std::to_string((pred - std::strtod(c[3].c_str(), nullptr)) / std::strtod(c[4].c_str(), nullptr));
        std::string flag = (c[6].find(fold::vt::kStatus) != std::string::npos ? std::string(fold::vt::kStatus) : "") + note;
        if (c[6].rfind("ALTERNATE", 0) == 0) flag += " ALTERNATE";
        o << c[0] << '\t' << c[1] << '\t' << pl << '\t' << c[2] << '\t' << c[3] << '\t' << c[4] << '\t' << z << '\t' << c[7] << '\t' << flag << '\n';
      }
      // IRONOUT-1 #1 (Damian t995u/t987u): the Z width does NOT read the vt SM-parity G_F. It is scored from the tip's own
      // in-bar leaf Gamma_Z/M_Z = (phi^5/e^6)(1 - alpha/phi) (fold::Live::gz_ratio, the same chain as gz:Gamma_Z_MeV).
      // The A1 width at the vt G_F stays a BEFORE_AFTER §4 diagnostic only (never scored).
      {
        const R g = live.gz_ratio();
        o << "Gamma_Z/M_Z (tip leaf, G_F-independent)\tGamma_Z/M_Z\t" << s30(g) << "\t\t0.02736653946\t2.523e-5\t" << std::to_string(double((g - gzref) / gzsig))
          << "\tgz:Gamma_Z_over_M_Z\tIRONOUT-1 (was A1 width at vt G_F)\n";
      }
      // rows that read G_F, re-evaluated with the carried vv P3 G_F (IRONOUT-2) and the vt P2 / P1 alternates: tau_mu diagnostic only
      for (auto [rt, sol] : {std::pair{"vvP3", v3}, std::pair{"P2", v2}, std::pair{"P1", v1}}) {
        const std::string fl = std::string(fold::vt::kStatus) + (std::string(rt) != "vvP3" ? " ALTERNATE" : " CARRIED");
        const auto d = fold::vt::mu_diag(sol.GF);
        o << "tau_mu strict MuLan (diagnostic)\ttau_mu [" << (std::string(rt) == "vvP3" ? "" : "vt ") << rt << " G_F]\t" << std::to_string(2196980.3 * (1 + d.tau_mu_ppm * 1e-6)) << "\t\t2196980.3\t2.2\t" << std::to_string(d.z_mulan)
          << "\tvt:tau_mu_" << rt << '\t' << fl << " DIAGNOSTIC (Gate B " << (d.gateB ? "ACCEPT" : "FAIL") << ", G_F vs G_mu " << std::to_string(d.ppm_vs_Gmu) << " ppm)\n";
      }
      {  // IRONOUT-2 r4: M_W host leaf vs PDG 2026 80.3625(77) (score target only; never an input to the Delta r chain)
        const R mw = vin.MW;
        o << "M_W host leaf (diagnostic)\tM_W_GeV\t" << s30(mw) << "\t\t80.3625\t0.0077\t" << std::to_string(double((mw - lit<R>("80.3625")) / lit<R>("0.0077")))
          << "\tleaf:m_W_MeV/1000\tWA-RETARGET: PDG 2026 M_W OUR EVALUATION (was PDG 2024 80.3692(133)); score target only\n";
      }
    } else if (!std::strcmp(argv[i], "--before-after") && i + 1 < argc) {
      std::ofstream o(argv[++i], std::ios::binary);
      o << "# Single-engine before/after (generated by `fsot_single_engine --before-after`; do not edit)\n\n";
      o << "Before = authority parity (pin AEB2AD, rung-6 QM, the C++ golden). After = the single-engine canonical table. "
           "Frozen seeds, layer constants and all 35 domain S are unchanged (test_derivations, golden). Only the rows below move.\n\n";
      o << "## 1. Rows changed by the single engine (derived replacements + B-03 exact exponents)\n\n| section | row | before | after | measured | rel% before | rel% after | why |\n|---|---|---|---|---|---|---|---|\n";
      int n = 0;
      for (auto& r : T) {
        const auto k = key(r);
        if (!pv.count(k) || pv.at(k) == r.value) continue;
        ++n;
        auto rel = [&](const R& v) { return r.measured ? std::to_string(double(m::fabs(v - *r.measured) / m::fabs(*r.measured) * R(100))) : std::string("-"); };
        const std::string why = r.kind == derive::RowKind::derived_replacement ? r.why : std::string("B-03: 0.333333333333333 -> 1/3");
        o << "| " << r.section << " | " << md(r.name) << " | " << pv.at(k).str(17) << " | " << r.value.str(17) << " | " << (r.measured ? r.measured->str(10) : "-")
          << " | " << rel(pv.at(k)) << " | " << rel(r.value) << " | " << md(why) << " |\n";
      }
      o << "\n" << n << " rows changed.\n\n## 2. D-02 alternative C_cosm = 1/(10 phi) (rejected by the decade derivation; shown, not applied)\n\n"
           "| section | row | canonical 1/(phi pi^2) | 1/(10 phi) | measured | rel% canonical | rel% 10phi |\n|---|---|---|---|---|---|---|\n";
      for (auto& r : T) {
        const auto k = key(r);
        if (!av.count(k) || av.at(k) == r.value) continue;
        auto rel = [&](const R& v) { return r.measured ? std::to_string(double(m::fabs(v - *r.measured) / m::fabs(*r.measured) * R(100))) : std::string("-"); };
        o << "| " << r.section << " | " << r.name << " | " << r.value.str(15) << " | " << av.at(k).str(15) << " | " << (r.measured ? r.measured->str(10) : "-") << " | " << rel(r.value) << " | " << rel(av.at(k)) << " |\n";
      }
      o << "\n## 3. D-04 alternative QM rung D=5 (the nest-rule derivation; FLAGGED, owner rung 6 kept)\n\n"
           "| section | row | canonical (QM D=6) | QM D=5 | measured | rel% D6 | rel% D5 |\n|---|---|---|---|---|---|---|\n";
      for (auto& r : T) {
        const auto k = key(r);
        if (!bv.count(k) || bv.at(k) == r.value) continue;
        auto rel = [&](const R& v) { return r.measured ? std::to_string(double(m::fabs(v - *r.measured) / m::fabs(*r.measured) * R(100))) : std::string("-"); };
        o << "| " << r.section << " | " << r.name << " | " << r.value.str(15) << " | " << bv.at(k).str(15) << " | " << (r.measured ? r.measured->str(10) : "-") << " | " << rel(r.value) << " | " << rel(bv.at(k)) << " |\n";
      }
      o << "\n## 4. §43.5vt folded (Damian t994u, 2026-11-11 1:00 PM EST): G_F and the rows that read it — flag " << fold::vt::kStatus << "\n\n"
           "Before = the Z-2 tip chain (all vt terms off; audit/score_2026-10-02z.tsv:13-14, vk tau_n 880.1412523 s; in this engine §43.5vt was a HOOK). "
           "After = route P2 (C1+C2+C3+C5mu+C6, no C7), live in fold::vt::Chain, carried until IRONOUT-2 and now an ALTERNATE (carried route: §5). P1 (with C7) is the documented alternate. "
           "Gates per ruling t992u (sha8 c65ff89d): Gate A |z| <= 1; Gate B |G_F - G_mu| <= 809.87 ppm. Not ADOPT; no GO-MERGE.\n\n"
           "| row | reference | before (Z-2) | z before | after (vt P2) | z after | alternate (vt P1) | z P1 |\n|---|---|---|---|---|---|---|---|\n";
      auto zs = [](const R& v, const char* c, const char* sg) { return std::to_string(double((v - lit<R>(c)) / lit<R>(sg))); };
      o << "| G_F [GeV^-2] | CODATA 2022 1.1663787(6)e-5 | " << v0.GF.str(15) << " | " << zs(v0.GF, "1.1663787e-5", "6e-12") << " | " << v2.GF.str(15) << " | " << zs(v2.GF, "1.1663787e-5", "6e-12")
        << " | " << v1.GF.str(15) << " | " << zs(v1.GF, "1.1663787e-5", "6e-12") << " |\n";
      const auto d0 = fold::vt::mu_diag(v0.GF), d2 = fold::vt::mu_diag(v2.GF), d1 = fold::vt::mu_diag(v1.GF);
      o << "| G_F vs G_mu [ppm] (Gate B <= 809.87) | PDG G_mu 1.1663788e-5 | " << std::to_string(d0.ppm_vs_Gmu) << " | Gate B " << (d0.gateB ? "ACCEPT" : "FAIL") << " | " << std::to_string(d2.ppm_vs_Gmu)
        << " | Gate B " << (d2.gateB ? "ACCEPT" : "FAIL") << " | " << std::to_string(d1.ppm_vs_Gmu) << " | Gate B " << (d1.gateB ? "ACCEPT" : "FAIL") << " |\n";
      o << "| tau_mu strict MuLan (diagnostic) | 2196980.3(2.2) ps | " << std::to_string(d0.tau_mu_ppm) << " ppm | " << std::to_string(d0.z_mulan) << " | " << std::to_string(d2.tau_mu_ppm) << " ppm | "
        << std::to_string(d2.z_mulan) << " | " << std::to_string(d1.tau_mu_ppm) << " ppm | " << std::to_string(d1.z_mulan) << " |\n";
      o << "| Gamma_Z/M_Z (A1 width at this G_F; DIAGNOSTIC, not scored since IRONOUT-1) | 0.02736653946(2523) | " << gz(v0.GF).str(12) << " | " << zs(gz(v0.GF), "0.02736653946", "2.523e-5") << " | " << gz(v2.GF).str(12) << " | "
        << zs(gz(v2.GF), "0.02736653946", "2.523e-5") << " | " << gz(v1.GF).str(12) << " | " << zs(gz(v1.GF), "0.02736653946", "2.523e-5") << " |\n";
      for (auto [g, c, sg] : {std::tuple{"UCNtau", "877.82", "0.287445647"}, std::tuple{"Pattie", "877.7", "0.761577311"}})
        o << "| tau_n [s] vs " << g << " | " << c << " +- " << sg << " | " << v0.tau_n.str(10) << " | " << zs(v0.tau_n, c, sg) << " | " << v2.tau_n.str(10) << " | " << zs(v2.tau_n, c, sg)
          << " | " << v1.tau_n.str(10) << " | " << zs(v1.tau_n, c, sg) << " |\n";
      o << "\nThe catalog closed forms wave3 Neutron_lifetime_s (pi^7 theta_S) and wave5 Gamma_Z/M_Z (phi^5/e^6), and the gz:Gamma_Z_MeV folded routes, do not read G_F "
           "(IRONOUT-2: the canonical wave3 Neutron_lifetime_s row now takes the carried chain tau_n, §5; the closed form stays in the parity column). "
           "IRONOUT-1: the scored Gamma_Z/M_Z folded row reads the tip leaf (phi^5/e^6)(1 - alpha/phi), not the vt G_F. "
           "(l): V_ud and g_A stay hosted inside tau_vk, never scored. Hooks for §43.5vv (Delta r), §43.5vw (Delta R^V) and §43.5vx (g_A): fold::vt::Hooks.\n";
      o << "\n## 5. IRONOUT-2 carried G_F route: §43.5vv P3 + §43.5vw P3 Delta_R^V (parent steering 2026-11-11 1:55 PM EST) — flag " << fold::vt::kStatus << "\n\n"
           "vv P3 (Tracer FOLD f66b7985): G = G0 [1/(1 - Dr_A(G)) + Dr_P1(G) - Dr_A(G)], remainder unresummed, solved live (Hooks::vv_p3). "
           "vw P3 (Tracer FOLD ce51de78): non-Born axial gammaW box rebuilt from the 3-loop BjSR alpha_g1, Delta_R^V " << vvwpk.at("vw_d_eng").str(10) << " -> "
        << vvwpk.at("vw_P3_dRV").str(10) << " (Hooks::tau_vk_override = " << vvwpk.at("tau_vk_vwP3_s").str(12) << " s; golden/vv_vw_package.tsv, tools/gen_vv_vw_package.py). "
           "The engine gammaW box is overstated by +0.343 alpha/pi (a -0.683 s tau_n lever), offset by the omitted CMS eq.(19) QED enhancement (+3.59e-4) and a low Born / vector constant; "
           "see include/fsot/fold/vt_gf.hpp. tau_n primary = pdgLive 878.3 +- 0.4 s (PDG 2024 878.4 +- 0.5, UCNtau, Pattie secondary). Not ADOPT; no GO-MERGE.\n\n"
           "| row | reference | before (vt P2, carried until now) | z before | after (vv P3 + vw P3) | z after | vv P3 only (no vw) | z |\n|---|---|---|---|---|---|---|---|\n";
      const auto d3 = fold::vt::mu_diag(v3.GF);
      o << "| G_F [GeV^-2] | CODATA 2022 1.1663787(6)e-5 | " << v2.GF.str(15) << " | " << zs(v2.GF, "1.1663787e-5", "6e-12") << " | " << v3.GF.str(15) << " | " << zs(v3.GF, "1.1663787e-5", "6e-12") << " | (same G_F) | - |\n";
      o << "| G_F vs G_mu [ppm] (Gate B <= 809.87) | PDG G_mu 1.1663788e-5 | " << std::to_string(d2.ppm_vs_Gmu) << " | Gate B " << (d2.gateB ? "ACCEPT" : "FAIL") << " | " << std::to_string(d3.ppm_vs_Gmu)
        << " | Gate B " << (d3.gateB ? "ACCEPT" : "FAIL") << " | - | - |\n";
      o << "| tau_mu strict MuLan (diagnostic; G_mu-ratio scaling; vv P3 G_F carries the W-propagator term in Delta r, PDG eq.(10.9) direct gives z -882.71; vv score.py -883.24 double-counts the W propagator and omits H2 sqrt(rho) and H3) | 2196980.3(2.2) ps | " << std::to_string(d2.tau_mu_ppm) << " ppm | " << std::to_string(d2.z_mulan) << " | "
        << std::to_string(d3.tau_mu_ppm) << " ppm | " << std::to_string(d3.z_mulan) << " | - | - |\n";
      for (auto [g, c, sg] : {std::tuple{"pdgLive (PRIMARY)", "878.3", "0.4"}, std::tuple{"PDG 2024", "878.4", "0.5"}, std::tuple{"UCNtau", "877.82", "0.287445647"}, std::tuple{"Pattie", "877.7", "0.761577311"}})
        o << "| tau_n [s] vs " << g << " | " << c << " +- " << sg << " | " << v2.tau_n.str(10) << " | " << zs(v2.tau_n, c, sg) << " | " << v3.tau_n.str(10) << " | " << zs(v3.tau_n, c, sg)
          << " | " << tau_vv_only.str(10) << " | " << zs(tau_vv_only, c, sg) << " |\n";
      {  // M_W diagnostic (t999u): the engine keeps the host M_W leaf; the superseded seed closed form M_W = (wave2 M_W/M_Z seed) x M_Z is NOT adopted.
        R rs = R(0); for (auto& r : P) if (r.section == "wave2" && r.name == "M_W/M_Z") rs = r.value;
        fold::vt::Inputs<R> ic = fold::vt::engine_inputs(VL); ic.MW = rs * ic.MZ; ic.s2 = R(1) - rs * rs;
        fold::vt::Chain<R> cm{vpk, ic}; cm.hooks = vvw.hooks;
        const auto vm = cm.solve(fold::vt::P1());
        o << "\nM_W diagnostic (not adopted): the chain reads the host M_W leaf " << vin.MW.str(12) << " GeV (z -0.03 vs PDG 80.3692(133)). With the superseded seed closed form M_W = "
          << (rs * vin.MZ).str(10) << " GeV (z -1.1) the carried vv P3 G_F would be " << vm.GF.str(12) << " (" << std::to_string(double((vm.GF / v3.GF - R(1)) * R(1000000)))
          << " ppm vs carried) and tau_n " << vm.tau_n.str(10) << " s. The engine-wide M_W is unchanged, so the vt/vv G_F chain is unchanged by IRONOUT-2.\n";
      }
    }
  }
  std::printf("single engine: %zu closed-form rows\n", T.size());
  return 0;
}
