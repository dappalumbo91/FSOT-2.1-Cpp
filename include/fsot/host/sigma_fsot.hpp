// fsot/host/sigma_fsot.hpp — derived FSOT uncertainty per scored row (SPEC t1027s4342 §1, Tracer sha8 bcefad59;
// HOLDOUT_CHECK item 1, approved by Damian t1027s4342 2026-11-18 12:08 EST). REPORTING ONLY: Damian put the kill
// band k on HOLD (t1031u, 12:20 EST), so nothing here produces a pass/fail verdict.
//
//   sigma_mult  sample standard deviation (n-1) of the in-engine competing forms of the same quantity (tip leaf vs
//               closed form vs constructed survey definition; value_parity when it is a genuine alternate form).
//               n = 1 -> 0. The LOOK_ELSEWHERE grammar is NOT folded in (that is a p-value proxy, G-05).
//   sigma_D     |v_D6 - v_D5| / sqrt(2) for rows that read a D_eff-dependent input (t1023u: v_D6 carried; D-04 open).
//   sigma_prec  RMS spread across emitted floating-point modes; 0 while only one mode is emitted.
//   sigma_fsot  sqrt(sigma_mult^2 + sigma_D^2 + sigma_prec^2)  (independent systematic variances, quadrature;
//               no prefactor, floor or cap)
//   z_combined  (v_carried - v_obs) / sqrt(sigma_obs_facing^2 + sigma_fsot^2), signed.
#pragma once
#include <cmath>
#include <vector>

namespace fsot::sigma {

struct Parts {
  double mult = 0, D = 0, prec = 0, fsot = 0;
};

// distinct forms only: two engine paths that evaluate to the same number are one form
inline double sample_sd_distinct(std::vector<double> v, double rel_tol = 1e-15) {
  std::vector<double> d;
  for (double x : v) {
    bool dup = false;
    for (double y : d) if (std::fabs(x - y) <= rel_tol * std::fmax(std::fabs(x), std::fabs(y))) { dup = true; break; }
    if (!dup) d.push_back(x);
  }
  if (d.size() < 2) return 0;
  double m = 0;
  for (double x : d) m += x;
  m /= double(d.size());
  double s = 0;
  for (double x : d) s += (x - m) * (x - m);
  return std::sqrt(s / double(d.size() - 1));
}

inline Parts parts(const std::vector<double>& forms, double v_D6, double v_D5, double prec = 0) {
  Parts p;
  p.mult = sample_sd_distinct(forms);
  p.D = std::fabs(v_D6 - v_D5) / std::sqrt(2.0);
  p.prec = prec;
  p.fsot = std::sqrt(p.mult * p.mult + p.D * p.D + p.prec * p.prec);
  return p;
}

// signed; facing-side sigma_obs chosen by the caller's sign convention (sigma_minus when v < central)
inline double z_combined(double v, double central, double sigma_minus, double sigma_plus, double sigma_fsot) {
  const double so = v >= central ? sigma_plus : sigma_minus;
  return (v - central) / std::sqrt(so * so + sigma_fsot * sigma_fsot);
}

// 2D CPL (w0, w_a) chi^2 = d^T C^-1 d with C = [[s0^2, r s0 sa], [r s0 sa, sa^2]] (SPEC §2.3).
inline double chi2_2d(double d0, double da, double s0, double sa, double rho) {
  const double det = s0 * s0 * sa * sa * (1 - rho * rho);
  return (sa * sa * d0 * d0 - 2 * rho * s0 * sa * d0 * da + s0 * s0 * da * da) / det;
}

}  // namespace fsot::sigma
