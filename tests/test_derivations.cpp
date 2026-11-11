// D-01..D-10 (fsot_unified/DISCREPANCIES.md) settled by derivation inside the engine. Prints a verdict per item and
// fails if a derivation stops reproducing the engine (or the engine drifts from what the derivation implies).
#include <cstdio>
#include <fstream>
#include <sstream>
#include <string>

#include "fsot/derive/discrepancies.hpp"
#include "fsot/trit.hpp"

using namespace fsot;
static int fails = 0;
#define CHECK(c, ...) do { if (!(c)) { std::printf("  FAIL: " __VA_ARGS__); std::printf("\n"); ++fails; } } while (0)

template <class R> void run(const char* tag) {
  Engine<R> F;
  // D-02
  const auto v = derive::derive_c_cosm(F);
  const auto p = derive::rebuild_layer2(F, m::ipow(F.PI, 2));
  const auto t = derive::rebuild_layer2(F, R(10));
  std::printf("[%s] D-02 decade=pi^2 rebuilds C_EFF,K: %s | decade=10 rebuilds C_EFF,K: %s\n", tag,
              v.pi2_reproduces_layer2 ? "bit-identical" : "NO", v.ten_reproduces_layer2 ? "yes" : "no");
  std::printf("[%s] D-02 derived C_cosm = 1/(phi*decade) = %.17g (engine %.17g); 1/(10phi) = %.17g needs decade=10, "
              "which moves C_EFF by %.3e and K by %.3e\n", tag, double(v.c_cosm_derived), double(F.C_COSM), double(t.c_cosm),
              double((t.c_eff - F.C_EFF) / F.C_EFF), double((t.k - F.K) / F.K));
  CHECK(v.pi2_reproduces_layer2, "decade pi^2 no longer rebuilds C_EFF/K");
  CHECK(!v.ten_reproduces_layer2, "decade 10 rebuilds C_EFF/K?");
  CHECK(v.c_cosm_derived == F.C_COSM, "derived C_cosm != engine C_COSM");
  (void)p;
  // D-03
  const auto c = derive::lean_sync(F);
  std::printf("[%s] D-03 Lean caches: S_cosm %.16g S_quant %.16g H0 %.15g T_CMB %.15g n_s %.16g Ob_h2(engine) %.16g "
              "Ob_h2(Lean formula) %.16g c_cosm %.16g\n", tag, double(c.S_cosm), double(c.S_quant), double(c.H0),
              double(c.T_CMB), double(c.n_s), double(c.Omega_b_h2_engine), double(c.Omega_b_h2_lean_formula), double(c.c_cosm));
  CHECK(std::abs(double(c.S_cosm) - (-0.5023773181761478)) < 1e-15, "S_cosm");
  CHECK(std::abs(double(c.S_quant) - 0.9552893400916406) < 1e-15, "S_quant (rung 6)");
  // D-04
  std::printf("[%s] D-04 QM continuous rung 5*5^(1/19) = %.6f; nest rule -> %d; engine (owner rung-6 override) -> %d\n", tag,
              derive::nest_rung_continuous(1), derive::nest_rung_rule("Quantum_Mechanics"), derived_D_eff("Quantum_Mechanics"));
  for (auto& tr : derive::qm_rung_trials())
    std::printf("        rule %-44s QM=%d, other rungs moved=%d%s\n", tr.rule, tr.qm, tr.others_moved,
                (tr.qm == 6 && tr.others_moved == 0) ? "  <- would derive 6" : "");
  int n_derive6 = 0;
  for (auto& tr : derive::qm_rung_trials()) if (tr.qm == 6 && tr.others_moved == 0) ++n_derive6;
  std::printf("        => %s\n", n_derive6 ? "a rule derives 6" : "no tested first-principles rule derives 6; derivation gives 5; FLAGGED (owner rung 6 kept)");
  CHECK(derive::nest_rung_rule("Quantum_Mechanics") == 5, "nest rule for QM");
  int other_mismatch = 0;
  for (auto n : domain_names()) if (n != "Quantum_Mechanics" && derive::nest_rung_rule(n) != derived_D_eff(n)) ++other_mismatch;
  CHECK(other_mismatch == 0, "34 non-QM rungs must equal the nest rule (%d differ)", other_mismatch);
  // D-05
  const auto ch = derive::chemlink_from_nest();
  const int gate = derive::long_range_gate_biochem(F);
  std::printf("[%s] D-05 ChemLink from nest: biochem %d condensed %d EM %d molecular %d physChem %d chem %d atomic %d; "
              "long-range gate ceil(eta_eff*%d) = ceil(%.4f) = %d\n", tag, ch.biochem, ch.condensed, ch.em, ch.molecular,
              ch.physchem, ch.chem, ch.atomic, ch.biochem, double(F.ETA_EFF) * ch.biochem, gate);
  CHECK(ch.biochem == 10 && ch.condensed == 11 && ch.em == 7 && ch.molecular == 7 && ch.physchem == 6 && ch.chem == 6 && ch.atomic == 6,
        "ChemLink nest table");
  CHECK(gate == 5, "long-range gate");
  // D-06
  std::printf("[%s] D-06 species inherit Neuroscience rung %d (no per-species D_eff)\n", tag, derived_D_eff("Neuroscience"));
  CHECK(derived_D_eff("Neuroscience") == 11, "Neuroscience rung");
}

int main() {
  run<double>("double");
#if defined(FSOT_HAVE_BOOST_MP)
  run<mp169>("mp169");
#endif
  // D-01: pin of the hub authority, LF vs CRLF
#ifdef FSOT_HUB_DATA_DIR
  {
    std::ifstream in(std::string(FSOT_HUB_DATA_DIR) + "/vendor/fsot_compute.py", std::ios::binary);
    if (in) {
      std::stringstream ss; ss << in.rdbuf(); const std::string raw = ss.str();
      std::string lf; for (char ch : raw) if (ch != '\r') lf += ch;
      const auto cr = derive::to_crlf(raw);
      std::printf("D-01 hub vendor/fsot_compute.py: raw pin %s | LF bytes pin %s | canonical(CRLF) pin %s (raw) / %s (from LF)\n",
                  derive::pin_raw(raw).c_str(), derive::pin_raw(lf).c_str(), derive::pin_canonical(raw).c_str(),
                  derive::pin_canonical(lf).c_str());
      CHECK(derive::pin_canonical(raw) == "AEB2AD" && derive::pin_canonical(lf) == "AEB2AD", "canonical pin must be AEB2AD for both checkouts");
      (void)cr;
    } else std::printf("D-01 skipped (no hub vendor file)\n");
  }
#else
  std::printf("D-01 skipped (FSOT_HUB_DATA not configured)\n");
#endif
  // D-09: both trit encodings are lossless on {-1,0,+1}
  {
    int ok = 0;
    for (int v = -1; v <= 1; ++v) {
      const auto b = trit::pack_t1(static_cast<trit::Trit>(v));
      const auto back = trit::unpack_t1(b);
      if (back && int(*back) == v) ++ok;
    }
    std::printf("D-09 T1 packing round-trips %d/3 trits\n", ok);
    CHECK(ok == 3, "T1 round trip");
  }
  std::printf("D-07/D-08/D-10: process items (build glob, stamp semantics, toolchains) - nothing to derive\n");
  std::puts(fails ? "DERIVATIONS: FAIL" : "DERIVATIONS: ALL PASS");
  return fails ? 1 : 0;
}
