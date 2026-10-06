#!/usr/bin/env python3
"""Round-ar scores under audit/FREEZE_2026-10-02ar (hashed before the run). Recomputes the move and any z from the json; does not trust a verdict string.
  python tools/score_2026_10_02ar.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02ar.tsv
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, sqrt, fabs, nstr
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); L = X.leaves(); R_ = Path(__file__).resolve().parents[1]
rows = []
def emitz(sec, name, inputs, v, c, s, th=0, cls="", note=""):
    v, c, s, th = mpf(v), mpf(c), mpf(s), mpf(th); sig = sqrt(s**2 + th**2); z = fabs(v - c) / sig
    rows.append([sec, name, inputs, nstr(v, 12), nstr(c, 10), nstr(sig, 4), nstr(z, 5), "agrees" if z <= 1 else "miss", nstr((v - c) / c * 100, 5) + " %", cls, note]); return z
def info(sec, name, inputs, v, cls="", note=""): rows.append([sec, name, inputs, nstr(mpf(v), 12), "-", "-", "-", "info", "-", cls, note])
def rec(sec, name, verdict, note): rows.append([sec, name, "-", "-", "-", "-", "-", verdict, "-", "-", note])
J = lambda f: json.loads((R_ / f).read_text(encoding="utf-8"))
rnd = lambda v: float("%.10g" % float(v))
def close(a, b):
    try: a, b = float(a), float(b)
    except (TypeError, ValueError): return False
    return abs(a - b) <= 1e-9 * max(1.0, abs(b))
mpM = X.kg_to_GeV(L["m_p_kg"]) * 1000
hbc = mpf("0.1973269804"); mpG = mpM / 1000
def fm2(Mr): return (hbc / mpG)**2 / (mpf(Mr)**2)
man = J("audit/scprofile_2026-10-02ar.json"); ag = J("audit/murun_2026-10-02ag_K14_D14_k12.json"); dpp = J("audit/rv_2026-10-02aq_A_j0.json")
s = "AR-1"
bad = []
b = man.get("basis") or {}
expect = {"K": 14, "D": 14.0, "kmax": 12.0, "nq": 1500, "mix": 0.2, "tol": 0.001, "itmax": 40, "Nc": 3}
for k, v in expect.items():
    if not close(b.get(k), v): bad.append("basis " + k)
if man.get("freeze") != "FREEZE_2026-10-02ar" or man.get("complete") is not True: bad.append("manifest")
inp = ag["inputs"]
if rnd(man.get("x_DPP")) != rnd(ag["x_DPP"]): bad.append("x_DPP")
if rnd(dpp["I1"]) != rnd("4.197466935") or rnd(dpp["Ir2"]) != rnd("20.00824379"): bad.append("DPP file")
a1 = man.get("AR-1")
if not a1: bad.append("AR-1 missing")
else:
    if not close(a1["M_over_mp"], inp["M_over_mp"]) or not close(a1["F_over_M"], inp["F_over_M"]): bad.append("AR-1 mass")
    if not close(a1["mpi_over_M"], float(inp["mpi_over_mp"]) / float(inp["M_over_mp"])): bad.append("AR-1 mpi")
    if not close(a1["Mpv_over_M"], inp["Mpv_over_M"]): bad.append("AR-1 Mpv")
    if not close(a1.get("mix"), 0.2) or not close(a1.get("tol"), 0.001) or a1.get("itmax") != 40 or a1.get("Nc") != 3: bad.append("AR-1 solver")
    if a1.get("K") != 14 or not close(a1.get("D"), 14.0) or not close(a1.get("kmax"), 12.0) or a1.get("nq") != 1500: bad.append("AR-1 basis")
def state(block):
    h = block.get("history") or []
    if not h or h[-1][2] is None: return "valence lost"
    d = h[-1][3]
    flag = bool(block.get("converged"))
    under = d is not None and float(d) < 1e-3
    if flag and under: return "converged"
    if flag != under: return "inconsistent"
    return "not converged"
if bad:
    rec(s, "AR-1 manifest", "refused", "the json does not match FREEZE_2026-10-02ar: " + ", ".join(bad))
    rec("GATE", "record rows of the 91", "unchanged", "z-only; 88/91 since owner record commit b99fc29")
else:
    st = state(a1); last = a1["history"][-1]
    info(s, "AR-1 solver", "self_consistent_m mix 0.2 tol 1e-3 itmax 40 Nc 3", len(a1["history"]), "diagnostic",
         "state %s; last E/M %s; ev %s; dtheta %s; %s s" % (st, last[1], last[2], last[3], a1["seconds"]))
    gap_path = "audit/rv_2026-10-02ar_gap_j0.json"
    gap = J(gap_path) if (R_ / gap_path).exists() else None
    r_dpp = mpf(dpp["Ir2"]) / mpf(dpp["I1"])
    def sea_note(e):
        I1 = mpf(e["I1"]); Ir2 = mpf(e["Ir2"]); sv1 = mpf(e["I_sea"][0]) + mpf(e["I_pv"][0]); sv2 = mpf(e["I_sea"][1]) + mpf(e["I_pv"][1])
        return I1, Ir2, sv1 / I1, sv2 / sv1
    if st == "valence lost" or gap is None or "I1" not in (gap or {}):
        rec(s, "AR-1 radius", "information" if st != "valence lost" else "valence lost", "no usable j=0 split; AR-2 not run; nothing rescored")
    else:
        I1, Ir2, share, rsea = sea_note(gap); r_sc = Ir2 / I1; move = fabs(r_sc - r_dpp) / r_dpp; Mr = mpf(a1["M_over_mp"])
        info(s, "AR-1 j=0 r_V^2 (fm^2)", "I[r^2]/I[1] on the solved profile, box j=0", r_sc * fm2(Mr), "diagnostic",
             "r M^2 %s; DPP r M^2 %s; move %s %%" % (nstr(r_sc, 8), nstr(r_dpp, 8), nstr(move * 100, 4)))
        info(s, "AR-1 j=0 sea+PV share of I[1]", "sea plus PV, box j=0", share, "diagnostic", "sea+PV-only r^2 %s fm^2; max |imag| %s" % (nstr(rsea * fm2(Mr), 6), gap["max_imag"]))
        if st == "inconsistent":
            rec(s, "AR-1 branch", "refused", "converged flag and last dtheta disagree; AR-2 is not judged; nothing rescored")
        elif st != "converged":
            rec(s, "AR-1 branch", "not converged", "j=0 radius is information; the 2% rule is not applied; AR-2 not run; nothing rescored")
        elif move <= mpf("0.02"):
            rec(s, "AR-1 branch", "stable", "scoring-box radius stable under self-consistency (move %s %% <= 2); no further boxes; no new 0.82236 validation; nothing rescored" % nstr(move * 100, 4))
        else:
            boxes = []
            missing = []
            for j in range(4):
                p = "audit/rv_2026-10-02ar_gap_j%d.json" % j
                if not (R_ / p).exists(): missing.append(j)
                else: boxes.append(J(p))
            if missing or any("I1" not in e for e in boxes):
                rec(s, "AR-1 branch", "incomplete", "move %s %% > 2 but boxes %s are missing; not a validation; nothing rescored" % (nstr(move * 100, 4), missing))
            else:
                def avg(v): return sum(v) / len(v)
                P = {k: [avg([mpf(e[k][i]) for e in boxes]) for i in range(2)] for k in ("I_val", "I_sea", "I_pv")}
                I1a = sum(P[k][0] for k in P); Ir2a = sum(P[k][1] for k in P); r2 = Ir2a / I1a
                spreads = [mpf(e["Ir2"]) / mpf(e["I1"]) for e in boxes]
                info(s, "AR-1 4-box r_V^2 (fm^2)", "<I[r^2]>/<I[1]>, boxes j=0..3", r2 * fm2(Mr), "FSOT · intermediate", "r M^2 %s; box spread %s %%" % (nstr(r2, 8), nstr((max(spreads) - min(spreads)) / r2 * 100, 4)))
                r2c = (mpf("0.84075")**2 + mpf("0.1155")) * (mpG / hbc)**2
                r2s = sqrt((2 * mpf("0.84075") * mpf("0.00064"))**2 + mpf("0.0017")**2) * (mpG / hbc)**2
                z = emitz(s, "AR-1 r_V^2 m_p^2, 4-box average (validation)", "FSOT soliton, self-consistent profile", r2 / Mr**2, r2c, r2s, 0, "validation (PDG r_p, <r_n^2>)",
                          "r_V^2 %s fm^2 vs 0.82236(201); PDG sigma only; move %s %%" % (nstr(r2 * fm2(Mr), 6), nstr(move * 100, 4)))
                word = "numerical at one level" if z <= 1 else "miss"
                rec(s, "AR-1 validation branch", word, "z %s. The round-ap chain is not carried. Delta alpha_had, G_F, Gamma_Z/M_Z and the 91 are not rescored. A passing radius needs its own later chain freeze" % nstr(z, 4))
        if st == "converged":
            a2 = man.get("AR-2")
            if not a2: rec("AR-2", "AR-2 sea scaling", "missing", "AR-1 converged but AR-2 is absent; nothing rescored")
            else:
                M3 = mpf(1) / 3
                bad2 = a2.get("M_over_mp_exact") != "1/3" or fabs(mpf(a2["M_over_mp"]) - M3) > mpf("1e-12")
                if not close(a2["F_over_M"], float(inp["F_over_mp"]) / (1.0 / 3.0)) or not close(a2["mpi_over_M"], float(inp["mpi_over_mp"]) / (1.0 / 3.0)): bad2 = True
                if not close(a2.get("x_DPP"), a1.get("x_DPP")) or not close(a2.get("mix"), 0.2) or a2.get("itmax") != 40: bad2 = True
                st2 = state(a2); last2 = a2["history"][-1]
                info("AR-2", "AR-2 solver at M/m_p = 1/3", "same basis and solver; x_DPP not re-fit", len(a2["history"]), "diagnostic",
                     "state %s; last E/M %s; ev %s; dtheta %s; %s s. H-40 on a different basis: unbound, E = 3.41 M; not adopted" % (st2, last2[1], last2[2], last2[3], a2["seconds"]))
                sp = "audit/rv_2026-10-02ar_sigma_j0.json"
                sig = J(sp) if (R_ / sp).exists() else None
                if bad2:
                    rec("AR-2", "AR-2 inputs", "refused", "AR-2 json does not match the frozen M/m_p = 1/3 setup; nothing rescored")
                elif sig is None or "I1" not in sig:
                    rec("AR-2", "AR-2 radius", "information" if st2 != "valence lost" else "valence lost", "no usable j=0 split; mass not adopted; nothing rescored")
                else:
                    I1s, Ir2s, share2, rsea2 = sea_note(sig); Mr2 = mpf(a2["M_over_mp"])
                    info("AR-2", "AR-2 j=0 sea+PV share of I[1]", "M/m_p = 1/3, box j=0", share2, "diagnostic",
                         "sea+PV-only r^2 %s fm^2; AR-1 sea+PV share %s; neither mass is selected by closeness to 0.82236" % (nstr(rsea2 * fm2(Mr2), 6), nstr(share, 6)))
                    info("AR-2", "AR-2 j=0 r_V^2 (fm^2)", "information only", (Ir2s / I1s) * fm2(Mr2), "diagnostic",
                         "M/m_p 0.4581682005 stays a diagnostic (FREEZE ab). H-40 E = 3.41 M is reported and not adopted")
                    rec("AR-2", "AR-2 mass choice", "not adopted", "neither mass is selected; the sigma-model mass is not installed")
if not any(r_[0] == "GATE" for r_ in rows):
    rec("GATE", "record rows of the 91", "unchanged", "z-only; 88/91 since owner record commit b99fc29")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02ar.py under audit/FREEZE_2026-10-02ar (hashed before the run)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
