#!/usr/bin/env python3
"""Round-au scores under audit/FREEZE_2026-10-02au (hashed before the run). Recomputes the move and any z from the json.
  python tools/score_2026_10_02au.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02au.tsv
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
man = J("audit/scprofile_2026-10-02au.json"); ar = J("audit/scprofile_2026-10-02ar.json"); ag = J("audit/murun_2026-10-02ag_K14_D14_k12.json"); dpp = J("audit/rv_2026-10-02aq_A_j0.json")
s = "AU-1"; bad = []; b = man.get("basis") or {}
for k, v in {"K": 14, "D": 14.0, "kmax": 12.0, "nq": 1500, "mix": 0.2, "tol": 0.001, "guard": 400, "rise_guard": 5, "Nc": 3}.items():
    if not close(b.get(k), v): bad.append("basis " + k)
if man.get("freeze") != "FREEZE_2026-10-02au" or man.get("complete") is not True: bad.append("manifest")
a1 = man.get("AU-1"); src = ar.get("AR-1")
if not a1 or not src: bad.append("AU-1 missing")
else:
    if not close(a1["M_over_mp"], src["M_over_mp"]) or not close(a1["F_over_M"], src["F_over_M"]) or not close(a1["mpi_over_M"], src["mpi_over_M"]): bad.append("AU-1 mass")
    if not close(a1.get("mix"), 0.2) or not close(a1.get("tol"), 0.001) or not close(a1.get("guard"), 400): bad.append("AU-1 step")
    if len(a1.get("history") or []) > 400: bad.append("AU-1 length")
    h0 = (a1.get("history") or [None])[0]
    if not h0 or h0[3] is None or abs(float(h0[3]) - 0.005515527562609979) > 1e-9: bad.append("start gap")
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
    rec(s, "AU-1 manifest", "refused", "the json does not match FREEZE_2026-10-02au: " + ", ".join(bad))
else:
    st = state(a1); last = a1["history"][-1]
    info(s, "AU-1 damped walk", "self_consistent_m mix 0.2, tol 1e-3, guard 400", len(a1["history"]), "diagnostic",
         "state %s; last E/M %s; ev %s; dtheta %s; %s s; recorded stop %s" % (st, last[1], last[2], last[3], a1["seconds"], a1.get("stop")))
    gp = "audit/rv_2026-10-02au_gap_j0.json"; gap = J(gp) if (R_ / gp).exists() else None
    r_dpp = mpf(dpp["Ir2"]) / mpf(dpp["I1"]); share = None
    if st == "valence lost" or gap is None or "I1" not in gap:
        rec(s, "AU-1 radius", "valence lost" if st == "valence lost" else "information", "no usable j=0 split; AR-2 not run; nothing rescored")
    else:
        I1, Ir2, share, rsea = sea_note(gap); r_sc = Ir2 / I1; move = fabs(r_sc - r_dpp) / r_dpp; Mr = mpf(a1["M_over_mp"])
        info(s, "AU-1 j=0 r_V^2 (fm^2)", "I[r^2]/I[1] on the damped profile, box j=0", r_sc * fm2(Mr), "diagnostic",
             "r M^2 %s; DPP r M^2 %s; move %s %%" % (nstr(r_sc, 8), nstr(r_dpp, 8), nstr(move * 100, 4)))
        info(s, "AU-1 j=0 sea+PV share of I[1]", "sea plus PV, box j=0", share, "diagnostic", "sea+PV-only r^2 %s fm^2; max |imag| %s" % (nstr(rsea * fm2(Mr), 6), gap["max_imag"]))
        if st == "inconsistent":
            rec(s, "AU-1 branch", "refused", "converged flag and last dtheta disagree; nothing rescored")
        elif st != "converged":
            rec(s, "AU-1 branch", "not converged", "j=0 radius is information; AR-2 not run; nothing rescored")
        elif move <= mpf("0.02"):
            rec(s, "AU-1 branch", "stable", "scoring-box radius stable under the damped step (move %s %% <= 2); no further boxes; no new 0.82236 validation; nothing rescored" % nstr(move * 100, 4))
        else:
            boxes, missing = [], []
            for j in range(4):
                p = "audit/rv_2026-10-02au_gap_j%d.json" % j
                if not (R_ / p).exists(): missing.append(j)
                else: boxes.append(J(p))
            if missing or any("I1" not in e for e in boxes):
                rec(s, "AU-1 branch", "incomplete", "move %s %% > 2 but boxes %s are missing; nothing rescored" % (nstr(move * 100, 4), missing))
            else:
                def avg(v): return sum(v) / len(v)
                P = {k: [avg([mpf(e[k][i]) for e in boxes]) for i in range(2)] for k in ("I_val", "I_sea", "I_pv")}
                I1a = sum(P[k][0] for k in P); Ir2a = sum(P[k][1] for k in P); r2 = Ir2a / I1a
                info(s, "AU-1 4-box r_V^2 (fm^2)", "<I[r^2]>/<I[1]>, boxes j=0..3", r2 * fm2(Mr), "FSOT · intermediate", "r M^2 %s" % nstr(r2, 8))
                r2c = (mpf("0.84075")**2 + mpf("0.1155")) * (mpG / hbc)**2
                r2s = sqrt((2 * mpf("0.84075") * mpf("0.00064"))**2 + mpf("0.0017")**2) * (mpG / hbc)**2
                z = emitz(s, "AU-1 r_V^2 m_p^2, 4-box average (validation)", "FSOT soliton, damped profile", r2 / Mr**2, r2c, r2s, 0, "validation (PDG r_p, <r_n^2>)",
                          "r_V^2 %s fm^2 vs 0.82236(201); PDG sigma only; move %s %%" % (nstr(r2 * fm2(Mr), 6), nstr(move * 100, 4)))
                rec(s, "AU-1 validation branch", "numerical at one level" if z <= 1 else "miss", "z %s. The round-ap chain is not carried. The 91 are not rescored." % nstr(z, 4))
        if st == "converged":
            a2 = man.get("AU-2"); inp = ag["inputs"]; M3 = mpf(1) / 3
            if not a2: rec("AU-2", "AU-2 sea scaling", "missing", "AU-1 converged but AU-2 is absent; nothing rescored")
            else:
                st2 = state(a2); last2 = a2["history"][-1]
                bad2 = a2.get("M_over_mp_exact") != "1/3" or fabs(mpf(a2["M_over_mp"]) - M3) > mpf("1e-12") or not close(a2.get("mix"), 0.2)
                if not close(a2["F_over_M"], float(inp["F_over_mp"]) / (1.0 / 3.0)) or not close(a2["mpi_over_M"], float(inp["mpi_over_mp"]) / (1.0 / 3.0)): bad2 = True
                if len(a2.get("history") or []) > 400: bad2 = True
                info("AU-2", "AU-2 damped walk at M/m_p = 1/3", "same x_DPP, mix 0.2", len(a2["history"]), "diagnostic",
                     "state %s; last E/M %s; ev %s; dtheta %s; %s s. H-40 on a different basis: unbound, E = 3.41 M; not adopted" % (st2, last2[1], last2[2], last2[3], a2["seconds"]))
                sp = "audit/rv_2026-10-02au_sigma_j0.json"; sig = J(sp) if (R_ / sp).exists() else None
                if bad2: rec("AU-2", "AU-2 inputs", "refused", "AU-2 json does not match M/m_p = 1/3 at mix 0.2; nothing rescored")
                elif sig is None or "I1" not in sig: rec("AU-2", "AU-2 radius", "information" if st2 != "valence lost" else "valence lost", "no usable j=0 split; mass not adopted")
                else:
                    I1s, Ir2s, share2, rsea2 = sea_note(sig)
                    info("AU-2", "AU-2 j=0 sea+PV share of I[1]", "M/m_p = 1/3, box j=0", share2, "diagnostic",
                         "sea+PV-only r^2 %s fm^2; AU-1 sea+PV share %s; neither mass is selected" % (nstr(rsea2 * fm2(a2["M_over_mp"]), 6), nstr(share, 6)))
                    info("AU-2", "AU-2 j=0 r_V^2 (fm^2)", "information only", (Ir2s / I1s) * fm2(a2["M_over_mp"]), "diagnostic", "M/m_p 0.4581682005 stays a diagnostic. H-40 E = 3.41 M is not adopted")
                    rec("AU-2", "AU-2 mass choice", "not adopted", "neither mass is selected; the sigma-model mass is not installed")
if not any(r_[0] == "GATE" for r_ in rows):
    rec("GATE", "record rows of the 91", "unchanged", "z-only; 88/91 since owner record commit b99fc29")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02au.py under audit/FREEZE_2026-10-02au (hashed before the run)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
