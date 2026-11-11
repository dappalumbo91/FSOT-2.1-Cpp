// fsot_single_engine — the consolidated FSOT engine table.
//   --table   <out.tsv>  every closed-form row: canonical (derived) value, authority-parity value, both D-02/D-04
//                        alternatives, measured, rel%, z (when the authority row carries sigma), row kind
//   --folded  <tsv> <out.tsv>  folded dial-in routes re-derived live and re-scored (input golden/folded_routes.tsv)
//   --before-after <out.md>    every row whose value differs from authority parity, and the variant deltas
//   §43.5vt (Damian t994u): the folded G_F / tau_n rows and every row that reads G_F carry SM_PARITY_REFINE_LATER
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

int main(int argc, char** argv) {
  Engine<R> canon(Mode::corrected), parity(Mode::parity), e10(Mode::corrected), d5(Mode::corrected);
  derive::with_c_cosm_10phi(e10);
  derive::with_qm_rung(d5, 5);
  auto T = derive::table(canon, true), P = derive::table(parity, false), A = derive::table(e10, true), B = derive::table(d5, true);
  std::map<std::string, R> pv, av, bv;
  for (auto& r : P) pv.emplace(key(r), r.value);
  for (auto& r : A) av.emplace(key(r), r.value);
  for (auto& r : B) bv.emplace(key(r), r.value);
  leaves::SeedLeaves<R> VL(canon);
  const auto vpk = fold::vt::Package<R>::load(FSOT_VT_PACKAGE_TSV);
  const fold::vt::Chain<R> vch{vpk, fold::vt::engine_inputs(VL)};
  const auto vin = fold::vt::engine_inputs(VL);
  const R s2h = fold::vt::leaf(VL, "sin2_theta_W_MSbar");
  const auto v0 = vch.solve(fold::vt::Route{false, false, false, false, false, false, false}), v2 = vch.solve(fold::vt::P2()), v1 = vch.solve(fold::vt::P1());
  const R gzref = lit<R>("0.02736653946"), gzsig = lit<R>("2.523e-5");  // audit/score_2026-10-02z.tsv:14 reference (published Gamma_Z/m_Z)
  auto gz = [&](const R& GF) { return fold::vt::gz_over_mz_A1(canon, GF, vin.MZ, s2h, vin.alpha); };
  for (int i = 1; i < argc; ++i) {
    if (!std::strcmp(argv[i], "--table") && i + 1 < argc) {
      std::ofstream o(argv[++i], std::ios::binary);
      o << "#section\tname\tformula\tkind\tvalue\tvalue_parity\tvalue_c_cosm_10phi\tvalue_qm_D5\tmeasured\tsigma\trel_pct\tz\tsensitive\n";
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
          if (r.sigma && *r.sigma > 0) o << double((r.value - *r.measured) / R(*r.sigma));
        } else o << "\t\t\t";
        o << '\t' << sens << '\n';
      }
    } else if (!std::strcmp(argv[i], "--folded") && i + 2 < argc) {
      std::ifstream in(argv[++i]); std::ofstream o(argv[++i], std::ios::binary);
      leaves::SeedLeaves<R> L(canon); fold::Live<R> live{canon, L, &vch};
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
        std::string z;
        if (!c[3].empty() && !c[4].empty()) z = std::to_string((pred - std::strtod(c[3].c_str(), nullptr)) / std::strtod(c[4].c_str(), nullptr));
        std::string flag = c[6].find(fold::vt::kStatus) != std::string::npos ? std::string(fold::vt::kStatus) : "";
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
      // rows that read G_F, re-evaluated with the folded vt G_F (P2 carried, P1 alternate): tau_mu diagnostic only
      for (auto [rt, sol] : {std::pair{"P2", v2}, std::pair{"P1", v1}}) {
        const std::string fl = std::string(fold::vt::kStatus) + (std::string(rt) == "P1" ? " ALTERNATE" : "");
        const auto d = fold::vt::mu_diag(sol.GF);
        o << "tau_mu strict MuLan (diagnostic)\ttau_mu [vt " << rt << " G_F]\t" << std::to_string(2196980.3 * (1 + d.tau_mu_ppm * 1e-6)) << "\t\t2196980.3\t2.2\t" << std::to_string(d.z_mulan)
          << "\tvt:tau_mu_" << rt << '\t' << fl << " DIAGNOSTIC (Gate B " << (d.gateB ? "ACCEPT" : "FAIL") << ", G_F vs G_mu " << std::to_string(d.ppm_vs_Gmu) << " ppm)\n";
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
        o << "| " << r.section << " | " << r.name << " | " << pv.at(k).str(17) << " | " << r.value.str(17) << " | " << (r.measured ? r.measured->str(10) : "-")
          << " | " << rel(pv.at(k)) << " | " << rel(r.value) << " | " << why << " |\n";
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
           "After = carried route P2 (C1+C2+C3+C5mu+C6, no C7), live in fold::vt::Chain. P1 (with C7) is the documented alternate. "
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
      o << "\nUnchanged: the catalog closed forms wave3 Neutron_lifetime_s (pi^7 theta_S) and wave5 Gamma_Z/M_Z (phi^5/e^6), and the gz:Gamma_Z_MeV folded routes, do not read G_F. "
           "IRONOUT-1: the scored Gamma_Z/M_Z folded row reads the tip leaf (phi^5/e^6)(1 - alpha/phi), not the vt G_F. "
           "(l): V_ud and g_A stay hosted inside tau_vk, never scored. Hooks for §43.5vv (Delta r), §43.5vw (Delta R^V) and §43.5vx (g_A): fold::vt::Hooks.\n";
    }
  }
  std::printf("single engine: %zu closed-form rows\n", T.size());
  return 0;
}
