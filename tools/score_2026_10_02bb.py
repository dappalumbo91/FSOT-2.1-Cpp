#!/usr/bin/env python3
"""Round-bb scores under audit/FREEZE_2026-10-02bb (hashed before the run). Checks the stored split.
  python tools/score_2026_10_02bb.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02bb.tsv
Does not open a record row. Does not rerun the spectrum."""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import fsot02d as X
from fsot02d import mpf, nstr
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves(); R_ = Path(__file__).resolve().parents[1]
rows = []
def info(sec, name, inputs, v, cls="", note=""): rows.append([sec, name, inputs, nstr(mpf(v), 12), "-", "-", "-", "info", "-", cls, note])
def rec(sec, name, verdict, note): rows.append([sec, name, "-", "-", "-", "-", "-", verdict, "-", "-", note])
J = lambda f: json.loads((R_ / f).read_text(encoding="utf-8"))
def close(a, b, rel=1e-9):
    try: a, b = float(a), float(b)
    except (TypeError, ValueError): return False
    return abs(a - b) <= rel * max(1.0, abs(b))
AR0 = 0.17211904981809267
R_AZ = 0.9063180381993936
NAMES = ("valence", "sea", "PV")
KEYS = ("S_val", "S_sea", "S_pv", "S", "P_val", "P_sea", "P_pv", "P", "c", "d", "theta", "new", "i", "r", "r_over_D", "abs_share_S", "abs_share_P")

def dominant(share):
    if share is None: return "null"
    return NAMES[max(range(3), key=lambda i: (float(share[i]), -i))]

def check_bin(bb, name, grid):
    bad = []
    b = bb.get(name)
    if not isinstance(b, dict) or any(k not in b for k in KEYS): return ["%s fields" % name]
    i = b["i"]
    if not isinstance(i, int) or i < 0 or i >= len(grid): return ["%s index" % name]
    if not close(b["r"], grid[i], 1e-12): bad.append("%s r" % name)
    if not close(b["r_over_D"], grid[i] / 14.0, 1e-12): bad.append("%s r/D" % name)
    if not close(b["d"], abs(float(b["new"]) - float(b["theta"])), 1e-12): bad.append("%s d" % name)
    if not close(b["S"], float(b["S_val"]) + float(b["S_sea"]) + float(b["S_pv"]), 1e-9): bad.append("%s S" % name)
    if not close(b["P"], float(b["P_val"]) + float(b["P_sea"]) + float(b["P_pv"]), 1e-9): bad.append("%s P" % name)
    if not close(b["c"], bb["c"], 1e-12): bad.append("%s c" % name)
    for key, parts in (("abs_share_S", ("S_val", "S_sea", "S_pv")), ("abs_share_P", ("P_val", "P_sea", "P_pv"))):
        den = sum(abs(float(b[p])) for p in parts)
        got = b[key]
        if den == 0.0:
            if got is not None: bad.append("%s share" % name)
        elif not isinstance(got, list) or len(got) != 3: bad.append("%s share" % name)
        else:
            for g, p in zip(got, parts):
                if not close(g, abs(float(b[p])) / den, 1e-9): bad.append("%s share" % name)
    return bad

s = "BB-1"; path = R_ / "audit/rv_2026-10-02bb.json"
if not path.exists():
    rec(s, "BB-1 force split", "refused", "no file; valence lost or the piece residual exceeded 1e-12; nothing rescored")
