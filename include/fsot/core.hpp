// fsot/core.hpp — freestanding FSOT 2.1 core: seeds, layers 1–2, the 35-domain nest and the scalar law
// S = K (T1 + T2 + T3) (authority vendor/fsot_compute.py, pin AEB2AD).
//
// No heap, exceptions, RTTI, iostream, <string>, <vector> or libm: only what the number type R brings.
// Intended for R = fsot::bt::BTFloat<P> (balanced ternary), so the whole evaluation is ternary. Every
// expression has the same operation order as fsot::Engine (engine.hpp), so CoreEngine<BTFloat<P>> and
// Engine<BTFloat<P>> give bit-identical trits (tests/test_core.cpp).
#pragma once
#include "fsot/ternary.hpp"

namespace fsot::core {

// §5 nest generations (micro -> macro), flattened with the generation index of each domain.
struct NestEntry { const char* name; int generation; bool medium; };
inline constexpr int NEST_GENERATIONS = 20;
inline constexpr NestEntry NEST[] = {
    {"Particle_Physics", 0, false},     {"Quantum_Mechanics", 1, false},  {"Atomic_Physics", 2, false},
    {"High_Energy_Physics", 2, false},  {"Physical_Chemistry", 3, false}, {"Chemistry", 3, false},
    {"Electromagnetism", 4, false},     {"Molecular_Chemistry", 4, false}, {"Optics", 5, false},
    {"Acoustics", 5, false},            {"Materials_Science", 5, false},  {"Quantum_Computing", 6, true},
    {"Quantum_Optics", 6, false},       {"Biology", 7, true},             {"Biochemistry", 8, false},
    {"Neuroscience", 9, false},         {"Condensed_Matter", 9, false},   {"Thermodynamics", 10, false},
    {"Fluid_Dynamics", 10, true},       {"Nuclear_Physics", 10, false},   {"Ecology", 10, true},
    {"Meteorology", 11, true},          {"Psychology", 11, false},        {"Atmospheric_Physics", 12, true},
    {"Oceanography", 12, true},         {"Seismology", 13, true},         {"Sociology", 13, false},
    {"Geophysics", 14, true},           {"Astronomy", 15, false},         {"Economics", 15, false},
    {"Planetary_Science", 16, false},   {"Quantum_Gravity", 17, true},    {"Particle_Astrophysics", 18, true},
    {"Astrophysics", 18, false},        {"Cosmology", 19, true},
};
inline constexpr int DOMAIN_COUNT = sizeof(NEST) / sizeof(NEST[0]);

constexpr bool streq(const char* a, const char* b) {
  while (*a && *a == *b) { ++a; ++b; }
  return *a == *b;
}

// number-type hooks; specialise for other types
template <class R> struct Traits;
template <int P> struct Traits<bt::BTFloat<P>> {
  static bt::BTFloat<P> pi() { return bt::pi<P>(); }
  static bt::BTFloat<P> e() { return bt::e<P>(); }
  static constexpr bt::BTFloat<P> lit(const char* s) { return bt::parse<P>(s); }
};

template <class R> R ipow(const R& x, int n) {  // binary powering, as fsot::m::ipow / mpmath
  if (n < 0) return R(1) / ipow(x, -n);
  R result(1), base(x);
  while (n) { if (n & 1) result = result * base; base = base * base; n >>= 1; }
  return result;
}

template <class R> class CoreEngine {
  using T = Traits<R>;
 public:
  // §1 seeds
  R PI = T::pi();
  R E = T::e();
  R PHI = (R(1) + sqrt(R(5))) / R(2);
  R GAMMA = T::lit("0.57721566490153286060651209008240243104215933593992");
  R G_CAT = T::lit("0.91596559417721901505460351493238411077414937428167");
  // §2 layer 1
  R ALPHA = log(PI) / (E * ipow(PHI, 13));
  R PSI_CON = R(1) - exp(R(-1));
  R ETA_EFF = R(1) / (PI - R(1));
  R BETA = R(1) / exp(pow(PI, PI) + (E - R(1)));
  R GAMMA_C = -log(R(2)) / PHI;
  R OMEGA = sin(PI / E) * sqrt(R(2));
  R THETA_S = sin(PSI_CON * ETA_EFF);
  R POOF = exp((-log(PI) / E) / (ETA_EFF * log(PHI)));
  // §3 layer 2
  R C_EFF = (R(1) - POOF * sin(THETA_S)) * (R(1) + (R(1) / ipow(PI, 4)) * G_CAT / (PI * PHI));
  R A_BLEED = sin(PI / E) * PHI / sqrt(R(2));
  R P_VAR = -cos(THETA_S + PI);
  R B_IN = C_EFF * (R(1) - sin(THETA_S) / PHI);
  R A_IN = A_BLEED * (R(1) + cos(THETA_S) / PHI);
  R SUCTION = POOF * (-cos(THETA_S - PI));
  R CHAOS = GAMMA_C / OMEGA;
  R P_BASE = GAMMA / E;
  R P_NEW = P_BASE * sqrt(R(2));
  R C_FACTOR = C_EFF * P_NEW;
  R K = PHI * (GAMMA / E) * sqrt(R(2)) / log(PI) * (R(1) - R(1) / ipow(PI, 4));

  // D_eff(g) = round(5 * 5^{g/(G-1)}): evaluated here in R (the authority uses IEEE double; no rung is
  // near a .5 tie, and tests/test_core.cpp checks all 35 against fsot::derived_D_eff).
  int derived_D_eff(int i) const {
    const R x = R(5) * exp(log(R(5)) * R(NEST[i].generation) / R(NEST_GENERATIONS - 1));
    return int(floor(x + R(1) / R(2)).to_int());
  }
  int fold_hits(int i) const { return streq(NEST[i].name, "High_Energy_Physics") ? 1 : 0; }
  bool fold_observed(int i) const { return !NEST[i].medium; }
  R fold_look(int i) const {
    if (streq(NEST[i].name, "Atomic_Physics")) return E / PI;
    if (streq(NEST[i].name, "High_Energy_Physics")) return R(1) - POOF / PI;
    return R(1);
  }

  // S = K (T1 + T2 + T3) with the authority's default ScalarInput (N = P = rho = scale = amplitude = 1,
  // trend_bias = 0, delta_theta = 1) — same operation order as Engine::compute_scalar.
  R scalar_from_fold(int D_eff, const R& look, int hits_i, bool observed) const {
    const R N(1), P(1), D(D_eff), dp = look, dt(1), hits(hits_i), rho(1), scale(1), amplitude(1), trend_bias(0);
    const R growth = exp(ALPHA * (R(1) - hits / N) * GAMMA / PHI);
    const R base = (N * P / sqrt(D)) * cos((PSI_CON + dp) / ETA_EFF) * exp(-ALPHA * hits / N + rho + B_IN * dp) *
                   (R(1) + growth * C_EFF);
    R T1 = base * (R(1) + P_NEW * log(D / R(25)));
    if (observed) T1 = T1 * exp(C_FACTOR * P_VAR) * cos(dp + P_VAR);
    const R T2 = scale * amplitude + trend_bias;
    const R valve = BETA * cos(dp) * (N * P / sqrt(D)) * (R(1) + CHAOS * (D - R(25)) / R(25)) *
                    (R(1) + POOF * cos(THETA_S + PI) + SUCTION * sin(THETA_S));
    const R sdt = sin(dt), cdt = cos(dt);
    const R acoustic = R(1) + (A_BLEED * sdt * sdt) / PHI + (A_IN * cdt * cdt) / PHI;
    const R phase = R(1) + B_IN * P_VAR;
    const R T3 = valve * acoustic * phase;
    return K * (T1 + T2 + T3);
  }
  R domain_scalar(int i) const { return scalar_from_fold(derived_D_eff(i), fold_look(i), fold_hits(i), fold_observed(i)); }
};

// Decimal rendering with ternary arithmetic only (scale by 10, peel digits with floor) into a caller
// buffer: "-d.ddddde-XX". Returns the number of chars written (excluding NUL).
template <int P> int to_decimal(const bt::BTFloat<P>& x, int sig, char* out, int cap) {
  using F = bt::BTFloat<P + 8>;
  int k = 0;
  auto put = [&](char c) { if (k + 1 < cap) out[k++] = c; };
  if (x.is_zero()) { put('0'); out[k] = 0; return k; }
  F v = x.template to<P + 8>();
  if (v.sign() < 0) { put('-'); v = -v; }
  const F ten(10), one(1);
  int e10 = 0;
  while (!(v < ten)) { v = v / ten; ++e10; }
  while (v < one) { v = v * ten; --e10; }
  char digits[128];
  if (sig > 120) sig = 120;
  for (int i = 0; i < sig; ++i) {
    const F d = floor(v);
    digits[i] = char('0' + d.to_int());
    v = (v - d) * ten;
  }
  // round half up on the next digit, with carry
  if (floor(v).to_int() >= 5) {
    int i = sig - 1;
    while (i >= 0 && digits[i] == '9') digits[i--] = '0';
    if (i >= 0) ++digits[i];
    else { for (int j = sig - 1; j > 0; --j) digits[j] = digits[j - 1]; digits[0] = '1'; ++e10; }
  }
  put(digits[0]);
  put('.');
  for (int i = 1; i < sig; ++i) put(digits[i]);
  put('e');
  if (e10 < 0) { put('-'); e10 = -e10; } else put('+');
  char eb[8]; int n = 0;
  do { eb[n++] = char('0' + e10 % 10); e10 /= 10; } while (e10);
  while (n < 2) eb[n++] = '0';
  while (n) put(eb[--n]);
  out[k] = 0;
  return k;
}

}  // namespace fsot::core
