// fsot/host/precision_gate.hpp — the one place the C++ verification's precision gate is configured.
//
// Gate (Damian's rule, adopted 2026-10-02): a prediction passes when
//     z = |value - central| / sigma  <=  Z_MAX = 1
// with sigma the published standard uncertainty on the side of the central value where the prediction
// lies (asymmetric PDG errors), taken from reference/published_2026-10-02.tsv (PDG 2024, CODATA 2022,
// AME2020, Planck 2018 via the PDG 2024 astrophysical-constants table). The same gate is applied to every
// row. The legacy relative check (|value-central|/|central| <= OLD_REL_PCT %) and the ppm error are
// reported next to it for comparison only. Nothing here changes an FSOT constant or a frozen value.
#pragma once
#include <cmath>

namespace fsot::gate {

inline constexpr double Z_MAX = 1.0;        // pass iff z <= Z_MAX
inline constexpr double OLD_REL_PCT = 2.0;  // legacy relative check, reported only

struct Ref { long double central; long double sigma_minus; long double sigma_plus; };
struct Score { long double z; long double rel_pct; long double ppm; bool pass_z; bool pass_old; };

inline Score score(long double value, const Ref& r) {
  const long double d = value - r.central;
  const long double sig = d >= 0 ? r.sigma_plus : r.sigma_minus;
  Score s;
  s.z = std::fabs(d) / sig;
  s.rel_pct = std::fabs(d) / std::fabs(r.central) * 100.0L;
  s.ppm = s.rel_pct * 1.0e4L;
  s.pass_z = s.z <= Z_MAX;
  s.pass_old = s.rel_pct <= OLD_REL_PCT;
  return s;
}

}  // namespace fsot::gate
