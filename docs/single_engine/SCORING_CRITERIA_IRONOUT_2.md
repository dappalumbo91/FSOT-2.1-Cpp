# Scoring criteria, iron-out pass 2 (Damian t999u, 2026-11-11 1:46 PM EST)

Ruling: "score everything against the best observed value, the world average where one exists. SM parity is only a
temporary floor; FSOT should aim to be more accurate than the SM." Machine-readable list:
`reference/scoring_criteria_ironout2.tsv`. Applied in the scorecard build (`build_ironout2.py`); nothing measured is
pasted into the engine.

| quantity | pass-1 primary | pass-2 primary (world average) | secondary gates |
|---|---|---|---|
| τ_n (every FSOT τ_n row) | UCNτ 2025 877.82 ± 0.287 s | **PDG 2024 878.4 ± 0.5 s** | UCNτ 877.82 ± 0.287; Pattie 2018 877.7 ± 0.76 |
| sin θ_C (wave3) | PDG global-fit λ 0.22501(68) | **PDG 2024 \|V_us\| 0.22431 ± 0.00085** (Eq. 12.8; λ = sin θ_C = \|V_us\|) | — |
| \|V_ud\| | global fit 0.97435(16) | **0.97367 ± 0.00032** (Eq. 12.7, superallowed) | — |
| \|V_us\| | 0.22501(68) | **0.22431 ± 0.00085** (12.8) | — |
| \|V_cd\| | 0.22487(68) | **0.221 ± 0.004** (12.9) | — |
| \|V_cs\| | 0.97349(16) | **0.975 ± 0.006** (12.10) | — |
| \|V_cb\| | 0.04183(79) | **(41.1 ± 1.2)e-3** (12.11) | — |
| \|V_ub\| | 0.003732(90) | **(3.82 ± 0.20)e-3** (12.12) | — |
| \|V_td\| | 0.00858(19) | **(8.6 ± 0.2)e-3** (12.13) | — |
| \|V_ts\| | 0.04111(77) | **(41.5 ± 0.9)e-3** (12.13) | — |
| \|V_tb\| | 0.999118(29) | **1.010 ± 0.027** (12.15) | — |
| J (Jarlskog) | global fit 3.12(13)e-5 | unchanged: no direct measurement exists, the fit is the best observed value (flagged) | — |

The PDG global fit (Eq. 12.27) imposes three-generation unitarity; it is a fit, not an observation, so it is no longer
a primary target. The 2026-10-02 precision audit (`audit/precision_2026-10-02.tsv`) is a frozen, dated record and is
not rewritten; its global-fit z column is superseded in the scorecard by the targets above.

Every other target already is a world average / CODATA / PDG summary value (pass 1 moved the folded single-experiment
routes onto their world averages). H0 has no agreed world value (tension) and keeps its flag.

Scaffolding (allowed temporarily, t999u): the 1s Bethe logarithm ln k0 = 2.984128555765 in IE_H and the He
ground-state eigenvalue used for the (not adopted) IE_He candidate are flagged **SCAFFOLD_PENDING_FSOT_DERIVATION**.
