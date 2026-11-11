#!/usr/bin/env python3
"""IRONOUT-2: the four vw validate bars, re-set to the precision of their inputs (Damian accepted, t1004s4215).

Tracer's §43.5vw validate record (out_vw.../validate_run.txt sha256 4c66f06d…, vw FOLD ce51de78 §3(b)) has
4 FAILs that are bar mis-specifications. The record itself is frozen in Tracer's ledger and is NOT edited.
This tool derives each corrected bar from the precision of the check's own inputs (stdlib only, no free
number), checks the recorded measured value against it, and re-computes the one check that needs no ledger
code ((iii), exact) live. It prints PASS/FAIL per row and exits non-zero on any FAIL.

  (iii) a^2, a^3 printed vs analytic: the CMS/BCK coefficients are printed to fixed decimals
        (4.583 - 0.3333 nf; 41.44 - 7.607 nf + 0.1775 nf^2), so the bar is the half-unit-in-the-last-place
        bound sum_k 0.5*10^-d_k * nf^k, per order, per n_f (max at n_f = 6: a^2 8.0e-4, a^3 9.8e-3).
  (iv)  alpha_s continuity at m_c, m_b: alpha_s is continuous but its slope jumps (n_f switch). The check
        probes t_th +- e (e = 1e-9) and subtracts 1.01 * 2e |beta(alpha, n_f above)|, so a perfectly
        continuous runner still leaves e * (|beta_{n_f-1}| - 1.01 |beta_{n_f}|) ~ e * |beta_{n_f-1} - beta_{n_f}|.
        Bar = e * |beta(alpha_th, n_f-1) - beta(alpha_th, n_f)| + 64 eps alpha_th (double round-off).
  (iv)  runner vs tip AlphaS: the tip AlphaS (tools/score_2026_10_02i.py AlphaS, h = 1e-3 in ln mu^2) picks
        n_f at each RK step midpoint and linearly interpolates its grid. Its own resolution at mu is the
        straddling step at the threshold crossed between M_Z and mu, (h/2)|beta_{n_f} - beta_{n_f+1}| at
        alpha_th, carried to mu by beta(alpha_mu)/beta(alpha_th), plus h^2/8 |alpha''| from interpolation,
        relative to alpha_mu. Bar = max over the validate's mu in (m_tau, m_b) of that.
"""
import math, sys, os, csv

Z3 = 1.2020569031595942853997
Z5 = 1.0369277551433699263313

def beta(a, nf):  # four-loop MS-bar d alpha / d ln mu^2 (PDG 2024 eq.(9.4)); identical to tip / vw beta()
    b0 = (33 - 2 * nf) / (12 * math.pi); b1 = (153 - 19 * nf) / (24 * math.pi**2)
    b2 = (2857 - 5033 / 9 * nf + 325 / 27 * nf**2) / (128 * math.pi**3)
    b3 = ((149753 / 6 + 3564 * Z3) - (1078361 / 162 + 6508 / 27 * Z3) * nf + (50065 / 162 + 6472 / 81 * Z3) * nf**2 + 1093 / 729 * nf**3) / (256 * math.pi**4)
    return -(b0 * a**2 + b1 * a**3 + b2 * a**4 + b3 * a**5)

