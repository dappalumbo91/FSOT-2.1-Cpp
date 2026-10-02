#!/usr/bin/env python3
"""Write docs/freezes/REFINEMENTS_2026-10-02b.{json,md,sha256}. No candidate is evaluated here."""
import hashlib, json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "freezes")
NAMED = ["1", "e", "phi", "sqrt(e)", "sqrt(phi)", "gamma", "G", "psi_con", "1/phi", "pi^{-4}", "e^{-4}", "pi+P_base", "gamma*psi_con^2"]
DRESS = ["alpha", "alpha^2", "alpha^3", "yy"]
FAMILY = [f"bare*(1{s}{d}*{x})" for d in DRESS for x in NAMED for s in "+-"]
alpha_def = "alpha = 1/(e^3 phi^4 - psi_con - (POOF*SUCTION)^2 C_factor^2/P_base) (hub alpha leaf, scripts/alpha_interface_seed_check.py; same alpha() as scripts/deuteron_binding_seed_check.py); yy = (POOF*SUCTION)^2"

fixes = [
  {"id": "F1", "item": "H0", "class": "channel (reference) fix, not a refinement",
   "statement": "FSOT H0 = 100(1 + S_cosm*A_bleed/A_in) is the global CMB-background expansion rate (hub vendor/fsot_seed_flavor.py seed_h0_global, commit 00ca7f1f 2026-09-15: 'Global CMB-background H0 ... Not SH0ES. Not Planck-2018-only 67.4. Live CMB+BAO class is P-ACT-LB2 (Louis et al. arXiv:2503.14452 eq. 41) 68.43+-0.27'). Scored reference: H0 = 68.43 +- 0.27 km/s/Mpc (ACT DR6 P-ACT-LB with DESI DR2, arXiv:2503.14452 abstract). Planck 2018 67.4(5) and SH0ES 73.0(1.0) are printed as alternates and not scored. Formula and pin unchanged.",
   "decided_by": "Damian, hub commit 00ca7f1f (2026-09-15), before this session",
   "held_out": ["P-ACT-LB with DESI DR1: 68.22 +- 0.36 (same paper)", "P-ACT without lensing/BAO: 67.62 +- 0.50 (same paper)"],
   "disclosure": "The pin value 68.445 was visible in the task-1 audit before this freeze; the channel was fixed by the 09-15 hub docstring, not by this z."},
  {"id": "F2", "item": "alpha_s(M_Z)", "class": "channel (route) fix, not a refinement",
   "statement": "PDG 2024 alpha_s(M_Z^2) = 0.1180(9) is the MS-bar coupling at mu = M_Z, five flavours (rpp2024-rev-qcd eq. 9.25 / summary). The FSOT quantity for that QCD-process coupling is seed_alpha_s_MZ = 2*(POOF/psi_con)^2 (hub vendor/fsot_seed_flavor.py, commit 8760d403 2026-08-03: 'QCD process orifice ... Wave-1 geometric 1/(e pi) is a different object (Ledger A freeze). Do not rewrite the freeze.'). The scored alpha_s row routes to that seed (evaluated in mp169 from the AEB2AD seeds); the wave1 pin 1/(e pi) row stays printed as an alternate (record 0). Reference: PDG 2024 0.1180(9) (the stale pin target 0.1179 is PDG 2022).",
   "decided_by": "Damian, hub commit 8760d403 (2026-08-03), before this session",
   "held_out": ["PDG 2024 average without lattice: 0.1175 +- 0.0010 (rev-qcd eq. 9.24; subset of the average, correlated)", "FLAG 2021 lattice: 0.1184 +- 0.0008 (rev-qcd eq. 9.23; subset, correlated)"],
   "disclosure": "The seed value was not computed in this session before this freeze."},
]

