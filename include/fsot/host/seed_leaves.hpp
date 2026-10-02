// fsot/host/seed_leaves.hpp — C++ port of the hub's committed seed leaves.
//
// Source: FSOT-2.1-Lean scripts/*_seed_check.py at ledger_b_data_commit 6f9c2560 (committed by
// dappalumbo91 2026-09-29 .. 2026-10-01; text in docs/TOE_ACCURACY_GOALS.md). Every leaf is a
// function of the pinned AEB2AD seeds only; the SI-exact constants (c, h, e, Cs hyperfine frequency,
// N_A) are the 2019 SI defining values. No coefficient was added or changed here. The original C++
// port covered only vendor/fsot_compute.py, so these leaves were missing from the C++ verification.
// golden/seed_leaves_6f9c2560.tsv is written by tools/dump_seed_leaves_golden.py, which runs the hub
// scripts unchanged; tests/test_seed_leaves.cpp compares every value below with it.
#pragma once
#include <cmath>
#include <map>
#include <string>
#include <vector>

#include "fsot/engine.hpp"

namespace fsot::leaves {

struct Leaf {
  std::string id;      // leaf id (golden key)
  std::string script;  // hub script that prints it
  std::string formula; // as committed in the hub
  std::string unit;
  long double value_ld;  // for reporting
  std::string value_str; // 50 significant digits (mp169) or repr (double)
};

// SI 2019 exact defining constants (used by the hub scripts as literals).
template <class R> struct SI {
  R c = lit<R>("299792458");
  R h = lit<R>("6.62607015e-34");
  R nu_Cs = lit<R>("9192631770");
  R e = lit<R>("1.602176634e-19");
  R N_A = lit<R>("6.02214076e23");
};

template <class R> struct SeedLeaves {
  const Engine<R>& F;
  SI<R> si;
  explicit SeedLeaves(const Engine<R>& eng) : F(eng) {}

  R ln2() const { return m::ln(R(2)); }
  R yy() const { return (F.POOF * F.SUCTION) * (F.POOF * F.SUCTION); }
  // alpha leaf: 1/alpha = e^3 phi^4 - psi_con - (POOF*SUCTION)^2 C_factor^2 / P_base   (alpha_interface_seed_check.py)
  R alpha_inv() const {
    return m::ipow(F.E, 3) * m::ipow(F.PHI, 4) - F.PSI_CON - yy() * F.C_FACTOR * F.C_FACTOR / F.P_BASE;
  }
  R alpha() const { return R(1) / alpha_inv(); }
  // electron g: 2(1 + (e/pi - ln2)/e^5 - (alpha/pi)^3 * A_bleed G^2 P_base / P_new)   (electron_g_seed_check.py)
  R g_e() const {
    const R bare = (F.E / F.PI - ln2()) / m::ipow(F.E, 5);
    const R third = m::ipow(alpha() / F.PI, 3);
    const R weight = F.A_BLEED * F.G_CAT * F.G_CAT * F.P_BASE / F.P_NEW;
    return R(2) * (R(1) + (bare - third * weight));
  }
  // electron mass: h nu_Cs / c^2 * exp(e^pi + (C_factor K ln2)^2 + G P_new psi_con - alpha^5 phi^2 / ln2^2)
  R m_e_kg() const {
    const R ex = m::pow(F.E, F.PI) + m::ipow(F.C_FACTOR * F.K * ln2(), 2) + F.G_CAT * F.P_NEW * F.PSI_CON -
                 m::ipow(alpha(), 5) * m::ipow(F.PHI, 2) / m::ipow(ln2(), 2);
    return si.h * si.nu_Cs / (si.c * si.c) * m::exp(ex);
  }
  R m_e_MeV() const { return m_e_kg() * si.c * si.c / si.e / lit<R>("1e6"); }
  R mev(const R& kg) const { return kg * si.c * si.c / si.e / lit<R>("1e6"); }
  R proton_ratio() const {
    return R(6) * m::ipow(F.PI, 5) + ln2() / m::ipow(F.E, 3) + alpha() * alpha() * (R(1) + F.PSI_CON / m::ipow(F.E, 3));
  }
  R neutron_delta() const { return F.E * yy() - F.B_IN / (F.P_NEW * m::ipow(F.E, 13)); }
  R g_p() const {
    return m::ipow(F.A_IN * F.P_NEW / F.P_BASE, 2) + (alpha() / m::ipow(F.PSI_CON, 3)) * (R(1) + yy() * yy());
  }
  R w_product() const { return m::pow(F.THETA_S, R(-6)) * m::pow(F.C_FACTOR, R(-4)) * F.GAMMA * F.GAMMA; }
  R m_W_MeV() const { return w_product() + m::pow(F.E, F.E); }
  R m_Z_MeV() const { return w_product() / m::sqrt(R(1) - (F.POOF + F.K / R(6))); }
  R pion_MeV() const { return m::pow(F.THETA_S, R(-4)) - F.THETA_S * F.THETA_S + alpha() / (F.PI - R(1)); }
  R tau_ratio() const { return m::ipow(F.PI, 7) * m::ln(F.PI) + m::ipow(F.E, 3); }

  // id -> value (mp leaves). Order = golden order.
  std::vector<std::pair<std::string, R>> mp_values() const {
    const R me = m_e_kg(), a = alpha(), c = si.c, h = si.h, pi = F.PI;
    const R compton = h / (me * c);
    const R radius = a * compton / (R(2) * pi);
    const R mp_kg = proton_ratio() * me;
    const R mn_kg = mp_kg * (R(1) + neutron_delta());
    const R ratio_mu = (m::ipow(F.PI, 3) - F.G_CAT * F.G_CAT) * m::ipow(F.PHI, 4) -
                       F.E * yy() * ln2() * F.P_NEW / F.P_BASE;
    const R ratio_u = R(6) * m::ipow(F.PI, 5) - F.PI * m::ipow(F.PHI, 3) + F.GAMMA / m::ipow(F.E, 2) +
                      a * ln2() / m::ipow(F.E, 3) + F.K * F.PI / m::ipow(F.E, 12);
    const R grav_first = m::ipow(F.E, 2) * m::ipow(F.PHI, 3) / m::ipow(ln2(), 3);
    const R grav_second = F.PHI * F.OMEGA / (F.GAMMA * F.GAMMA * ln2());
    const R G = h / (R(2) * pi) * c / (me * me) * m::exp(-(grav_first + grav_second));
    const R he_bare = F.PI / m::ipow(F.GAMMA, 4);
    const R h3_bare = m::ipow(F.E, 2) + R(1) / F.G_CAT;
    return {
        {"alpha_inv", alpha_inv()},
        {"g_e", g_e()},
        {"m_e_kg", me},
        {"R_inf", a * a * me * c / (R(2) * h)},
        {"a_0", h / (R(2) * pi * me * c * a)},
        {"lambda_C", compton},
        {"r_e", radius},
        {"sigma_T", R(8) * pi * radius * radius / R(3)},
        {"E_h", a * a * me * c * c},
        {"mu_B", si.e * h / (R(4) * pi * me)},
        {"m_p_over_m_e", proton_ratio()},
        {"m_p_kg", mp_kg},
        {"mu_N", si.e * h / (R(4) * F.PI * mp_kg)},
        {"m_n_over_m_p", R(1) + neutron_delta()},
        {"m_n_kg", mn_kg},
        {"G_N", G},
        {"g_p", g_p()},
        {"m_mu_over_m_e", ratio_mu},
        {"m_mu_kg", ratio_mu * me},
        {"u_over_m_e", ratio_u},
        {"u_kg", ratio_u * me},
        {"M_12C", R(12) * si.N_A * ratio_u * me},
        {"m_Z_MeV", m_Z_MeV()},
        {"m_tau_MeV", tau_ratio() * m_e_MeV()},
        {"r_p_fm", m::ipow(F.G_CAT, 7) + F.P_NEW},
        {"m_pi_pm_MeV", pion_MeV()},
        {"m_D_pm_MeV", m::ipow(F.P_VAR / F.P_BASE, 5) + F.PI / R(4)},
        {"m_K_pm_MeV", m::pow(F.G_CAT, R(-7)) + m::pow(F.P_BASE, R(-4)) - m::pow(F.PI, R(-4))},
        {"m_c_over_m_b", F.C_COSM / F.P_BASE + a * m::sqrt(F.PHI)},
        {"m_W_MeV", m_W_MeV()},
        {"m_W_over_m_Z", m_W_MeV() / m_Z_MeV()},
        {"m_pi_over_m_p", pion_MeV() / mev(mp_kg)},
        {"mu_p_over_mu_N", g_p() / R(2)},
        {"m_n_minus_m_p_MeV", mev(mn_kg) - mev(mp_kg)},
        {"m_H_MeV", (F.THETA_S + m::ipow(F.E, 3)) / m::ipow(F.C_FACTOR, 7)},
        {"m_t_over_m_W", m::fabs(F.S_COSM) / m::fabs(F.CHAOS) + F.PSI_CON},
        {"sin2_theta_W_MSbar", (F.GAMMA - R(1) / m::ipow(F.PI, 2)) / m::pow(F.PHI, lit<R>("1.5")) + a * a},
        {"m_tau_over_m_e", tau_ratio()},
        {"dm2_32", m::ipow(F.G_CAT * F.SUCTION, 3) * (R(1) + yy())},
        {"B_He4_MeV", he_bare * (R(1) - a * a * (F.PI + F.P_BASE))},
        {"B_H3_MeV", h3_bare * (R(1) + yy() * (F.GAMMA * F.PSI_CON * F.PSI_CON))},
    };
  }
};

// CKM magnitudes: vendor/fsot_seed_flavor.py evaluates in IEEE double from float(seed); |V_cs| uses the
// second-row identity sqrt(1 - lambda^2 - A^2 lambda^4) as committed in ckm_magnitude_seed_check.py
// (the raw seed_ckm_magnitudes() dict stores |V_ud| under the V_cs key; see docs/AUDIT_LOG.md H-03).
// Operation order mirrors the Python so the doubles are bit-identical (no FMA: -ffp-contract=off).
struct CKM { double lam, A, rhob, etab; std::map<std::string, double> mags; };
template <class R> CKM ckm_double(const Engine<R>& F) {
  auto f = [](const R& x) { return static_cast<double>(x); };
  CKM k;
  k.lam = f(F.POOF) * (1.0 + f(F.ETA_EFF));
  k.A = f(F.E) / (f(F.PI) * f(F.A_BLEED));
  k.rhob = f(F.GAMMA) * f(F.E) / std::pow(f(F.PI), 2.0);
  k.etab = std::pow(f(F.G_CAT), 2.0) * f(F.K);
  const double lam = k.lam, A = k.A, rhob = k.rhob, etab = k.etab;
  const double fac = 1.0 - 0.5 * lam * lam;
  const double rho = rhob / fac, eta = etab / fac;
  const double r_b = std::sqrt(rho * rho + eta * eta);
  const double r_t = std::sqrt(std::pow(1.0 - rhob, 2.0) + etab * etab);
  const double v_ud = std::sqrt(std::max(1.0 - lam * lam, 0.0));
  k.mags["V_ud"] = v_ud;
  k.mags["V_us"] = lam;
  k.mags["V_ub"] = A * std::pow(lam, 3.0) * r_b;
  k.mags["V_cd"] = lam;
  k.mags["V_cs"] = std::pow(1.0 - lam * lam - (A * A) * std::pow(lam, 4.0), 0.5);
  k.mags["V_cb"] = A * std::pow(lam, 2.0);
  k.mags["V_td"] = A * std::pow(lam, 3.0) * r_t;
  k.mags["V_ts"] = A * std::pow(lam, 2.0) * (1.0 - std::pow(lam, 2.0) * (0.5 - rhob));
  k.mags["V_tb"] = 1.0 - 0.5 * std::pow(A, 2.0) * std::pow(lam, 4.0);
  return k;
}

}  // namespace fsot::leaves
