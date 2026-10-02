# REFINEMENTS_2026-10-02c: train/test result (frozen before any target was scored)

No class met the pre-stated acceptance criterion. No rule is frozen, and no dressing is applied to Gamma_Z/M_Z, the deuteron binding or mu_d. The targets keep their bare pin values (open). Held-out members are scored bare, for information only.

Protocol: docs/freezes/PROTOCOL_2026-10-02c.json (commit 44adf76). Training output sha256 5a230be70bf1ec076450adfc804c625958ad6633c3b508ef9de250581d48957c. Patterns examined: 539. Accepted: none.

| class | n | sign | alpha power | P3 LOO | P3 full | P4 best | accepted | note |
|---|---|---|---|---|---|---|---|---|
| W_widths | 6 | 4/6 | 5/6 | 6/6 | none | - | no | Sign agreement 4/6 fails (i). All six bare pins already pass, so the leave-one-out selection is 'none' 6/6. No correction pattern exists to transfer. |
| M_moments | 2 | 1/2 | 1/2 | 0/2 | none | - | no | Only 2 distinct observables, so it fails (i). The g_e dressing is negative and alpha^3-order; the g_p dressing is positive, additive and alpha^1-order (signs 1/2, powers 4 vs 1). |
| B1_binding_leaves | 2 | 1/2 | 2/2 | 0/2 | none | - | no | Only 2 members, so it fails (i). He-4's dressing is -alpha^2(pi+P_base) and H-3's is +yy*gamma*psi_con^2 (sign 1/2). Each leaf's dressing applied to the other gives z 9414 (He-4) and 2853 (H-3): the nuclear dressings do not transfer. |
| B2_binding_ledgerB | 13 | 7/13 | 9/13 | 0/13 | none | 1 0/13 | no | Sign 7/13 fails (ii). Leave-one-out 0/13 for P3 and 0/13 for every P4 variable (1, A, A^-1/3, B/A): the residuals of the Ledger B B/A formula vary in sign at the 1e-3 level, against AME2020 sigma of order 1e-7 relative. |
| T_thermal | 3 | 3/3 | 3/3 | 3/3 | none | - | no | (i) and (ii) hold: 3/3 bare-high, all alpha^1-order (-0.41 %, -1.8 %, -1.6 %). But all three bare pins already pass, so the full-training selection is 'none' and there is no correction to freeze (fails (iii)). Note: the bare T_CMB is LOW, the opposite sign to the class. |
