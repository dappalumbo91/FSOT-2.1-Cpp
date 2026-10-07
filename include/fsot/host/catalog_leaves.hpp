// fsot/host/catalog_leaves.hpp — catalog leaves from owner-decisions-2026-10-02i.
//
// Each formula is the leaf that script froze, evaluated on the AEB2AD seeds.
// Alpha is the inverse-alpha leaf, not the domain constant ALPHA.
// These rows are not on the 91. The authority pin stays AEB2AD.
// Quantum_Mechanics keeps its derived depth. Calcium, hydrogen, carbon dioxide
// sublimation, deuteron binding, and the deuteron moment stay on their bare formulas.
#pragma once
#include "fsot/host/seed_leaves.hpp"

namespace fsot::catalog {

template <class R> struct Scored {
  R value;
  R center;
  R sigma;
  R z() const { return m::fabs(value - center) / sigma; }
};

template <class R> struct Leaves {
  const Engine<R>& F;
  R a;
  explicit Leaves(const leaves::SeedLeaves<R>& L) : F(L.F), a(L.alpha()) {}

  // phi^4/ln(pi) * (1 - alpha*(4/pi^4)*(1 - alpha*e)). NIST ASD 5.12.
  Scored<R> aluminum_ie() const {
    const R bare = m::ipow(F.PHI, 4) / m::ln(F.PI);
    const R piece = R(4) / m::ipow(F.PI, 4);
    return {bare * (R(1) - a * piece * (R(1) - a * F.E)), lit<R>("5.985769"), lit<R>("0.000003")};
  }

  // phi^7/sqrt(5) * (1 - alpha*(5/phi^7)*(1 + alpha*(7-phi)*(1 + alpha*sqrt(phi)))).
  Scored<R> chlorine_ie() const {
    const R bare = m::ipow(F.PHI, 7) / m::sqrt(R(5));
    const R piece = R(5) / m::ipow(F.PHI, 7);
    const R q2 = R(7) - F.PHI;
    const R q3 = m::sqrt(F.PHI);
    return {bare * (R(1) - a * piece * (R(1) + a * q2 * (R(1) + a * q3))), lit<R>("12.967633"),
            lit<R>("0.000016")};
  }

  // e^2 + sqrt(gamma)*(1 + alpha*(1/2)*(1 + alpha*(e^2-2)*(1 - alpha*(e^2-2)))).
  Scored<R> silicon_ie() const {
    const R e2 = F.E * F.E;
    const R root = m::sqrt(F.GAMMA);
    const R diff = e2 - R(2);
    const R half = R(1) / R(2);
    return {e2 + root * (R(1) + a * half * (R(1) + a * diff * (R(1) - a * diff))), lit<R>("8.15168"),
            lit<R>("0.00003")};
  }

  // pi^2 + (1/phi)*(1 - alpha*(2/pi^2)*(1 + alpha*(pi+phi^2)*(1 + alpha*(2/pi^2)))).
  Scored<R> phosphorus_ie() const {
    const R pi2 = F.PI * F.PI;
    const R inv = R(1) / F.PHI;
    const R piece = R(2) / pi2;
    const R q2 = F.PI + F.PHI * F.PHI;
    return {pi2 + inv * (R(1) - a * piece * (R(1) + a * q2 * (R(1) + a * piece))), lit<R>("10.486686"),
            lit<R>("0.000015")};
  }

  // (phi^6/sqrt(3))*(1 - alpha*(6/phi^18)*(1 + alpha*(6*bare)*(1 - alpha*2*(1 + alpha*(phi^6+3)*(1+alpha))))).
  Scored<R> sulfur_ie() const {
    const R bare = m::ipow(F.PHI, 6) / m::sqrt(R(3));
    const R piece = R(6) / m::ipow(F.PHI, 18);
    const R q2 = R(6) * bare;
    const R q4 = m::ipow(F.PHI, 6) + R(3);
    return {bare * (R(1) - a * piece * (R(1) + a * q2 * (R(1) - a * R(2) * (R(1) + a * q4 * (R(1) + a))))),
            lit<R>("10.3600167"), lit<R>("0.0000014")};
  }

  // (gamma^-5 + Poof) * (1 - alpha*(Poof*gamma^5)*(1 - alpha*(5/gamma^5)*(1 - alpha*5*(1 + alpha*(5/gamma)*(1 - alpha*5*(1+gamma)))))).
  Scored<R> argon_ie() const {
    const R g5 = m::pow(F.GAMMA, R(-5));
    const R bare = g5 + F.POOF;
    const R piece = F.POOF * m::ipow(F.GAMMA, 5);
    const R q2 = R(5) * g5;
    const R q4 = R(5) / F.GAMMA;
    const R q5 = R(5) * (R(1) + F.GAMMA);
    return {bare * (R(1) - a * piece *
                              (R(1) - a * q2 * (R(1) - a * R(5) * (R(1) + a * q4 * (R(1) - a * q5))))),
            lit<R>("15.7596119"), lit<R>("0.0000005")};
  }

  // (phi^3 + pi^-2) * (1 + alpha*pi^-2*(1 + alpha*(3-pi^-2)*(1 - alpha*(2/phi^3)*(1 - alpha*2)))).
  Scored<R> potassium_ie() const {
    const R phi3 = m::ipow(F.PHI, 3);
    const R pim2 = m::pow(F.PI, R(-2));
    const R bare = phi3 + pim2;
    const R p2 = R(3) - pim2;
    const R p3 = R(2) / phi3;
    return {bare * (R(1) + a * pim2 * (R(1) + a * p2 * (R(1) - a * p3 * (R(1) - a * R(2))))),
            lit<R>("4.34066373"), lit<R>("9e-8")};
  }

  // (pi^7 * gamma^6) * (1 - alpha*(1/(7*pi))*(1 + alpha*6*(1+gamma))). Half of the last quoted mK.
  Scored<R> methane_bp() const {
    const R bare = m::ipow(F.PI, 7) * m::ipow(F.GAMMA, 6);
    const R p1 = R(1) / (R(7) * F.PI);
    const R p2 = R(6) * (R(1) + F.GAMMA);
    return {bare * (R(1) - a * p1 * (R(1) + a * p2)), lit<R>("111.667"), lit<R>("0.0005")};
  }

  // (e^5 * phi) * (1 - alpha*(1/5)*(1 - alpha*5*(1+e))). Bar from the stated 0.05% vapor pressure.
  Scored<R> ammonia_bp() const {
    const R bare = m::ipow(F.E, 5) * F.PHI;
    const R nist = lit<R>("239.832");
    const R p_nist = lit<R>("101325");
    const R slope = (p_nist - lit<R>("1.0070e5")) / (nist - lit<R>("239.71"));
    const R bar = (p_nist * lit<R>("0.0005")) / slope;
    const R p1 = R(1) / R(5);
    const R p2 = R(5) * (R(1) + F.E);
    return {bare * (R(1) - a * p1 * (R(1) - a * p2)), nist, bar};
  }

  // (pi^8 * gamma^6) * (1 + alpha*(gamma/pi)*(1 + alpha*6*(1+gamma))). Half of the printed hundredth.
  Scored<R> ethanol_bp() const {
    const R bare = m::ipow(F.PI, 8) * m::ipow(F.GAMMA, 6);
    const R p1 = F.GAMMA / F.PI;
    const R p2 = R(6) * (R(1) + F.GAMMA);
    return {bare * (R(1) + a * p1 * (R(1) + a * p2)), lit<R>("351.44"), lit<R>("0.005")};
  }

  // (e^6 * pi / phi) * (1 + alpha*(e/6)). Half of the printed integer.
  Scored<R> nacl_lattice() const {
    const R bare = m::ipow(F.E, 6) * F.PI / F.PHI;
    return {bare * (R(1) + a * (F.E / R(6))), lit<R>("786"), lit<R>("0.5")};
  }

  // (e^4 + phi^7) * (1 + alpha*(phi/e)). Half of the printed integer.
  Scored<R> olive_oil_viscosity() const {
    const R bare = m::ipow(F.E, 4) + m::ipow(F.PHI, 7);
    return {bare * (R(1) + a * (F.PHI / F.E)), lit<R>("84"), lit<R>("0.5")};
  }

  // e^3 * (1 - alpha/e). Half of the printed integer.
  Scored<R> cyclohexane_kf() const {
    const R bare = m::ipow(F.E, 3);
    return {bare * (R(1) - a * (R(1) / F.E)), lit<R>("20"), lit<R>("0.5")};
  }
};

}  // namespace fsot::catalog
