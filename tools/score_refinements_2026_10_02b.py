#!/usr/bin/env python3
"""Score docs/freezes/REFINEMENTS_2026-10-02b (written and committed before this script existed).

  python tools/score_refinements_2026_10_02b.py --hub <FSOT-2.1-Lean checkout at 6f9c2560> --out audit/refinements_2026-10-02b.tsv

Uses the hub engine vendor/fsot_compute.py unchanged (mpmath, 50 digits) and the references in
reference/published_2026-10-02.tsv. Prints every candidate, the full look-elsewhere family, the held-out
checks and the Ledger B miss diagnosis. Nothing here is adopted by z.
"""
import argparse, json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
hub = Path(a.hub).resolve()
sys.path.insert(0, str(hub / "vendor"))
import fsot_compute as F  # noqa: E402
from mpmath import mpf, sqrt, pi, nstr, fabs  # noqa: E402

freeze = json.load(open(ROOT / "docs/freezes/REFINEMENTS_2026-10-02b.json", encoding="utf-8"))

refs = {}
for line in open(ROOT / "reference/published_2026-10-02.tsv", encoding="utf-8"):
    if line.startswith("#") or not line.strip():
        continue
    f = line.rstrip("\n").split("\t"); f += [""] * (9 - len(f))
    refs[f[0]] = f
def ref(k):
    f = refs[k]
    if f[1] == "direct":
        return mpf(f[2]), mpf(f[3]), mpf(f[4])
    op, _, arg = f[1].partition(":"); p = arg.split("/")
    if op == "ratio":
        (ca, sa, _), (cb, sb, _) = ref(p[0]), ref(p[1])
        c = ca / cb; s = fabs(c) * sqrt((sa / ca) ** 2 + (sb / cb) ** 2); return c, s, s
    raise SystemExit("unsupported op " + op)
def z(v, c, sm, sp):
    return fabs(v - c) / (sp if v >= c else sm)

E, PHI, G, GAMMA, PSI = F.E, F.PHI, F.G_CAT, F.GAMMA, F.PSI_CON
POOF, SUC, CF, PB, PN, TH = F.POOF, F.SUCTION, F.C_FACTOR, F.P_BASE, F.P_NEW, F.THETA_S
yy = (POOF * SUC) ** 2
alpha = 1 / (E**3 * PHI**4 - PSI - yy * CF**2 / PB)
m_H = (TH + E**3) / CF**7
w_prod = TH ** (-6) * CF ** (-4) * GAMMA**2
m_W = w_prod + E**E
m_Z = w_prod / sqrt(1 - (POOF + F.K / 6))
m_t_over_W = fabs(F.S_COSM) / fabs(F.CHAOS) + PSI
dm21 = (POOF * G * PN) ** 3
dm32 = (G * SUC) ** 3 * (1 + yy)
bare = {"T_CMB": (PHI**2 + PB * fabs(F.S_COSM), "T0_K"),
        "Gamma_Z/M_Z": (PHI**5 / E**6, "Gamma_Z_over_M_Z"),
        "Deuteron_binding": (sqrt(E) / E + PHI, "B_H2_MeV"),
        "Deuteron_mu": (G**4 + POOF, "mu_d_over_mu_N")}
NAMED = {"1": mpf(1), "e": E, "phi": PHI, "sqrt(e)": sqrt(E), "sqrt(phi)": sqrt(PHI), "gamma": GAMMA, "G": G,
         "psi_con": PSI, "1/phi": 1 / PHI, "pi^{-4}": pi ** (-4), "e^{-4}": E ** (-4), "pi+P_base": pi + PB,
         "gamma*psi_con^2": GAMMA * PSI**2}
DRESS = {"alpha": alpha, "alpha^2": alpha**2, "alpha^3": alpha**3, "yy": yy}
assert list(NAMED) == freeze["named_seeds"] and list(DRESS) == freeze["dressings"]

rows = []
def emit(section, cid, item, formula, v, rk, extra=""):
    c, sm, sp = ref(rk); zz = z(v, c, sm, sp)
    rows.append([section, cid, item, formula, nstr(v, 15), rk, nstr(c, 12), nstr(sm, 6), nstr(zz, 6), "PASS" if zz <= 1 else "FAIL", extra])
    return zz

