// fsot/engine.hpp — C++20 port of the FSOT 2.1 authority
//   github.com/dappalumbo91/FSOT-2.1-Lean  vendor/fsot_compute.py  (pin AEB2AD)
// Scalar law S = K (T1 + T2 + T3). Zero free parameters: every value below is
// derived from the five seeds (pi, e, phi, gamma, G). Nothing here is edited
// relative to the authority; golden tests compare every value to the Python.
#pragma once
#include <array>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

#include "fsot/real.hpp"

namespace fsot {

inline constexpr std::string_view AUTHORITY_PIN_PREFIX = "AEB2AD";
inline constexpr std::string_view AUTHORITY_SHA256 =
    "AEB2ADAD6E80F487772C5DF90A2E3DDA71624AB831A6A83B94AB471AC9AAC170";

template <class R> struct Result {
  std::string name;
  std::string formula;
  R computed;
  std::optional<R> measured;
  std::optional<double> sigma;
};

template <class R> struct ScalarInput;  // fwd

// §5 nest: unique nested-orifice chain of the 25-D fluid (micro -> macro).
inline const std::vector<std::vector<std::string_view>>& nest_generations() {
  static const std::vector<std::vector<std::string_view>> g = {
      {"Particle_Physics"},
      {"Quantum_Mechanics"},
      {"Atomic_Physics", "High_Energy_Physics"},
      {"Physical_Chemistry", "Chemistry"},
      {"Electromagnetism", "Molecular_Chemistry"},
      {"Optics", "Acoustics", "Materials_Science"},
      {"Quantum_Computing", "Quantum_Optics"},
      {"Biology"},
      {"Biochemistry"},
      {"Neuroscience", "Condensed_Matter"},
      {"Thermodynamics", "Fluid_Dynamics", "Nuclear_Physics", "Ecology"},
      {"Meteorology", "Psychology"},
      {"Atmospheric_Physics", "Oceanography"},
      {"Seismology", "Sociology"},
      {"Geophysics"},
      {"Astronomy", "Economics"},
      {"Planetary_Science"},
      {"Quantum_Gravity"},
      {"Particle_Astrophysics", "Astrophysics"},
      {"Cosmology"},
  };
  return g;
}

// Bulk-medium orifices (dark). Everything else is a counted specimen.
inline constexpr std::array<std::string_view, 12> MEDIUM_ORIFICES = {
    "Quantum_Computing", "Biology",     "Fluid_Dynamics",      "Ecology",
    "Meteorology",       "Atmospheric_Physics", "Oceanography", "Seismology",
    "Geophysics",        "Quantum_Gravity", "Particle_Astrophysics", "Cosmology"};

inline bool fold_observed(std::string_view name) {
  for (auto m : MEDIUM_ORIFICES) if (m == name) return false;
  return true;
}
inline int fold_hits(std::string_view name) { return name == "High_Energy_Physics" ? 1 : 0; }

// D_eff(g) = round(5 * 5^{g/(G-1)}). Python evaluates this in IEEE double with
// round-half-even; we do the same so integer rungs match bit-for-bit.
inline int derived_D_eff(std::string_view name) {
  const auto& gens = nest_generations();
  const int G = static_cast<int>(gens.size());
  if (G < 2) return 25;
  for (int g = 0; g < G; ++g)
    for (auto n : gens[g])
      if (n == name)
        return static_cast<int>(std::nearbyint(5.0 * std::pow(5.0, static_cast<double>(g) / (G - 1))));
  throw std::out_of_range("no nest generation for " + std::string(name));
}

inline std::vector<std::string_view> domain_names() {
  std::vector<std::string_view> out;
  for (auto& grp : nest_generations()) for (auto n : grp) out.push_back(n);
  return out;
}

template <class R> struct DomainConfig {
  std::string_view name;
  int D_eff;
  int hits;
  R delta_psi;  // look
  R delta_theta;
  bool observed;
  R C;  // interpretation label; does not enter S
};

// parity:    byte-parity with the pinned authority (truncated exponent literals kept as written).
// corrected: truncated decimal exponents (audit B-03, e.g. "0.333333333333333") are evaluated as the exact
//            rational p/q. Only closed-form rows change; seeds, layers and the 35 domain S are identical.
enum class Mode { parity, corrected };

template <class R> class Engine {
 public:
  using T = real_traits<R>;
  Mode mode = Mode::parity;
  R xexp(const R& literal, int p, int q) const { return mode == Mode::corrected ? R(p) / R(q) : literal; }
  // §1 seeds
  R PI = T::pi();
  R E = T::e();
  R PHI = (R(1) + m::sqrt(R(5))) / R(2);
  R GAMMA = lit<R>("0.57721566490153286060651209008240243104215933593992");
  R G_CAT = lit<R>("0.91596559417721901505460351493238411077414937428167");
  // §2 layer 1
  R ALPHA = m::ln(PI) / (E * m::ipow(PHI, 13));
  R PSI_CON = R(1) - m::exp(R(-1));
  R ETA_EFF = R(1) / (PI - R(1));
  R BETA = R(1) / m::exp(m::pow(PI, PI) + (E - R(1)));
  R GAMMA_C = -m::ln(R(2)) / PHI;
  R OMEGA = m::sin(PI / E) * m::sqrt(R(2));
  R THETA_S = m::sin(PSI_CON * ETA_EFF);
  R POOF = m::exp((-m::ln(PI) / E) / (ETA_EFF * m::ln(PHI)));
  // §3 layer 2
  R C_EFF = (R(1) - POOF * m::sin(THETA_S)) *
            (R(1) + (R(1) / m::ipow(PI, 4)) * G_CAT / (PI * PHI));
  R A_BLEED = m::sin(PI / E) * PHI / m::sqrt(R(2));
  R P_VAR = -m::cos(THETA_S + PI);
  R B_IN = C_EFF * (R(1) - m::sin(THETA_S) / PHI);
  R A_IN = A_BLEED * (R(1) + m::cos(THETA_S) / PHI);
  R SUCTION = POOF * (-m::cos(THETA_S - PI));
  R CHAOS = GAMMA_C / OMEGA;
  R P_BASE = GAMMA / E;
  R P_NEW = P_BASE * m::sqrt(R(2));
  R C_FACTOR = C_EFF * P_NEW;
  R K = PHI * (GAMMA / E) * m::sqrt(R(2)) / m::ln(PI) * (R(1) - R(1) / m::ipow(PI, 4));
  R C_COSM = R(1) / (PHI * m::ipow(PI, 2));

  std::vector<DomainConfig<R>> DOMAINS;
  R S_COSM, S_QUANT, S_CHEM;

  explicit Engine(Mode md = Mode::parity) : mode(md) {
    for (auto n : domain_names())
      DOMAINS.push_back({n, derived_D_eff(n), fold_hits(n), fold_look(n), R(1), fold_observed(n), fold_C(n)});
    S_COSM = domain_scalar("Cosmology");
    S_QUANT = domain_scalar("Quantum_Mechanics");
    S_CHEM = domain_scalar("Chemistry");
  }

  R fold_look(std::string_view name) const {
    if (name == "Atomic_Physics") return E / PI;               // bound well
    if (name == "High_Energy_Physics") return R(1) - POOF / PI;  // collision
    return R(1);
  }

  R fold_C(std::string_view n) const {
    const R gp = GAMMA / PHI, ep = E / PI;
    if (n == "Particle_Physics" || n == "Quantum_Mechanics") return gp;
    if (n == "Atomic_Physics" || n == "Physical_Chemistry" || n == "Chemistry" || n == "Electromagnetism") return ep;
    if (n == "Molecular_Chemistry") return m::ln(PI) / E;
    if (n == "Optics" || n == "Quantum_Optics") return PI / E;
    if (n == "Acoustics") return A_BLEED / m::sqrt(R(2));
    if (n == "Quantum_Computing") return m::sqrt(R(2)) / E;
    if (n == "Biology" || n == "Biochemistry") return m::ln(PHI) / m::sqrt(R(2));
    if (n == "Thermodynamics") return GAMMA / E;
    if (n == "Neuroscience") return C_FACTOR;
    if (n == "Condensed_Matter") return A_BLEED / E;
    if (n == "Fluid_Dynamics") return A_BLEED / PHI;
    if (n == "Nuclear_Physics") return ALPHA / PHI;
    if (n == "Ecology") return m::ln(PHI) / PHI;
    if (n == "Meteorology" || n == "Atmospheric_Physics" || n == "Geophysics") return CHAOS;
    if (n == "Materials_Science") return A_IN / E;
    if (n == "Psychology") return P_BASE;
    if (n == "Oceanography") return A_IN / PHI;
    if (n == "Seismology") return CHAOS / R(2);
    if (n == "Sociology" || n == "Economics") return GAMMA / m::ln(PI);
    if (n == "High_Energy_Physics") return ALPHA / m::sqrt(R(2));
    if (n == "Astronomy" || n == "Planetary_Science" || n == "Astrophysics") return m::ipow(PI, 2) / PHI;
    if (n == "Quantum_Gravity") return R(1) / m::ipow(PHI, 2);
    if (n == "Particle_Astrophysics") return m::ipow(PI, 2) / E;
    if (n == "Cosmology") return C_COSM;
    throw std::out_of_range("no interpretation C for " + std::string(n));
  }

  // §4 24-parameter input; defaults mirror the Python dataclass.
  struct ScalarInput {
    R N{1}, P{1}, D_eff{25}, psi_con, delta_psi{1}, recent_hits{0}, rho{1}, B_in, C_eff, P_new;
    bool observed = false;
    R beta, chaos, poof, suction, theta_s, delta_theta{1}, A_bleed, A_in, P_var;
    R scale{1}, amplitude{1}, trend_bias{0}, alpha;
  };
  ScalarInput default_input() const {
    ScalarInput s;
    s.psi_con = PSI_CON; s.B_in = B_IN; s.C_eff = C_EFF; s.P_new = P_NEW;
    s.beta = BETA; s.chaos = CHAOS; s.poof = POOF; s.suction = SUCTION; s.theta_s = THETA_S;
    s.A_bleed = A_BLEED; s.A_in = A_IN; s.P_var = P_VAR; s.alpha = ALPHA;
    return s;
  }

  // S = K (T1 + T2 + T3)
  R compute_scalar(const ScalarInput& s) const {
    const R& N = s.N; const R& P = s.P; const R& D = s.D_eff;
    const R& dp = s.delta_psi; const R& dt = s.delta_theta; const R& hits = s.recent_hits;
    // Term 1: observer-modulated base
    const R growth = m::exp(s.alpha * (R(1) - hits / N) * GAMMA / PHI);
    const R base = (N * P / m::sqrt(D)) * m::cos((s.psi_con + dp) / ETA_EFF) *
                   m::exp(-s.alpha * hits / N + s.rho + s.B_in * dp) * (R(1) + growth * s.C_eff);
    R T1 = base * (R(1) + s.P_new * m::ln(D / R(25)));
    if (s.observed) T1 = T1 * m::exp(C_FACTOR * s.P_var) * m::cos(dp + s.P_var);
    // Term 2: linear modulation
    const R T2 = s.scale * s.amplitude + s.trend_bias;
    // Term 3: valve-acoustic-phase
    const R valve = s.beta * m::cos(dp) * (N * P / m::sqrt(D)) * (R(1) + s.chaos * (D - R(25)) / R(25)) *
                    (R(1) + s.poof * m::cos(s.theta_s + PI) + s.suction * m::sin(s.theta_s));
    const R sdt = m::sin(dt), cdt = m::cos(dt);
    const R acoustic = R(1) + (s.A_bleed * sdt * sdt) / PHI + (s.A_in * cdt * cdt) / PHI;
    const R phase = R(1) + s.B_in * s.P_var;
    const R T3 = valve * acoustic * phase;
    return K * (T1 + T2 + T3);
  }

  R scalar_from_fold(int D_eff, const R& look, int hits, bool observed) const {
    ScalarInput si = default_input();
    si.D_eff = R(D_eff); si.delta_psi = look; si.delta_theta = R(1);
    si.recent_hits = R(hits); si.observed = observed;
    return compute_scalar(si);
  }

  const DomainConfig<R>& domain(std::string_view name) const {
    for (auto& d : DOMAINS) if (d.name == name) return d;
    throw std::out_of_range("unknown domain " + std::string(name));
  }
  R domain_scalar(std::string_view name) const {
    const auto& d = domain(name);
    return scalar_from_fold(d.D_eff, d.delta_psi, d.hits, d.observed);
  }

  // Ledger B correction c = m (1 + |S| f), f_domain = ALPHA (not a prediction).
  R fsot_correct(const R& measured, std::string_view domain_name) const {
    return measured * (R(1) + m::fabs(domain_scalar(domain_name)) * ALPHA);
  }

  using Res = Result<R>;
  using Results = std::vector<Res>;
  static Res mk(std::string n, std::string f, R v) { return Res{std::move(n), std::move(f), v, std::nullopt, std::nullopt}; }
  static Res mk(std::string n, std::string f, R v, R meas) { return Res{std::move(n), std::move(f), v, meas, std::nullopt}; }
  static Res mk(std::string n, std::string f, R v, R meas, double sig) { return Res{std::move(n), std::move(f), v, meas, sig}; }

// Closed-form sections (§6–§26), generated from the authority by tools/gen_closed_forms.py
#include "fsot/closed_forms.gen.inc"
};

}  // namespace fsot
