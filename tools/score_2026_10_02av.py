#!/usr/bin/env python3
"""Round-av scores under audit/FREEZE_2026-10-02av (hashed before the run). Recomputes the move and any z from the json.
  python tools/score_2026_10_02av.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02av.tsv
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
def close(a, b):
    try: a, b = float(a), float(b)
    except (TypeError, ValueError): return False
    return abs(a - b) <= 1e-9 * max(1.0, abs(b))
mpM = X.kg_to_GeV(L["m_p_kg"]) * 1000
hbc = mpf("0.1973269804"); mpG = mpM / 1000
def fm2(Mr): return (hbc / mpG)**2 / (mpf(Mr)**2)
man = J("audit/scprofile_2026-10-02av.json"); ag = J("audit/murun_2026-10-02ag_K14_D14_k12.json"); dpp = J("audit/rv_2026-10-02aq_A_j0.json")
s = "AV-1"; bad = []; b = man.get("basis") or {}
for k, v in {"K": 14, "D": 14.0, "kmax": 12.0, "nq": 1500, "mix": 0.2, "tol": 0.001, "itmax": 400, "Nc": 3}.items():
    if not close(b.get(k), v): bad.append("basis " + k)
if man.get("freeze") != "FREEZE_2026-10-02av" or man.get("complete") is not True: bad.append("manifest")
inp = ag["inputs"]
if not close(man.get("x_DPP"), ag["x_DPP"]): bad.append("x_DPP")
if not close(dpp["I1"], 4.197466935) or not close(dpp["Ir2"], 20.00824379): bad.append("DPP file")
a1 = man.get("AV-1")
if not a1: bad.append("AV-1 missing")
else:
    M = float(inp["M_over_mp"]); mpi = float(inp["mpi_over_mp"]) / M
    if not close(a1["M_over_mp"], M) or not close(a1["F_over_M"], inp["F_over_M"]) or not close(a1["mpi_over_M"], mpi): bad.append("AV-1 mass")
    if not close(a1.get("mix"), 0.2) or not close(a1.get("tol"), 0.001) or not close(a1.get("itmax"), 400): bad.append("AV-1 step")
    h = a1.get("history") or []
    if not h or len(h) > 400: bad.append("AV-1 length")
def state(block):
    h = block.get("history") or []
    if not h or h[-1][2] is None: return "valence lost"
    d = h[-1][3]; flag = bool(block.get("converged")); under = d is not None and float(d) < 1e-3
    if flag and under: return "converged"
    if flag != under: return "inconsistent"
    return "not converged"
def sea_note(e):
    I1 = mpf(e["I1"]); Ir2 = mpf(e["Ir2"]); sv1 = mpf(e["I_sea"][0]) + mpf(e["I_pv"][0]); sv2 = mpf(e["I_sea"][1]) + mpf(e["I_pv"][1])
    return I1, Ir2, sv1 / I1, sv2 / sv1
if bad:
    rec(s, "AV-1 manifest", "refused", "the json does not match FREEZE_2026-10-02av: " + ", ".join(bad))
else:
    st = state(a1); last = a1["history"][-1]; h = a1["history"]
    info(s, "AV-1 one call", "self_consistent_m mix 0.2, tol 1e-3, itmax 400, from the DPP", len(h), "diagnostic",
         "state %s; last E/M %s; ev %s; dtheta %s; %s s" % (st, last[1], last[2], last[3], a1["seconds"]))
    d0 = h[0][3]
    info(s, "AV-1 step 0 dtheta", "information next to round ar 0.17211904981809267; a difference does not stop the call", d0, "diagnostic",
         "absolute difference %s" % nstr(fabs(mpf(d0) - mpf("0.17211904981809267")), 6))
    if len(h) > 39 and h[39][3] is not None:
        info(s, "AV-1 step 39 dtheta", "information next to round ar 0.005631712767651509; a difference does not stop the call", h[39][3], "diagnostic",
             "absolute difference %s" % nstr(fabs(mpf(h[39][3]) - mpf("0.005631712767651509")), 6))
    else:
        rec(s, "AV-1 step 39", "information", "the call returned before step 39; round-ar step 39 stays 0.005631712767651509")
    gp = "audit/rv_2026-10-02av_gap_j0.json"; gap = J(gp) if (R_ / gp).exists() else None
    r_dpp = mpf(dpp["Ir2"]) / mpf(dpp["I1"]); share = None
    if st == "valence lost" or gap is None or "I1" not in gap:
        rec(s, "AV-1 radius", "valence lost" if st == "valence lost" else "information", "no usable j=0 split; AV-2 not run; nothing rescored")
    else:
        I1, Ir2, share, rsea = sea_note(gap); r_sc = Ir2 / I1; move = fabs(r_sc - r_dpp) / r_dpp; Mr = mpf(a1["M_over_mp"])
        info(s, "AV-1 j=0 r_V^2 (fm^2)", "I[r^2]/I[1] on the one-call profile, box j=0", r_sc * fm2(Mr), "diagnostic",
             "r M^2 %s; DPP r M^2 %s; move %s %%" % (nstr(r_sc, 8), nstr(r_dpp, 8), nstr(move * 100, 4)))
        info(s, "AV-1 j=0 sea+PV share of I[1]", "sea plus PV, box j=0", share, "diagnostic", "sea+PV-only r^2 %s fm^2; max |imag| %s" % (nstr(rsea * fm2(Mr), 6), gap["max_imag"]))
        if st == "inconsistent":
            rec(s, "AV-1 branch", "refused", "converged flag and last dtheta disagree; nothing rescored")
        elif st != "converged":
            rec(s, "AV-1 branch", "not converged", "j=0 radius is information; AV-2 not run; nothing rescored")
        elif move <= mpf("0.02"):
            rec(s, "AV-1 branch", "stable", "scoring-box radius stable under the one call (move %s %% <= 2); no further boxes; no new 0.82236 validation; nothing rescored" % nstr(move * 100, 4))
        else:
            boxes, missing = [], []
            for j in range(4):
                p = "audit/rv_2026-10-02av_gap_j%d.json" % j
                if not (R_ / p).exists(): missing.append(j)
                else: boxes.append(J(p))
            if missing or any("I1" not in e for e in boxes):
                rec(s, "AV-1 branch", "incomplete", "move %s %% > 2 but boxes %s are missing; nothing rescored" % (nstr(move * 100, 4), missing))
            else:
                def avg(v): return sum(v) / len(v)
                P = {k: [avg([mpf(e[k][i]) for e in boxes]) for i in range(2)] for k in ("I_val", "I_sea", "I_pv")}
                I1a = sum(P[k][0] for k in P); Ir2a = sum(P[k][1] for k in P); r2 = Ir2a / I1a
                info(s, "AV-1 4-box r_V^2 (fm^2)", "<I[r^2]>/<I[1]>, boxes j=0..3", r2 * fm2(Mr), "FSOT · intermediate", "r M^2 %s" % nstr(r2, 8))
                r2c = (mpf("0.84075")**2 + mpf("0.1155")) * (mpG / hbc)**2
                r2s = sqrt((2 * mpf("0.84075") * mpf("0.00064"))**2 + mpf("0.0017")**2) * (mpG / hbc)**2
                z = emitz(s, "AV-1 r_V^2 m_p^2, 4-box average (validation)", "FSOT soliton, one call", r2 / Mr**2, r2c, r2s, 0, "validation (PDG r_p, <r_n^2>)",
                          "r_V^2 %s fm^2 vs 0.82236(201); PDG sigma only; move %s %%" % (nstr(r2 * fm2(Mr), 6), nstr(move * 100, 4)))
                rec(s, "AV-1 validation branch", "numerical at one level" if z <= 1 else "miss", "z %s. The round-ap chain is not carried. The 91 are not rescored." % nstr(z, 4))
        if st == "converged":
            a2 = man.get("AV-2"); M3 = mpf(1) / 3
            if not a2: rec("AV-2", "AV-2 sea scaling", "missing", "AV-1 converged but AV-2 is absent; nothing rescored")
            else:
                st2 = state(a2); last2 = a2["history"][-1]
                bad2 = a2.get("M_over_mp_exact") != "1/3" or fabs(mpf(a2["M_over_mp"]) - M3) > mpf("1e-12") or not close(a2.get("mix"), 0.2) or not close(a2.get("itmax"), 400)
                if not close(a2["F_over_M"], float(inp["F_over_mp"]) / (1.0 / 3.0)) or not close(a2["mpi_over_M"], float(inp["mpi_over_mp"]) / (1.0 / 3.0)): bad2 = True
                if not a2.get("history") or len(a2["history"]) > 400: bad2 = True
                info("AV-2", "AV-2 one call at M/m_p = 1/3", "same x_DPP, mix 0.2, itmax 400", len(a2["history"]), "diagnostic",
                     "state %s; last E/M %s; ev %s; dtheta %s; %s s. H-40 on a different basis: unbound, E = 3.41 M; not adopted" % (st2, last2[1], last2[2], last2[3], a2["seconds"]))
                sp = "audit/rv_2026-10-02av_sigma_j0.json"; sig = J(sp) if (R_ / sp).exists() else None
                if bad2: rec("AV-2", "AV-2 inputs", "refused", "AV-2 json does not match M/m_p = 1/3 at mix 0.2, itmax 400; nothing rescored")
                elif sig is None or "I1" not in sig: rec("AV-2", "AV-2 radius", "information" if st2 != "valence lost" else "valence lost", "no usable j=0 split; mass not adopted")
                else:
                    I1s, Ir2s, share2, rsea2 = sea_note(sig)
                    info("AV-2", "AV-2 j=0 sea+PV share of I[1]", "M/m_p = 1/3, box j=0", share2, "diagnostic",
                         "sea+PV-only r^2 %s fm^2; AV-1 sea+PV share %s; neither mass is selected" % (nstr(rsea2 * fm2(a2["M_over_mp"]), 6), nstr(share, 6)))
                    info("AV-2", "AV-2 j=0 r_V^2 (fm^2)", "information only", (Ir2s / I1s) * fm2(a2["M_over_mp"]), "diagnostic", "M/m_p 0.4581682005 stays a diagnostic. H-40 E = 3.41 M is not adopted")
                    rec("AV-2", "AV-2 mass choice", "not adopted", "neither mass is selected; the sigma-model mass is not installed")
if not any(r_[0] == "GATE" for r_ in rows):
    rec("GATE", "record rows of the 91", "unchanged", "z-only; 88/91 since owner record commit b99fc29")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02av.py under audit/FREEZE_2026-10-02av (hashed before the run)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
