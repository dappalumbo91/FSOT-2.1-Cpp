#!/usr/bin/env python3
"""Round-aa (FREEZE_2026-10-02aa, AA-1): M/m_p from the DP gap equation with the FSOT condensate pin read in proton units.
The gap equation is scale-free, so M/m_p = [M0/n^(1/4)]_(rho = R/3) x (n/m_p^4)^(1/4). Writes audit/gap_2026-10-02aa.json (numpy/scipy)."""
import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gap_2026_10_02x as G
import fsot02d as X
ap = __import__("argparse").ArgumentParser(); ap.add_argument("--hub", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); P = X.pins() if hasattr(X, "pins") else None
P = X.pins(); L = X.leaves()
G2 = float(P["wave9|Gluon_condensate"])                       # <(alpha_s/pi)G^2>/m_p^4 (pure number, AA-1 reading)
n4 = (G2 / 8) ** 0.25                                         # n^(1/4)/m_p
k = G.M0_of(1000.0**4, 1 / 3000.0) / 1000.0                   # M0/n^(1/4) at rho = R/3 (scale-free)
mp = float(X.kg_to_GeV(L["m_p_kg"]) * 1000)
out = {"generated_by": "tools/gap_2026_10_02aa.py", "freeze": "FREEZE_2026-10-02aa", "G2_over_mp4": G2, "n_quarter_over_mp": float("%.12g" % n4),
       "M0_over_n_quarter": float("%.12g" % k), "M_over_mp": float("%.12g" % (k * n4)), "M_MeV_byproduct": float("%.12g" % (k * n4 * mp)),
       "round_y_M_over_mp": float("%.12g" % (346.066684753 / mp))}
Path(__file__).resolve().parents[1].joinpath("audit/gap_2026-10-02aa.json").write_text(json.dumps(out, indent=1) + "\n")
print(out)
