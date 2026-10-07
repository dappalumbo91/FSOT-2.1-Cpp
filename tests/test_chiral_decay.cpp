// Lifetime F_pi and F_K/F_pi. Passes when the Durr-scale reading matches the
// AEB2AD evaluation and both |z| values are <= 1. The residue checkpoint is
// unchanged. Not a precision-record row.
#include <cstdio>
#include <string>

#include "fsot/host/chiral_decay.hpp"

using namespace fsot;

static int fails = 0;

static void expect(bool ok, const char* name, const std::string& detail) {
  if (ok) return;
  std::printf("  FAIL %s %s\n", name, detail.c_str());
  ++fails;
}

int main() {
#if !defined(FSOT_HAVE_BOOST_MP)
  std::puts("CHIRAL DECAY: skipped (needs Boost.Multiprecision)");
  return 0;
#else
  Engine<mp169> eng;
  leaves::SeedLeaves<mp169> seeds(eng);
  const decay::Reading<mp169> row = decay::from_leaves<mp169>(eng, seeds);
  const mp169 zp = row.z_pi();
  const mp169 zr = row.z_ratio();
  const mp169 tol = lit<mp169>("1e-12");
  expect(m::fabs(row.pi.value - lit<mp169>("92.4012708541314751")) <= tol, "F_pi", to_string(row.pi.value, 21));
  expect(m::fabs(zp) <= mp169(1), "pi bar", to_string(zp, 16));
  expect(m::fabs(zp - lit<mp169>("0.8374505961")) <= lit<mp169>("1e-9"), "pi z", to_string(zp, 16));
  expect(m::fabs(row.ratio - lit<mp169>("1.191537555726962")) <= tol, "ratio", to_string(row.ratio, 18));
  expect(m::fabs(zr) <= mp169(1), "ratio bar", to_string(zr, 16));
  expect(m::fabs(zr - lit<mp169>("-0.79164013")) <= lit<mp169>("1e-7"), "ratio z", to_string(zr, 16));
  expect(m::fabs(row.pi.lbar1 - lit<mp169>("-0.15209172795246319")) <= lit<mp169>("1e-16"), "lbar1",
         to_string(row.pi.lbar1, 20));
  expect(m::fabs(row.pi.lbar2 - lit<mp169>("4.2429916610952306")) <= lit<mp169>("1e-15"), "lbar2",
         to_string(row.pi.lbar2, 20));

  const mp169 mp = seeds.mev(seeds.proton_ratio() * seeds.m_e_kg());
  const mp169 F = mp / (mp169(2) * m::sqrt(mp169(3)) * eng.PI);
  const mp169 M_pi = seeds.pion_MeV();
  const mp169 rho = mp169(2) * m::sqrt(mp169(2)) * eng.PI * F;
  const mp169 Msig = F * m::sqrt(mp169(16) * eng.PI * eng.PI / mp169(3));
  const auto check = [&](const char* name, const mp169& mu) {
    const mp169 L = m::ln(M_pi * M_pi / (mu * mu));
    const decay::Pieces<mp169> p = decay::at_log<mp169>(F, M_pi, row.pi.residue, L);
    const mp169 z = (p.value - row.pi_center) / row.pi_sigma;
    expect(m::fabs(z) <= mp169(1), name, to_string(p.value, 18) + " z " + to_string(z, 8));
  };
  check("mu=Mpi", M_pi);
  check("mu=Msig", Msig);
  check("mu=rho", rho);

  std::printf("chiral_decay F_pi %s  z %s  ratio %s  z %s  %s\n", to_string(row.pi.value, 18).c_str(),
              to_string(zp, 8).c_str(), to_string(row.ratio, 16).c_str(), to_string(zr, 8).c_str(),
              fails ? "FAIL" : "PASS");
  if (fails) {
    std::printf("CHIRAL DECAY: %d failures\n", fails);
    return 1;
  }
  std::puts("CHIRAL DECAY: pass, record unchanged");
  return 0;
#endif
}