# fixes (channel), scored set
emit("fix", "F1", "H0", "100(1+S_cosm*A_bleed/A_in)", 100 * (1 + F.S_COSM * F.A_BLEED / F.A_IN), "H0_CMB_BAO", "scored reference")
for rk in ("H0", "H0_SH0ES"):
    emit("alternate", "F1", "H0", "100(1+S_cosm*A_bleed/A_in)", 100 * (1 + F.S_COSM * F.A_BLEED / F.A_IN), rk, "printed, not scored")
for rk in ("H0_PACT_LB_DR1", "H0_PACT"):
    emit("held_out", "F1", "H0", "100(1+S_cosm*A_bleed/A_in)", 100 * (1 + F.S_COSM * F.A_BLEED / F.A_IN), rk, "")
as_seed = 2 * (POOF / PSI) ** 2
emit("fix", "F2", "alpha_s(M_Z)", "2*(POOF/psi_con)^2", as_seed, "alpha_s_MZ", "scored reference")
emit("alternate", "F2", "alpha_s(M_Z)", "1/(e*pi) (wave1 pin)", 1 / (E * pi), "alpha_s_MZ", "printed, not scored")
for rk in ("alpha_s_MZ_nolattice", "alpha_s_MZ_FLAG2021"):
    emit("held_out", "F2", "alpha_s(M_Z)", "2*(POOF/psi_con)^2", as_seed, rk, "input to the PDG average; correlated")

# candidates
emit("candidate", "C-MHW-1", "m_H/m_W", "leaf m_H / leaf m_W", m_H / m_W, "m_H_over_m_W", "chosen (S1)")
emit("candidate", "C-MHW-2", "m_H/m_W", "1/(3 P_new (1-C_factor))", 1 / (3 * PN * (1 - CF)), "m_H_over_m_W", "not chosen")
emit("held_out", "C-MHW-1", "m_H/m_Z", "leaf m_H / leaf m_Z", m_H / m_Z, "m_H_over_m_Z", "sibling")
emit("held_out", "C-MHW-1", "m_H/m_t", "leaf m_H / (leaf m_t/m_W * leaf m_W)", m_H / (m_t_over_W * m_W), "m_H_over_m_t", "sibling")
emit("candidate", "C-DM-1", "Dm2_21/Dm2_32", "(POOF G P_new)^3 / [(G SUCTION)^3 (1+yy)]", dm21 / dm32, "dm2_21_over_dm2_32", "chosen (S1)")
emit("held_out", "C-DM-1", "Dm2_21", "(POOF G P_new)^3", dm21, "dm2_21", "sibling")
c21, s21, _ = ref("dm2_21"); c32, s32, _ = ref("dm2_32")
c31 = c32 + c21; r31 = c21 / c31; s_r31 = r31 * sqrt((s21 / c21 * (1 - r31)) ** 2 + (s32 / c31) ** 2)
v = dm21 / dm32; zz = fabs(v - r31) / s_r31
rows.append(["held_out", "C-DM-1", "Dm2_21/Dm2_31 (convention check)", "same value", nstr(v, 15), "dm2_21/(dm2_32+dm2_21)", nstr(r31, 12), nstr(s_r31, 6), nstr(zz, 6), "PASS" if zz <= 1 else "FAIL", "normal ordering, PDG 2024 inputs; not the row's label"])
chosen = {"T_CMB": ("yy", "1"), "Gamma_Z/M_Z": ("yy", "1"), "Deuteron_binding": ("yy", "gamma*psi_con^2"), "Deuteron_mu": ("yy", "1")}
cid = {"T_CMB": "C-TCMB", "Gamma_Z/M_Z": "C-GZ", "Deuteron_binding": "C-BD", "Deuteron_mu": "C-MUD"}
for item, (b, rk) in bare.items():
    emit("bare", cid[item], item, "pin AEB2AD closed form", b, rk, "status quo")
    d, x = chosen[item]
    emit("candidate", cid[item], item, f"bare*(1+{d}*{x})", b * (1 + DRESS[d] * NAMED[x]), rk, "chosen (S2)")

