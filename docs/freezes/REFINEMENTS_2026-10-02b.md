# REFINEMENTS_2026-10-02b (frozen-pending; written before any candidate was scored)

Authority pin AEB2AD (vendor/fsot_compute.py sha256 AEB2ADAD6E80F487772C5DF90A2E3DDA71624AB831A6A83B94AB471AC9AAC170); hub data 6f9c25605a52acabe662a42fc003afa5bf66b959.

Definitions: alpha = 1/(e^3 phi^4 - psi_con - (POOF*SUCTION)^2 C_factor^2/P_base) (hub alpha leaf, scripts/alpha_interface_seed_check.py; same alpha() as scripts/deuteron_binding_seed_check.py); yy = (POOF*SUCTION)^2.

## Data / channel fixes (bug fixes, decided by Damian before this session)

### F1 H0 (channel (reference) fix, not a refinement)

FSOT H0 = 100(1 + S_cosm*A_bleed/A_in) is the global CMB-background expansion rate (hub vendor/fsot_seed_flavor.py seed_h0_global, commit 00ca7f1f 2026-09-15: 'Global CMB-background H0 ... Not SH0ES. Not Planck-2018-only 67.4. Live CMB+BAO class is P-ACT-LB2 (Louis et al. arXiv:2503.14452 eq. 41) 68.43+-0.27'). Scored reference: H0 = 68.43 +- 0.27 km/s/Mpc (ACT DR6 P-ACT-LB with DESI DR2, arXiv:2503.14452 abstract). Planck 2018 67.4(5) and SH0ES 73.0(1.0) are printed as alternates and not scored. Formula and pin unchanged.

Held-out: P-ACT-LB with DESI DR1: 68.22 +- 0.36 (same paper); P-ACT without lensing/BAO: 67.62 +- 0.50 (same paper).

Disclosure: The pin value 68.445 was visible in the task-1 audit before this freeze; the channel was fixed by the 09-15 hub docstring, not by this z.

### F2 alpha_s(M_Z) (channel (route) fix, not a refinement)

PDG 2024 alpha_s(M_Z^2) = 0.1180(9) is the MS-bar coupling at mu = M_Z, five flavours (rpp2024-rev-qcd eq. 9.25 / summary). The FSOT quantity for that QCD-process coupling is seed_alpha_s_MZ = 2*(POOF/psi_con)^2 (hub vendor/fsot_seed_flavor.py, commit 8760d403 2026-08-03: 'QCD process orifice ... Wave-1 geometric 1/(e pi) is a different object (Ledger A freeze). Do not rewrite the freeze.'). The scored alpha_s row routes to that seed (evaluated in mp169 from the AEB2AD seeds); the wave1 pin 1/(e pi) row stays printed as an alternate (record 0). Reference: PDG 2024 0.1180(9) (the stale pin target 0.1179 is PDG 2022).

Held-out: PDG 2024 average without lattice: 0.1175 +- 0.0010 (rev-qcd eq. 9.24; subset of the average, correlated); FLAG 2021 lattice: 0.1184 +- 0.0008 (rev-qcd eq. 9.23; subset, correlated).

Disclosure: The seed value was not computed in this session before this freeze.

## Candidates (frozen-pending)

| id | item | statement | chosen | sha256(statement) |
|---|---|---|---|---|
| C-MHW-1 | m_H/m_W | m_H/m_W = leaf m_H_MeV / leaf m_W_MeV = [(theta_S+e^3)/C_factor^7] / [theta_S^-6 C_factor^-4 gamma^2 + e^e] (hub 6b3ce06c and 4afc9aad, 2026-09-29) | yes | `1fb2ea9cb3e0101f` |
| C-MHW-2 | m_H/m_W | m_H/m_W = 1/(3 P_new (1 - C_factor)) (quotient of seed_higgs_GeV and seed_m_W_GeV, hub vendor/fsot_seed_flavor.py, 2026-08) | no | `585ed18b019022cf` |
| C-DM-1 | Dm2_21/Dm2_32 | Dm2_21/Dm2_32 = (POOF*G*P_new)^3 / [(G*SUCTION)^3 (1+yy)] (seed_dm2()['dm2_21'] over leaf dm2_32, scripts/atmospheric_neutrino_seed_check.py; identical to seed_dm2()['dm2_31_abs'] numerically) | yes | `9c606910f538a4f3` |
| C-TCMB | T_CMB | T_CMB = (phi^2 + P_base*|S_cosm|) * (1 + yy) | yes | `b3374ceb77a1ebac` |
| C-GZ | Gamma_Z/M_Z | Gamma_Z/M_Z = (phi^5/e^6) * (1 + yy) | yes | `958ecb442811e534` |
| C-BD | Deuteron_binding | B_d = (sqrt(e)/e + phi) * (1 + yy*gamma*psi_con^2) | yes | `e73fdd799044e2db` |
| C-MUD | Deuteron_mu | mu_d/mu_N = (G^4 + POOF) * (1 + yy) | yes | `699eef7c42c31ac4` |

