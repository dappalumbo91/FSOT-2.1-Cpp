// §43.5vt folded (Damian t994u): G_F and τ_n from the tip-native Δr chain, live in the engine. Flag SM_PARITY_REFINE_LATER.
#include <cmath>
#include <cstdio>
#include <string>
#include <tuple>

#include "fsot/fold/folded_routes.hpp"
#include "fsot/fold/vt_gf.hpp"

using namespace fsot;
static int fails = 0;
template <class R> static void eq(const char* what, const R& v, const char* ref, double tol) {
  const R r = lit<R>(ref); const double rel = double(m::fabs(v - r) / m::fabs(r));
  const bool ok = rel <= tol; if (!ok) ++fails;
  std::printf("  [%s] %-46s %s vs %s (rel %.2e, tol %.0e)\n", ok ? "PASS" : "FAIL", what, v.str(18).c_str(), ref, rel, tol);
}
int main() {
#if !defined(FSOT_HAVE_BOOST_MP)
  std::puts("VT G_F: skipped (needs Boost.Multiprecision)"); return 0;
#else
  using R = mp169;
  const auto pk = fold::vt::Package<R>::load(FSOT_VT_PACKAGE_TSV);
  std::printf("%s\nstatus flag: %s\n", pk.header.c_str(), fold::vt::kStatus);
  Engine<R> F; leaves::SeedLeaves<R> L(F);
  const auto in = fold::vt::engine_inputs(L);
  std::puts("electroweak inputs: engine seed leaves vs banked vt package");
  eq("M_W", in.MW, pk.at("MW_GeV").str(50).c_str(), 1e-40); eq("M_Z", in.MZ, pk.at("MZ_GeV").str(50).c_str(), 1e-40);
  eq("alpha", in.alpha, pk.at("alpha").str(50).c_str(), 1e-40); eq("s_W^2", in.s2, pk.at("s2").str(50).c_str(), 1e-40);
  eq("m_t", in.mt, pk.at("mt_GeV").str(50).c_str(), 1e-40);
  eq("M_H", fold::vt::leaf(L, "m_H_MeV") / R(1000), pk.at("mH_GeV").str(50).c_str(), 1e-40);
  fold::vt::Chain<R> ch{pk, in};
  const auto p0 = ch.solve_raw(fold::vt::P0()), p2 = ch.solve(fold::vt::P2()), p1 = ch.solve(fold::vt::P1());
  std::puts("fixed points vs tracer results.tsv / score_stdout.txt (90b5458e / cabadc6c)");
  eq("P0 G_chain (Z-2 re-solve)", p0.G, "1.165384508425289e-5", 1e-15);
  eq("P0 G_chain vs carried Z-2 G_F (12 digits)", p0.G, "1.16538450843e-5", 5e-12);
  eq("P2 G_F,vt (carried)", p2.GF, "1.16690544271959e-5", 1e-14);
  eq("P2 tau_n [s]", p2.tau_n, "877.8484108", 1e-10);
  eq("P2 Delta r", p2.dr, "0.0364340402878", 1e-11); eq("P2 Delta rho", p2.drho, "0.00809677124308", 1e-11);
  eq("P2 Delta r_rem", p2.rem, "0.0041710867212", 1e-11); eq("P2 C5mu", p2.c5mu, "0.001398696172", 1e-9);
  eq("P2 ratio-1 [ppm vs Z-2]", (p2.ratio - R(1)) * R(1000000), "1305.0922", 1e-7);
  eq("P1 G_F,vt (alternate, with C7)", p1.GF, "1.16704997054391e-5", 1e-14);
  eq("P1 tau_n [s]", p1.tau_n, "877.6309982", 1e-10); eq("P1 Delta r", p1.dr, "0.0365533685902", 1e-11);
  eq("P1 C7", p1.c7, "0.000122335156", 1e-8);
  std::printf("  iterations P0 %d P1 %d P2 %d (tracer 20/19/19), last step P2 %.1e\n", p0.iterations, p1.iterations, p2.iterations, double(p2.last_step));
  const double zu = double((p2.tau_n - lit<R>("877.82")) / lit<R>("0.287445647")), zp = double((p2.tau_n - lit<R>("877.7")) / lit<R>("0.761577311"));
  std::printf("  P2 tau_n z UCNtau %+.6f (tracer +0.098839) Pattie %+.6f (+0.19487)\n", zu, zp);
  if (std::fabs(zu - 0.098839) > 2e-6 || std::fabs(zp - 0.19487) > 2e-5) ++fails;
  // rows that read G_F: authority A1 Γ_Z/M_Z (tools/fsot02d.py compute(GF_override)), checked at the Z-2 G_F first.
  const R s2h = fold::vt::leaf(L, "sin2_theta_W_MSbar");
  eq("Gamma_Z/M_Z A1 at Z-2 G_F (audit 02z.tsv:14)", fold::vt::gz_over_mz_A1(F, pk.at("GF_Z2"), in.MZ, s2h, in.alpha), "0.027240443295", 5e-12);
  const R gz2 = fold::vt::gz_over_mz_A1(F, p2.GF, in.MZ, s2h, in.alpha);
  std::printf("  Gamma_Z/M_Z A1 at vt P2 G_F = %s  z %+.4f (was %+.4f at Z-2)  [%s]\n", gz2.str(15).c_str(),
              double((gz2 - lit<R>("0.02736653946")) / lit<R>("2.523e-5")),
              double((fold::vt::gz_over_mz_A1(F, pk.at("GF_Z2"), in.MZ, s2h, in.alpha) - lit<R>("0.02736653946")) / lit<R>("2.523e-5")), fold::vt::kStatus);
  // IRONOUT-1 #1: the scored Z width reads the tip leaf (phi^5/e^6)(1 - alpha/phi), not any G_F; it must stay in bar.
  {
    fold::Live<R> lv{F, L, nullptr};
    const auto gzl = lv("gz:Gamma_Z_over_M_Z");
    const double zl = gzl ? double((*gzl - lit<R>("0.02736653946")) / lit<R>("2.523e-5")) : 99;
    std::printf("  IRONOUT-1 Gamma_Z/M_Z tip leaf = %s  z %+.4f (G_F-independent; A1-at-vt-G_F is diagnostic only)\n", gzl ? gzl->str(15).c_str() : "?", zl);
    if (!gzl || std::fabs(zl) > 1 || *gzl != lv.gz_ratio()) ++fails;
  }
  // ruling t992u diagnostics
  for (auto [nm, s, ppm, z] : {std::tuple{"P2", p2, 451.52, -901.2}, std::tuple{"P1", p1, 575.43, -1148.3}}) {
    const auto d = fold::vt::mu_diag(s.GF);
    std::printf("  %s: G_F vs G_mu %+.2f ppm (ruling %+.2f), tau_mu %+.1f ppm, strict MuLan z %+.1f (ruling %+.1f); Gate A %s, Gate B %s\n", nm, d.ppm_vs_Gmu, ppm,
                d.tau_mu_ppm, d.z_mulan, z, d.gateA ? "PASS" : "FAIL", d.gateB ? "ACCEPT-AT-SM-PARITY" : "FAIL");
    if (std::fabs(d.ppm_vs_Gmu - ppm) > 0.01 || std::fabs(d.z_mulan - z) > 0.1 || d.gateA || !d.gateB) ++fails;
  }
  // hooks: empty / neutral hook values reproduce the folded route exactly
  fold::vt::Chain<R> h = ch; h.hooks.vv_rem_add = R(0); h.hooks.tau_vk_override = pk.at("tau_vk_s");
  const auto ph = h.solve(fold::vt::P2());
  if (ph.GF != p2.GF || ph.tau_n != p2.tau_n) { ++fails; std::puts("  [FAIL] neutral hooks change the result"); }
  else std::puts("  [PASS] hooks vv_rem_add=0 / tau_vk_override=tau_vk reproduce P2 bit-identically");
  fold::vt::Chain<R> hr = ch; hr.hooks.vv_route = fold::vt::P1();
  if (hr.solve(fold::vt::P2()).GF != p1.GF) { ++fails; std::puts("  [FAIL] vv_route hook"); } else std::puts("  [PASS] hook vv_route swaps the term set (P2 -> P1 reproduces P1)");
  // Live keys used by golden/folded_routes.tsv
  fold::Live<R> live{F, L, &ch};
  if (!live("vt:G_F_P2") || *live("vt:G_F_P2") != p2.GF || !live("vt:tau_n_P1") || *live("vt:tau_n_P1") != p1.tau_n) { ++fails; std::puts("  [FAIL] live vt keys"); }
  // IRONOUT-2: carried vv P3 G_F + vw P3 Delta_R^V (Tracer vv FOLD f66b7985, vw FOLD ce51de78), reproduced live to ~1e-12
  {
    const auto vvw = fold::vt::Package<R>::load(FSOT_VV_VW_PACKAGE_TSV);
    std::printf("vv/vw package: %s\n", vvw.header.empty() ? "(header)" : vvw.header.c_str());
    fold::vt::Chain<R> c3 = ch; c3.hooks = fold::vt::vv_p3_vw_p3(vvw);
    const auto raw = c3.solve_raw_vv_p3(), p0r = c3.solve_raw(fold::vt::P0());
    eq("vv OFF G_chain (vv score.py build)", p0r.G, vvw.at("vv_OFF_G_chain").str(50).c_str(), 1e-25);
    eq("vv P3 G_chain (solve_P3, live)", raw.G, vvw.at("vv_P3_G_chain").str(50).c_str(), 1e-25);
    eq("vv A  Dr check: P1 G_chain (vt solve) ", c3.solve_raw(fold::vt::P1()).G, vvw.at("vv_P1_G_chain").str(50).c_str(), 1e-25);
    const auto s3 = c3.solve(fold::vt::P1());
    eq("vv P3 G_F [GeV^-2] (FOLD 1.16689392890418e-5)", s3.GF, "1.16689392890418e-5", 1e-14);
    eq("vv P3 G_F vs package (50 digits)", s3.GF, vvw.at("vv_P3_GF").str(50).c_str(), 1e-25);
    eq("vv P3 tau_n (no vw) [s] (FOLD 877.8657345)", pk.at("tau_vk_s") / (s3.ratio * s3.ratio), "877.8657345", 1e-10);
    eq("vv P3 tau_n (no vw) vs package", pk.at("tau_vk_s") / (s3.ratio * s3.ratio), vvw.at("vv_P3_tau_n_s").str(50).c_str(), 1e-12);
    eq("vv P3 + vw P3 tau_n [s] (FOLD 878.4325396)", s3.tau_n, "878.4325396", 1e-10);
    eq("vv P3 + vw P3 tau_n vs vw score.py tau_of", s3.tau_n, vvw.at("vw_P3_tau_n_s").str(50).c_str(), 1e-12);
    eq("vw P3 Delta_R^V (FOLD 0.02380031545)", vvw.at("vw_P3_dRV"), "0.02380031545", 1e-10);
    eq("vw d_eng == vt package vk_dRV_us", vvw.at("vw_d_eng"), pk.at("vk_dRV_us").str(50).c_str(), 1e-28);
    const auto d = fold::vt::mu_diag(s3.GF);
    std::printf("  vv P3: G_F vs G_mu %+.2f ppm (FOLD +441.65), strict MuLan z %+.2f (FOLD -883.24); Gate B %s; flag %s\n", d.ppm_vs_Gmu, d.z_mulan,
                d.gateB ? "ACCEPT-AT-SM-PARITY" : "FAIL", fold::vt::kStatus);
    if (std::fabs(d.ppm_vs_Gmu - 441.65) > 0.01 || !d.gateB) ++fails;
    // tau_n vs the IRONOUT-2 primary (pdgLive 878.3 +- 0.4): Tracer re-score vw P3 z +0.331
    const double zl = double((s3.tau_n - lit<R>("878.3")) / lit<R>("0.4"));
    std::printf("  [%s] vv P3 + vw P3 tau_n z vs pdgLive 878.3(4) = %+.4f (Tracer +0.331)\n", std::fabs(zl - 0.331) < 5e-4 ? "PASS" : "FAIL", zl);
    if (std::fabs(zl - 0.331) >= 5e-4) ++fails;
    fold::Live<R> lv{F, L, &ch, &c3};
    if (!lv("vvw:tau_n") || *lv("vvw:tau_n") != s3.tau_n || !lv("vvw:G_F") || *lv("vvw:G_F") != s3.GF) { ++fails; std::puts("  [FAIL] live vvw keys"); }
    // vt P2 stays reproducible as the alternate (unchanged by the hooks on the separate chain)
    if (ch.solve(fold::vt::P2()).GF != p2.GF) { ++fails; std::puts("  [FAIL] vt P2 alternate moved"); } else std::puts("  [PASS] vt P2 alternate unchanged");
  }
  // double instantiation sanity (package read at double)
  { const auto pd = fold::vt::Package<double>::load(FSOT_VT_PACKAGE_TSV); Engine<double> Fd; leaves::SeedLeaves<double> Ld(Fd);
    fold::vt::Chain<double> cd{pd, fold::vt::engine_inputs(Ld)}; const double g = cd.solve(fold::vt::P2()).GF;
    const double rel = std::fabs(g / 1.16690544271959e-5 - 1); std::printf("  [%s] double P2 G_F %.15g (rel %.1e)\n", rel < 1e-12 ? "PASS" : "FAIL", g, rel); if (rel >= 1e-12) ++fails; }
  std::puts(fails ? "VT G_F: FAIL" : "VT G_F: ALL PASS");
  return fails ? 1 : 0;
#endif
}
