# DERIVATIONS_2026-10-02d (frozen before any of these numbers is computed)

Leaf source: golden/seed_leaves_6f9c2560.tsv (hub seed leaves, 50 digits). z: |value - central|/sigma with the published sigma. Order: 1) this freeze; 2) score B rows and A; train C1; freeze REFINEMENTS_2026-10-02d; 3) score C1 targets, held-out and C2.

## Inputs

- **G_F**: Damian's seed G_F = 1/(sqrt2 v^2), v = (theta_S + e^3)/C_factor^6/1000*phi GeV (hub vendor/fsot_seed_flavor.py seed_G_F/seed_vev_GeV), evaluated with fsot_compute mp constants
- **M_Z**: leaf m_Z_MeV / 1000 (GeV)
- **M_W**: leaf m_W_MeV / 1000 (GeV)
- **s2**: leaf sin2_theta_W_MSbar (used as the effective mixing; scheme approximation disclosed)
- **alpha**: 1/leaf alpha_inv
- **alpha_s**: seed_alpha_s_MZ = 2(POOF/psi_con)^2 (02b channel fix)
- **m_e, m_mu**: leaves m_e_kg, m_mu_kg, converted to GeV with exact SI c and e
- **m_tau**: leaf m_tau_MeV / 1000
- **mu_p**: leaf mu_p_over_mu_N
- **R_ell, BR_Z_***: AEB2AD pins (pin_lineage)
- **unit constants**: hbar = 6.582119569e-16 eV s and hbar*c from exact SI h, c, e (unit conversions, not physics inputs)

## A. Gamma_Z structural route

- A1 (the only scored candidate): Gamma_Z = sum over f in {nu_e, nu_mu, nu_tau, e, mu, tau, u, c, d, s, b} of N_c(f) * G_F M_Z^3/(6 sqrt2 pi) * [(T3_f - 2 Q_f s2)^2 + T3_f^2] * (1 + 3 Q_f^2 alpha/(4 pi)) * (1 + alpha_s/pi if quark). Massless fermions, top excluded, N_c = 3 for quarks. Gamma_Z/M_Z = Gamma_Z(A1)/M_Z. This is the single scored candidate (tier frozen-pending).
- A2: Gamma_Z = 3 Gamma_ll(A1) + Gamma_inv(A1) + R_ell(pin) Gamma_ll(A1)
- A3: Gamma_Z = Gamma_ee(A1) / BR_Z_ee(pin)
- A4: Gamma_Z = Gamma_inv(A1) / BR_Z_inv(pin)
- look-elsewhere: 4
- held-out Gamma_inv: 3 Gamma_nunu(A1) vs PDG 2024 499.2(1.5) MeV
- held-out Gamma_ll: Gamma_ee(A1) vs PDG 2024 83.984(86) MeV
- held-out sigma_had0: 12 pi Gamma_ee Gamma_had /(M_Z^2 Gamma_Z^2) (hbar c)^2 with A1 widths vs PDG 2024 41.481(33) nb
- held-out R_ell: Gamma_had(A1)/Gamma_ee(A1) vs PDG Gamma_had/Gamma_ll derived row

## B. New rows (all frozen-pending)

