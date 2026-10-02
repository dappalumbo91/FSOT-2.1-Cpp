#!/usr/bin/env python3
"""Training step of docs/freezes/PROTOCOL_2026-10-02c (committed before this script). No target is evaluated here.

  python tools/train_2026_10_02c.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/train_2026-10-02c.tsv
"""
import argparse, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub = Path(a.hub).resolve(); sys.path.insert(0, str(hub / "vendor"))
import fsot_compute as F  # noqa: E402
from mpmath import mpf, sqrt, pi, ln, nstr, fabs  # noqa: E402

proto = json.load(open(ROOT / "docs/freezes/PROTOCOL_2026-10-02c.json", encoding="utf-8"))
refs = {}
for line in open(ROOT / "reference/published_2026-10-02.tsv", encoding="utf-8"):
    if line.startswith("#") or not line.strip(): continue
    f = line.rstrip("\n").split("\t"); f += [""] * (9 - len(f)); refs[f[0]] = f
def ref(k):
    f = refs[k]
    if f[1] == "direct": return mpf(f[2]), mpf(f[3])
    p = f[1].split(":")[1].split("/"); (ca, sa), (cb, sb) = ref(p[0]), ref(p[1]); c = ca / cb
    return c, fabs(c) * sqrt((sa / ca) ** 2 + (sb / cb) ** 2)
lin = {}
for line in open(ROOT / "reference/pin_lineage_2026-10-02.tsv", encoding="utf-8"):
    if line.startswith("#"): continue
    f = line.rstrip("\n").split("\t"); lin[f[0]] = mpf(f[5])

E, PHI, G, GAMMA, PSI, POOF, SUC, CF, PB, PN = F.E, F.PHI, F.G_CAT, F.GAMMA, F.PSI_CON, F.POOF, F.SUCTION, F.C_FACTOR, F.P_BASE, F.P_NEW
yy = (POOF * SUC) ** 2
alpha = 1 / (E**3 * PHI**4 - PSI - yy * CF**2 / PB)
NAMED = dict(zip(["1", "e", "phi", "sqrt(e)", "sqrt(phi)", "gamma", "G", "psi_con", "1/phi", "pi^{-4}", "e^{-4}", "pi+P_base", "gamma*psi_con^2"],
                 [mpf(1), E, PHI, sqrt(E), sqrt(PHI), GAMMA, G, PSI, 1 / PHI, pi ** (-4), E ** (-4), pi + PB, GAMMA * PSI**2]))
DRESS = {"alpha": alpha, "alpha^2": alpha**2, "alpha^3": alpha**3, "yy": yy}
OPTIONS = [("none", mpf(0))] + [(f"(1{'+' if s > 0 else '-'}{dn}*{xn})", s * dv * xv) for dn, dv in DRESS.items() for xn, xv in NAMED.items() for s in (1, -1)]
assert len(OPTIONS) == 105

# AME2020 B/A (keV) from the committed extract
ame = {}
for line in open(ROOT / "reference/evidence/ame2020_ba_extracts.txt", encoding="utf-8"):
    if line.startswith("#"): continue
    body = line.split("\t", 1)[1]
    m = re.match(r"^.{1,5}\s*-?\d+\s+(\d+)\s+(\d+)\s+(\d+)\s+([A-Z][a-z]?)\s", body)
    fl = body[m.end():].split()
    ame[f"{m.group(4)}-{m.group(3)}"] = (mpf(fl[2]) / 1000, mpf(fl[3]) / 1000, int(m.group(3)))
geo = json.load(open(hub / "data/geochemistry_benchmark.json", encoding="utf-8"))["records"]

# member = (name, bare, central, sigma, structural A or None, used_dressing)
cls = {}
cls["W_widths"] = [("Neutron_lifetime_s", lin["wave3|Neutron_lifetime_s"], *ref("tau_n_s"), None, "none (pin)"),
                   ("R_b", lin["wave5|R_b"], *ref("R_b"), None, "none (pin)"), ("R_c", lin["wave5|R_c"], *ref("R_c"), None, "none (pin)"),
                   ("BR_Z_ee", lin["wave8|BR_Z_ee"], *ref("BR_Z_ee"), None, "none (pin)"), ("BR_Z_had", lin["wave8|BR_Z_had"], *ref("BR_Z_had"), None, "none (pin)"),
                   ("BR_Z_inv", lin["wave8|BR_Z_inv"], *ref("BR_Z_inv"), None, "none (pin)")]
ge_bare = 2 * (1 + (E / pi - ln(2)) / E**5)
gp_bare = (F.A_IN * PN / PB) ** 2
cls["M_moments"] = [("g_e", ge_bare, *ref("g_e_abs"), None, "-2(alpha/pi)^3*A_bleed*G^2*P_base/P_new"),
                    ("g_p", gp_bare, *ref("g_p"), None, "+alpha/psi_con^3*(1+yy^2) (additive)")]
