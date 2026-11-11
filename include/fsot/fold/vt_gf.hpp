// fsot/fold/vt_gf.hpp — §43.5vt folded: G_F from the tip-native higher-order Δr chain, and τ_n through it.
//
// STATUS SM_PARITY_REFINE_LATER (Damian t994u, 2026-11-11 1:00 PM EST; ruling RULING_t992u_SM_PARITY_GATE.md sha8
// c65ff89d): τ_n passes Gate A; G_F fails Gate A (strict MuLan τ_μ z ≈ −901) and is ACCEPTED at Gate B
// (|FSOT − G_μ| = +452 ppm ≤ max(σ_SM,pred 809.87 ppm, |SM res| 665.56 ppm)). Not ADOPT, no GO-MERGE.
//
// Carried route P2 = C1+C2+C3+C5µ+C6 (no C7), by the pre-registered lowest-χ²/N rule; P1 (with C7) is the documented
// alternate. Source: tracer dialin/out_vt_tau_n_gf_z2_mu_consistent_dr2_completion/{score.py ebdda985, results.tsv
// 90b5458e, DONE.md}; the C++ solve mirrors score.py:60-90 (solve, tconv) and the vq score.py:137-165 helpers
// (xt_of, xt0, c5_eval, c6_of) line for line.
//
// Live vs banked: the electroweak inputs (M_W, M_Z, α, s_W², m_t) come from the engine's own seed leaves and are
// checked against the vt package. The fixed point, x_t(G), Δρ, the C5µ Δr^(2) and T_conv terms, and C6 are evaluated
// here at every iteration. Only loop-invariant coefficients (one-loop B0/polylog integrals, α_s running, Δα, the
// carried Z-2 G_F and the vk τ_n engine value) are banked in golden/vt_package.tsv (tools/gen_vt_package.py, 50 digits).
//
// Hooks for the leaves still refining it (left empty = vt P2 as folded):
//   vv (Δr two-loop remainder): Hooks::vv_rem_add (additive to Δr_rem every iteration), or Hooks::vv_route to swap terms
//   vw (ΔR^V, γW box) and vx (g_A^eff in 1+3g_A²): both live inside τ_vk; Hooks::tau_vk_override takes the rebuilt τ_vk
#pragma once
#include <cmath>
#include <limits>
#include <fstream>
#include <map>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>

#include "fsot/engine.hpp"
#include "fsot/host/seed_leaves.hpp"

