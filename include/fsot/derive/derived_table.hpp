// fsot/derive/derived_table.hpp — the single-engine table: the authority's closed forms with every literal-only or
// measured-input row replaced by the engine's own derived value where one exists.
//
//   * B-03 cube-root exponents: Mode::corrected (exact p/q instead of the 15-digit 0.333333333333333 literal).
//   * DNA_base_pair: a0 = 0.529177 (measured Bohr radius, 6 decimals) -> the seed leaf a_0 (seed_leaves.hpp, 1e10 * m).
//   * Proton_radius: formula "exact", value = target literal 0.8413 -> the seed leaf r_p = G^7 + P_new.
//   * Definition rows (STDP_Tau_*_ms = 20, Metatron_* = 13/27, Max_Trits = 27, Potts3_beta = 1/9, Quark_condensate = 1/4):
//     no seed derivation exists; kept, tagged "definition", and never scored.
// Variants for the two FLAGGED/derived constants are produced by re-seating the engine members the closed forms read:
//   with_qm_rung(5): S_QUANT and the QM domain at the nest-rule rung (D-04 alternative);
//   with_c_cosm_10phi(): C_COSM = 1/(10 phi) (D-02 alternative; the derivation rejects it, kept for the before/after).
#pragma once
#include <map>
#include <set>
#include <string>
#include <vector>

#include "fsot/host/seed_leaves.hpp"