cands = [
  {"id": "C-MHW-1", "item": "m_H/m_W", "statement": "m_H/m_W = leaf m_H_MeV / leaf m_W_MeV = [(theta_S+e^3)/C_factor^7] / [theta_S^-6 C_factor^-4 gamma^2 + e^e] (hub 6b3ce06c and 4afc9aad, 2026-09-29)", "chosen": True},
  {"id": "C-MHW-2", "item": "m_H/m_W", "statement": "m_H/m_W = 1/(3 P_new (1 - C_factor)) (quotient of seed_higgs_GeV and seed_m_W_GeV, hub vendor/fsot_seed_flavor.py, 2026-08)", "chosen": False},
  {"id": "C-DM-1", "item": "Dm2_21/Dm2_32", "statement": "Dm2_21/Dm2_32 = (POOF*G*P_new)^3 / [(G*SUCTION)^3 (1+yy)] (seed_dm2()['dm2_21'] over leaf dm2_32, scripts/atmospheric_neutrino_seed_check.py; identical to seed_dm2()['dm2_31_abs'] numerically)", "chosen": True},
  {"id": "C-TCMB", "item": "T_CMB", "statement": "T_CMB = (phi^2 + P_base*|S_cosm|) * (1 + yy)", "chosen": True},
  {"id": "C-GZ", "item": "Gamma_Z/M_Z", "statement": "Gamma_Z/M_Z = (phi^5/e^6) * (1 + yy)", "chosen": True},
  {"id": "C-BD", "item": "Deuteron_binding", "statement": "B_d = (sqrt(e)/e + phi) * (1 + yy*gamma*psi_con^2)", "chosen": True},
  {"id": "C-MUD", "item": "Deuteron_mu", "statement": "mu_d/mu_N = (G^4 + POOF) * (1 + yy)", "chosen": True},
]
for c in cands:
    c["statement_sha256"] = hashlib.sha256(c["statement"].encode()).hexdigest()
    c["tier"] = "frozen-pending"

rules = {
  "S1_route_items": "m_H/m_W and Dm2_21/Dm2_32: use the latest committed hub leaves for the numerator and denominator (Damian's leaf-quotient pattern: m_W/m_Z, m_pi/m_p, m_n-m_p). Where a committed leaf is missing (Dm2_21), use the committed seed function. Never chosen by z.",
  "S2_family_items": "Single formula per item, fixed before scoring. Nuclear binding (deuteron): the dressing of the nearest-A committed binding leaf, triton B_H3 = bare*(1 + yy*gamma*psi_con^2) (hub 2026-09-29). Every other family item (T_CMB, Gamma_Z/M_Z, mu_d): Damian's documented cross-sector precision polish *(1 + (POOF*SUCTION)^2) (seed_higgs_GeV, seed_dm2 docstrings). Signs are taken from the precedent (+), never from the data.",
  "family_for_look_elsewhere_only": f"{len(FAMILY)} forms per family item: bare*(1 +- d*x), d in {DRESS}, x in Damian's named-seed list (scripts/deuteron_binding_seed_check.py named_seeds(), {len(NAMED)} entries). Scored only to measure the chance rate of z<=1; nothing is adopted from it. The S2 choices are members of this family.",
  "not_used": "lowest z; Damian's uniqueness-in-window rule (z-based) is printed for information only.",
}
N = {"alpha_s(M_Z)": 1, "H0": 0, "m_H/m_W": 2, "Dm2_21/Dm2_32": 1, "T_CMB": len(FAMILY), "Gamma_Z/M_Z": len(FAMILY), "Deuteron_binding": len(FAMILY), "Deuteron_mu": len(FAMILY)}
held = {
  "m_H/m_W": "sibling m_H/m_Z = leaf m_H / leaf m_Z vs PDG 2024 125.20(11)/91.1880(20); sibling m_H/m_t = leaf m_H / (leaf m_t/m_W * leaf m_W) vs PDG 2024 125.20(11)/172.57(29)",
  "Dm2_21/Dm2_32": "sibling Dm2_21 seed alone vs PDG 2024 7.53(18)e-5 eV^2; convention check vs Dm2_21/Dm2_31 with Dm2_31 = Dm2_32 + Dm2_21 (normal ordering, PDG 2024 inputs)",
  "T_CMB": "none independent (FIRAS is the only absolute measurement at this precision)",
  "Gamma_Z/M_Z": "none independent",
  "Deuteron_binding": "none independent (AME2020 per-nucleon and mass-excess routes are the same data)",
  "Deuteron_mu": "none independent",
}
disclosure = [
  "Seen before this freeze (from task 1 and hub scripts): the bare z of every item; Damian's printed deuteron windows (alpha^2: pi^-4; alpha^3: sqrt(e), phi; his decision 'the bare sum stays') and his mu_d*(1+alpha^2) result; the H0 pin value. The deuteron-binding and mu_d choices are therefore not blind in the strict sense; S2 fixes them by precedent, not by those windows.",
  "Not computed before this freeze: seed_alpha_s_MZ, every candidate value above, every family value.",
]
doc = {"freeze": "REFINEMENTS_2026-10-02b", "date": "2026-10-02", "tier": "frozen-pending",
       "authority_pin": "AEB2AD (vendor/fsot_compute.py sha256 AEB2ADAD6E80F487772C5DF90A2E3DDA71624AB831A6A83B94AB471AC9AAC170)",
       "hub_data_commit": "6f9c25605a52acabe662a42fc003afa5bf66b959",
       "definitions": alpha_def, "named_seeds": NAMED, "dressings": DRESS, "family": FAMILY,
       "fixes": fixes, "candidates": cands, "selection_rules": rules, "candidate_count": N,
       "candidate_count_total": sum(N.values()), "held_out": held, "disclosure": disclosure,
       "scorer": "tools/score_refinements_2026_10_02b.py (Python/mpmath, hub engine) and apps/fsot_precision.cpp (C++ mp169) after this commit"}
