# DERIVATIONS_2026-10-02f (frozen before any FSOT-input Delta r / G_F number is computed)

## Inputs

- **leaves**: golden/seed_leaves_6f9c2560.tsv: m_W_MeV, m_Z_MeV, alpha_inv, m_e_kg, m_mu_kg, m_tau_MeV, m_t_over_m_W, m_c_over_m_b, m_H_MeV, m_p_kg
- **pin**: AEB2AD wave8|m_t/m_b
- **masses**: m_t = (m_t/m_W leaf) m_W; m_b = m_t/(wave8|m_t/m_b); m_c = (m_c/m_b leaf) m_b; m_H = leaf; M_W, M_Z = leaves
- **light_quarks**: FSOT has no absolute u, d, s mass (only m_u/m_d and m_s/m_d ratios). Pre-declared principled choice: constituent m_u = m_d = m_s = m_p/3 from the FSOT m_p leaf (a constituent mass is the scale at which a perturbative quark loop mimics the hadronic vacuum polarisation).
- **alpha_s**: seed alpha_s(M_Z) = 2(POOF/psi_con)^2 everywhere alpha_s appears (hadronic (1+alpha_s/pi) factor and the Delta rho QCD factor)
- **s2_on_shell**: s^2 = 1 - (M_W/M_Z)^2 from the leaves, c^2 = 1 - s^2; alpha = alpha(0) = 1/alpha_inv leaf

## Delta r pieces

