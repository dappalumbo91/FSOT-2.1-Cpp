#!/usr/bin/env python3
"""Round-ba scores under audit/FREEZE_2026-10-02ba (hashed before the run). Recomputes the split from the json.
  python tools/score_2026_10_02ba.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02ba.tsv
Does not open a record row. Does not select a mass."""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, nstr
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves(); R_ = Path(__file__).resolve().parents[1]
rows = []
def info(sec, name, inputs, v, cls="", note=""): rows.append([sec, name, inputs, nstr(mpf(v), 12), "-", "-", "-", "info", "-", cls, note])
def rec(sec, name, verdict, note): rows.append([sec, name, "-", "-", "-", "-", "-", verdict, "-", "-", note])
J = lambda f: json.loads((R_ / f).read_text(encoding="utf-8"))
def close(a, b):
    try: a, b = float(a), float(b)
    except (TypeError, ValueError): return False
    return abs(a - b) <= 1e-9 * max(1.0, abs(b))
mpM = X.kg_to_GeV(L["m_p_kg"]) * 1000
hbc = mpf("0.1973269804"); mpG = mpM / 1000
def fm2(Mr): return (hbc / mpG)**2 / (mpf(Mr)**2)
ag = J("audit/murun_2026-10-02ag_K14_D14_k12.json"); dpp = J("audit/rv_2026-10-02aq_A_j0.json")
s = "BA-1"; path = R_ / "audit/rv_2026-10-02ba_j0.json"; bad = []
if not path.exists():
    rec(s, "BA-1 radius", "valence lost", "no j=0 file; nothing rescored")
else:
    ba = J("audit/rv_2026-10-02ba_j0.json"); inp = ag["inputs"]; M = 1.0 / 3.0
    if ba.get("freeze") != "FREEZE_2026-10-02ba" or ba.get("solver") != "none": bad.append("manifest")
    if ba.get("K") != 14 or ba.get("j") != 0 or ba.get("nq") != 1500: bad.append("basis")
    if not close(ba.get("D"), 14.0) or not close(ba.get("kmax"), 12.0): bad.append("box")
    if abs(float(ba.get("M_over_mp", 0)) - M) > 1e-15: bad.append("M")
    if not close(ba.get("mpi_over_M"), float(inp["mpi_over_mp"]) / M): bad.append("mpi")
    if not close(ba.get("F_over_M"), float(inp["F_over_mp"]) / M): bad.append("F")
    if not close(ba.get("Mpv_over_M"), inp["Mpv_over_M"]): bad.append("Mpv")
    if not close(ba.get("x_DPP"), ag["x_DPP"]): bad.append("x_DPP")
    if not close(dpp["I1"], 4.197466935) or not close(dpp["Ir2"], 20.00824379): bad.append("DPP file")
    parts = ("I_val", "I_sea", "I_pv")
    if any(k not in ba or len(ba[k]) != 2 for k in parts): bad.append("split")
    else:
        i1 = sum(float(ba[k][0]) for k in parts); ir2 = sum(float(ba[k][1]) for k in parts)
        if not close(ba.get("I1"), i1) or not close(ba.get("Ir2"), ir2): bad.append("totals")
    if bad:
        rec(s, "BA-1 manifest", "refused", "the json does not match FREEZE_2026-10-02ba: " + ", ".join(bad))
    else:
        Mr0 = mpf(inp["M_over_mp"]); Mr = mpf(M)
        def piece(e, Mr_):
            I1 = mpf(e["I1"]); Ir2 = mpf(e["Ir2"]); v1 = mpf(e["I_val"][0]); v2 = mpf(e["I_val"][1])
            s1_ = mpf(e["I_sea"][0]) + mpf(e["I_pv"][0]); s2 = mpf(e["I_sea"][1]) + mpf(e["I_pv"][1])
            return I1, Ir2, Ir2 / I1 * fm2(Mr_), v2 / v1 * fm2(Mr_), s1_ / I1, s2 / s1_ * fm2(Mr_), -mpf(e["I_pv"][1]) / mpf(e["I_sea"][1])
        I1, Ir2, r_new, rval, share, rsea, pvc = piece(ba, Mr)
        _, _, r_old, rval0, share0, rsea0, pvc0 = piece(dpp, Mr0)
        r_fixed = (mpf(dpp["Ir2"]) / mpf(dpp["I1"])) * fm2(Mr)
        info(s, "BA-1 M/m_p", "IEEE 1/3; F/M recorded and unused by the DPP sums", Mr, "diagnostic",
             "mpi/M %s; F/M %s; Mpv/M %s; x_DPP %s; solver none; %s s" % (nstr(mpf(ba["mpi_over_M"]), 8), nstr(mpf(ba["F_over_M"]), 8), nstr(mpf(ba["Mpv_over_M"]), 8), nstr(mpf(ba["x_DPP"]), 10), ba["seconds"]))
        info(s, "BA-1 j=0 r_V^2 (fm^2)", "I[r^2]/I[1] on the DPP at M/m_p = 1/3, box j=0", r_new, "diagnostic",
             "r M^2 %s; I[1] %s; max |imag| %s; compared with 0.82236(201) as information only" % (nstr(Ir2 / I1, 8), nstr(I1, 10), ba["max_imag"]))
        info(s, "BA-1 j=0 sea+PV share of I[1]", "sea plus PV, box j=0", share, "diagnostic",
             "sea+PV-only r^2 %s fm^2; valence-only r^2 %s fm^2; PV cancels %s %% of the bare sea I[r^2]" % (nstr(rsea, 6), nstr(rval, 6), nstr(pvc * 100, 4)))
        info(s, "DPP j=0 r_V^2 at M/m_p = 0.4581682005 (fm^2)", "committed audit/rv_2026-10-02aq_A_j0.json", r_old, "diagnostic",
             "sea+PV share of I[1] %s; sea+PV-only r^2 %s fm^2; valence-only r^2 %s fm^2; PV cancels %s %%" % (nstr(share0, 5), nstr(rsea0, 6), nstr(rval0, 6), nstr(pvc0 * 100, 4)))
        info(s, "BA-1 fixed-shape rescaling of the committed j=0 ratio onto M/m_p = 1/3 (fm^2)", "same I[r^2]/I[1], fm factor only", r_fixed, "diagnostic",
             "shape ratio (new r M^2)/(committed r M^2) = %s; the unit factor alone is not the sea check" % nstr((Ir2 / I1) / (mpf(dpp["Ir2"]) / mpf(dpp["I1"])), 6))
        rec(s, "BA-1 selection", "information", "neither mass is selected by closeness to 0.82236; M/m_p = 0.4581682005 stays a diagnostic (FREEZE_2026-10-02ab); round o / H-40 found M = m_p/3 unbound at E = 3.41 M on a different basis and that mass is not adopted; nothing installed")
rec("GATE", "record rows of the 91", "unchanged", "z-only; 91/91 since FREEZE_2026-10-02ay")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02ba.py under audit/FREEZE_2026-10-02ba (hashed before the run)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
