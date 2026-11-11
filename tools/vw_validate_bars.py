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
  (iv)  alpha_s continuity at m_c, m_b (re-derived 2026-11-11 after Tracer flagged the first bars as tailored): alpha_s is
        continuous but its slope jumps at the n_f switch. The check's statistic |a(t+e) - a(t-e)| - 1.01*2e|beta(a, n_f above)|
        (e = 1e-9) therefore has the exact a-priori value P = e*(|beta(a, n_f-1)| - 1.02*|beta(a, n_f)|) for a perfectly
        continuous runner. The continuity DEFECT is statistic - P, and its honest bound is double round-off in the two short
        RK4 legs from the shared grid node: 8 ulp(alpha_th). Bar on the statistic = P + 8 ulp(alpha); the full-precision
        statistics from a live re-run of Tracer's runner are banked and checked against it (defects -1.5e-17, +2.9e-18).
        (The first bars, e*|beta_{n_f-1} - beta_{n_f}|, were not fitted to the residuals but sat 19-21 % above them for no
        principled reason; they are withdrawn.)
  (iv)  runner vs tip AlphaS: the tip AlphaS (tools/score_2026_10_02i.py AlphaS, documented grid h = 1e-3 in ln mu^2) picks
        n_f at each RK step midpoint, so the step straddling m_b integrates a fraction f of h with the wrong n_f. Worst case
        (any threshold position) f = 1/2: bar = (h/2)|beta_4 - beta_5| at alpha(m_b), carried to mu by beta(alpha_mu)/beta(alpha_b),
        + h^2/8 |alpha''| (interpolation), relative to alpha_mu, max over the validate's mu in (m_tau, m_b). Not tailored: it does
        not use the residual. Cross-check: the actual straddle fraction of this grid (f = 0.08517, threshold at grid x 5963.915)
        predicts 2.041e-6 / 1.670e-6 / 1.483e-6 at mu = 2 / 3 / 4 GeV vs the measured 2.0265e-6 / 1.6607e-6 / 1.4773e-6,
        so the residual is fully explained (Tracer's "4.7e-15 at the tip's own nodes" holds only above m_b; below it the
        nodes differ by 2.17e-6).
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

    # (iv) continuity at m_c, m_b: bar = P + 8 ulp(alpha), P the statistic's a-priori slope-jump value
    e = 1e-9
    for key, a_th, nlo in (("iv_continuity_m_c", inp["alpha_s_at_m_c"], 3), ("iv_continuity_m_b", inp["alpha_s_at_m_b"], 4)):
        P = e * (abs(beta(a_th, nlo)) - 1.02 * abs(beta(a_th, nlo + 1)))
        u = 8 * eps * a_th
        live_stat = inp[key + "_live_stat"]
        ok = abs(live_stat - P) <= u
        bars[key] = (P + u, ok, f"P = e(|beta_{nlo}|-1.02|beta_{nlo+1}|) = {P:.10g}; live statistic {live_stat:.17g}, defect {live_stat - P:+.3g} vs 8 ulp {u:.3g}")

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
        r = rows[k]; meas = float(r["measured"]); half = 0.5 * 10 ** (math.floor(math.log10(meas)) - 5)  # record prints 6 s.f.
        ok = meas <= bar + half and (ok_live is None or ok_live)
        fails += not ok
        out.append(f"[{'PASS' if ok else 'FAIL'}] {k}: measured {meas:.6g} vs precision bar {bar:.3g} (old bar {r['old_bar']}; {r['status']}) {note}")
        if r["new_bar"] != "PLACEHOLDER" and abs(float(r["new_bar"]) / bar - 1) > 1e-3:
            fails += 1; out.append(f"[FAIL] {k}: reference new_bar {r['new_bar']} != derived {bar:.6g}")
    [print(f"BAR\t{k}\t{b[0]:.10g}") for k, b in bars.items()] if "--bars" in sys.argv else None
    print("\n".join(out)); print("VW VALIDATE (accepted bars): " + ("no FAIL" if not fails else f"{fails} FAIL"))
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