- **decomposition**: Delta r = Delta alpha - (c^2/s^2) Delta rho + Delta r_rem   (Hioki hep-ph/9511224 eqs. 2.1-2.4; PDG 2024 EW review eq. 10.23)
- **Delta_alpha_lep**: (alpha/3pi) sum_l [ln(M_Z^2/m_l^2) - 5/3]  +  (alpha/pi)^2 sum_l [ (1/4) ln(M_Z^2/m_l^2) + zeta3 - 5/24 ], l = e, mu, tau leaves. Omitted and disclosed: the 3-loop term (~1.5e-6) and mass-suppressed terms.
- **Delta_alpha_top**: -(alpha/pi)(4/45)(M_Z^2/m_t^2) from the m_t leaf
- **Delta_alpha_had_H1_PRIMARY**: FSOT-only perturbative quark loop: (alpha/3pi) sum_{q=u,d,s,c,b} N_c Q_q^2 [ln(M_Z^2/m_q^2) - 5/3] (1 + alpha_s/pi), masses as in inputs. LIMITATION: the u, d, s region is non-perturbative; a quark-loop estimate is not a dispersive evaluation.
- **Delta_alpha_had_H2_secondary**: EXTERNAL PDG 2024 Delta alpha_had^(5)(M_Z) = 0.02783(6) (EW review line 231). Never confirmed.
- **Delta_rho**: Delta rho = 3 G_F m_t^2/(8 sqrt2 pi^2) [1 - (2/3)(1 + pi^2/3) alpha_s/pi]; the m_b^2 contribution to Delta rho is neglected. The two-loop electroweak rho^(2)(m_H/m_t) function was not reliably recalled and no source was retrieved: OMITTED and disclosed (it is O(1e-4) in Delta r). The QCD factor uses alpha_s(M_Z) (seed), not alpha_s(m_t): disclosed.
- **Delta_r_rem**: (i) non-leading top log, Hioki eq. 2.3 minus its m_t^2 term (which is the -(c^2/s^2) Delta rho above): -(alpha/(16 pi s^2)) * 4 (c^2/s^2 - 1/3 - 3 m_b^2/(s^2 M_Z^2)) ln(m_t/M_Z); (ii) Higgs, Hioki eq. 2.4: (11 alpha/(24 pi s^2)) ln(m_H/M_Z); (iii) bosonic constant of the classic one-loop result (as written in arXiv:1001.1759 eq. 12): (alpha/(4 pi s^2)) [6 + (7 - 4 s^2)/(2 s^2) ln c^2]. Disclosed: (iii) comes from a different paper than (i)-(ii); Hioki leaves Delta r[alpha] unspecified, so pairing (iii) with (i)-(ii) is an approximation whose consistency at O(alpha) non-leading level is not verified here.
- **solve**: G_F = pi alpha / (sqrt2 M_W^2 s^2 (1 - Delta r)); Delta rho depends on G_F, so iterate from G_F(tree) until |dG_F/G_F| < 1e-30. alpha(M_Z) = alpha/(1 - Delta alpha), Delta alpha = Delta alpha_lep + Delta alpha_had (+ Delta alpha_top reported separately as part of Delta r's Delta alpha). Linear 1/(1-Delta r) form (no resummation variant scored).

## Disclosure

Before this freeze, while designing H1, a back-of-envelope evaluation with textbook masses gave Delta alpha_had ~ 0.024 (~13 % below the dispersive 0.02783); the H1 choice (constituent m_p/3) was NOT altered after that. While reading Hioki eq. 2.3 the sign of the top-log term was checked against the rendered page image (the text extraction was garbled); a rough textbook-number size estimate of Delta r_rem was also made (about +0.003 with the source sign); the source sign is used as printed, not chosen by value. The PDG anchors Delta r = 0.03685 and Delta alpha_had = 0.02783 were known before freezing.

## Downstream

Round-d/e constructions rerun UNCHANGED (tools/fsot02d.compute with GF_override) with G_F(H1) and G_F(H2): G_F, Gamma_Z (A1), Gamma_Z/M_Z, Gamma_inv, Gamma_ll, sigma_had0, R_ell, Gamma_W, tau_mu, tau_tau (external BR, round d) and tau_tau with the round-e FSOT BR(tau->e). Gamma_Z/M_Z counts as confirmed ONLY if it passes z <= 1 under H1. H2 is reported alongside and never confirmed.

## Comparisons

- **Delta_r**: PDG 2024 EW review line 478: 0.03685, sigma 0.00021 (0.00020 m_t and 0.00006 alpha(M_Z) in quadrature); an SM evaluation, used as a consistency anchor
- **Delta_alpha_had**: PDG 0.02783(6) (H1 only)
- **G_F**: CODATA 2022 (reference G_F_GeVm2)

## Alternatives (look-elsewhere)

- **light-quark mass choice**: m_p/3 constituent (scored); current masses from ratios: impossible (no absolute FSOT light mass); m_pi-based cutoff (not scored)
- **Delta rho alpha_s scale**: alpha_s(M_Z) (scored); alpha_s(m_t) (not scored)
- **Delta r_rem constant (iii)**: included (scored); omitted (not scored)
- **resummation**: linear 1/(1-Delta r) (scored); (1-Delta alpha)(1+c^2/s^2 Delta rho) (not scored)
- **hadronic**: H1 primary; H2 secondary

Look-elsewhere counts: {'hadronic': 2, 'light-quark choice': 3, 'Delta rho alpha_s scale': 2, 'Delta r_rem constant': 2, 'resummation': 2, 'lost-route patterns': 7}

## Lost-route search (read-only on all other repos)

- **scope**: Mirror clones of all 40 dappalumbo91 repositories (public, private, archived; Fsuft-u-works empty); every unique text blob < 3 MB reachable from any ref, full history including deleted files; patterns for mu_n, triton/He-3 moments, f_pi, P_D, deuteron binding, Delta r, alpha(M_Z). 678 raw hits, all inspected. Plus all historical versions of the sec. 66/67 entries of FSOT_Mathematical_Database_Unified.json in the hub history.
- **rule**: only routes committed before 2026-10-02 count; a found route is ported unchanged and scored; FSOT-2.1-Cpp hits (this repo) are excluded
- **mu_n**: none found
- **mu_t (triton)**: none found
- **f_pi**: none found (so no tau_pi+)
- **P_D**: none found (AV18 5.76 % stays external)
- **Delta_r / alpha(M_Z)**: none found
- **He-3**: current hub sec. 67 #1037 P_VAR^-7 - 1/C_FACTOR (fsot_aggregate DB, already scored); an older parallel version -(E-GAMMA) = -2.14107 sits in the hub's vendor/cosmology/database copy (commit 5d0d5f31, 2026-07-10 00:52 EDT): ported unchanged and scored as historical
- **H-2 moment**: current #1036 C_EFF^-6/A_BLEED^9 (already scored); older parallel version E/PI = 0.865256 in vendor/cosmology/database (5d0d5f31, 2026-07-10): scored as historical
- **deuteron binding**: sqrt(e)/e + phi (wave3) copied into fsot_compute.py in many repos (FSOT-2.0-code fsot/compute.py etc.) and Ledger B #72 - both already scored; hub scripts/deuteron_binding_seed_check.py (last touched efe18686, 2026-10-01) keeps the bare sum - no new route
- **dependent_builds**: tau_pi+ and two-nucleon mu_d need f_pi and mu_n: NOT POSSIBLE

Order: 1) this freeze; 2) tools/score_2026_10_02f.py computes and scores; one push at the end
