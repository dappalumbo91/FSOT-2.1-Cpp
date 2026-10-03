#!/usr/bin/env python3
"""Write audit/FREEZE_2026-10-02lm.{md,json,sha256}: the D_eff -> unit map branch (owner steer, round l). Committed BEFORE its scoring code."""
import hashlib, json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "audit")
F = {
 "freeze": "FREEZE_2026-10-02lm", "date": "2026-10-02", "parent_freeze": "FREEZE_2026-10-02l (9c6dbbc)",
 "owner_steer": ("Damian: in FSOT dimensionality is carried by D_eff, the effective dimension through which quantities bleed between domains; "
                 "make D_eff (and the domain S with its recent_hits/observed structure) the mechanism that carries a dimensionless FSOT number "
                 "into a dimensional quantity; freeze one consistent map on a training subset and score held-out leaves."),
 "definition": ("each unit-read leaf N is carried to a dimensional value Q = N x A_unit x g(domain), where A_unit is the m_e-anchor natural unit of "
                "the quantity (m_e c^2 for masses/energies, hbar/(m_e c) for lengths, m_e c^2/k_B for temperature, m_e c^2/hbar for rates, "
                "(m_e c^2)^2 for squared masses), all from the FSOT m_e seed leaf; g is a single function of the domain fold variables only"),
 "domain_assignment": {"m_pi+-, m_K+-, m_D+-, r_p, dm2_32": "Particle_Physics (D_eff 5, hits 0, observed, S = 0.950197)",
                       "m_W, m_Z, m_H": "High_Energy_Physics (D_eff 6, hits 1, observed, S = 0.887330)",
                       "B(2H), B(3H), B(4He)": "Nuclear_Physics (D_eff 12, hits 0, observed, S = 0.936388)",
                       "T_CMB, H0": "Cosmology (D_eff 25, hits 0, medium, S = -0.502377)"},
 "families": {"M1 power of D_eff": "ln g = a + b ln(D_eff/5)", "M2 exponential of D_eff": "ln g = a + b (D_eff - 5)", "M3 S-dependent": "ln g = a + b S_domain"},
 "training": "m_pi+- (Particle_Physics), B(2H) (Nuclear_Physics), T_CMB (Cosmology): a, b by least squares in ln g against the measured values",
 "held_out": "m_K+-, m_D+-, r_p, dm2_32, m_W, m_Z, m_H, B(3H), B(4He), H0",
 "measured": {"m_K+-": "493.677(15) MeV PDG 2024", "m_D+-": "1869.66(5) MeV PDG 2024", "r_p": "0.8409(4) fm PDG 2024", "dm2_32": "2.455(28)e-3 eV^2 PDG 2024 NO",
              "m_W": "80369.2(13.3) MeV PDG 2024", "m_Z": "91187.6(2.1) MeV PDG 2024", "m_H": "125200(110) MeV PDG 2024", "B(2H)": "2.224566 MeV AME2020",
              "B(3H)": "8.481798 MeV AME2020", "B(4He)": "28.295674 MeV AME2020", "T_CMB": "2.7255(6) K FIRAS", "H0": "67.4(5) km/s/Mpc Planck (PDG 2024)", "m_pi+-": "139.57039(18) MeV PDG 2024"},
 "gate": "a family is a consistent D_eff -> unit map iff every held-out leaf is within 2 % of its measured value; the training residual is reported",
 "look_elsewhere": "3 families x 1 domain assignment",
 "disclosure": ("reasoned before this freeze: the factor each leaf needs, g = unit/A_unit, depends on the SI unit the leaf is read in (MeV, fm, K, km/s/Mpc, eV^2), "
                "and r_p and m_pi+- sit in the same domain with different units, so a map of the domain variables alone is not expected to carry both; "
                "the test is run as frozen regardless"),
}
open(os.path.join(D, "FREEZE_2026-10-02lm.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(F, indent=1, ensure_ascii=False) + "\n")
open(os.path.join(D, "FREEZE_2026-10-02lm.md"), "w", encoding="utf-8", newline="\n").write("# FREEZE_2026-10-02lm (D_eff -> unit map; committed before its scoring code)\n\n```json\n" + json.dumps(F, indent=1, ensure_ascii=False) + "\n```\n")
with open(os.path.join(D, "FREEZE_2026-10-02lm.sha256"), "w", newline="\n") as f:
    for n in ("FREEZE_2026-10-02lm.json", "FREEZE_2026-10-02lm.md"):
        f.write(hashlib.sha256(open(os.path.join(D, n), "rb").read()).hexdigest() + "  " + n + "\n")
print("written")
