// fsot/fold/folded_routes.hpp — dial-in PASS/INCLUDE routes folded into the engine.
//
// golden/folded_routes.tsv (tools/gen_folded_routes.py, from the dial-in ledger STATUS.tsv, sha256 recorded in its
// header) lists every folded leaf: the tip prediction the route scored, the held-out observation and sigma, and the
// recorded z. `live` names the engine function that re-derives the prediction here; live() below evaluates it, so a
// folded route is re-derived and re-scored by the engine on every ctest run instead of being trusted as a number.
// Excluded: 43.5vt (G_F) is a HOOK only (pending the muon-decay cross-check; G_F is tip-native only); (l): V_ud and g_A
// are never scored as targets here.
#pragma once
#include <optional>
#include <string>

#include "fsot/host/nucleon_radius.hpp"
#include "fsot/host/seed_leaves.hpp"

namespace fsot::fold {

template <class R> struct Live {
  const Engine<R>& F;
  const leaves::SeedLeaves<R>& L;
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
    if (key == "dm21:pathA") return m::ipow(F.POOF * F.G_CAT * F.P_NEW, 3);
    if (key == "host:sqrt8t0_over_r0") return leaves::sqrt8t0_over_r0<R>();
    if (key == "host:mu_p") return L.mu_p_host();
    if (key == "host:c_D") return L.c_D_host();
    if (key == "host:c_E") return L.c_E_host();
    if (key == "nucleon:r_v2_over_2") return nucleon::r_v2<R>(F, L).value / R(2);
    return std::nullopt;
  }
};

}  // namespace fsot::fold
