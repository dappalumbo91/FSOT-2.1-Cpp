#!/usr/bin/env python3
"""Write docs/freezes/REFINEMENTS_2026-10-02d.{md,json,sha256} from audit/train_2026-10-02d.tsv (C1 training verdicts), before any C1 target is scored."""
import hashlib, json, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."); D = os.path.join(R, "docs", "freezes")
def sha(p): return hashlib.sha256(open(os.path.join(R, p), "rb").read()).hexdigest()
verdict = {}
for line in open(os.path.join(R, "audit/train_2026-10-02d.tsv"), encoding="utf-8"):
    if line.startswith("verdict\t"):
        _, k, v = line.rstrip("\n").split("\t", 2); verdict[k] = json.loads(v)
acc = [k for k, v in verdict.items() if v["accepted"]]
doc = {"freeze": "REFINEMENTS_2026-10-02d", "date": "2026-10-02", "derivations_freeze": "DERIVATIONS_2026-10-02d (commit 73f89a5, 08:53:29 EDT)",
       "derivations_sha256": {n.split()[1]: n.split()[0] for n in open(os.path.join(D, "DERIVATIONS_2026-10-02d.sha256")).read().splitlines()},
       "c1_verdicts": verdict, "accepted_rules": acc, "patterns_examined_c1": 218,
       "training_output_sha256": sha("audit/train_2026-10-02d.tsv"), "rows_output_sha256": sha("audit/rows_2026-10-02d.tsv"),
       "note": "No C1 target (mu_d pin, sec.67 #1036, two-nucleon mu_d, Gamma_Z/M_Z pin) and no C1 held-out member (Mn-55, R_ell) has been evaluated at this point. Part A and part B rows were scored under DERIVATIONS_2026-10-02d (audit/rows_2026-10-02d.tsv)."}
J = os.path.join(D, "REFINEMENTS_2026-10-02d.json")
json.dump(doc, open(J, "w", encoding="utf-8"), indent=2, ensure_ascii=False); open(J, "a").write("\n")
L = ["# REFINEMENTS_2026-10-02d (C1 training frozen before any C1 target is scored)", "", f"Derivations: {doc['derivations_freeze']}.", "", "| class | n | sign | alpha-power | P3 LOO | P3 full | P4 best | accepted |", "|---|---|---|---|---|---|---|---|"]
for k, v in verdict.items():
    L.append(f"| {k} | {v['n']} | {v['sign_agree']} | {v['alpha_power_agree']} | {v['p3_loo_pass']} | {v['p3_full_selection']} | {v['p4_best']} | {v['accepted']} |")
L += ["", f"Accepted rules: {acc or 'none'}. Patterns examined (C1): 218.", "", doc["note"], "", f"training output sha256 {doc['training_output_sha256']}; rows output sha256 {doc['rows_output_sha256']}", ""]
open(os.path.join(D, "REFINEMENTS_2026-10-02d.md"), "w", encoding="utf-8").write("\n".join(L))
with open(os.path.join(D, "REFINEMENTS_2026-10-02d.sha256"), "w") as fh:
    for n in ("REFINEMENTS_2026-10-02d.json", "REFINEMENTS_2026-10-02d.md"):
        fh.write(hashlib.sha256(open(os.path.join(D, n), "rb").read()).hexdigest() + "  " + n + "\n")
print("accepted:", acc)