# look-elsewhere family
summary = []
for item, (b, rk) in bare.items():
    hits = 0; n = 0; byd = {}
    for dn, dv in DRESS.items():
        for xn, xv in NAMED.items():
            for s in (+1, -1):
                val = b * (1 + s * dv * xv)
                zz = emit("family", cid[item], item, f"bare*(1{'+' if s > 0 else '-'}{dn}*{xn})", val, rk, "")
                n += 1
                if zz <= 1:
                    hits += 1; byd[dn] = byd.get(dn, 0) + 1
    summary.append([item, n, hits, hits / n, byd])
tot_n = sum(s[1] for s in summary); tot_h = sum(s[2] for s in summary)

# Ledger B misses: hub stored values (golden/ledger_b_genuine_misses_6f9c2560.tsv) vs cited references
lb = []
for line in open(ROOT / "golden/ledger_b_genuine_misses_6f9c2560.tsv", encoding="utf-8"):
    f = line.rstrip("\n").split("\t")
    if f[0] == "file":
        continue
    lb.append(f)
with open(a.out, "w", encoding="utf-8") as o:
    o.write("# generated by tools/score_refinements_2026_10_02b.py; freeze docs/freezes/REFINEMENTS_2026-10-02b.json committed before scoring\n")
    o.write("#section\tid\titem\tformula\tvalue\tref_key\tcentral\tsigma\tz\tz<=1\tnote\n")
    for r in rows:
        o.write("\t".join(r) + "\n")
    o.write("#look_elsewhere\titem\tN\thits_z<=1\tfraction\thits_by_dressing\n")
    for s in summary:
        o.write(f"look_elsewhere\t{s[0]}\t{s[1]}\t{s[2]}\t{s[3]:.4f}\t{json.dumps(s[4], sort_keys=True)}\n")
    o.write(f"look_elsewhere\tALL_FAMILY\t{tot_n}\t{tot_h}\t{tot_h / tot_n:.4f}\t\n")
    o.write("#ledger_b\tfile\tindex\tname\tcomputed\tstored_measured\tstored_error_pct\terror_pct_vs_stored_measured\tref_key\tz_vs_ref\tdiagnosis\n")
    LBREF = {"tau_reion": [("tau_reion_PlanckBAO", "stored 'measured' = Planck 2018 TT,TE,EE+lowE+lensing+BAO"), ("tau_reion_Planck", "stored error_pct 0.006335 was computed against this value"), ("tau_reion", "PDG 2024")],
             "D_H_ratio": [("D_H_Cooke2018", "stored 'measured' = Cooke 2018"), ("D_H", "PDG 2024 eq. 24.2; stored error_pct 0.090986 was computed against this value")]}
    for f in lb:
        name, comp, meas, stored = f[2], mpf(f[5]), mpf(f[6]), f[7]
        rel = fabs(comp - meas) / fabs(meas) * 100
        if name in LBREF:
            for rk, note in LBREF[name]:
                c, sm, sp = ref(rk)
                o.write(f"ledger_b\t{f[0]}\t{f[1]}\t{name}\t{nstr(comp, 15)}\t{nstr(meas, 12)}\t{stored}\t{nstr(rel, 6)}\t{rk}\t{nstr(z(comp, c, sm, sp), 6)}\t{note}\n")
        elif name.startswith("Mean_dependency_length"):
            o.write(f"ledger_b\t{f[0]}\t{f[1]}\t{name}\t{nstr(comp, 15)}\t{nstr(meas, 12)}\t{stored}\t{nstr(rel, 6)}\thub band 8.7% (sigma 0.2 words)\t{nstr(fabs(comp - meas) / mpf('0.2'), 6)}\tno published source in the hub row; stored error_pct matches measured=2.4, not the stored 2.3\n")
        else:
            o.write(f"ledger_b\t{f[0]}\t{f[1]}\t{name}\t{nstr(comp, 15)}\t{nstr(meas, 12)}\t{stored}\t{nstr(rel, 6)}\tnone\t-\tno published periodicity found (CHIME/FRB 2023 repeater search: no detections); not z-gateable\n")
print(f"candidates scored; family hits {tot_h}/{tot_n} = {tot_h / tot_n:.4f}")
