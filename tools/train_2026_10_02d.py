#!/usr/bin/env python3
"""Step 2 of DERIVATIONS_2026-10-02d (frozen first): score part A and the part-B rows, and train the C1 class search. No C1 target is evaluated here.

  python tools/train_2026_10_02d.py --hub <FSOT-2.1-Lean @ 6f9c2560> --rows-out audit/rows_2026-10-02d.tsv --out audit/train_2026-10-02d.tsv
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, sqrt, pi, ln, fabs, nstr
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--rows-out", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); ref = X.refs(); P = X.pins(); R = X.compute(hub, F)
import fsot_seed_flavor as SF  # noqa: E402  (float cross-check of the seed G_F)
assert fabs(R["GF"] - mpf(SF.seed_G_F())) / R["GF"] < mpf("1e-14"), "seed G_F mismatch"
def z(v, c, s): return fabs(v - c) / s
rows = []
def emit(sec, name, inputs, v, c, s, note=""):
    rows.append([sec, name, inputs, nstr(v, 15), nstr(c, 12), nstr(s, 5), nstr(z(v, c, s), 5), "PASS" if z(v, c, s) <= 1 else "FAIL", nstr((v - c) / c * 10**6, 6), note])
# A
gzmz = ref("Gamma_Z_over_M_Z")
emit("A", "Gamma_Z/M_Z (A1, candidate)", "G_F seed, m_Z, sin2_MSbar, alpha leaves, alpha_s seed", R["GZ_over_MZ_A1"], *gzmz, "frozen-pending candidate")
emit("A", "Gamma_Z GeV (A1)", "same", R["Gamma_Z_A1"], *ref("Gamma_Z_GeV"))
for k, lab in (("Gamma_Z_A2", "A2 = 3Gll+Ginv+R_ell(pin)Gll"), ("Gamma_Z_A3", "A3 = Gee/BR_Z_ee(pin)"), ("Gamma_Z_A4", "A4 = Ginv/BR_Z_inv(pin)")):
    emit("A_alt", f"Gamma_Z GeV ({lab})", "reported, not a candidate", R[k], *ref("Gamma_Z_GeV"), "alternative (look-elsewhere 4)")
emit("A_heldout", "Gamma_inv MeV", "3 Gamma_nunu(A1)", R["Gamma_inv"] * 1000, *ref("Gamma_inv_MeV"))
emit("A_heldout", "Gamma_ll MeV", "Gamma_ee(A1)", R["Gamma_ee"] * 1000, *ref("Gamma_ll_MeV"))
emit("A_heldout", "sigma_had0 nb", "A1 widths, m_Z", R["sigma_had0_nb"], *ref("sigma_had0_nb"))
emit("A_heldout", "R_ell", "Gamma_had(A1)/Gamma_ee(A1)", R["R_ell_A1"], *ref("R_ell_derived"))
emit("A_heldout", "Gamma_had MeV (info)", "A1", R["Gamma_had"] * 1000, mpf("1744.4"), mpf("2.0"), "PDG 1744.4(2.0) MeV, same table (sum-gauge-higgs-bosons line 75); info only")
# B
emit("B", "G_F GeV^-2 (diagnostic)", "seed v = (theta_S+e^3)/C_factor^6/1000*phi", R["GF"], *ref("G_F_GeVm2"))
emit("B", "Gamma_W GeV", "G_F seed, m_W leaf, alpha_s seed", R["Gamma_W"], *ref("Gamma_W_GeV"))
emit("B", "tau_mu s", "G_F seed, m_mu, m_e, alpha leaves", R["tau_mu"], *ref("tau_mu_s"))
emit("B", "tau_tau s", "tau_mu(B), m_mu, m_tau leaves, BR(tau->e nu nu) EXTERNAL PDG", R["tau_tau"], *ref("tau_tau_s"), "1 external input")
emit("B", "tau_pi+ s", "not constructed (FSOT has no f_pi)", mpf(0), mpf(1), mpf(1), "NOT CONSTRUCTED")
rows[-1][3:9] = ["-", "2.6033e-8", "-", "-", "n/a", "-"]
emit("B", "mu_n/mu_N", "-(2/3) mu_p leaf (SU(6))", R["mu_n"], *ref("mu_n_over_mu_N"))
emit("B", "mu_t/mu_N", "mu_p leaf (Schmidt, S state)", R["mu_t"], *ref("mu_t_over_mu_N"))
s67 = R["sec67"]
emit("B", "mu_h/mu_N", f"Damian sec.67 #1037 {s67['He-3']['formula']} ({s67['He-3']['source']})", R["mu_h"], *ref("mu_h_over_mu_N"))
# C1 training
E, PHI, G, GAMMA, PSI, POOF, SUC, CF, PB, PN = F.E, F.PHI, F.G_CAT, F.GAMMA, F.PSI_CON, F.POOF, F.SUCTION, F.C_FACTOR, F.P_BASE, F.P_NEW
yy = (POOF * SUC) ** 2
alpha = 1 / (E**3 * PHI**4 - PSI - yy * CF**2 / PB)
NAMED = dict(zip(["1", "e", "phi", "sqrt(e)", "sqrt(phi)", "gamma", "G", "psi_con", "1/phi", "pi^{-4}", "e^{-4}", "pi+P_base", "gamma*psi_con^2"],
                 [mpf(1), E, PHI, sqrt(E), sqrt(PHI), GAMMA, G, PSI, 1 / PHI, pi ** (-4), E ** (-4), pi + PB, GAMMA * PSI**2]))
DRESS = {"alpha": alpha, "alpha^2": alpha**2, "alpha^3": alpha**3, "yy": yy}
OPTIONS = [("none", mpf(0))] + [(f"(1{'+' if s > 0 else '-'}{dn}*{xn})", s * dv * xv) for dn, dv in DRESS.items() for xn, xv in NAMED.items() for s in (1, -1)]
assert len(OPTIONS) == 105
nuc = {"Li-7": ("mu_Li7", 7, mpf(3) / 2), "B-11": ("mu_B11", 11, mpf(3) / 2), "C-13": ("mu_C13", 13, mpf(1) / 2), "N-14": ("mu_N14", 14, mpf(1)),
       "F-19": ("mu_F19", 19, mpf(1) / 2), "Na-23": ("mu_Na23", 23, mpf(3) / 2), "Al-27": ("mu_Al27", 27, mpf(5) / 2), "P-31": ("mu_P31", 31, mpf(1) / 2)}
# member = (name, bare, central, sigma, (A, J) or None)
cls = {}
cls["W2_widths"] = [("Neutron_lifetime_s", P["wave3|Neutron_lifetime_s"], *ref("tau_n_s"), None), ("R_b", P["wave5|R_b"], *ref("R_b"), None),
                    ("R_c", P["wave5|R_c"], *ref("R_c"), None), ("BR_Z_ee", P["wave8|BR_Z_ee"], *ref("BR_Z_ee"), None),
                    ("BR_Z_had", P["wave8|BR_Z_had"], *ref("BR_Z_had"), None), ("BR_Z_inv", P["wave8|BR_Z_inv"], *ref("BR_Z_inv"), None),
                    ("Gamma_W", R["Gamma_W"], *ref("Gamma_W_GeV"), None), ("tau_mu", R["tau_mu"], *ref("tau_mu_s"), None), ("tau_tau", R["tau_tau"], *ref("tau_tau_s"), None)]
cls["M2_moments"] = [("g_e", R["ge_bare"], *ref("g_e_abs"), None), ("g_p", R["gp_bare"], *ref("g_p"), (1, mpf(1) / 2)),
                     ("mu_n", R["mu_n"], *ref("mu_n_over_mu_N"), (1, mpf(1) / 2)), ("mu_t", R["mu_t"], *ref("mu_t_over_mu_N"), (3, mpf(1) / 2)),
                     ("mu_h", R["mu_h"], *ref("mu_h_over_mu_N"), (3, mpf(1) / 2))]
for nm, (key, A, J) in nuc.items():
    cls["M2_moments"].append((f"sec67_{nm}", s67[nm]["value"], *ref(key), (A, J)))
def first_option(members):
    for name, fac in OPTIONS:
        if all(z(b * (1 + fac), c, s) <= 1 for (_, b, c, s, _) in members): return name, fac
    return "none", mpf(0)
trows, verdict = [], {}
for k, mem in cls.items():
    n = len(mem)
    deltas = [(c - b) / b for (_, b, c, s, _) in mem]
    signs = [1 if d > 0 else -1 for d in deltas]
    kpow = [int(round(float(ln(fabs(d)) / ln(alpha)))) for d in deltas]
    for (nm, b, c, s, st), d, kp in zip(mem, deltas, kpow):
        trows.append(["member", k, nm, nstr(b, 15), nstr(c, 12), nstr(s, 4), nstr(z(b, c, s), 5), nstr(d, 6), str(kp), "-" if st is None else f"A={st[0]} J={nstr(st[1], 3)}"])
    sign_agree = max(signs.count(1), signs.count(-1)); p2 = max(kpow.count(x) for x in set(kpow))
    loo3 = []
    for i in range(n):
        rest = mem[:i] + mem[i + 1:]; name, fac = first_option(rest)
        _, b, c, s, _ = mem[i]; zz = z(b * (1 + fac), c, s); loo3.append(zz)
        trows.append(["loo_P3", k, mem[i][0], name, nstr(zz, 5)])
    full3 = first_option(mem)[0]; p3_ok = sum(1 for zz in loo3 if zz <= 1)
    best4 = None
    if k == "M2_moments":
        sub = [m for m in mem if m[4] is not None]; ns = len(sub)
        for vn, vf in (("1", lambda st: mpf(1)), ("A", lambda st: mpf(st[0])), ("A^-1/3", lambda st: mpf(st[0]) ** (mpf(-1) / 3)), ("J", lambda st: st[1])):
            ok = 0
            for i in range(ns):
                rest = sub[:i] + sub[i + 1:]
                xs = [vf(st) for (_, b, c, s, st) in rest]; ys = [(c - b) / b for (_, b, c, s, st) in rest]
                cc = sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)
                _, b, c, s, st = sub[i]; zz = z(b * (1 + cc * vf(st)), c, s); ok += zz <= 1
                trows.append(["loo_P4", k, sub[i][0], f"v={vn} c={nstr(cc, 6)}", nstr(zz, 5)])
            trows.append(["P4_summary", k, f"v={vn}", f"loo_pass={ok}/{ns}"])
            if best4 is None or ok > best4[1]: best4 = (vn, ok, ns)
    loo_best = max(p3_ok, best4[1] if best4 else 0)
    p4_pass = bool(best4 and best4[1] * 3 >= 2 * best4[2])
    accepted = n >= 3 and sign_agree == n and (p3_ok * 3 >= 2 * n and full3 != "none" or p4_pass)
    verdict[k] = dict(n=n, sign_agree=f"{sign_agree}/{n}", alpha_power_agree=f"{p2}/{n}", p3_loo_pass=f"{p3_ok}/{n}", p3_full_selection=full3,
                      p4_best=(f"{best4[0]} {best4[1]}/{best4[2]}" if best4 else "-"), accepted=bool(accepted))
hdr = "# generated by tools/train_2026_10_02d.py under docs/freezes/DERIVATIONS_2026-10-02d (committed first)\n"
with open(a.rows_out, "w", encoding="utf-8") as o:
    o.write(hdr + "#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tz<=1\tppm\tnote\n")
    for r in rows: o.write("\t".join(r) + "\n")
with open(a.out, "w", encoding="utf-8") as o:
    o.write(hdr + "# C1 training only; no C1 target evaluated\n#member\tclass\tname\tbare\tcentral\tsigma\tz_bare\tdelta=(m-b)/b\talpha_power\tstructure\n")
    for r in trows: o.write("\t".join(r) + "\n")
    for k, v in verdict.items(): o.write("verdict\t" + k + "\t" + json.dumps(v, sort_keys=True) + "\n")
for r in rows: print(" | ".join(r))
for k, v in verdict.items(): print(k, v)
