#!/usr/bin/env python3
"""Write docs/freezes/PROTOCOL_2026-10-02c.{md,json,sha256}: the train/test protocol, fixed before any training number is computed."""
import hashlib, json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "freezes")
NAMED = ["1", "e", "phi", "sqrt(e)", "sqrt(phi)", "gamma", "G", "psi_con", "1/phi", "pi^{-4}", "e^{-4}", "pi+P_base", "gamma*psi_con^2"]
DRESS = ["alpha", "alpha^2", "alpha^3", "yy"]
classes = {
  "W_widths": {"target": "Gamma_Z/M_Z = phi^5/e^6 (vs PDG 2024 Gamma_Z/M_Z)",
    "train": ["Neutron_lifetime_s pin pi^7*theta_S (PDG 878.4(5) s)", "R_b pin G/phi^3 (PDG 0.21629(66))", "R_c pin -ln2+e/pi (PDG 0.1721(30))",
              "BR_Z_ee pin gamma^6/ln3 (PDG 3.3632(42) %)", "BR_Z_had pin sin(gamma)+POOF (PDG 69.911(56) %)", "BR_Z_inv pin (1/3)/A_in (PDG 20.000(55) %)"],
    "held_out": "R_ell pin G^3/gamma^6 vs Gamma(had)/Gamma(ll) = 69.911(56)%/3.3658(23)% (PDG 2024; sigma propagated as uncorrelated)",
    "excluded": "BR_H_* rows (PDG gives signal strengths, not measured BRs); no FSOT row exists for Gamma_W, muon, pion or tau lifetimes"},
  "M_moments": {"target": "mu_d/mu_N = G^4 + POOF",
    "train": ["electron g: leaf g_e (bare 2(1+(e/pi-ln2)/e^5), dressing -2(alpha/pi)^3*A_bleed*G^2*P_base/P_new)",
              "proton g: leaf g_p (bare (A_in P_new/P_base)^2, dressing +alpha/psi_con^3*(1+yy^2)); mu_p/mu_N = g_p/2 is the same observable and is not counted twice"],
    "held_out": "none (only two distinct observables)", "excluded": "pin mu_p_muN pi(1-gamma^4) and (g-2)/2 pin: same observables as the leaves"},
  "B1_binding_leaves": {"target": "B_d = sqrt(e)/e + phi",
    "train": ["He-4 leaf: bare pi/gamma^4, dressing -alpha^2(pi+P_base)", "H-3 leaf: bare e^2+1/G, dressing +yy*gamma*psi_con^2"], "held_out": "none", "excluded": ""},
  "B2_binding_ledgerB": {"target": "Ledger B geochemistry #72 H-2 B/A (FSOT's other deuteron route) and, only if the accepted pattern is a dressing form, sqrt(e)/e+phi",
    "train": ["Ledger B geochemistry_benchmark.json #74..#86 B/A (He-4, Li-6, Li-7, Be-9, C-12, N-14, O-16, Fe-56, Ni-62, U-235, U-238, Pu-239, Pb-208) vs AME2020 B/A"],
    "held_out": "#73 He-3 B/A vs AME2020", "excluded": ""},
  "T_thermal": {"target": "T_CMB = phi^2 + P_base*|S_cosm|",
    "train": ["Omega_b_h2 pin |S_cosm|(1-S_chem) (PDG 0.02237(15))", "N_eff pin P_new*e*pi+ln(phi) (PDG 2.99(17))", "eta_b pin POOF^11/(pi*gamma) (PDG 6.04(12)e-10)"],
    "held_out": "Y_p pin theta_S*sin(1) (PDG 0.2448(33))", "excluded": "Omega_r and n_gamma (derived from T_CMB itself)"},
}
patterns = {
  "P1_sign": "sign of delta_i = (measured - bare)/bare; consistent iff the same in all training members",
  "P2_alpha_power": "k_i = nearest integer to ln|delta_i|/ln(alpha); consistent iff equal in all training members",
  "P3_common_dressing": f"D in [none] + bare*(1 + s*d*x), d in {DRESS}, x in Damian's 13 named seeds, s in (+,-): 105 options. Leave-one-out: on the n-1 other members take the first D in this fixed order (none; then d, x, s in list order, + before -) that gives z<=1 on all of them; predict the left-out member with it (none if no D qualifies).",
  "P4_structural_fit": "B2 only: delta = c*v, one parameter, unweighted least squares through the origin, v in {1, A, A^(-1/3), B/A}; leave-one-out prediction.",
}
crit = ("A class pattern is ACCEPTED only if (i) at least 3 training members, (ii) P1 sign agreement n/n, and (iii) leave-one-out z<=1 for at least 2/3 of "
        "the training members under a P3 or P4 predictor whose full-training selection is not 'none'. The accepted rule is the full-training selection "
        "(same order). It is frozen in REFINEMENTS_2026-10-02c before it is applied to any target or held-out member. Nothing is chosen by target z.")