doc["candidates_sha256"] = hashlib.sha256(json.dumps(cands, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
J = os.path.join(D, "REFINEMENTS_2026-10-02b.json")
json.dump(doc, open(J, "w", encoding="utf-8"), indent=2, ensure_ascii=False); open(J, "a").write("\n")
L = ["# REFINEMENTS_2026-10-02b (frozen-pending; written before any candidate was scored)", "",
     f"Authority pin {doc['authority_pin']}; hub data {doc['hub_data_commit']}.", "", f"Definitions: {alpha_def}.", "",
     "## Data / channel fixes (bug fixes, decided by Damian before this session)", ""]
for f in fixes:
    L += [f"### {f['id']} {f['item']} ({f['class']})", "", f["statement"], "", f"Held-out: {'; '.join(f['held_out'])}.", "", f"Disclosure: {f['disclosure']}", ""]
L += ["## Candidates (frozen-pending)", "", "| id | item | statement | chosen | sha256(statement) |", "|---|---|---|---|---|"]
for c in cands:
    L.append(f"| {c['id']} | {c['item']} | {c['statement']} | {'yes' if c['chosen'] else 'no'} | `{c['statement_sha256'][:16]}` |")
L += ["", "## A-priori selection rules", ""] + [f"- **{k}**: {v}" for k, v in rules.items()]
L += ["", "## Candidate count", "", "| item | N |", "|---|---|"] + [f"| {k} | {v} |" for k, v in N.items()] + [f"| **total** | **{sum(N.values())}** |"]
L += ["", "Family forms (each family item): " + ", ".join(FAMILY), "", "## Held-out checks", ""] + [f"- {k}: {v}" for k, v in held.items()]
L += ["", "## Disclosure", ""] + [f"- {d}" for d in disclosure] + ["", f"candidates_sha256 = {doc['candidates_sha256']}", ""]
open(os.path.join(D, "REFINEMENTS_2026-10-02b.md"), "w", encoding="utf-8").write("\n".join(L))
with open(os.path.join(D, "REFINEMENTS_2026-10-02b.sha256"), "w") as fh:
    for n in ("REFINEMENTS_2026-10-02b.json", "REFINEMENTS_2026-10-02b.md"):
        fh.write(hashlib.sha256(open(os.path.join(D, n), "rb").read()).hexdigest() + "  " + n + "\n")
print("total candidates", sum(N.values()))
