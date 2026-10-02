# Look-elsewhere count

`fsot_look_elsewhere [--tsv audit/look_elsewhere.tsv]` asks, for each target: how many alternative closed
forms built from the same five seeds (π, e, φ, γ, Catalan G) land at least as close to the target as the
FSOT expression does?

## Grammars

| Grammar | Form | Size |
|---|---|---|
| **M** (monomials) | (p/q)·s₁^a·s₂^b·s₃^c: up to 3 distinct seeds; a, b, c ∈ {−6…6}\{0} ∪ {±½, ±⅓}; p, q ≤ 12 coprime | 3,967,691 distinct values |
| **S** (two-term) | u ± v, where u and v are unit monomials of up to 2 seeds, same exponents | about 10.5 M |

- **Tolerance:** the FSOT expression's own relative error, tol = |c − t|/|t|.
- **Expected count:** the local density of M values in |t|/1.05…|t|·1.05, scaled to the window ±tol.
- **Ledger A kill bands:** for these rows the tool also counts the M and S values that fall inside the published band.
- **Lower bound:** FSOT expressions like (a − b)/(c + d), or forms with derived constants (S_cosm, K, C_EFF, …), come from a much larger space. These counts are therefore a **lower bound** on the trials factor.
- **Exclusions:** the 21 non-prediction rows (computed = target, or a measured input) are left out.

## Result (pin AEB2AD; full table in `audit/look_elsewhere.tsv`)

**Closed forms plus Ledger A (343 targets):**
- For **325** targets, at least one M-grammar value is at least as close as the FSOT expression.
- The median number of such values is 66.
- 18 targets have none (16 closed-form, 2 Ledger A).

**Ledger A:**

| Row | FSOT rel. error | M values as close | M expected | S values as close | M / S inside kill band |
|---|---|---|---|---|---|
| T_CMB | 2.8e−4 | 196 | 195 | 486 | 375 / 959 |
| H0_PLANCK_CLASS | 1.6e−2 | 6,812 | 6,790 | 12,576 | 9,731 / 19,570 |
| First_Riemann_zero | 1.7e−5 | 11 | 9.6 | 80 | 238 / 1,211 |
| Dark_energy_wa | 1.2e−5 | 10 | 8.8 | 21 | 202,325 / 512,694 |
| inv_alpha_em | 1.4e−6 | 0 | 0.55 | 2 | 423 / 816 |
| m_mu_over_m_e | 1.4e−6 | 0 | 0.48 | 1 | 1,310 / 952 |
| m_tau_over_m_e | 9.5e−6 | 1 | 1.4 | 0 | 774 / 140 |

The other Ledger A rows are in the TSV.

## Reading the counts

- **"M values as close" ≈ "M expected"** (e.g. T_CMB 196 vs 195, First_Riemann_zero 11 vs 9.6). The FSOT match is about as close as a random member of the monomial grammar at that location.
- **"M values as close" = 0 with "M expected" < 1** (inv_alpha_em, m_mu_over_m_e). The match is tighter than the M grammar typically achieves. It still has to be weighed against the size of the grammar the FSOT expression itself comes from: m_mu/m_e, for example, uses the integer coefficients 35 and 145, which M doesn't contain.
- **Kill bands:** several hold 10³–10⁵ grammar values (Dark_energy_wa: 202,325). Surviving such a band discriminates little between candidate formulas.
