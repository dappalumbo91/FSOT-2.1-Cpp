#!/usr/bin/env python3
"""Write audit/FREEZE_2026-10-02n.{md,json,sha256}. Committed BEFORE the round-n scoring script and the soliton solver exist."""
import hashlib, json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "audit")
F = {
 "freeze": "FREEZE_2026-10-02n", "date": "2026-10-02", "authority_pin": "AEB2AD (unchanged)", "hub_data_commit": "6f9c2560 (unchanged)",
 "N-1 physical F_pi at NLO": {
  "physics": ("SU(2) ChPT: F_pi = F [1 + M_pi^2 lbar4/(16 pi^2 F^2)] (Gasser-Leutwyler 1984). In the quark-level linear sigma model the sigma is "
              "the chiral partner with m_sigma = 2 M_Q and tree-level sigma exchange gives l4^r(m_sigma) = F^2/m_sigma^2; with F = M_Q sqrt(N_c)/(2 pi) "
              "this is 16 pi^2 F^2/m_sigma^2 = N_c. Running lbar4 = 16 pi^2 l4^r(mu) - ln(M^2/mu^2) to mu = m_sigma gives lbar4 = N_c + ln(m_sigma^2/M_pi^2)."),
  "forms": {"N-1a (one loop, sigma scale)": "lbar4 = N_c + ln(4 M_Q^2/M_pi^2)", "N-1b (tree only)": "lbar4 = N_c"},
  "FSOT inputs": "M_Q = m_p/3 (anchored), N_c = 3, F = M-3a m_p/(2 sqrt3 pi), M_pi = pi+- leaf",
  "validation": "same forms with PDG m_p, M_pi+: F_pi/F within 2 % of FLAG 2+1 1.062(7)",
  "score": "F_pi vs 92.07(57) (FLAG 130.2(8)/sqrt2), lbar4 vs FLAG 2+1 4.40(28) (information); agree iff validation passes and within 2 %",
  "look_elsewhere": 2,
  "disclosure": "mental evaluation before freeze: N-1a ~94.8 MeV, N-1b ~90.5 MeV; m_sigma/M_pi ~ 4.48"},
 "N-2 g_A, chiral quark soliton (valence level)": {
  "physics": ("chiral quark model H = alpha.p + beta M (cos theta + i gamma5 tau.rhat sin theta) with constituent mass M = M_Q = m_p/3; "
              "hedgehog profile theta(r) = 2 arctan(r0^2/r^2) (Diakonov-Petrov-Pobylitsa 1988 variational form); grand-spin-0 valence level from "
              "u' = -M sin(theta) u + (E + M cos theta) v, v' = -(2/r) v + M sin(theta) v - (E - M cos theta) u, u(0) finite, v(0) = 0, decaying at infinity; "
              "Dirac-sea energy at leading gradient order E_sea = (F^2/2) 4 pi Int r^2 dr [theta'^2 + 2 sin^2 theta / r^2] with F = M-3a; "
              "soliton E(r0) = N_c E_val(r0) + E_sea(r0) minimized over r0 M in [0.2, 4]"),
  "g_A projection": "g_A = ((N_c + 2)/3) Int (u^2 - v^2/3) r^2 dr / Int (u^2 + v^2) r^2 dr (valence quark; sea axial contribution neglected)",
  "numerics": "shooting on E in (-M, M) with RK4 on r in [1e-6, 12/M] (mpmath-free, double precision); memory cap ulimit -v 6000000, run alone",
  "validation": "same with PDG m_p/3 and FLAG F_pi: g_A within 10 % of PDG 1.2754(13)",
  "score": "FSOT g_A vs 1.2754(13); FSOT-only if F and M_Q are FSOT; agree iff validation passes and within 2 %",
  "look_elsewhere": 1, "fallback": "if no bound valence level or no interior minimum: reported as no soliton"},
 "N-3 downstream": {
  "gate": "run KSRF/VMD -> Delta alpha_had -> Gamma_Z/M_Z only if N-1 F_pi and N-2 g_A are FSOT-only and agree; then require LMD m_rho = 2 sqrt2 pi F_pi within 1 % of 775.26(23)",
  "deuteron": ("LO pionless EFT with the FSOT B(2H) leaf: gamma = sqrt(m_N B)/hbar c, point rms radius r_d = 1/(sqrt8 gamma), held-out vs the deuteron structure radius "
               "1.97507(78) fm (CODATA 2018, r_str); gate 2 %; mu_d not computable (no FSOT mu_n leaf); g_piNN enters only at NLO (not run this round)"),
  "look_elsewhere": 1},
 "N-4 eta/eta'": "not built: no physically grounded FSOT form for chi_top was found; next branch is chi_top from an instanton-liquid density with FSOT Lambda",
 "N-5 D_eff on one reference leaf per domain": {
  "references": "Particle_Physics pi+- (r = M/m_e), High_Energy_Physics W, Nuclear_Physics B(2H), Atomic_Physics E_h (E_h/(m_e c^2), SI leaf)",
  "families": {"P1": "ln r = a + b D_eff, trained on pi (D 5) and B(2H) (D 12); held-out W (D 6), E_h (D 6)",
               "P2": "ln r = a + b D_eff + c S, trained on pi, W, B(2H); held-out E_h"},
  "measured": "pi+- 139.57039, W 80369.2, B(2H) 2.224566 (AME2020), E_h 4.3597447222060e-18 J (CODATA 2018)",
  "gate": "2 %", "look_elsewhere": 2},
 "counting": "none of F_pi, g_A, r_d is among the 91 rows; totals change only if a record row is newly confirmed",
}
open(os.path.join(D, "FREEZE_2026-10-02n.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(F, indent=1, ensure_ascii=False) + "\n")
open(os.path.join(D, "FREEZE_2026-10-02n.md"), "w", encoding="utf-8", newline="\n").write("# FREEZE_2026-10-02n (committed before the round-n scoring script and soliton solver)\n\n```json\n" + json.dumps(F, indent=1, ensure_ascii=False) + "\n```\n")
with open(os.path.join(D, "FREEZE_2026-10-02n.sha256"), "w", newline="\n") as f:
    for n in ("FREEZE_2026-10-02n.json", "FREEZE_2026-10-02n.md"):
        f.write(hashlib.sha256(open(os.path.join(D, n), "rb").read()).hexdigest() + "  " + n + "\n")
print("written")
