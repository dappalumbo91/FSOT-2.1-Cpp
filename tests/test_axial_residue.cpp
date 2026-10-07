// Leaf-curvature axial residue. The test passes when the C++ evaluation reproduces
// the scored miss. A z inside the lifetime bar is a failure of this checkpoint.
#include <cmath>
#include <cstdio>
#include <string>

#include "fsot/host/axial_residue.hpp"
#include "fsot/host/seed_leaves.hpp"

using namespace fsot;

static int fails = 0;

static void expect(bool ok, const char* name, const std::string& detail) {
  if (ok) return;
  std::printf("  FAIL %s %s\n", name, detail.c_str());
  ++fails;
}

int main() {
#if !defined(FSOT_HAVE_BOOST_MP)
  std::puts("AXIAL RESIDUE: skipped (needs Boost.Multiprecision)");
  return 0;
#else
  const mp169 pi_quad = axial::integrate_unit_interval<mp169>([](const mp169& x) {
    return mp169(4) / (mp169(1) + x * x);
  });
  const mp169 pi = real_traits<mp169>::pi();
  expect(m::fabs(pi_quad - pi) <= lit<mp169>("1e-24"), "quadrature pi",
         to_string(pi_quad, 20));

  Engine<mp169> eng;
  leaves::SeedLeaves<mp169> leaves(eng);
  const mp169 mp = leaves.mev(leaves.proton_ratio() * leaves.m_e_kg());
  const mp169 F = mp / (mp169(2) * m::sqrt(mp169(3)) * eng.PI);
  const mp169 Mpi = leaves.pion_MeV();
  const axial::Residue<mp169> r = axial::leaf_curvature(F, Mpi);
  const axial::LifetimeBar<mp169> bar = axial::lifetime_bar<mp169>();
  const mp169 z = (r.F_pi - bar.center) / bar.sigma;
  const mp169 z_trunc = (r.F_trunc - bar.center) / bar.sigma;
  const mp169 z_sigma = (r.F_sigma - bar.center) / bar.sigma;

  const mp169 abs_tol = lit<mp169>("1e-12");
  expect(m::fabs(r.F_pi - lit<mp169>("92.67279093804169177")) <= abs_tol, "F_pi",
         to_string(r.F_pi, 24));
  expect(m::fabs(r.F_trunc - lit<mp169>("92.88662150974877399")) <= abs_tol, "truncation",
         to_string(r.F_trunc, 24));
  expect(m::fabs(r.F_sigma - lit<mp169>("92.55458128806102028")) <= abs_tol, "sigma-mass sibling",
         to_string(r.F_sigma, 24));
  expect(m::fabs(r.d_phi - lit<mp169>("0.01374879020777750513")) <= lit<mp169>("2e-9"), "d_phi",
         to_string(r.d_phi, 18));
  expect(m::fabs(r.d_bubble - lit<mp169>("0.04415137445690631327")) <= lit<mp169>("2e-9"), "d_bubble",
         to_string(r.d_bubble, 18));
  expect(m::fabs(r.d_tadpole - lit<mp169>("-0.27173073637176604342")) <= lit<mp169>("2e-9"), "d_tadpole",
         to_string(r.d_tadpole, 18));
  expect(m::fabs((r.d_phi + r.d_bubble + r.d_tadpole) - (r.F_pi - r.F_trunc)) <= abs_tol, "split sum",
         to_string(r.d_phi + r.d_bubble + r.d_tadpole, 18));
  expect(z > mp169(1), "miss", to_string(z, 16));
  expect(m::fabs(z - lit<mp169>("3.6305478313896237")) <= lit<mp169>("1e-9"), "z",
         to_string(z, 16));
  expect(m::fabs(z_trunc - lit<mp169>("5.83019940063710")) <= lit<mp169>("1e-9"), "z truncation",
         to_string(z_trunc, 16));
  expect(r.F_sigma < r.F_pi && (r.F_pi - r.F_sigma) > lit<mp169>("0.05"), "sibling separated",
         to_string(r.F_sigma, 16));
  expect(z_sigma > mp169(1), "sibling also misses", to_string(z_sigma, 16));

  const axial::Slopes<mp169> s = axial::small_xi_slopes(lit<mp169>("1e-8"));
  expect(m::fabs(s.Ub_over_xi - s.half_Lm1) <= lit<mp169>("1e-5"), "bubble log 1/2",
         to_string(s.Ub_over_xi, 16));
  expect(m::fabs(s.Ut_over_xi - s.half_Lp1) <= lit<mp169>("1e-5"), "tadpole log 1/2",
         to_string(s.Ut_over_xi, 16));
  const mp169 dF_eV = s.d_ratio * F * lit<mp169>("1e6");
  expect(m::fabs(dF_eV) <= lit<mp169>("1e-4"), "small-xi remainder eV", to_string(dF_eV, 12));

  std::printf("chiral F %s MeV\n", to_string(r.F, 18).c_str());
  std::printf("charged pion %s MeV\n", to_string(r.M_pi, 18).c_str());
  std::printf("leaf residue %s MeV  z %s  MISS\n", to_string(r.F_pi, 18).c_str(), to_string(z, 12).c_str());
  std::printf("truncation   %s MeV  z %s  unchanged\n", to_string(r.F_trunc, 18).c_str(),
              to_string(z_trunc, 12).c_str());
  std::printf("sigma-mass   %s MeV  z %s  not the residue\n", to_string(r.F_sigma, 18).c_str(),
              to_string(z_sigma, 12).c_str());
  std::printf("split MeV  vev %s  bubble %s  tadpole %s\n", to_string(r.d_phi, 12).c_str(),
              to_string(r.d_bubble, 12).c_str(), to_string(r.d_tadpole, 12).c_str());
  std::puts(fails ? "AXIAL RESIDUE: FAIL" : "AXIAL RESIDUE: MISS RECORDED");
  return fails ? 1 : 0;
#endif
}