def run(a, t1, t2, nf, h=1e-4):
    n = max(1, int(math.ceil(abs(t2 - t1) / h))); dt = (t2 - t1) / n
    for _ in range(n):
        k1 = beta(a, nf); k2 = beta(a + .5 * dt * k1, nf); k3 = beta(a + .5 * dt * k2, nf); k4 = beta(a + dt * k3, nf)
        a += dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    return a

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ref = os.path.join(here, "..", "reference", "vw_validate_bars.tsv")
    rows = {r["check"]: r for r in csv.DictReader((l for l in open(ref, encoding="utf-8") if not l.startswith("#")), delimiter="\t")}
    inp = {k: float(v["measured"]) for k, v in rows.items() if v["kind"] == "input"}
    eps = 2.0**-52; fails = 0; out = []

    # (iii) live, exact in double: analytic Larin-Vermaseren a^2, a^3 vs the printed coefficients
    a2 = lambda nf: 55 / 12 - nf / 3
    a3 = lambda nf: 13841 / 216 + 44 / 9 * Z3 - 55 / 2 * Z5 + nf * (-10339 / 1296 - 61 / 54 * Z3 + 5 / 3 * Z5) + nf**2 * 115 / 648
    p2 = lambda nf: 4.583 - 0.3333 * nf; p3 = lambda nf: 41.44 - 7.607 * nf + 0.1775 * nf**2
    u2 = lambda nf: 0.5e-3 + 0.5e-4 * nf; u3 = lambda nf: 0.5e-2 + 0.5e-3 * nf + 0.5e-4 * nf**2
    live = max(max(abs(a2(n) - p2(n)), abs(a3(n) - p3(n))) for n in range(3, 7))
    ok_iii = all(abs(a2(n) - p2(n)) <= u2(n) and abs(a3(n) - p3(n)) <= u3(n) for n in range(3, 7))
    bar_iii = max(max(u2(n), u3(n)) for n in range(3, 7))
    bars = {"iii_a2_a3_vs_analytic": (bar_iii, ok_iii, f"live max {live:.6g} (recorded {rows['iii_a2_a3_vs_analytic']['measured']}); per order/n_f half-ULP of print")}

    # (iv) continuity at m_c, m_b
    e = 1e-9
    for key, a_th, nlo in (("iv_continuity_m_c", inp["alpha_s_at_m_c"], 3), ("iv_continuity_m_b", inp["alpha_s_at_m_b"], 4)):
        b = e * abs(beta(a_th, nlo) - beta(a_th, nlo + 1)) + 64 * eps * a_th
        bars[key] = (b, None, f"e|beta_{nlo}-beta_{nlo+1}| at alpha_s {a_th}")

    # (iv) runner vs tip AlphaS, mu in the validate list with m_tau < mu < m_b (b threshold crossed from M_Z)
    h = 1e-3; mb = inp["m_b_pole_GeV"]; ab = inp["alpha_s_at_m_b"]; tb = 2 * math.log(mb)
    worst = 0.0
    for mu in (2.0, 3.0, 4.0):
        t = 2 * math.log(mu); am = run(ab, tb, t, 4)
        strad = 0.5 * h * abs(beta(ab, 4) - beta(ab, 5)) * abs(beta(am, 4) / beta(ab, 4))
        db = beta(am, 4); d2 = abs(db * (beta(am * (1 + 1e-6), 4) - beta(am * (1 - 1e-6), 4)) / (2e-6 * am))
        worst = max(worst, (strad + h * h / 8 * d2) / am)
    bars["iv_runner_vs_tip_AlphaS"] = (worst, None, f"(h/2)|beta_4-beta_5| at m_b carried to mu in (m_tau,m_b) + h^2/8|alpha''|, h={h}")

    for k, (bar, ok_live, note) in bars.items():
        r = rows[k]; meas = float(r["measured"]); ok = meas <= bar and (ok_live is None or ok_live)
        fails += not ok
        out.append(f"[{'PASS' if ok else 'FAIL'}] {k}: measured {meas:.6g} vs precision bar {bar:.3g} (old bar {r['old_bar']}; {r['status']}) {note}")
        if r["new_bar"] != "PLACEHOLDER" and abs(float(r["new_bar"]) / bar - 1) > 1e-3:
            fails += 1; out.append(f"[FAIL] {k}: reference new_bar {r['new_bar']} != derived {bar:.6g}")
    [print(f"BAR\t{k}\t{b[0]:.6g}") for k, b in bars.items()] if "--bars" in sys.argv else None
    print("\n".join(out)); print("VW VALIDATE (accepted bars): " + ("no FAIL" if not fails else f"{fails} FAIL"))
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
