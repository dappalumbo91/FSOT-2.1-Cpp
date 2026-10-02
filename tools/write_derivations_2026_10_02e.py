#!/usr/bin/env python3
"""Write docs/freezes/DERIVATIONS_2026-10-02e.{md,json,sha256}. Committed BEFORE any downstream number (v, G_F, widths, lifetimes, alpha_s(m_tau), BR) is computed."""
import hashlib, json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "freezes")
step1 = {
  "bug_fix": ("hub vendor/fsot_seed_flavor.py::seed_vev_GeV() documents the tree relation v = 2 m_W sin(theta_W)/sqrt(4 pi alpha) but returns "
              "(theta_S + e^3)/C_factor^6/1000*phi = 58.24 GeV, an erroneous implementation that disagrees with its own docstring (and with v ~ 246 GeV). "
              "seed_G_F() = 1/(sqrt2 v^2) inherits it. This repo implements the documented relation with FSOT leaves; the hub fix is left to Grok Build. "
              "The vendor engine is not edited."),
  "relation": "v = 2 m_W s_W / sqrt(4 pi alpha);  G_F = 1/(sqrt2 v^2) = pi alpha /(sqrt2 m_W^2 s_W^2)  (tree level; equivalent to PDG eq. 10.23/10.26 with Delta r -> 0)",
  "scheme_reasoning": (
    "G_F is defined by the muon lifetime, a q^2 ~ 0 quantity; PDG 2024 (Electroweak review eqs. 10.23-10.26) relates it to the W mass in two standard schemes: "
    "on-shell, M_W^2 s_W^2 = A0^2/(1 - Delta r) with s_W^2 = 1 - M_W^2/M_Z^2, A0 = (pi alpha(0)/(sqrt2 G_F))^1/2, Delta r = 0.03685; and MS-bar, "
    "M_W^2 s_Z^2(hat) = A0^2/(1 - Delta r_W(hat)), Delta r_W(hat) = 0.06937, of which 1 - alpha/alpha_hat(M_Z) ~ 0.0665 is absorbed if alpha_hat(M_Z) replaces alpha(0). "
    "S1 (on-shell, alpha(0)) is the scheme whose every input is a physical low-energy or pole quantity, the same footing as the muon-decay definition of G_F, and it is "
    "the scheme of Damian's own mass sector (seed_m_Z_GeV = m_W/cos(theta_W^os)); all its inputs are FSOT leaves. S2 (MS-bar s^2 leaf with alpha_hat^(5)(M_Z)) has the "
    "smaller known residual (~0.3 %) but needs alpha_hat(M_Z), which FSOT does not predict, so it carries one EXTERNAL input (PDG 127.930(8)). Both are defensible; "
    "S1 is pre-declared PRIMARY because it is FSOT-only and scheme-consistent with FSOT's mass relation. Expected a priori (textbook, before computing): S1 omits "
    "Delta r ~ 3.7 %, so G_F(S1) should come out a few % low unless FSOT's leaves differ from the measured masses."),
  "schemes": {
    "S1_primary": "s_W^2 = 1 - (m_W/m_Z)^2 from leaves m_W_MeV, m_Z_MeV; alpha = 1/alpha_inv leaf (alpha(0)). All FSOT. Only S1 can confirm Gamma_Z/M_Z.",
    "S2_secondary": "s_W^2 = leaf sin2_theta_W_MSbar; alpha = 1/127.930 (PDG 2024 MS-bar alpha^(5)(M_Z), EXTERNAL). Reported, frozen-pending, never confirmed.",
    "rejected_a_priori": ["MS-bar s^2 with alpha(0): mixed-scheme pairing", "on-shell s^2 with alpha(M_Z): mixed-scheme pairing"]},
  "scheme_look_elsewhere": 4,
  "downstream_unchanged": ("The round-d constructions (DERIVATIONS_2026-10-02d) are rerun UNCHANGED with G_F replaced by G_F(S): A1 Gamma_Z, Gamma_Z/M_Z, held-out "
                           "Gamma_inv, Gamma_ll, sigma_had0, R_ell (A2-A4 still reported, not candidates), Gamma_W, tau_mu, tau_tau (external BR, as frozen in round d), and G_F itself."),
  "counting": "Gamma_Z/M_Z counts as confirmed only if A1 under S1 gives z <= 1. Every other row stays frozen-pending as a new row.",
}
step2 = {
  "search_for_existing_routes": ("Searched hub vendor/*.py (seed functions), vendor/fsot_aggregate/FSOT_Mathematical_Database_Unified.json (sec. 66 particle masses, "
                                 "sec. 67 nuclear muN) and data/*.json for an FSOT route to mu_n, mu_t (triton) and f_pi: none exists. No new formula is invented "
                                 "(inventing a seed expression to match a measured value would be tuning to the target)."),
  "mu_n": "NOT CONSTRUCTED (no FSOT route). The SU(6) stand-in of round d remains a frozen-pending stand-in only.",
  "mu_t": "NOT CONSTRUCTED (no FSOT route).",
  "f_pi_and_tau_pi": "NOT CONSTRUCTED: no FSOT f_pi, hence no tau_pi+.",
  "two_nucleon_mu_d": "NOT REDONE: it requires an FSOT mu_n, which does not exist.",
  "alpha_s_mtau": {
    "start": "alpha_s^(5)(mu = M_Z) = seed 2(POOF/psi_con)^2 at M_Z = leaf m_Z_MeV/1000",
    "running": ("4-loop MS-bar beta function, d(a)/d ln mu^2 = -(b0 a^2 + b1 a^3 + b2 a^4 + b3 a^5), a = alpha_s/pi, b0 = (11 - 2nf/3)/4, "
                "b1 = (102 - 38nf/3)/16, b2 = (2857/2 - 5033nf/18 + 325nf^2/54)/64, b3 = [149753/6 + 3564 z3 - (1078361/162 + 6508 z3/27) nf + "
                "(50065/162 + 6472 z3/81) nf^2 + 1093 nf^3/729]/256 (van Ritbergen-Vermaseren-Larin 1997); RK4 in ln mu^2 with 4000 steps per segment"),
    "thresholds": ("decoupling at mu = m_b and mu = m_c (MS-bar masses at their own scale) with the 3-loop relation alpha^(nl) = alpha^(nh)[1 + (11/72) a^2 + "
                   "(564731/124416 - 82043 z3/27648 - 2633 nl/31104) a^3] (Chetyrkin-Kniehl-Steinhauser 1997); m_b = m_t/(m_t/m_b) with m_t = leaf m_t_over_m_W * "
                   "leaf m_W_MeV and m_t/m_b = AEB2AD pin wave8|m_t/m_b; m_c = leaf m_c_over_m_b * m_b"),
    "path": "nf=5 from M_Z down to m_b; nf=4 down to m_c; nf=3 up to m_tau = leaf m_tau_MeV (the nf=3 convention of tau analyses and of the PDG value)",
    "measured": "PDG 2024 QCD review alpha_s(m_tau^2) = 0.314(14)",
    "alternatives_not_scored": ["matching at mu = 2 m_h", "nf=4 at m_tau (no charm decoupling)"], "count": 3},
  "BR_tau_e_and_tau_tau_FSOT": {
    "construction": ("R_tau = 3(|V_ud|^2 + |V_us|^2) S_EW (1 + delta_P), delta_P = a + 5.2023 a^2 + 26.366 a^3 + 127.08 a^4 (fixed-order, nf=3; Baikov-Chetyrkin-Kuhn 2008), "
                     "a = alpha_s^(3)(m_tau)/pi; S_EW = 1 + (2 alpha/pi) ln(M_Z/m_tau) (leading log, FSOT alpha, M_Z, m_tau); V_ud, V_us = FSOT CKM leaves; "
                     "BR_e = 1/(1 + f(m_mu^2/m_tau^2) + R_tau), f(x) = 1 - 8x + 8x^3 - x^4 - 12x^2 ln x; Gamma_e = G_F^2 m_tau^5/(192 pi^3)(1 + alpha/(2pi)(25/4 - pi^2)); "
                     "tau_tau = hbar BR_e/Gamma_e with G_F(S1) (and S2 reported). Quark-mass and non-perturbative corrections omitted (known ~1e-3 level)."),
    "measured": "BR(tau->e nu nu) PDG 2024 17.82(4) %; tau_tau PDG 2024 290.3(5) fs",
    "alternatives_not_scored": ["contour-improved PT", "S_EW = 1.0201 external"], "count": 3},
  "sec67_report": "recompute the six non-reproducing sec. 67 entries with the current fsot_compute constants and list stored vs recomputed vs measured; stored values are NOT replaced",
}
doc = {"freeze": "DERIVATIONS_2026-10-02e", "date": "2026-10-02", "authority_pin": "AEB2AD", "hub_data_commit": "6f9c25605a52acabe662a42fc003afa5bf66b959",
       "step1_vev_GF": step1, "step2_missing": step2, "z": "|value - central|/sigma with the published sigma",
       "look_elsewhere": {"scheme": 4, "alpha_s_mtau": 3, "BR_tau/tau_tau": 3, "downstream_A_alternatives": 4},
       "order": "1) this freeze; 2) compute and score step 1 and step 2 (tools/score_2026_10_02e.py); one push at the end"}
