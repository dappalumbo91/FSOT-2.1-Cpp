#!/usr/bin/env python3
"""IRONOUT-2: Tracer's §43.5vw validate bars, derived by GB under the principle Damian accepted in t1004s4215 (bars follow
from the inputs / the check's own construction; no Damian-named numbers). Audited by Tracer at 1f0192f: none tailored.

The record (out_vw.../validate_run.txt sha256 4c66f06d…, vw FOLD ce51de78 §3(b)) is frozen in Tracer's ledger and is NOT
edited. Each bar is derived here with no free number and without using the measured residual; the recorded value is
then checked against it (two-sided, |value| <= bar). (iii) is recomputed live. Exit status non-zero on any FAIL.

  (iii) a^2, a^3 printed vs analytic (input-precision bar): the CMS/BCK coefficients are printed to fixed decimals
        (4.583 - 0.3333 nf; 41.44 - 7.607 nf + 0.1775 nf^2); bar = half-unit-in-the-last-place bound
        sum_k 0.5*10^-d_k * nf^k, per order, per n_f (max at n_f = 6: a^2 8.0e-4, a^3 9.8e-3).
  (iv)  alpha_s continuity at m_c, m_b, m_t (probe-bias bars, one rule for all three thresholds): the frozen check's
        statistic is |a(t+e) - a(t-e)| - 1.01 * 2e |beta(a, n_f above)| (e = 1e-9). A continuous runner whose slope jumps
        at the n_f switch moves e(|beta_lo| + |beta_hi|) across the probe, so the statistic carries the probe bias
        P = e(|beta_lo| - 1.02 |beta_hi|) even with zero true jump. Bar = e |beta_lo - beta_hi| (the full slope jump);
        effective tolerance on the true jump = bar - P = 0.02 e |beta_hi| (1.98e-12 at m_c, 6.17e-13 at m_b, at m_t
        likewise); the offset-corrected true jump (statistic - P, live re-run of Tracer's runner) is ~1e-17.
        No round-off allowance is added: double round-off on alpha (< 1e-15) is far below every effective tolerance.
  (iv)  runner vs tip AlphaS (input-fixed grid bar): the tip AlphaS (tools/score_2026_10_02i.py AlphaS) runs down from M_Z
        on a grid of n = round(|ln m_tau^2 - ln M_Z^2| / 1e-3) steps (actual step 0.99999719e-3) and picks n_f at each step
        midpoint, so the step straddling m_b integrates the fraction f = min(frac x_b, 1 - frac x_b) of a step with the
        wrong n_f (x_b = grid position of m_b, fixed by the inputs: f = 0.085). Bar(mu) = f h |beta_4 - beta_5|(alpha_b)
        carried to mu by beta(alpha_mu)/beta(alpha_b), relative to alpha_mu, for mu below m_b, + h^2/8 |alpha''|/alpha
        (linear interpolation) at every mu; max over the validate's 8 scales (2, 3, 4, 5, 10, 50, 91, 150 GeV).
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
    fails = 0; out = []; bars = {}

    # (iii) live: analytic Larin-Vermaseren a^2, a^3 vs the printed coefficients
    a2 = lambda nf: 55 / 12 - nf / 3
    a3 = lambda nf: 13841 / 216 + 44 / 9 * Z3 - 55 / 2 * Z5 + nf * (-10339 / 1296 - 61 / 54 * Z3 + 5 / 3 * Z5) + nf**2 * 115 / 648
    p2 = lambda nf: 4.583 - 0.3333 * nf; p3 = lambda nf: 41.44 - 7.607 * nf + 0.1775 * nf**2
    u2 = lambda nf: 0.5e-3 + 0.5e-4 * nf; u3 = lambda nf: 0.5e-2 + 0.5e-3 * nf + 0.5e-4 * nf**2
    live = max(max(abs(a2(n) - p2(n)), abs(a3(n) - p3(n))) for n in range(3, 7))
    ok_iii = all(abs(a2(n) - p2(n)) <= u2(n) and abs(a3(n) - p3(n)) <= u3(n) for n in range(3, 7))
    bars["iii_a2_a3_vs_analytic"] = (max(max(u2(n), u3(n)) for n in range(3, 7)), ok_iii,
                                     f"input-precision bar; live max {live:.6g} (recorded {rows['iii_a2_a3_vs_analytic']['measured']})")

    # (iv) continuity: probe-bias bars, one rule at m_c, m_b, m_t
    e = 1e-9
    for th, nlo in (("m_c", 3), ("m_b", 4), ("m_t", 5)):
        a = inp[f"alpha_s_at_{th}"]; blo, bhi = abs(beta(a, nlo)), abs(beta(a, nlo + 1))
        P = e * (blo - 1.02 * bhi); bar = e * abs(beta(a, nlo) - beta(a, nlo + 1))
        live_stat = inp[f"iv_continuity_{th}_live_stat"]
        bars[f"iv_continuity_{th}"] = (bar, None, f"probe-bias bar e|beta_{nlo}-beta_{nlo+1}|; probe bias P {P:.6g}; effective tolerance on the true jump "
                                       f"{bar - P:.3g}; offset-corrected true jump (live statistic - P) {live_stat - P:+.2g}")

    # (iv) runner vs tip AlphaS: input-fixed tip grid
    MZ, mtau, mb, ab = inp["M_Z_GeV"], inp["m_tau_GeV"], inp["m_b_pole_GeV"], inp["alpha_s_at_m_b"]
    t0, tlo = math.log(MZ**2), math.log(mtau**2)
    n = max(1, int(round(abs(tlo - t0) / 1e-3))); h = abs(tlo - t0) / n
    tb = 2 * math.log(mb); xb = (t0 - tb) / h; fr = xb - math.floor(xb); f = min(fr, 1 - fr)
    worst, wmu = 0.0, None
    for mu in (2.0, 3.0, 4.0, 5.0, 10.0, 50.0, 91.0, 150.0):
        t = 2 * math.log(mu); below = t < tb; nf = 4 if below else 5
        am = run(ab, tb, t, nf)
        strad = f * h * abs(beta(ab, 4) - beta(ab, 5)) * abs(beta(am, 4) / beta(ab, 4)) if below else 0.0
        d2 = abs(beta(am, nf) * (beta(am * (1 + 1e-6), nf) - beta(am * (1 - 1e-6), nf)) / (2e-6 * am))
        b = (strad + h * h / 8 * d2) / am
        if b > worst: worst, wmu = b, mu
    bars["iv_runner_vs_tip_AlphaS"] = (worst, None, f"input-fixed grid: h {h:.8g}, m_b at grid x {xb:.3f}, straddle f {f:.4f}; max at mu {wmu} GeV")

    for k, (bar, ok_live, note) in bars.items():
        r = rows[k]; meas = float(r["measured"]); half = 0.5 * 10 ** (math.floor(math.log10(abs(meas))) - 5)  # record prints 6 s.f.
        ok = abs(meas) <= bar + half and (ok_live is None or ok_live)  # two-sided
        fails += not ok
        out.append(f"[{'PASS' if ok else 'FAIL'}] {k}: |measured| {abs(meas):.6g} vs bar {bar:.6g} (old bar {r['old_bar']}) {note}")
        if r["new_bar"] != "PLACEHOLDER" and abs(float(r["new_bar"]) / bar - 1) > 1e-6:
            fails += 1; out.append(f"[FAIL] {k}: reference new_bar {r['new_bar']} != derived {bar:.10g}")
    if "--bars" in sys.argv:
        for k, b in bars.items(): print(f"BAR\t{k}\t{b[0]:.10g}")
    print("\n".join(out)); print("VW VALIDATE (derived bars): " + ("no FAIL" if not fails else f"{fails} FAIL"))
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
