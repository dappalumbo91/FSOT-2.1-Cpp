# IRONOUT-1 #6: scoring-criteria changes (NOT physics changes)

Damian t995u, 2026-11-11. Nothing in this commit changes an FSOT value or formula, and no formula was retuned to a new
target. It records which reference each row is scored against, with citations, in
`reference/scoring_criteria_ironout1.tsv`. The scorecard (gf_trace_20261111/scorecard/ironout1) reads that file.

## 1. Stale or rounded targets
The engine's `measured` literals come from the authority closed forms and are left untouched (the parity column and
the archive cross-check need them). The scored target is the accepted value in the TSV:
- HCl dipole 1.08 → 1.1086(3) D
- FCC site percolation 0.1982 → 0.1992365(10)
- sin²θ_W 0.23122 → 0.23129(4)
- sinθ_C 0.22759 → λ 0.22501(68) (the origin of 0.22759 isn't known; FSOT carries 3 Cabibbo values, so this needs a decision from Damian)
- BR(H→gg) 0.0785 → 0.0818 (YR4)
- 3D Ising η 0.0363 → 0.0362978(20)
- 3D Ising δ 4.7898 → 4.78984(1)
- SAW γ_3D 1.1575 → 1.156953(1)
- KT T/J 0.8935 → 0.8929(1)
- Hénon λ 0.4192 → 0.41922(1)
- Age/T_CMB 5.043 → 5.0622
- water T_max-density 3.98 → 3.983035(67)
- boiling point of H₂O 373.15 → 373.124
- CO₂ sublimation point 194.65 → 194.686
- dipoles of H₂O and NH₃ rounded targets → measured
- pK_w 14 → 13.995

## 2. Mislabeled rows
wave3 `Ising2D_beta/nu/gamma` carry 3D-Ising targets. 2D Ising is exact: β = 1/8, ν = 1, γ = 7/4. They are relabeled 3D
in the formula column (IRONOUT-1 #2). The archive key is kept, and the target is not changed to fit.

## 3. Single-experiment → world average (the single-experiment gate stays as a secondary check)
- Γ_Z ALEPH/DELPHI/L3/OPAL → LEP 2495.5(2.3) MeV
- Δm²₂₁ solar → NuFIT 6.0 7.49(19)e-5 eV²
- m_K± Cheng → PDG 493.677(15)
- r_p Grinin → CODATA 2022 0.84075(64)
- m_H CMS 2020 → PDG 125.20(11)
- τ_n UCNτ → PDG 2024 878.4(5) s, with UCNτ and Pattie kept as gates

The pre-registered dial-in records (golden/folded_routes.tsv) are not edited.

## 4. The authority "sigma" field isn't an uncertainty
In the authority `Result.sigma`, the value printed as "σ=" is a claimed |z| against the authority's own reference σ:
- H0 2.1 = (68.44 − 67.4)/0.5
- α_s 0.9
- T_CMB 1.3
- τ_n 0.4

The single-engine table used it as an absolute σ: z = diff/sigma. For example, α_s z = −0.0009 against "σ" 0.9.
- The column is renamed `auth_sigma_tag`, and the table z is now left blank.
- `tools/worst_residuals.py` no longer z-scores table rows.

Scored z now comes only from fsot_precision (published σ) and the folded routes. A side effect: `wave8|m_t/m_b` (rel 0.38 %) drops out of WORST_RESIDUALS §A. It had z −1.58 only against the claimed-z tag. It has no published-σ pin, so it needs one.

## 5. SM benchmark for πH Γ1s
The scorecard's mainstream number for πH Γ1s was "816 ± 20 (estimate)". It is replaced by a computed value: the same Deser freeze the route uses (8α³μ_c²q₀(1+1/P)(1+δ_Γ)², δ_Γ = 0.006(5)) at a⁻ = 86.1(9)e-3 M_π⁻¹ (Baru et al. 2011) gives 816.1 ± 18.9 meV.