J = os.path.join(D, "DERIVATIONS_2026-10-02e.json")
json.dump(doc, open(J, "w", encoding="utf-8"), indent=2, ensure_ascii=False); open(J, "a").write("\n")
L = ["# DERIVATIONS_2026-10-02e (frozen before any downstream number is computed)", "", "## Step 1: v / G_F bug fix", "", step1["bug_fix"], "",
     f"Relation: {step1['relation']}", "", "### Scheme decision (a priori)", "", step1["scheme_reasoning"], ""]
L += [f"- **{k}**: {v}" for k, v in step1["schemes"].items()] + [f"- scheme look-elsewhere: {step1['scheme_look_elsewhere']}", "", step1["downstream_unchanged"], "", step1["counting"], "", "## Step 2: missing pieces", ""]
for k, v in step2.items():
    L += [f"- **{k}**: " + (v if isinstance(v, str) else json.dumps(v, ensure_ascii=False))]
L += ["", f"Look-elsewhere: {doc['look_elsewhere']}", "", f"Order: {doc['order']}", ""]
open(os.path.join(D, "DERIVATIONS_2026-10-02e.md"), "w", encoding="utf-8").write("\n".join(L))
with open(os.path.join(D, "DERIVATIONS_2026-10-02e.sha256"), "w") as fh:
    for n in ("DERIVATIONS_2026-10-02e.json", "DERIVATIONS_2026-10-02e.md"):
        fh.write(hashlib.sha256(open(os.path.join(D, n), "rb").read()).hexdigest() + "  " + n + "\n")
