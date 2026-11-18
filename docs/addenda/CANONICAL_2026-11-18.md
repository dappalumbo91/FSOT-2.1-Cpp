# Addendum 2026-11-18: canonical cosmology picks, retired target, FSOT sigma (report only)

Authority: Damian t1027s4342 (2026-11-18, "Go ahead with all of them"); SPEC t1027s4342 (Tracer sha8 bcefad59, ruling
90974dcb); kill band k put ON HOLD by Damian t1031u (2026-11-18 12:20 EST). This is an addendum. No freeze file,
pinned authority row (AEB2AD) or Ledger A freeze is edited.

## 1. Canonical values (addendum only)

| quantity | canonical | engine row | reference | z | frozen value kept unedited |
|---|---|---|---|---|---|
| w_a | -0.808109771581081 (-gamma e phi / pi) | validation_suite / Dark_energy_wa | Unite+BAO+CMB w_a -0.60 (+0.17/-0.19), arXiv:2609.05053 Table 8 | -1.10 | frozen -1.018 (z -2.20) |
| lithium underproduction factor | pi * C_EFF = 3.00885414782507 | route `lifac` (include/fsot/host/quantum_vcb_lithium.hpp) | BBN/obs 7Li/H = 4.72(70)/1.45(25) = 3.255(740), PDG 2026 rev-bbang-nucleosynthesis | -0.33 | 2.85 / 3.0 legacy values |

Both rows are reported in audit/precision_2026-10-02.tsv at record=0 (reported, not yet in the scored record set).

## 2. Retired target

`predictions|Dark_energy_wa` carries measured -0.830 in the pinned AEB2AD closed-form table (golden/single_engine_table.tsv:297).
-0.83 is a rounded DESI w0 misused as a w_a target. It is retired as a target: no report scores against it, the pinned
row stays byte-identical for pin parity, and w_a is scored against reference key `wa_cpl_unite` and jointly (below).

## 3. Joint (w0, w_a) — report only

apps/fsot_cpl_joint.cpp, refs reference/cpl_w0wa_joint_2026-11-18.tsv, output audit/cpl_w0wa_joint_2026-11-18.tsv.
All four DESI DR2 (arXiv:2503.14738 Table V) combinations with rho Scout-derived from official chains (Scout 43_5ww):
DESI+CMB chi2 42.5 (2 dof), +Pantheon+ 96.3, +Union3 83.7, +DESY5 120.7. None is picked. Unite prints no covariance:
its report is the 1D pulls (w0 z -4.02, w_a z -1.10); its chi2 147.8 uses the FoM-derived rho ~ -0.91 and is an
APPROXIMATE sensitivity line. The w0 sector drives the miss. It stays OPEN under t1026u.

## 4. FSOT sigma (report only)

audit/precision_2026-10-02.tsv carries sigma_mult, sigma_D, sigma_prec, sigma_fsot and signed z_combined
(include/fsot/host/sigma_fsot.hpp). k is a parameter (`fsot_precision --k-report K` prints a count only), with no
pass/fail verdict. The Ledger B |z| <= 2 gate stays PROVISIONAL (#111). No kill rule is wired into PRED-001; the
bridge rule is unchanged pending Damian.

## 5. V_ud

Route L sqrt(1 - lambda^2) = 0.974324 and Route C A_IN - ln 2 = 0.973707 are different formulas (634 ppm). They are
not unified here: unification is by derivation only (OPEN). Their split is carried as sigma_mult = 0.000437 on the
V_ud rows. Hosted tau_n stays on Route L.

Open misses left OPEN: CPL w0, S8 (closed form vs constructed sigma_8 sqrt(Omega_m/0.3) = 0.8314; sigma_mult 0.00043),
a_mu, V_ud unification, D-04 (D_eff derivation yields 5).