namespace fsot::derive {

enum class RowKind { seed, derived_replacement, definition };
inline const char* kind_name(RowKind k) { return k == RowKind::seed ? "seed" : k == RowKind::derived_replacement ? "derived-replacement" : "definition"; }
inline bool is_definition_row(const std::string& n) {
  static const std::set<std::string> d = {"STDP_Tau_Plus_ms", "STDP_Tau_Minus_ms", "Metatron_Spheres", "Metatron_Pathways",
                                          "Max_Trits", "Potts3_beta", "Quark_condensate"};
  return d.count(n) > 0;
}

template <class R> struct Row {
  std::string section, name, formula;
  R value;
  std::optional<R> measured;
  std::optional<double> sigma;
  RowKind kind = RowKind::seed;
  std::string why;  // derived replacements: one-line provenance (BEFORE_AFTER §1)
};

template <class R> void with_qm_rung(Engine<R>& F, int D) {
  for (auto& d : F.DOMAINS) if (d.name == "Quantum_Mechanics") d.D_eff = D;
  F.S_QUANT = F.domain_scalar("Quantum_Mechanics");
}
template <class R> void with_c_cosm_10phi(Engine<R>& F) {
  F.C_COSM = R(1) / (R(10) * F.PHI);
  for (auto& d : F.DOMAINS) if (d.name == "Cosmology") d.C = F.C_COSM;
}

// IRONOUT-1 (Damian t995u/t987u, 2026-11-11): rows the scorecard put outside what standard science accepts, re-derived
// from rows the engine already has IN BAR. Nothing measured is pasted, no parameter is fitted, the authority closed
// forms (and the parity column) are untouched; only the canonical value of the rows below moves.
//  #2 critical exponents, d = 3, from the engine's in-bar pair via the standard scaling relations
//     (Josephson d nu = 2 - alpha; Rushbrooke alpha + 2 beta + gamma = 2; Fisher gamma = nu (2 - eta); Widom gamma = beta (delta - 1)):
//     3D Ising from dynamical_systems Ising3D_nu_dyn / Ising3D_beta_dyn; O(2)/XY from wave7 XY_nu / XY_eta (both in bar).
//     The wave3 rows keyed "Ising2D_*" carry 3D targets (2D Ising is exact: beta 1/8, nu 1, gamma 7/4): RELABELED 3D in the
//     formula column; the archive key is kept so the parity/archive cross-check (tools/check.py [10]) still resolves.
//     O(3)/Heisenberg: no in-bar nu/beta/eta exists in the engine -> not touched.
//  #3 IE_H from the engine's own in-bar leaves: R_inf h c (seed leaf R_inf = alpha^2 m_e c / 2h), reduced mass m_p/m_e
//     (seed leaf), Dirac 1s binding mu c^2 [1 - sqrt(1 - alpha^2)], and the one-loop 1s Lamb shift
//     (4 alpha^5 m c^2 / 3 pi)[ln(1/alpha^2) - ln k0(1s) + 19/30] with the 1s Bethe logarithm ln k0 = 2.984128555765
//     (a pure number of the Coulomb problem; Drake & Swainson, PRA 41, 1243 (1990)); e = 1.602176634e-19 C exact (SI 2019).
template <class R> void ironout1(const Engine<R>& F, const leaves::SeedLeaves<R>& L, std::vector<Row<R>>& out) {
  auto find = [&](const char* sec, const char* nm) -> Row<R>* {
    for (auto& r : out) if (r.section == sec && r.name == nm) return &r;
    return nullptr;
  };
  auto set = [&](const char* sec, const char* nm, const R& v, const std::string& formula, const std::string& why) {
    if (auto* r = find(sec, nm)) { r->value = v; r->formula = formula; r->kind = RowKind::derived_replacement; r->why = why; }
  };
  const R d = R(3);
  if (auto *pn = find("dynamical_systems", "Ising3D_nu_dyn"), *pb = find("dynamical_systems", "Ising3D_beta_dyn"); pn && pb) {
    const R nu = pn->value, be = pb->value, al = R(2) - d * nu, ga = d * nu - R(2) * be, et = R(2) - ga / nu, de = R(1) + ga / be;
    const std::string src = " [3D Ising; nu, beta = dynamical_systems Ising3D_nu_dyn, Ising3D_beta_dyn (in bar)]";
    set("wave3", "Ising2D_beta", be, "RELABELED 3D Ising beta = Ising3D_beta_dyn" + src, "IRONOUT-1 #2: mislabeled 2D -> 3D Ising beta = in-bar beta_dyn");
    set("wave3", "Ising2D_nu", nu, "RELABELED 3D Ising nu = Ising3D_nu_dyn" + src, "IRONOUT-1 #2: mislabeled 2D -> 3D Ising nu = in-bar nu_dyn");
    set("wave3", "Ising2D_gamma", ga, "RELABELED 3D Ising gamma = d nu - 2 beta (Rushbrooke+Josephson, d=3)" + src, "IRONOUT-1 #2: 3D Ising gamma by Rushbrooke+Josephson");
    set("wave7", "Ising3D_alpha", al, "alpha = 2 - d nu (Josephson, d=3)" + src, "IRONOUT-1 #2: Josephson from in-bar nu");
    set("wave7", "Ising3D_eta", et, "eta = 2 - gamma/nu, gamma = d nu - 2 beta (Fisher)" + src, "IRONOUT-1 #2: Fisher from in-bar nu, beta");
    set("wave7", "Ising3D_delta", de, "delta = 1 + gamma/beta, gamma = d nu - 2 beta (Widom)" + src, "IRONOUT-1 #2: Widom from in-bar nu, beta");
  }
  if (auto *pn = find("wave7", "XY_nu"), *pe = find("wave7", "XY_eta"); pn && pe) {
    const R nu = pn->value, et = pe->value;
    const std::string src = " [3D XY / O(2); nu, eta = wave7 XY_nu, XY_eta (in bar)]";
    set("wave8", "XY_beta", nu * (d - R(2) + et) / R(2), "beta = nu (d - 2 + eta)/2 (Fisher+Rushbrooke+Josephson, d=3)" + src, "IRONOUT-1 #2: O(2) beta from in-bar nu, eta");
    set("wave8", "XY_gamma", nu * (R(2) - et), "gamma = nu (2 - eta) (Fisher)" + src, "IRONOUT-1 #2: O(2) gamma from in-bar nu, eta (one exponent set)");
  }
  {  // #3 IE_H [eV]
    R Rinf = R(0), rpe = R(0);
    for (auto& [id, v] : L.mp_values()) { if (id == "R_inf") Rinf = v; if (id == "m_p_over_m_e") rpe = v; }
    const R a = L.alpha(), pi = F.PI;
    const R mc2 = R(2) * Rinf * L.si.h * L.si.c / (a * a) / L.si.e;  // m_e c^2 [eV] = 2 R_inf h c / alpha^2
    const R mu = R(1) / (R(1) + R(1) / rpe);                           // mu / m_e
    const R dirac = mu * mc2 * (R(1) - m::sqrt(R(1) - a * a));          // Dirac 1s binding, reduced mass
    const R lnk0 = lit<R>("2.984128555765");                           // 1s Bethe logarithm (pure number)
    const R lamb = R(4) * m::ipow(a, 5) * mc2 / (R(3) * pi) * m::ipow(mu, 3) * (m::ln(R(1) / (a * a)) - lnk0 + R(19) / R(30));
    set("chemistry_ionization", "IE_H", dirac - lamb,
        "mu c^2 [1 - sqrt(1 - alpha^2)] - (4 alpha^5 m c^2 / 3 pi) mu^3 [ln alpha^-2 - ln k0(1s) + 19/30]; m c^2 = 2 R_inf h c / alpha^2, mu = 1/(1 + m_e/m_p) [seed leaves R_inf, alpha, m_p/m_e]",
        "IRONOUT-1 #3: reduced-mass Dirac + 1s Lamb from in-bar R_inf, alpha, m_p/m_e");
  }
}

template <class R> std::vector<Row<R>> table(const Engine<R>& F, bool derived) {
  std::vector<Row<R>> out;
  leaves::SeedLeaves<R> L(F);
  for (auto& [sec, fn] : F.sections()) {
    for (auto& r : (F.*fn)()) {
      Row<R> x{sec, r.name, r.formula, r.computed, r.measured, r.sigma, RowKind::seed};
      if (is_definition_row(x.name)) x.kind = RowKind::definition;
      if (derived && x.name == "DNA_base_pair") {
        R a0 = R(0);
        for (auto& [id, v] : L.mp_values()) if (id == "a_0") a0 = v * lit<R>("1e10");
        x.value = R(2) * F.PI * a0 * (R(1) + F.GAMMA / (m::ipow(F.PI, 2) * F.E));
        x.formula = "2\u03c0a\u2080(1 + \u03b3/(\u03c0\u00b2e)), a\u2080 = seed leaf a_0";
        x.kind = RowKind::derived_replacement;
        x.why = "measured a0=0.529177 -> seed leaf a_0";
      }
      if (derived && x.name == "Proton_radius") {
        x.value = m::ipow(F.G_CAT, 7) + F.P_NEW;
        x.formula = "G\u2077 + P_new (seed leaf r_p)";
        x.kind = RowKind::derived_replacement;
        x.why = "target literal -> seed leaf r_p";
      }
      out.push_back(std::move(x));
    }
  }
  if (derived) ironout1(F, L, out);
  return out;
}

}  // namespace fsot::derive
