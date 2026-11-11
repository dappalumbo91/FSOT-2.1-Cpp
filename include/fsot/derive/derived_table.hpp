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
#include <stdexcept>
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
  std::optional<double> wa_sigma;  // IRONOUT-2 retarget: published world-average sigma (z is printed only from this)
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
    // SCAFFOLD_PENDING_FSOT_DERIVATION (Damian t999u): ln k0(1s) is a Coulomb-problem number allowed as temporary
    // scaffolding only; it is not yet an FSOT derivation.
    const R lnk0 = lit<R>("2.984128555765");                           // 1s Bethe logarithm (pure number)
    const R lamb = R(4) * m::ipow(a, 5) * mc2 / (R(3) * pi) * m::ipow(mu, 3) * (m::ln(R(1) / (a * a)) - lnk0 + R(19) / R(30));
    set("chemistry_ionization", "IE_H", dirac - lamb,
        "mu c^2 [1 - sqrt(1 - alpha^2)] - (4 alpha^5 m c^2 / 3 pi) mu^3 [ln alpha^-2 - ln k0(1s) + 19/30]; m c^2 = 2 R_inf h c / alpha^2, mu = 1/(1 + m_e/m_p) [seed leaves R_inf, alpha, m_p/m_e]; ln k0(1s) = 2.984128555765 SCAFFOLD_PENDING_FSOT_DERIVATION",
        "IRONOUT-1 #3: reduced-mass Dirac + 1s Lamb from in-bar R_inf, alpha, m_p/m_e (ln k0 SCAFFOLD_PENDING_FSOT_DERIVATION)");
  }
}