count = {"W_widths": 107, "M_moments": 107, "B1_binding_leaves": 107, "B2_binding_ledgerB": 111, "T_thermal": 107}
doc = {"protocol": "PROTOCOL_2026-10-02c", "date": "2026-10-02", "authority_pin": "AEB2AD", "hub_data_commit": "6f9c25605a52acabe662a42fc003afa5bf66b959",
       "alpha": "alpha = 1/(e^3 phi^4 - psi_con - yy C_factor^2/P_base) (hub alpha leaf); yy = (POOF*SUCTION)^2", "z": "|value - central|/sigma with the published sigma",
       "classes": classes, "patterns": patterns, "acceptance": crit, "patterns_examined_per_class": count, "patterns_examined_total": sum(count.values()),
       "T_CMB_independent_checks": ["FSOT-internal: T0 implied by the FSOT eta_b and Omega_b_h2 pins via PDG 2024 BBN 'Omega_b ~ eta10 h^-2/274' (n_gamma ~ T^3)",
                                    "External: Noterdaeme et al. 2011 (arXiv:1012.3164) T_CMB(z) = (2.725 +- 0.002)(1+z)^(1-beta) K normalisation; discrimination power reported as |candidate - bare|/sigma"],
       "disclosure": "Known before this protocol: the target bare z values and the 02b results (T_CMB polish z 0.999; Gamma_Z family hits alpha*{gamma,psi_con,1/phi} with minus sign; deuteron windows). Not computed before this protocol: any training residual of this protocol."}
J = os.path.join(D, "PROTOCOL_2026-10-02c.json")
json.dump(doc, open(J, "w", encoding="utf-8"), indent=2, ensure_ascii=False); open(J, "a").write("\n")
L = ["# PROTOCOL_2026-10-02c: train/test search for the open items (fixed before any training number was computed)", "", f"alpha: {doc['alpha']}. z: {doc['z']}.", "", "## Classes", ""]
for k, c in classes.items():
    L += [f"### {k}", f"- target: {c['target']}"] + [f"- train: {t}" for t in c["train"]] + [f"- held-out: {c['held_out']}", f"- excluded: {c['excluded'] or '-'}", ""]
L += ["## Patterns examined", ""] + [f"- **{k}**: {v}" for k, v in patterns.items()] + ["", "## Acceptance criterion", "", crit, "",
      f"Patterns examined: {count} (total {sum(count.values())}).", "", "## T_CMB independent checks", ""] + [f"- {t}" for t in doc["T_CMB_independent_checks"]] + ["", "## Disclosure", "", doc["disclosure"], ""]
open(os.path.join(D, "PROTOCOL_2026-10-02c.md"), "w", encoding="utf-8").write("\n".join(L))
with open(os.path.join(D, "PROTOCOL_2026-10-02c.sha256"), "w") as fh:
    for n in ("PROTOCOL_2026-10-02c.json", "PROTOCOL_2026-10-02c.md"):
        fh.write(hashlib.sha256(open(os.path.join(D, n), "rb").read()).hexdigest() + "  " + n + "\n")
print("patterns examined", sum(count.values()))