cls["B1_binding_leaves"] = [("He-4", pi / GAMMA**4, *ref("B_He4_MeV"), 4, "*(1-alpha^2(pi+P_base))"),
                            ("H-3", E**2 + 1 / G, *ref("B_H3_MeV"), 3, "*(1+yy*gamma*psi_con^2)")]
idx = {"He-4": 74, "Li-6": 75, "Li-7": 76, "Be-9": 77, "C-12": 78, "N-14": 79, "O-16": 80, "Fe-56": 81, "Ni-62": 82, "U-235": 83, "U-238": 84, "Pu-239": 85, "Pb-208": 86}
cls["B2_binding_ledgerB"] = []
for nm, i in idx.items():
    r = geo[i]; assert r["name"] == nm, (r["name"], nm)
    c, s, A = ame[nm]
    cls["B2_binding_ledgerB"].append((nm, mpf(repr(r["computed"])), c, s, A, "none (Ledger B row)"))
cls["T_thermal"] = [("Omega_b_h2", lin["wave1|Omega_b_h2"], *ref("Omega_b_h2"), None, "none (pin)"), ("N_eff", lin["wave2|N_eff"], *ref("N_eff"), None, "none (pin)"),
                    ("eta_b", lin["wave10|eta_baryon_photon"], *ref("eta_b"), None, "none (pin)")]

def z(v, c, s): return fabs(v - c) / s
def first_option(members):
    for name, fac in OPTIONS:
        if all(z(b * (1 + fac), c, s) <= 1 for (_, b, c, s, _, _) in members): return name, fac
    return "none", mpf(0)
rows, verdict = [], {}
for k, mem in cls.items():
    n = len(mem)
    deltas = [(c - b) / b for (_, b, c, s, _, _) in mem]
    signs = [1 if d > 0 else -1 for d in deltas]
    kpow = [int(round(float(ln(fabs(d)) / ln(alpha)))) for d in deltas]
    for (nm, b, c, s, A, used), d, kp in zip(mem, deltas, kpow):
        rows.append(["member", k, nm, nstr(b, 15), nstr(c, 12), nstr(s, 4), nstr(z(b, c, s), 5), nstr(d, 6), str(kp), used])
    sign_agree = max(signs.count(1), signs.count(-1))
    p2 = max(kpow.count(x) for x in set(kpow))
    loo3 = []
    for i in range(n):
        rest = mem[:i] + mem[i + 1:]
        name, fac = first_option(rest) if rest else ("none", mpf(0))
        _, b, c, s, _, _ = mem[i]; zz = z(b * (1 + fac), c, s); loo3.append((name, zz))
        rows.append(["loo_P3", k, mem[i][0], name, nstr(zz, 5)])
    full3 = first_option(mem)[0]
    p3_ok = sum(1 for _, zz in loo3 if zz <= 1)
    best4 = None
    if k == "B2_binding_ledgerB":
        for vn, vf in (("1", lambda A, c: mpf(1)), ("A", lambda A, c: mpf(A)), ("A^-1/3", lambda A, c: mpf(A) ** (mpf(-1) / 3)), ("B/A", lambda A, c: c)):
            ok = 0
            for i in range(n):
                rest = mem[:i] + mem[i + 1:]
                xs = [vf(A, c) for (_, b, c, s, A, _) in rest]; ys = [(c - b) / b for (_, b, c, s, A, _) in rest]
                cc = sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)
                _, b, c, s, A, _ = mem[i]; zz = z(b * (1 + cc * vf(A, c)), c, s); ok += zz <= 1
                rows.append(["loo_P4", k, mem[i][0], f"v={vn} c={nstr(cc, 6)}", nstr(zz, 5)])
            rows.append(["P4_summary", k, f"v={vn}", f"loo_pass={ok}/{n}"])
            if best4 is None or ok > best4[1]: best4 = (vn, ok)
    loo_best = max(p3_ok, best4[1] if best4 else 0)
    accepted = n >= 3 and sign_agree == n and loo_best * 3 >= 2 * n and (full3 != "none" or (best4 and best4[1] * 3 >= 2 * n))
    verdict[k] = dict(n=n, sign_agree=f"{sign_agree}/{n}", alpha_power_agree=f"{p2}/{n}", p3_loo_pass=f"{p3_ok}/{n}", p3_full_selection=full3,
                      p4_best=(f"{best4[0]} {best4[1]}/{n}" if best4 else "-"), accepted=bool(accepted))
with open(a.out, "w", encoding="utf-8") as o:
    o.write("# generated by tools/train_2026_10_02c.py under docs/freezes/PROTOCOL_2026-10-02c (committed first); no target evaluated\n")
    o.write("#member\tclass\tname\tbare\tcentral\tsigma\tz_bare\tdelta=(m-b)/b\talpha_power\tdressing_used_by_leaf\n")
    for r in rows: o.write("\t".join(r) + "\n")
    for k, v in verdict.items(): o.write("verdict\t" + k + "\t" + json.dumps(v, sort_keys=True) + "\n")
for k, v in verdict.items(): print(k, v)