// IRONOUT-2 (Damian t999u, 2026-11-11 1:46 PM EST): ONE engine-wide value per physical quantity, the FSOT version that
// lands closest to the best observed value (world average where one exists; reference/scoring_criteria_ironout2.tsv).
// Only rows whose own value was the farther one move; each takes another FSOT value the engine already computes (a
// tip seed leaf / scored pin from the frozen precision audit, or another table row). Nothing measured is pasted,
// nothing is fitted, no leaf and no fold (fold::vt included) changes. Quantities where a NON-leaf version is closer
// than the tip leaf (V_ud, V_us = lambda, V_cd, V_cs, m_mu/m_e, m_tau/m_mu) are NOT unified: moving the leaf would
// change the /workspace/mainC tip and the banked vt tau_vk (conflicts, docs/single_engine/IRONOUT_2.md).
struct Unify { const char* sec; const char* name; const char* src; const char* why; };
inline const std::vector<Unify>& ironout2_list() {
  static const std::vector<Unify> u = {
      // seed closed form -> scored pin / tip leaf (pin closer to the world average for every one)
      {"wave1", "alpha_s(M_Z)", "pin:wave1|alpha_s(M_Z)", "seed -> tip leaf alpha_s"},
      {"wave1", "T_CMB", "pin:wave1|T_CMB", "seed -> scored pin T_CMB"},
      {"validation_suite", "sin2_theta_W", "pin:validation_suite|sin2_theta_W", "seed -> tip leaf sin2_theta_W_MSbar"},
      {"wave2", "sin2_theta_W", "pin:wave2|sin2_theta_W", "seed -> tip leaf sin2_theta_W_MSbar"},
      {"wave2", "1/alpha_em", "pin:wave2|1/alpha_em", "seed -> tip leaf alpha_inv"},
      {"wave2", "M_W/M_Z", "pin:wave2|M_W/M_Z", "seed -> tip leaf m_W/m_Z (host M_W)"},
      {"wave2", "m_pi/m_p", "pin:wave2|m_pi/m_p", "seed -> scored pin m_pi/m_p"},
      {"wave3", "Deuteron_binding_MeV", "pin:wave3|Deuteron_binding_MeV", "seed -> scored pin B_d"},
      {"wave4", "Dm2_21/Dm2_32", "pin:wave4|Dm2_21/Dm2_32", "seed -> scored pin Dm2 ratio"},
      {"wave4", "|V_ub|", "pin:wave4||V_ub|", "seed -> tip CKM leaf V_ub"},
      {"wave4", "mu_p_muN", "pin:wave4|mu_p_muN", "seed -> tip leaf mu_p"},
      {"wave4", "m_c/m_b", "pin:wave4|m_c/m_b", "seed -> scored pin m_c/m_b"},
      {"wave5", "Gamma_Z/M_Z", "pin:wave5|Gamma_Z/M_Z", "seed -> tip leaf Gamma_Z/M_Z"},
      {"wave7", "m_tau/m_mu", "pin:wave7|m_tau/m_mu", "seed -> tip leaf ratio (m_tau/m_e)/(m_mu/m_e)"},
      {"wave8", "He4_binding_MeV", "pin:wave8|He4_binding_MeV", "seed -> tip leaf B_He4"},
      {"wave8", "Triton_binding_MeV", "pin:wave8|Triton_binding_MeV", "seed -> tip leaf B_H3"},
      {"wave8", "Deuteron_mu_muN", "pin:wave8|Deuteron_mu_muN", "seed -> scored pin mu_d"},
      {"wave9", "|V_tb|", "pin:wave9||V_tb|", "seed -> tip CKM leaf V_tb"},
      {"wave10", "m_mu/m_e", "pin:wave10|m_mu/m_e", "seed -> tip leaf m_mu/m_e"},
      {"wave10", "(g-2)/2_electron", "pin:wave10|(g-2)/2_electron", "seed -> tip leaf a_e"},
      // second CKM closed forms -> tip CKM leaf (leaf closer to the PDG direct value)
      {"wave3", "|V_cb|", "CKM_V_cb", "closed form -> tip CKM leaf V_cb"},
      {"wave4", "|V_td|", "CKM_V_td", "closed form -> tip CKM leaf V_td"},
      {"wave4", "|V_ts|", "CKM_V_ts", "closed form -> tip CKM leaf V_ts"},
      {"wave4", "Jarlskog_J", "leaf:Jarlskog_J", "closed form -> tip J leaf"},
      // second lepton-ratio formula -> tip leaf
      {"lepton_ratios", "m_tau/m_e_lepton", "pin:wave3|m_tau/m_e", "lepton_ratios formula -> tip leaf m_tau/m_e"},
      // duplicates inside the table
      {"wave8", "H2O_bond_angle", "row:validation_suite|Water_bond_angle", "duplicate -> validation_suite Water_bond_angle"},
      {"wave7", "Golden_angle_deg", "row:validation_suite|Golden_angle", "duplicate -> validation_suite Golden_angle (exact)"},
      {"validation_suite", "Feigenbaum_delta", "row:wave4|Feigenbaum_delta", "duplicate -> wave4 Feigenbaum_delta"},
      {"validation_suite", "Feigenbaum_alpha", "row:wave4|Feigenbaum_alpha", "duplicate -> wave4 Feigenbaum_alpha"},
      {"wave3", "sin_theta_C", "row:wave3||V_us|", "sin theta_C = |V_us|: -> wave3 |V_us| closed form (closest Cabibbo value)"},
      // IRONOUT-2 r4 (Tracer REFINEMENT_LIST r4 LAMBDA-CKM): against PDG 2026 direct |V_cd| 0.2247(22) / |V_cs| 0.969(5) the
      // tip CKM leaf is closer than the wave8 closed form (V_cd: leaf z +0.20 vs closed form -1.68; V_cs: +0.88 vs +1.18).
      // Keep-the-closest rule: the rows take the leaf (no leaf changes; no in-bar row leaves its bar).
      {"wave8", "|V_cd|", "pin:wave8||V_cd|", "closed form -> tip CKM leaf V_cd (closer to PDG 2026 direct 0.2247(22))"},
      {"wave8", "|V_cs|", "pin:wave8||V_cs|", "closed form -> tip CKM leaf V_cs (closer to PDG 2026 direct 0.969(5))"},
  };
  return u;
}
// pins: id -> value string from the frozen precision audit (audit/precision_2026-10-02.tsv, the tip's scored values).
// lv_canon / lv_var (optional): seed-leaf values of the canonical and of THIS table's engine. A frozen pin that is a live
// seed leaf (canonical leaf == pin to 1e-12) is carried into a variant engine (D-02 10phi / D-04 QM-D5 columns) as
// pin * leaf_var / leaf_canon, so a variant that moves the leaf's inputs (e.g. C_cosm for m_c/m_b) moves the row too
// (bug found by Tracer r4: the 10phi column showed the m_c/m_b pin frozen at its canonical value).
template <class R> void ironout2(std::vector<Row<R>>& out, const std::map<std::string, std::string>& pins,
                                 const std::vector<std::pair<std::string, R>>* lv_canon = nullptr,
                                 const std::vector<std::pair<std::string, R>>* lv_var = nullptr) {
  auto find = [&](const std::string& sec, const std::string& nm) -> Row<R>* {
    for (auto& r : out) if (r.section == sec && r.name == nm) return &r;
    return nullptr;
  };
  std::vector<std::pair<Row<R>*, R>> todo;  // resolve every source first, then assign (sources are pre-unification values)
  for (const auto& u : ironout2_list()) {
    Row<R>* r = find(u.sec, u.name);
    if (!r) throw std::runtime_error(std::string("ironout2: no row ") + u.sec + "|" + u.name);
    const std::string s = u.src;
    if (s.rfind("row:", 0) == 0) {
      const auto bar = s.find('|', 4);
      Row<R>* q = find(s.substr(4, bar - 4), s.substr(bar + 1));
      if (!q) throw std::runtime_error("ironout2: no source row " + s);
      todo.emplace_back(r, q->value);
    } else {
      auto it = pins.find(s);
      if (it == pins.end()) throw std::runtime_error("ironout2: no precision value " + s);
      R v = lit<R>(it->second.c_str());
      if (lv_canon && lv_var) {
        const std::string* hit = nullptr; R lc = 0;
        for (const auto& [id, val] : *lv_canon)
          if (val != R(0) && m::fabs(val / v - R(1)) < lit<R>("1e-12")) { if (hit) { hit = nullptr; break; } hit = &id; lc = val; }
        if (hit)
          for (const auto& [id, val] : *lv_var) if (id == *hit) { v = v * (val / lc); break; }
      }
      todo.emplace_back(r, v);
    }
  }
  for (std::size_t i = 0; i < todo.size(); ++i) {
    const auto& u = ironout2_list()[i];
    Row<R>* r = todo[i].first;
    r->value = todo[i].second;
    r->formula += std::string(" [IRONOUT-2 unify: value = ") + u.src + "]";
    r->kind = RowKind::derived_replacement;
    r->why = std::string("IRONOUT-2 unify: ") + u.why;
  }
  // IRONOUT-2 criteria (Damian t999u; Tracer 2026-11-11): rows whose authority target is stale are scored against the
  // world average of reference/scoring_criteria_ironout2.tsv. Only the comparison target moves, never a value.
  struct Retarget { const char* sec; const char* name; const char* obs; double sigma; const char* src; };
  // sigma 0 = exact constant (no z). Values: Scout WAVE90 re-extract 43_5wf (PDG 2026, Takahashi et al. IJMPA 41 2630011).
  static const Retarget rt[] = {
      {"wave3", "sin_theta_C", "0.22431", 0.00085, "PDG 2026 CKM review Eq. (12.8) direct |V_us| 0.22431(85) (was stale authority target 0.22759)"},
      {"wave8", "|V_cd|", "0.2247", 0.0022, "PDG 2026 CKM review Eq. (12.9) direct |V_cd| 0.2247(22) (was 0.221)"},
      {"wave8", "|V_cs|", "0.969", 0.005, "PDG 2026 CKM review Eq. (12.10) direct |V_cs| 0.969(5) (was fit 0.9735)"},
      {"wave5", "D_H_ratio", "2.508e-5", 0.029e-5, "PDG 2026 BBN review Eq. (24.2) (D/H)_p 2.508(29)e-5 (was 2.547e-5)"},
      {"wave2", "tau_reion", "0.0544", 0.0073, "Planck 2018 VI TT,TE,EE+lowE+lensing 0.0544(73) = PDG 2026 cosmology 0.054(7) (sigma added; FIT LCDM)"},
      {"wave8", "gamma_2_Stieltjes", "-0.0096903631928723185", 0.0, "exact Stieltjes constant gamma_2 (was -0.00946)"},
      {"wave4", "r_p_fm", "0.84075", 0.00064, "CODATA 2022 r_p 0.84075(64) fm (was 0.8414)"},
      {"validation_suite", "Proton_radius", "0.84075", 0.00064, "CODATA 2022 r_p 0.84075(64) fm (was 0.8413)"},
  };
  for (const auto& t : rt) {
    Row<R>* r = find(t.sec, t.name);
    if (!r) throw std::runtime_error(std::string("ironout2 retarget: no row ") + t.sec + "|" + t.name);
    r->measured = lit<R>(t.obs);
    r->sigma.reset();  // the authority's claimed-|z| tag referred to the stale target
    if (t.sigma > 0) r->wa_sigma = t.sigma; else r->wa_sigma.reset();
    r->why += std::string("; target -> ") + t.src;
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
