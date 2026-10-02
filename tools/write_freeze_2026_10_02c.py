#!/usr/bin/env python3
"""Write docs/freezes/REFINEMENTS_2026-10-02c.{md,json,sha256} from the training output (no target evaluated)."""
import hashlib, json, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
D = os.path.join(R, "docs", "freezes"); T = os.path.join(R, "audit", "train_2026-10-02c.tsv")
verdict = {}
for l in open(T, encoding="utf-8"):
    if l.startswith("verdict\t"):
        _, k, v = l.rstrip("\n").split("\t", 2); verdict[k] = json.loads(v)
accepted = [k for k, v in verdict.items() if v["accepted"]]
notes = {
  "W_widths": "Sign agreement 4/6 fails (i). All six bare pins already pass, so the leave-one-out selection is 'none' 6/6. No correction pattern exists to transfer.",
  "M_moments": "Only 2 distinct observables, so it fails (i). The g_e dressing is negative and alpha^3-order; the g_p dressing is positive, additive and alpha^1-order (signs 1/2, powers 4 vs 1).",
  "B1_binding_leaves": "Only 2 members, so it fails (i). He-4's dressing is -alpha^2(pi+P_base) and H-3's is +yy*gamma*psi_con^2 (sign 1/2). Each leaf's dressing applied to the other gives z 9414 (He-4) and 2853 (H-3): the nuclear dressings do not transfer.",
  "B2_binding_ledgerB": "Sign 7/13 fails (ii). Leave-one-out 0/13 for P3 and 0/13 for every P4 variable (1, A, A^-1/3, B/A): the residuals of the Ledger B B/A formula vary in sign at the 1e-3 level, against AME2020 sigma of order 1e-7 relative.",
  "T_thermal": "(i) and (ii) hold: 3/3 bare-high, all alpha^1-order (-0.41 %, -1.8 %, -1.6 %). But all three bare pins already pass, so the full-training selection is 'none' and there is no correction to freeze (fails (iii)). Note: the bare T_CMB is LOW, the opposite sign to the class.",
}
doc = {"freeze": "REFINEMENTS_2026-10-02c", "date": "2026-10-02", "tier": "frozen-pending", "protocol": "docs/freezes/PROTOCOL_2026-10-02c.json (commit 44adf76)",
       "training_output": "audit/train_2026-10-02c.tsv", "training_output_sha256": hashlib.sha256(open(T, "rb").read()).hexdigest(),
       "verdicts": verdict, "notes": notes, "accepted_rules": accepted, "patterns_examined_total": 539,
       "statement": "No class met the pre-stated acceptance criterion. No rule is frozen, and no dressing is applied to Gamma_Z/M_Z, the deuteron binding or mu_d. The targets keep their bare pin values (open). Held-out members are scored bare, for information only.",
       }
J = os.path.join(D, "REFINEMENTS_2026-10-02c.json")
json.dump(doc, open(J, "w", encoding="utf-8"), indent=2, ensure_ascii=False); open(J, "a").write("\n")
L = ["# REFINEMENTS_2026-10-02c: train/test result (frozen before any target was scored)", "", doc["statement"], "",
     f"Protocol: {doc['protocol']}. Training output sha256 {doc['training_output_sha256']}. Patterns examined: 539. Accepted: {accepted or 'none'}.", "",
     "| class | n | sign | alpha power | P3 LOO | P3 full | P4 best | accepted | note |", "|---|---|---|---|---|---|---|---|---|"]
for k, v in verdict.items():
    L.append(f"| {k} | {v['n']} | {v['sign_agree']} | {v['alpha_power_agree']} | {v['p3_loo_pass']} | {v['p3_full_selection']} | {v['p4_best']} | {'yes' if v['accepted'] else 'no'} | {notes[k]} |")
open(os.path.join(D, "REFINEMENTS_2026-10-02c.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
with open(os.path.join(D, "REFINEMENTS_2026-10-02c.sha256"), "w") as fh:
    for n in ("REFINEMENTS_2026-10-02c.json", "REFINEMENTS_2026-10-02c.md"):
        fh.write(hashlib.sha256(open(os.path.join(D, n), "rb").read()).hexdigest() + "  " + n + "\n")
print("accepted:", accepted)