- **Gamma_W**: Gamma_W = G_F M_W^3/(6 sqrt2 pi) * (3 + 2 N_c (1 + alpha_s/pi)) (CKM row unitarity, two open quark doublets, massless) | alternatives (not scored): no QCD factor; explicit FSOT CKM leaves sum_{i=u,c; j=d,s,b} |V_ij|^2 instead of 2 | count 3
- **tau_mu**: tau_mu = hbar / Gamma_mu, Gamma_mu = G_F^2 m_mu^5/(192 pi^3) F(m_e^2/m_mu^2) (1 + alpha/(2 pi)(25/4 - pi^2)), F(x) = 1 - 8x + 8x^3 - x^4 - 12 x^2 ln x | alternatives (not scored): no QED factor; no phase-space factor | count 3
- **tau_tau**: tau_tau = tau_mu(primary) * (m_mu/m_tau)^5 * BR(tau -> e nu nu) | external: BR(tau -> e nu nu) = 17.82(4) % (PDG 2024), marked external; FSOT has no alpha_s(m_tau) | alternatives (not scored): FSOT-only BR = 1/(2 + N_c(1 + alpha_s(M_Z)/pi)) (wrong scale) | count 2
- **tau_pi**: NOT CONSTRUCTED: Gamma(pi -> mu nu) needs f_pi, which FSOT does not predict (no hub row). Using an external f_pi (itself fixed by this decay in PDG) would test the data against itself. | count 0
- **mu_n**: mu_n = -(2/3) mu_p (SU(6) quark-model ratio) with FSOT mu_p leaf | alternatives (not scored): mu_n = mu_d(sec. 67 #1036) - mu_p: rejected a priori because it uses the deuteron, a part-C target | count 2
- **mu_t**: mu_t = mu_p (S-state, unpaired-proton Schmidt value) with FSOT mu_p leaf | alternatives (not scored): isoscalar sum rule mu_t = mu_p + mu_n - mu_h with FSOT rows | count 2
- **mu_h**: mu_h = P_VAR^-7 - C_FACTOR^-1 (Damian's existing derivation, FSOT Mathematical Database sec. 67 #1037), recomputed with fsot_compute; the stored database Value is authoritative if the recomputation differs by more than 1e-12 relative | alternatives (not scored): Schmidt mu_h = mu_n row | count 2
- **G_F_diagnostic**: seed G_F vs CODATA 2022 Fermi coupling 1.1663787(6)e-5 GeV^-2 (diagnostic row; G_F feeds Gamma_W, tau_mu, tau_tau and A1) | count 1

## C1. Class search (protocol first)

Round-c criterion unchanged: a class pattern is ACCEPTED only if (i) n >= 3 training members, (ii) P1 sign agreement n/n, and (iii) leave-one-out z <= 1 for at least 2/3 of the training members under a P3 or P4 predictor whose full-training selection is not 'none'. The rule is frozen in REFINEMENTS_2026-10-02d before any target or held-out member is scored.

- P1: sign agreement of delta = (measured - bare)/bare
- P2: alpha-power agreement, k = round(ln|delta|/ln alpha)
- P3: the same 105 dressing options and fixed order as round c (none; then {alpha, alpha^2, alpha^3, yy} x 13 named seeds x {+,-}), LOO
- P4: M2 only, nuclear members (all except g_e): delta = c*v, unweighted least squares through the origin, v in {1, A, A^(-1/3), J}, LOO
- class **W2_widths**: {"train": ["tau_n pin", "R_b pin", "R_c pin", "BR_Z_ee pin", "BR_Z_had pin", "BR_Z_inv pin", "Gamma_W (B)", "tau_mu (B)", "tau_tau (B)"], "held_out": "R_ell pin vs derived Gamma_had/Gamma_ll", "target": "Gamma_Z/M_Z pin phi^5/e^6 (and A1 if a rule is accepted)", "patterns": 107}
- class **M2_moments**: {"train": ["g_e leaf (bare)", "g_p leaf (bare)", "mu_n (B)", "mu_t (B)", "mu_h (B)", "sec.67 Li-7 K^4/P_BASE^3", "sec.67 B-11 S_quant^-7+S_quant^-6", "sec.67 C-13 PHI-G", "sec.67 N-14 OMEGA^-7+B_IN^6", "sec.67 F-19 PHI^2", "sec.67 Na-23 PI-G", "sec.67 Al-27 PI^2/E", "sec.67 P-31 S_quant^-2-CHAOS^3"], "measured_nuclear": "IAEA LiveChart ground-state magnetic dipoles (reference/evidence/iaea_livechart_ground_states.csv)", "held_out": "sec.67 Mn-55 G^-3+OMEGA^3 (last sec.67 entry by index; chosen by position, not by value)", "target": "mu_d pin G^4+POOF; also Damian's sec.67 #1036 C_EFF^-6/A_BLEED^9 and the C2 two-nucleon value", "patterns": 111}
- class **binding**: {"note": "no new binding member was requested or exists; round-c B1/B2 results (0 accepted) stand and are not re-run", "patterns": 0}
- sec. 67 source: hub vendor/fsot_aggregate/FSOT_Mathematical_Database_Unified.json (sec. 67 Nuclear muN, #1035-#1046); formulas recomputed with fsot_compute (C_FAC = C_FACTOR, S_quant = S_QUANT); stored Value authoritative on mismatch > 1e-12 relative
- patterns examined: 218

## C2. Two-nucleon deuteron

- mu_d_two_nucleon_primary: mu_d = mu_S - (3/2)(mu_S - 1/2) P_D with mu_S = mu_p(leaf) + mu_n(B row)
- P_D: EXTERNAL INPUT: P_D = 5.76 % (Argonne v18, Wiringa-Stoks-Schiavilla, PRC 51, 38 (1995), arXiv:nucl-th/9408016 Table 10). FSOT has no D-state probability.
- alternatives_not_scored: ['P_D = 0 (pure S state)']
- count: 2
- diagnostic_not_candidate: the same formula with CODATA mu_n, to separate the mu_n row error from the two-nucleon formula error
- B_d_two_nucleon: NOT CONSTRUCTED: needs the deuteron mass or NN scattering parameters (a_t, r_t), none of which FSOT predicts. Using measured a_t, r_t would reproduce B_d by construction.
- measured: CODATA 2022 mu_d 0.8574382335(22)

## Look-elsewhere: {'A': 4, 'B': 15, 'C1': 218, 'C2': 2}

## Disclosure

Known before this freeze, from textbooks or the cited sources, not from computing these rows: tree-level Z/W widths with measured inputs miss the electroweak rho correction at about 0.5 %; the SU(6) ratio -2/3 differs from mu_n/mu_p by a few %; the Schmidt values miss mu_t and mu_h by several %; AV18 gives mu_d 0.847 (impulse) and 0.871 (with corrections); Damian's sec. 67 entries carry their own stored 'Error' strings. Not computed before this freeze: any of these rows with FSOT inputs, and any training residual of C1.
