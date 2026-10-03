#!/usr/bin/env python3
"""Write audit/FREEZE_2026-10-02m.{md,json,sha256}. Committed BEFORE the round-m scoring script exists."""
import hashlib, json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "audit")
F = {
 "freeze": "FREEZE_2026-10-02m", "date": "2026-10-02", "authority_pin": "AEB2AD (unchanged)", "hub_data_commit": "6f9c2560 (unchanged)",
 "owner_instruction": "round m: continue the round-l next branches; derive inside FSOT; freeze before scoring; held-out tests; look-elsewhere counts",
 "M-1 ratio organization": {
  "ratios": "r = MeV-read leaf / 1.956952 (pure m_e multiples; 1.956952 = MeV/(m_e c^2) from the FSOT m_e leaf, used as the exact quotient 1/m_e[MeV])",
  "domain ratio structure": {
   "Particle_Physics (D_eff 5)": "pi, K by L-A1 (round l); D: heavy-light, r_D = r_c + Lambda-bar/m_e (no FSOT absolute m_c: recorded, not derived)",
   "High_Energy_Physics (D_eff 6, hits 1)": "r_Z = r_W / (m_W/m_Z leaf) (internal consistency of the W/Z pair); r_H: no FSOT quartic coupling",
   "Nuclear_Physics (D_eff 12)": "r(3H)/r(2H), r(4He)/r(3H) (Tjon structure; pionless-EFT LO unitary limit gives B(4He)/B(3H) ~ 4.61, Hammer-Platter 2007)"},
  "organization test": "families ln r = a + b D_eff (R1), a + b ln D_eff (R2), a + b S_domain (R3); training pi+- (PP), m_W (HEP), B(2H) (NUC); held-out m_K+-, m_D+-, m_Z, m_H, B(3H), B(4He); gate 2 % on the measured value",
  "tjon test": "held-out B(4He) = 4.61 x B(3H) leaf (LO universal tetramer ratio) vs AME2020 28.295674; gate 2 %",
  "look_elsewhere": "3 families + 1 Tjon ratio",
  "disclosure": "a one-variable map of the domain gives the same r for every leaf of a domain, so K/D vs pi and Z/H vs W are not expected to pass; run as frozen"},
 "M-2 mesons beyond LO": {
  "M-2a pi0 (EM, Das-Guralnik-Mathur-Low-Young 1967)": {
   "physics": ("the pi+ - pi0 splitting is electromagnetic (the QCD part is O((m_d-m_u)^2), ~0.1 MeV, neglected); DGMLY: Delta_pi = (3 alpha/4pi) M_V^2 M_A^2/(M_A^2-M_V^2) ln(M_A^2/M_V^2); "
               "Weinberg sum rules M_A^2 = 2 M_V^2 and large-N_c lowest-meson dominance M_V^2 = 24 pi^2 F^2/N_c with N_c = 3 give Delta_pi = 12 pi alpha ln2 F^2"),
   "FSOT inputs": "alpha (FSOT seed), M_pi+- leaf; F variants: K-1a 91.7766 (HYBRID) and M-3 F_QLsM (FSOT-only)",
   "prediction": "M_pi0 = sqrt(M_pi+-^2 - Delta_pi), held-out vs PDG 134.9768(5)",
   "validation": "PDG M_pi+-, FLAG F_pi 92.07: pass iff within 2 %"},
  "M-2b K0 via the L5/L8-free ratio Q (Gasser-Leutwyler 1985)": {
   "physics": ("Q^2 = (m_s^2 - m_ud^2)/(m_d^2 - m_u^2) fixes the QCD kaon splitting with no NLO low-energy constants: "
               "(M_K0^2 - M_K+^2)_QCD = Mh_K^2 (Mh_K^2 - Mh_pi^2)/(Q^2 Mh_pi^2), Mh_pi = M_pi0 (M-2a), Mh_K^2 = M_K+^2 - Delta_K + split/2 (solved by fixed point); "
               "EM: Delta_K = (1 + eps) Delta_pi; variant a eps = 0 (Dashen), variant b eps = 0.79 (FLAG 2024, HYBRID, the Dashen-violating term)"),
   "FSOT inputs": "Q from the m_u/m_d and m_s/m_d pins (22.7315), M_K+- leaf, M-2a",
   "prediction": "M_K0 held-out vs PDG 497.611(13)", "validation": "PDG masses, FLAG Q 22.5 (2+1+1), FLAG F: pass iff within 2 %"},
  "M-2c eta, eta' (U(3) large-N_c, Witten-Veneziano)": {
   "physics": ("octet-singlet mass matrix at LO in large N_c: M_88^2 = (2/3)(Bm + 2 Bm_s), M_00^2 = (2/3)(2Bm + Bm_s) + M0^2, M_08^2 = -(2 sqrt2/3)(Bm_s - Bm); "
               "Bm = Mh_pi^2/2, Bm_s = Mh_K^2 - Bm (from M-2a/M-2b variant a); Witten-Veneziano M0^2 = 2 N_f chi_top/F^2 with N_f = 3"),
   "inputs": "chi_top^(1/4) = 191(5) MeV (quenched lattice, Del Debbio-Giusti-Pica 2005; HYBRID), F = K-1a",
   "prediction": "eigenvalues -> M_eta, M_eta' held-out vs PDG 547.862(17), 957.78(6); mixing angle reported",
   "validation": "PDG masses, FLAG F, same chi: pass iff each within 5 %"},
  "L5, L8": "no FSOT form this round (needs a scalar-resonance mass); M-2b uses Q precisely because it is L5/L8-independent",
  "look_elsewhere": "M-2a 1 form x 2 F inputs; M-2b 1 form x 2 eps; M-2c 1 form",
  "disclosure": "mental estimate before freeze: M-2a with K-1a F gives M_pi0 ~133.7 MeV"},
 "M-3 f_pi and g_A": {
  "M-3a F (quark-level linear sigma model, Delbourgo-Scadron 1995)": {
   "physics": "quark-level Goldberger-Treiman F = M_Q/g_piqq with g_piqq = 2 pi/sqrt(N_c) (N_c = 3) and constituent mass M_Q = m_p/3 from the anchored proton: F = m_p/(2 sqrt3 pi)",
   "score": "vs physical F_pi 92.07(57) (FLAG, 130.2/sqrt2) and vs chiral-limit F_0 = 92.07/1.062 (FLAG ratio, HYBRID comparison)",
   "validation": "PDG m_p in the same formula vs FLAG F_pi: pass iff within 10 %", "class": "FSOT-only (m_p anchored, N_c = 3)",
   "disclosure": "mental estimate before freeze: ~86.2 MeV"},
  "M-3b g_A": "no FSOT-internal form this round (SU(6) 5/3, MIT bag, Skyrme failed in rounds j/k)",
  "M-3c g_piNN": "GT g_A m_N/F with M-3a F and lattice g_A: HYBRID",
  "look_elsewhere": "M-3a 1 form, 2 comparisons"},
 "downstream gate": "KSRF/VMD -> Delta alpha_had -> Gamma_Z/M_Z and the deuteron chain run only if F and g_A are both FSOT-only and validated within 2 %",
 "counting": "pi0, eta, eta', K0, F, g_A are not among the 91 rows; totals change only if a record row is newly confirmed",
}
open(os.path.join(D, "FREEZE_2026-10-02m.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(F, indent=1, ensure_ascii=False) + "\n")
open(os.path.join(D, "FREEZE_2026-10-02m.md"), "w", encoding="utf-8", newline="\n").write("# FREEZE_2026-10-02m (committed before the round-m scoring script)\n\n```json\n" + json.dumps(F, indent=1, ensure_ascii=False) + "\n```\n")
with open(os.path.join(D, "FREEZE_2026-10-02m.sha256"), "w", newline="\n") as f:
    for n in ("FREEZE_2026-10-02m.json", "FREEZE_2026-10-02m.md"):
        f.write(hashlib.sha256(open(os.path.join(D, n), "rb").read()).hexdigest() + "  " + n + "\n")
print("written")