## A-priori selection rules

- **S1_route_items**: m_H/m_W and Dm2_21/Dm2_32: use the latest committed hub leaves for the numerator and denominator (Damian's leaf-quotient pattern: m_W/m_Z, m_pi/m_p, m_n-m_p). Where a committed leaf is missing (Dm2_21), use the committed seed function. Never chosen by z.
- **S2_family_items**: Single formula per item, fixed before scoring. Nuclear binding (deuteron): the dressing of the nearest-A committed binding leaf, triton B_H3 = bare*(1 + yy*gamma*psi_con^2) (hub 2026-09-29). Every other family item (T_CMB, Gamma_Z/M_Z, mu_d): Damian's documented cross-sector precision polish *(1 + (POOF*SUCTION)^2) (seed_higgs_GeV, seed_dm2 docstrings). Signs are taken from the precedent (+), never from the data.
- **family_for_look_elsewhere_only**: 104 forms per family item: bare*(1 +- d*x), d in ['alpha', 'alpha^2', 'alpha^3', 'yy'], x in Damian's named-seed list (scripts/deuteron_binding_seed_check.py named_seeds(), 13 entries). Scored only to measure the chance rate of z<=1; nothing is adopted from it. The S2 choices are members of this family.
- **not_used**: lowest z; Damian's uniqueness-in-window rule (z-based) is printed for information only.

## Candidate count

| item | N |
|---|---|
| alpha_s(M_Z) | 1 |
| H0 | 0 |
| m_H/m_W | 2 |
| Dm2_21/Dm2_32 | 1 |
| T_CMB | 104 |
| Gamma_Z/M_Z | 104 |
| Deuteron_binding | 104 |
| Deuteron_mu | 104 |
| **total** | **420** |

Family forms (each family item): bare*(1+alpha*1), bare*(1-alpha*1), bare*(1+alpha*e), bare*(1-alpha*e), bare*(1+alpha*phi), bare*(1-alpha*phi), bare*(1+alpha*sqrt(e)), bare*(1-alpha*sqrt(e)), bare*(1+alpha*sqrt(phi)), bare*(1-alpha*sqrt(phi)), bare*(1+alpha*gamma), bare*(1-alpha*gamma), bare*(1+alpha*G), bare*(1-alpha*G), bare*(1+alpha*psi_con), bare*(1-alpha*psi_con), bare*(1+alpha*1/phi), bare*(1-alpha*1/phi), bare*(1+alpha*pi^{-4}), bare*(1-alpha*pi^{-4}), bare*(1+alpha*e^{-4}), bare*(1-alpha*e^{-4}), bare*(1+alpha*pi+P_base), bare*(1-alpha*pi+P_base), bare*(1+alpha*gamma*psi_con^2), bare*(1-alpha*gamma*psi_con^2), bare*(1+alpha^2*1), bare*(1-alpha^2*1), bare*(1+alpha^2*e), bare*(1-alpha^2*e), bare*(1+alpha^2*phi), bare*(1-alpha^2*phi), bare*(1+alpha^2*sqrt(e)), bare*(1-alpha^2*sqrt(e)), bare*(1+alpha^2*sqrt(phi)), bare*(1-alpha^2*sqrt(phi)), bare*(1+alpha^2*gamma), bare*(1-alpha^2*gamma), bare*(1+alpha^2*G), bare*(1-alpha^2*G), bare*(1+alpha^2*psi_con), bare*(1-alpha^2*psi_con), bare*(1+alpha^2*1/phi), bare*(1-alpha^2*1/phi), bare*(1+alpha^2*pi^{-4}), bare*(1-alpha^2*pi^{-4}), bare*(1+alpha^2*e^{-4}), bare*(1-alpha^2*e^{-4}), bare*(1+alpha^2*pi+P_base), bare*(1-alpha^2*pi+P_base), bare*(1+alpha^2*gamma*psi_con^2), bare*(1-alpha^2*gamma*psi_con^2), bare*(1+alpha^3*1), bare*(1-alpha^3*1), bare*(1+alpha^3*e), bare*(1-alpha^3*e), bare*(1+alpha^3*phi), bare*(1-alpha^3*phi), bare*(1+alpha^3*sqrt(e)), bare*(1-alpha^3*sqrt(e)), bare*(1+alpha^3*sqrt(phi)), bare*(1-alpha^3*sqrt(phi)), bare*(1+alpha^3*gamma), bare*(1-alpha^3*gamma), bare*(1+alpha^3*G), bare*(1-alpha^3*G), bare*(1+alpha^3*psi_con), bare*(1-alpha^3*psi_con), bare*(1+alpha^3*1/phi), bare*(1-alpha^3*1/phi), bare*(1+alpha^3*pi^{-4}), bare*(1-alpha^3*pi^{-4}), bare*(1+alpha^3*e^{-4}), bare*(1-alpha^3*e^{-4}), bare*(1+alpha^3*pi+P_base), bare*(1-alpha^3*pi+P_base), bare*(1+alpha^3*gamma*psi_con^2), bare*(1-alpha^3*gamma*psi_con^2), bare*(1+yy*1), bare*(1-yy*1), bare*(1+yy*e), bare*(1-yy*e), bare*(1+yy*phi), bare*(1-yy*phi), bare*(1+yy*sqrt(e)), bare*(1-yy*sqrt(e)), bare*(1+yy*sqrt(phi)), bare*(1-yy*sqrt(phi)), bare*(1+yy*gamma), bare*(1-yy*gamma), bare*(1+yy*G), bare*(1-yy*G), bare*(1+yy*psi_con), bare*(1-yy*psi_con), bare*(1+yy*1/phi), bare*(1-yy*1/phi), bare*(1+yy*pi^{-4}), bare*(1-yy*pi^{-4}), bare*(1+yy*e^{-4}), bare*(1-yy*e^{-4}), bare*(1+yy*pi+P_base), bare*(1-yy*pi+P_base), bare*(1+yy*gamma*psi_con^2), bare*(1-yy*gamma*psi_con^2)

## Held-out checks

- m_H/m_W: sibling m_H/m_Z = leaf m_H / leaf m_Z vs PDG 2024 125.20(11)/91.1880(20); sibling m_H/m_t = leaf m_H / (leaf m_t/m_W * leaf m_W) vs PDG 2024 125.20(11)/172.57(29)
- Dm2_21/Dm2_32: sibling Dm2_21 seed alone vs PDG 2024 7.53(18)e-5 eV^2; convention check vs Dm2_21/Dm2_31 with Dm2_31 = Dm2_32 + Dm2_21 (normal ordering, PDG 2024 inputs)
- T_CMB: none independent (FIRAS is the only absolute measurement at this precision)
- Gamma_Z/M_Z: none independent
- Deuteron_binding: none independent (AME2020 per-nucleon and mass-excess routes are the same data)
- Deuteron_mu: none independent

## Disclosure

- Seen before this freeze (from task 1 and hub scripts): the bare z of every item; Damian's printed deuteron windows (alpha^2: pi^-4; alpha^3: sqrt(e), phi; his decision 'the bare sum stays') and his mu_d*(1+alpha^2) result; the H0 pin value. The deuteron-binding and mu_d choices are therefore not blind in the strict sense; S2 fixes them by precedent, not by those windows.
- Not computed before this freeze: seed_alpha_s_MZ, every candidate value above, every family value.

candidates_sha256 = ce972127e0f918ab6b069feda23c066d5e03e25e69ee0b4d7a4dc0e0a7d74634
