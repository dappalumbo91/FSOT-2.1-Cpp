#!/usr/bin/env python3
"""Build audit/heavy_2026-10-02p.json from the logged heavy run (scratch_p/heavy_run1_killed.log): the run printed every DPP observable dict
and every self-consistent iteration (it, E, eps_val, max dtheta) at full repr precision but was stopped by the time limit before writing its JSON.
None of the self-consistent iterations converged (60 iterations each), so the frozen primary profile is DPP in every case."""
import ast, json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import fsot02d as X
hub, F = X.setup(sys.argv[1]); L = X.leaves(); mp = float(X.kg_to_GeV(L["m_p_kg"]) * 1000); mpP = 938.27208943; Fpi = 130.2 / math.sqrt(2)
meta = {"P1_sanity_M420_F93": (420.0, math.exp(0.5 * 4 * math.pi**2 * 93.0**2 / (3 * 420.0**2)), mpP, 12), "P1_FSOT": (mp / 3, math.sqrt(math.e), mp, 12),
        "P1_validation": (mpP / 3, math.exp(0.5 * 4 * math.pi**2 * Fpi**2 / (3 * (mpP / 3)**2)), mpP, 12), "P1_FSOT_conv": (mp / 3, math.sqrt(math.e), mp, 14)}
out = {"generated_by": "tools/heavy_2026_10_02p.py (values transcribed by tools/heavy_log_to_json_2026_10_02p.py from the run log)", "freeze": "FREEZE_2026-10-02p", "inputs": {"m_p": mp}}
for line in open(sys.argv[2], encoding="utf-8"):
    f = line.split()
    if len(f) > 2 and f[1] == "DPP":
        M, Mpv, MN, K = meta[f[0]]
        out[f[0]] = {"M_MeV": M, "Mpv_over_M": Mpv, "M_N_MeV": MN, "D": float(K), "kmax": float(K), "Kmax": K, "DPP": ast.literal_eval(line[line.index("{"):]), "SC_converged": False, "SC_history": []}
    elif len(f) > 9 and f[1] == "sc" and f[0] in out:
        out[f[0]]["SC_history"].append([int(f[2]), float(f[4]), float(f[6]), float(f[8])])
def rnd(o):
    if isinstance(o, dict): return {k: rnd(v) for k, v in o.items()}
    if isinstance(o, list): return [rnd(v) for v in o]
    if isinstance(o, float): return float("%.10g" % o)
    return o
Path(sys.argv[3]).write_text(json.dumps(rnd(out), indent=1) + "\n", encoding="utf-8")
print({k: (len(v["SC_history"]) if isinstance(v, dict) and "SC_history" in v else None) for k, v in out.items()})