else:
    bb = J("audit/rv_2026-10-02bb.json"); ag = J("audit/murun_2026-10-02ag_K14_D14_k12.json"); inp = ag["inputs"]
    M = float(inp["M_over_mp"]); bad = []
    if bb.get("freeze") != "FREEZE_2026-10-02bb" or bb.get("solver") != "one step, no mix": bad.append("manifest")
    if bb.get("K") != 14 or bb.get("nq") != 1500 or bb.get("Nc") != 3: bad.append("basis")
    if not close(bb.get("D"), 14.0) or not close(bb.get("kmax"), 12.0): bad.append("box")
    if not close(bb.get("M_over_mp"), M, 1e-15): bad.append("M")
    if not close(bb.get("F_over_M"), inp["F_over_M"]): bad.append("F")
    if not close(bb.get("mpi_over_M"), float(inp["mpi_over_mp"]) / M): bad.append("mpi")
    if not close(bb.get("Mpv_over_M"), inp["Mpv_over_M"]): bad.append("Mpv")
    if not close(bb.get("x_DPP"), ag["x_DPP"]): bad.append("x_DPP")
    if not close(bb.get("step0_gap"), AR0, 1e-18) or not close(bb.get("r_az"), R_AZ, 1e-18): bad.append("labels")
    if float(bb.get("rel_residual_S", 1)) > 1e-12 or float(bb.get("rel_residual_P", 1)) > 1e-12: bad.append("residual")
    c_ref = 4 * np.pi * (float(inp["mpi_over_mp"]) / M) ** 2 * float(inp["F_over_M"]) ** 2
    if not close(bb.get("c"), c_ref, 1e-12): bad.append("c")
    x, _w = np.polynomial.legendre.leggauss(1500); grid = 0.5 * 14.0 * (x + 1)
    iaz = int(np.argmin(np.abs(grid - R_AZ)))
    bad += check_bin(bb, "max_bin", grid); bad += check_bin(bb, "az_bin", grid)
    if "max_bin" in bb and "az_bin" in bb and isinstance(bb["max_bin"], dict) and isinstance(bb["az_bin"], dict):
        if not close(bb.get("max_d"), bb["max_bin"].get("d"), 1e-12): bad.append("max d")
        if bb["az_bin"].get("i") != iaz: bad.append("az index")
    if bad:
        rec(s, "BB-1 manifest", "refused", "the json does not match FREEZE_2026-10-02bb: " + ", ".join(bad))
    else:
        mpG = X.kg_to_GeV(L["m_p_kg"]); hbc = mpf("0.1973269804")
        def fm(r): return mpf(r) * hbc / (mpG * mpf(M))
        gap = abs(float(bb["max_d"]) - AR0); matched = gap <= 1e-8
        mx, az = bb["max_bin"], bb["az_bin"]
        info(s, "BB-1 max |new-theta|", "one step on the edge-tailed diagnostic DPP; committed step 0 is 0.17211904981809267", bb["max_d"], "diagnostic",
             "absolute difference %s; valence %s; c %s; residual S %s; residual P %s; %s s" % (nstr(mpf(gap), 6), nstr(mpf(bb["valence"]), 12), nstr(mpf(bb["c"]), 8), nstr(mpf(bb["rel_residual_S"]), 3), nstr(mpf(bb["rel_residual_P"]), 3), bb["seconds"]))
        info(s, "BB-1 radius of the max bin (1/M)", "first index of the maximum", mx["r"], "diagnostic",
             "bin %s; r/D %s; %s fm; theta %s; new %s" % (mx["i"], nstr(mpf(mx["r_over_D"]), 6), nstr(fm(mx["r"]), 6), nstr(mpf(mx["theta"]), 8), nstr(mpf(mx["new"]), 8)))
        info(s, "BB-1 scalar density at the max bin", "valence, sea, PV, beside S - c", mx["S"] - mx["c"], "diagnostic",
             "S_val %s; S_sea %s; S_pv %s; S %s; largest |S| piece %s" % (nstr(mpf(mx["S_val"]), 6), nstr(mpf(mx["S_sea"]), 6), nstr(mpf(mx["S_pv"]), 6), nstr(mpf(mx["S"]), 6), dominant(mx["abs_share_S"])))
        info(s, "BB-1 pseudoscalar density at the max bin", "valence, sea, PV", mx["P"], "diagnostic",
             "P_val %s; P_sea %s; P_pv %s; largest |P| piece %s" % (nstr(mpf(mx["P_val"]), 6), nstr(mpf(mx["P_sea"]), 6), nstr(mpf(mx["P_pv"]), 6), dominant(mx["abs_share_P"])))
        info(s, "BB-1 labeled bin at the step-44 radius", "r = 0.9063180381993936, not a search", az["d"], "diagnostic",
             "bin %s; r %s; r/D %s; %s fm; |new-theta| %s; largest |S| %s; largest |P| %s" % (az["i"], nstr(mpf(az["r"]), 8), nstr(mpf(az["r_over_D"]), 6), nstr(fm(az["r"]), 6), nstr(mpf(az["d"]), 8), dominant(az["abs_share_S"]), dominant(az["abs_share_P"])))
        if matched:
            rec(s, "BB-1 force identity", "information", "the split reproduces the solver's first-step gap; nothing installed; M = m_p/3 stays off the record; no radius row")
        else:
            rec(s, "BB-1 force identity", "refused", "max |new-theta| is not the committed step-0 gap 0.17211904981809267 within 1e-8; the split is not the solver's force; the freeze is not edited")
rec("GATE", "record rows of the 91", "unchanged", "z-only; 91/91 since FREEZE_2026-10-02ay")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02bb.py under audit/FREEZE_2026-10-02bb (hashed before the run)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
