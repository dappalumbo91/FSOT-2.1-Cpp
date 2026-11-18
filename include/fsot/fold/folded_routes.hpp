// fsot/fold/folded_routes.hpp — dial-in PASS/INCLUDE routes folded into the engine.
//
// golden/folded_routes.tsv (tools/gen_folded_routes.py, from the dial-in ledger STATUS.tsv, sha256 recorded in its
// header) lists every folded leaf: the tip prediction the route scored, the held-out observation and sigma, and the
// recorded z. `live` names the engine function that re-derives the prediction here; live() below evaluates it, so a
// folded route is re-derived and re-scored by the engine on every ctest run instead of being trusted as a number.
// IRONOUT-2: the carried G_F route is §43.5vv P3 + §43.5vw P3 Delta_R^V (keys vvw:*); vt P2/P1 are alternates.
// 43.5vt (G_F, τ_n) is folded flagged SM_PARITY_REFINE_LATER (Damian t994u; ruling t992u c65ff89d): carried P2,
// alternate P1, both re-derived by fold::vt::Chain (vt_gf.hpp). (l): V_ud and g_A are never scored as targets here.
#pragma once
#include <optional>
#include <string>

#include "fsot/host/nucleon_radius.hpp"
#include "fsot/host/seed_leaves.hpp"
#include "fsot/fold/vt_gf.hpp"

namespace fsot::fold {

template <class R> struct Live {
  const Engine<R>& F;
  const leaves::SeedLeaves<R>& L;
  const vt::Chain<R>* vt = nullptr;  // §43.5vt chain (keys vt:*); nullptr -> vt keys unresolved (test FAIL)
  const vt::Chain<R>* vvw = nullptr;  // IRONOUT-2 carried chain: vv P3 G_F + vw P3 Delta_R^V (keys vvw:*)
  // Gamma_Z = M_Z * (phi^5/e^6)(1 - alpha/phi): catalog leaf Gamma_Z/M_Z (PHYSICAL_MAP leaf:Gamma_Z/M_Z), alpha = leaf.
  R gz_ratio() const { return m::ipow(F.PHI, 5) / m::ipow(F.E, 6) * (R(1) - L.alpha() / F.PHI); }
  std::optional<R> operator()(const std::string& key) const {
    if (key == "leaf:m_W_MeV") return L.m_W_MeV();
    if (key == "leaf:m_Z_MeV") return L.m_Z_MeV();
    if (key == "leaf:m_tau_MeV") return L.tau_ratio() * L.m_e_MeV();
    if (key == "leaf:m_D_pm_MeV") return m::ipow(F.P_VAR / F.P_BASE, 5) + F.PI / R(4);
    if (key == "leaf:m_K_pm_MeV") return m::pow(F.G_CAT, R(-7)) + m::pow(F.P_BASE, R(-4)) - m::pow(F.PI, R(-4));
    if (key == "leaf:r_p_fm") return m::ipow(F.G_CAT, 7) + F.P_NEW;
    if (key == "leaf:m_H_GeV") return (F.THETA_S + m::ipow(F.E, 3)) / m::ipow(F.C_FACTOR, 7) / R(1000);
    if (key == "leaf:dm2_32") return m::ipow(F.G_CAT * F.SUCTION, 3) * (R(1) + L.yy());
    if (key == "gz:Gamma_Z_MeV") return L.m_Z_MeV() * gz_ratio();
    if (key == "gz:Gamma_Z_over_M_Z") return gz_ratio();  // IRONOUT-1: Z width never reads the vt G_F
    if (key == "dm21:pathA") return m::ipow(F.POOF * F.G_CAT * F.P_NEW, 3);
    if (key == "host:sqrt8t0_over_r0") return leaves::sqrt8t0_over_r0<R>();
    if (key == "host:mu_p") return L.mu_p_host();
    if (key == "host:c_D") return L.c_D_host();
    if (key == "host:c_E") return L.c_E_host();
    if (key == "nucleon:r_v2_over_2") return nucleon::r_v2<R>(F, L).value / R(2);
    if (vt && key.rfind("vt:", 0) == 0) {
      const bool p1 = key.size() > 3 && key.compare(key.size() - 3, 3, "_P1") == 0;
      const auto s = vt->solve(p1 ? vt::P1() : vt::P2());
      if (key.rfind("vt:tau_n_", 0) == 0) return s.tau_n;
      if (key.rfind("vt:G_F_", 0) == 0) return s.GF;
    }
    if (vvw && key.rfind("vvw:", 0) == 0) {
      const auto s = vvw->solve(vt::P1());  // route ignored: Hooks::vv_p3 selects the vv P3 fixed point
      if (key == "vvw:tau_n") return s.tau_n;
      if (key == "vvw:G_F") return s.GF;
      if (key == "vvw:G_F_noW") return s.GF_noW;
      if (key == "vvw:tau_n_vvP3") return vvw->pk.at("tau_vk_s") / (s.ratio * s.ratio);
    }
    return std::nullopt;
  }
};

}  // namespace fsot::fold
