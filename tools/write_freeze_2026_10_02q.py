#!/usr/bin/env python3
"""Write audit/FREEZE_2026-10-02q.{md,json,sha256}. Committed BEFORE the round-q solver changes, results and scorer exist."""
import hashlib, json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "audit")
F = {
 "freeze": "FREEZE_2026-10-02q", "date": "2026-10-03", "authority_pin": "AEB2AD (unchanged)", "hub_data_commit": "6f9c2560 (unchanged)",
 "Q-1 chiral quark soliton with a physical pion mass": {
  "pion mass": ("explicit chiral breaking by the meson term E_m = m_pi^2 F^2 Int d^3r (1 - cos theta) with m_pi = FSOT pi+- leaf and F = M sqrt(N_c)/(2 pi) (FSOT); "
                "massive DPP profile theta = 2 arctan[(r0^2/r^2)(1 + m_pi r) e^(-m_pi r)] (Yukawa tail)"),
  "self-consistent iteration": ("stationarity -sin theta (S - 4 pi m_pi^2 F^2) + cos theta P = 0 -> theta = atan2(-P, -(S - 4 pi m_pi^2 F^2)); linear mixing 0.2; "
                                "box-edge handling: for r > 0.75 D theta is replaced by the massive tail (1 + m_pi r) e^(-m_pi r)/r^2 matched at 0.75 D; at most 40 iterations; converged iff max|d theta| < 1e-3"),
  "primary": "self-consistent profile if converged with the valence level in (-M, M); otherwise the massive-DPP scan minimum (stated)",
  "observables": "as round p (cqsm_rot): g_A = g_A^(0) + g_A^(1), I, M_Delta - M_N = 3/(2I), mu_S, mu_V^(0) (sign as corrected in round p, -(N_c M_N/9)[...]), mu_V^(1), mu_p, mu_n; Omega^1 signs fixed to the literature signs at the sanity point",
  "binding": "E = N_c eps_val + E_sea + E_m vs N_c M at M = m_p/3",
  "numerics (time box)": "D = 10/M, k_max = 10 M, K <= 8 for every case (smaller than round p: stated; no separate convergence run); r0 M scanned on [0.6, 2.0] step 0.1; results written to JSON per case",
  "sanity (Christov et al. 1996 table 1, M = 420, m_pi = 140, F = 93)": "g_A in [1.1, 1.5], M_Delta - M_N in [200, 350], mu_p in [1.6, 2.6], mu_n in [-2.0, -1.0]",
  "validation": "PDG m_p/3, PDG m_pi+, M_PV from FLAG F_pi: g_A, mu_p, mu_n within 10 %, Delta-N within 15 %",
  "score": "g_A gate 2 % (downstream deferred to round r even if it agrees); Delta-N 15 %; mu_p, mu_n 2 %",
  "disclosure": "the round-p chiral-limit values (g_A 1.1755, mu_p 3.27, mu_n -2.51, sanity mu_V 5.44 vs 3.44) were seen; the pion mass is expected to lower mu_V and change g_A",
  "look_elsewhere": "2 profiles (primary scored)"},
 "counting": "Deuteron_mu not recomputed this round; totals change only if a record row is newly confirmed",
}
open(os.path.join(D, "FREEZE_2026-10-02q.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(F, indent=1, ensure_ascii=False) + "\n")
open(os.path.join(D, "FREEZE_2026-10-02q.md"), "w", encoding="utf-8", newline="\n").write("# FREEZE_2026-10-02q (committed before the round-q solver changes, results and scorer)\n\n```json\n" + json.dumps(F, indent=1, ensure_ascii=False) + "\n```\n")
with open(os.path.join(D, "FREEZE_2026-10-02q.sha256"), "w", newline="\n") as f:
    for n in ("FREEZE_2026-10-02q.json", "FREEZE_2026-10-02q.md"):
        f.write(hashlib.sha256(open(os.path.join(D, n), "rb").read()).hexdigest() + "  " + n + "\n")
print("written")