namespace fsot::fold::vt {

inline constexpr const char* kStatus = "SM_PARITY_REFINE_LATER";

template <class R> struct Package {
  std::map<std::string, R> v;
  std::string header;
  const R& at(const std::string& k) const {
    auto it = v.find(k);
    if (it == v.end()) throw std::runtime_error("vt package: missing " + k);
    return it->second;
  }
  static Package load(const std::string& path) {
    Package p; std::ifstream in(path);
    if (!in) throw std::runtime_error("cannot open " + path);
    std::string line;
    while (std::getline(in, line)) {
      if (line.rfind("#vt_package", 0) == 0) { p.header = line; continue; }
      if (line.empty() || line[0] == '#') continue;
      std::stringstream ss(line); std::string k, val;
      std::getline(ss, k, '\t'); std::getline(ss, val, '\t');
      p.v.emplace(k, lit<R>(val.c_str()));
    }
    return p;
  }
};

struct Route { bool c1 = true, c2 = true, c3 = true, c5 = true, tconv = true, c6 = true, c7 = true; };
inline Route P0() { return Route{false, false, false, false, false, false, false}; }  // Z-2 re-solve (all off)
inline Route P1() { return Route{}; }                                                // PRIMARY, with C7 (alternate)
inline Route P2() { Route r; r.c7 = false; return r; }                               // carried (LEE, no C7)

template <class R> struct Hooks {
  std::optional<R> vv_rem_add;       // §43.5vv: extra Δr_rem term (e.g. FHWW/ACFW O(α²) completion minus what it replaces)
  std::optional<Route> vv_route;     // §43.5vv: replace the term switches (e.g. C2/C5µ off when vv supplies them)
  std::optional<R> tau_vk_override;  // §43.5vw / §43.5vx: τ_vk rebuilt with the refined ΔR^V and/or g_A^eff
};

// Electroweak inputs; by default the engine seed leaves (checked == package in tests/test_vt_gf.cpp).
template <class R> struct Inputs { R MW, MZ, alpha, s2, mt; };

template <class R> struct Solution {
  R G, ratio, GF, tau_n, dr, drho, rem, c5mu, c7; int iterations; R last_step;
};

template <class R> struct Chain {
  const Package<R>& pk;
  Inputs<R> in;
  Hooks<R> hooks{};

  R xt_of(const R& G) const { return G * in.mt * in.mt / (R(8) * m::sqrt(R(2)) * m::ipow(real_traits<R>::pi(), 2)); }
  R xt0() const { return in.alpha * in.mt * in.mt / (R(16) * real_traits<R>::pi() * in.s2 * in.MW * in.MW); }

  // hooked = false for the P0 Z-2 baseline (the normalisation G_F,Z2 / G_chain(P0) must not move with a hook)
  Solution<R> solve_raw(Route r, bool hooked = false) const {
    if (hooked && hooks.vv_route) r = *hooks.vv_route;
    const R pi = real_traits<R>::pi(), s2 = in.s2, c2 = R(1) - s2, k = c2 / s2, NC = pk.at("NC");
    const R a_s = pk.at("a_s_mt"), da = pk.at("Delta_alpha");
    const R rho2 = r.c2 ? pk.at("rho2_C2") : pk.at("rho2_tip");
    const R q = R(1) - pk.at("q1") * a_s - pk.at("q2") * a_s * a_s + (r.c3 ? pk.at("q3_C3") * a_s * a_s * a_s : R(0));
    const R rem0 = r.c1 ? pk.at("rem_C1") : pk.at("rem_tip");
    const R d7 = r.c7 ? pk.at("C7") : R(0);
    const R ZT = (in.MZ / in.mt) * (in.MZ / in.mt);
    const R G0 = pi * in.alpha / (m::sqrt(R(2)) * in.MW * in.MW * s2);
    const R tol = std::numeric_limits<R>::epsilon() * R(64) > lit<R>("1e-30") ? std::numeric_limits<R>::epsilon() * R(64) : lit<R>("1e-30");
    R G = G0, omr = 1, drho = 0, rem = 0, c5 = 0, step = 1; int it = 0;
    for (; it < 300; ++it) {
      const R xt = xt_of(G); rem = rem0 + d7 + (hooked && hooks.vv_rem_add ? *hooks.vv_rem_add : R(0)); c5 = 0;
      if (r.c6) rem += R(-3) * xt * k * a_s * pk.at("CF") * (ZT * pk.at("C6_B1") + ZT * ZT * pk.at("C6_B2"));
      if (r.c5) {
        const R k8 = R(8) * in.MW * in.MW * G / m::sqrt(R(2)), e2s2 = R(4) * pi * in.alpha / s2;
        const R sub_k8 = pk.at("C5_Ar") * xt * xt + pk.at("C5_Aa") * xt * k8;
        c5 = pk.at("C5_fh") * xt + pk.at("C5_fa") * xt - k * (e2s2 / k8) * sub_k8;
        if (r.tconv) {
          const R Rd = R(2) * k * k * NC * xt * (pk.at("C5mu_Y") - NC * xt0());
          const R Rc = -k * R(3) * xt * pk.at("rem_C1");
          c5 += Rd - Rc;
        }
        rem += c5;
      }
      drho = R(3) * xt * (R(1) + xt * rho2) * q;
      omr = (R(1) - da) * (R(1) + k * drho) - rem;
      const R nG = pi * in.alpha / (m::sqrt(R(2)) * in.MW * in.MW * s2 * omr);
      step = m::fabs(nG - G) / G; G = nG;
      if (step < tol) { ++it; break; }
    }
    return Solution<R>{G, R(1), R(0), R(0), R(1) - omr, drho, rem, c5, d7, it, step};
  }

  // ratio to the Z-2 re-solve, G_F = carried G_F,Z2 × ratio, τ_n = τ_vk / ratio² (score.py:225, (7a)).
  Solution<R> solve(Route r) const {
    const auto p0 = solve_raw(P0());
    auto s = solve_raw(r, true);
    s.ratio = s.G / p0.G;
    s.GF = pk.at("GF_Z2") * s.ratio;
    const R tvk = hooks.tau_vk_override ? *hooks.tau_vk_override : pk.at("tau_vk_s");
    s.tau_n = tvk / (s.ratio * s.ratio);
    return s;
  }
};

// Electroweak inputs from the engine's seed leaves (vn score.py:62-64 definitions).
template <class R> R leaf(const leaves::SeedLeaves<R>& L, const std::string& name) {
  for (auto& kv : L.mp_values()) if (kv.first == name) return kv.second;
  throw std::runtime_error("seed leaf missing: " + name);
}
template <class R> Inputs<R> engine_inputs(const leaves::SeedLeaves<R>& L) {
  Inputs<R> in;
  in.MW = L.m_W_MeV() / R(1000); in.MZ = L.m_Z_MeV() / R(1000); in.alpha = L.alpha();
  in.s2 = R(1) - (in.MW / in.MZ) * (in.MW / in.MZ); in.mt = leaf(L, "m_t_over_m_W") * in.MW;
  return in;
}

// Authority A1 Z width with an injected G_F (tip tools/fsot02d.py:60-77 compute(GF_override)), as Γ_Z/M_Z.
template <class R> R gz_over_mz_A1(const Engine<R>& F, const R& GF, const R& MZ, const R& s2hat, const R& alpha) {
  const R pi = real_traits<R>::pi(), als = R(2) * m::ipow(F.POOF / F.PSI_CON, 2);
  const R G0 = GF * MZ * MZ * MZ / (R(6) * m::sqrt(R(2)) * pi);
  auto width = [&](R T3, R Q, int Nc, bool quark) {
    return R(Nc) * G0 * (m::ipow(T3 - R(2) * Q * s2hat, 2) + T3 * T3) * (R(1) + R(3) * Q * Q * alpha / (R(4) * pi)) * (quark ? R(1) + als / pi : R(1));
  };
  const R nu = width(R(1) / 2, R(0), 1, false), ee = width(-R(1) / 2, R(-1), 1, false);
  const R up = width(R(1) / 2, R(2) / 3, 3, true), dn = width(-R(1) / 2, -R(1) / 3, 3, true);
  return (R(3) * ee + R(3) * nu + R(2) * up + R(3) * dn) / MZ;
}

// Ruling t992u diagnostics (reference numbers from the ruling, never FSOT inputs): G_μ = 1.1663788e-5 (PDG 2024 §10
// eq.(10.8)); strict MuLan τ_μ = 2196980.3 ± 2.2 ps (arXiv:1211.0960); Gate B threshold 809.87 ppm of G_F.
struct MuDiag { double ppm_vs_Gmu, tau_mu_ppm, z_mulan; bool gateA, gateB; };
template <class R> MuDiag mu_diag(const R& GF) {
  const double g = double(GF), Gmu = 1.1663788e-5, tau = 2196980.3, sig = 2.2, thrB = 809.87;
  const double ppm = (g / Gmu - 1) * 1e6, tppm = ((Gmu / g) * (Gmu / g) - 1) * 1e6, z = tppm * 1e-6 * tau / sig;
  return {ppm, tppm, z, std::fabs(z) <= 1, std::fabs(ppm) <= thrB};
}

}  // namespace fsot::fold::vt
