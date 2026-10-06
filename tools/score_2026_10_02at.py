#!/usr/bin/env python3
"""Round-at scores under audit/FREEZE_2026-10-02at (hashed before the run). Recomputes the locked mix, the move and any z from the json.
  python tools/score_2026_10_02at.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/score_2026-10-02at.tsv
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
START = 0.005515527562609979
A1 = 0.19354601067473753
SETT = (1.0, 0.5, 0.25, 0.125)
def locked_mix(probe):
    gaps = {float(row["mix"]): float(row["next_gap"]) for row in probe}
    def gap(a):
        hits = [v for k, v in gaps.items() if abs(k - a) <= 1e-15]
        if len(hits) != 1: raise KeyError(a)
        return hits[0]
    for alp in SETT: gap(alp)
    if not close(gap(1.0), A1): raise ValueError("alpha1")
    best = min(SETT, key=lambda alp: (gap(alp), -alp))
    if gap(best) < START: return best
    return 0.2
mpM = X.kg_to_GeV(L["m_p_kg"]) * 1000
hbc = mpf("0.1973269804"); mpG = mpM / 1000
def fm2(Mr): return (hbc / mpG)**2 / (mpf(Mr)**2)
man = J("audit/scprofile_2026-10-02at.json"); ar = J("audit/scprofile_2026-10-02ar.json"); ag = J("audit/murun_2026-10-02ag_K14_D14_k12.json"); dpp = J("audit/rv_2026-10-02aq_A_j0.json")
s = "AT-1"; bad = []; b = man.get("basis") or {}
for k, v in {"K": 14, "D": 14.0, "kmax": 12.0, "nq": 1500, "tol": 0.001, "guard": 200, "rise_guard": 5, "Nc": 3}.items():
    if not close(b.get(k), v): bad.append("basis " + k)
if man.get("freeze") != "FREEZE_2026-10-02at" or man.get("complete") is not True: bad.append("manifest")
probe = man.get("probe") or []
try: star = locked_mix(probe)
except (KeyError, ValueError, TypeError): star = None; bad.append("probe")
if star is not None:
    for row in probe:
        if row.get("source") == "probe":
            try:
                off = abs(float(row.get("pre_gap")) - START) > 1e-9
            except (TypeError, ValueError):
                off = True
            if off: bad.append("start gap")
    if not close((man.get("lock") or {}).get("alpha_star"), star): bad.append("lock")
a1 = man.get("AT-1"); src = ar.get("AR-1")
if not a1 or not src: bad.append("AT-1 missing")
elif star is not None and not close(a1.get("mix"), star): bad.append("AT-1 mix")
if a1 and src:
    if not close(a1["M_over_mp"], src["M_over_mp"]) or not close(a1["F_over_M"], src["F_over_M"]) or not close(a1["mpi_over_M"], src["mpi_over_M"]): bad.append("AT-1 mass")
    if not close(a1.get("tol"), 0.001) or not close(a1.get("guard"), 200): bad.append("AT-1 step")
    if len(a1.get("history") or []) > 200: bad.append("AT-1 length")
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
    rec(s, "AT-1 manifest", "refused", "the json does not match FREEZE_2026-10-02at: " + ", ".join(bad))
else:
    st = state(a1); last = a1["history"][-1]
    gaps = ", ".join("%s -> %s" % (nstr(mpf(row["mix"]), 4), nstr(mpf(row["next_gap"]), 6)) for row in probe)
    info(s, "AT-1 locked mix", "smallest next gap in {1, 1/2, 1/4, 1/8}, else 0.2 if none is below the start gap", star, "diagnostic",
         "start gap %s; probe %s; alpha = 1 is the recorded AS-1 pass 1 and was not recomputed" % (nstr(mpf(START), 8), gaps))
    info(s, "AT-1 walk", "self_consistent_m mix %s, tol 1e-3, guard 200" % nstr(mpf(star), 4), len(a1["history"]), "diagnostic",
         "state %s; last E/M %s; ev %s; dtheta %s; %s s; recorded stop %s" % (st, last[1], last[2], last[3], a1["seconds"], a1.get("stop")))
    gp = "audit/rv_2026-10-02at_gap_j0.json"; gap = J(gp) if (R_ / gp).exists() else None
    r_dpp = mpf(dpp["Ir2"]) / mpf(dpp["I1"]); share = None
    if st == "valence lost" or gap is None or "I1" not in gap:
        rec(s, "AT-1 radius", "valence lost" if st == "valence lost" else "information", "no usable j=0 split; AR-2 not run; nothing rescored")
    else:
        I1, Ir2, share, rsea = sea_note(gap); r_sc = Ir2 / I1; move = fabs(r_sc - r_dpp) / r_dpp; Mr = mpf(a1["M_over_mp"])
        info(s, "AT-1 j=0 r_V^2 (fm^2)", "I[r^2]/I[1] on the walked profile, box j=0", r_sc * fm2(Mr), "diagnostic",
             "r M^2 %s; DPP r M^2 %s; move %s %%" % (nstr(r_sc, 8), nstr(r_dpp, 8), nstr(move * 100, 4)))
        info(s, "AT-1 j=0 sea+PV share of I[1]", "sea plus PV, box j=0", share, "diagnostic", "sea+PV-only r^2 %s fm^2; max |imag| %s" % (nstr(rsea * fm2(Mr), 6), gap["max_imag"]))
        if st == "inconsistent":
            rec(s, "AT-1 branch", "refused", "converged flag and last dtheta disagree; nothing rescored")
        elif st != "converged":
            rec(s, "AT-1 branch", "not converged", "j=0 radius is information; AR-2 not run; nothing rescored")
        elif move <= mpf("0.02"):
            rec(s, "AT-1 branch", "stable", "scoring-box radius stable under the locked step (move %s %% <= 2); no further boxes; no new 0.82236 validation; nothing rescored" % nstr(move * 100, 4))
        else:
            boxes, missing = [], []
            for j in range(4):
                p = "audit/rv_2026-10-02at_gap_j%d.json" % j
                if not (R_ / p).exists(): missing.append(j)
                else: boxes.append(J(p))
            if missing or any("I1" not in e for e in boxes):
                rec(s, "AT-1 branch", "incomplete", "move %s %% > 2 but boxes %s are missing; nothing rescored" % (nstr(move * 100, 4), missing))
            else:
                def avg(v): return sum(v) / len(v)
                P = {k: [avg([mpf(e[k][i]) for e in boxes]) for i in range(2)] for k in ("I_val", "I_sea", "I_pv")}
                I1a = sum(P[k][0] for k in P); Ir2a = sum(P[k][1] for k in P); r2 = Ir2a / I1a
                info(s, "AT-1 4-box r_V^2 (fm^2)", "<I[r^2]>/<I[1]>, boxes j=0..3", r2 * fm2(Mr), "FSOT · intermediate", "r M^2 %s" % nstr(r2, 8))
                r2c = (mpf("0.84075")**2 + mpf("0.1155")) * (mpG / hbc)**2
                r2s = sqrt((2 * mpf("0.84075") * mpf("0.00064"))**2 + mpf("0.0017")**2) * (mpG / hbc)**2
                z = emitz(s, "AT-1 r_V^2 m_p^2, 4-box average (validation)", "FSOT soliton, locked-step profile", r2 / Mr**2, r2c, r2s, 0, "validation (PDG r_p, <r_n^2>)",
                          "r_V^2 %s fm^2 vs 0.82236(201); PDG sigma only; move %s %%" % (nstr(r2 * fm2(Mr), 6), nstr(move * 100, 4)))
                rec(s, "AT-1 validation branch", "numerical at one level" if z <= 1 else "miss", "z %s. The round-ap chain is not carried. The 91 are not rescored." % nstr(z, 4))
        if st == "converged":
            a2 = man.get("AT-2"); inp = ag["inputs"]; M3 = mpf(1) / 3
            if not a2: rec("AT-2", "AT-2 sea scaling", "missing", "AT-1 converged but AT-2 is absent; nothing rescored")
            else:
                st2 = state(a2); last2 = a2["history"][-1]
                bad2 = a2.get("M_over_mp_exact") != "1/3" or fabs(mpf(a2["M_over_mp"]) - M3) > mpf("1e-12") or not close(a2.get("mix"), star)
                if not close(a2["F_over_M"], float(inp["F_over_mp"]) / (1.0 / 3.0)) or not close(a2["mpi_over_M"], float(inp["mpi_over_mp"]) / (1.0 / 3.0)): bad2 = True
                if len(a2.get("history") or []) > 200: bad2 = True
                info("AT-2", "AT-2 walk at M/m_p = 1/3", "same x_DPP, locked mix %s" % nstr(mpf(star), 4), len(a2["history"]), "diagnostic",
                     "state %s; last E/M %s; ev %s; dtheta %s; %s s. H-40 on a different basis: unbound, E = 3.41 M; not adopted" % (st2, last2[1], last2[2], last2[3], a2["seconds"]))
                sp = "audit/rv_2026-10-02at_sigma_j0.json"; sig = J(sp) if (R_ / sp).exists() else None
                if bad2: rec("AT-2", "AT-2 inputs", "refused", "AT-2 json does not match M/m_p = 1/3 at the locked mix; nothing rescored")
                elif sig is None or "I1" not in sig: rec("AT-2", "AT-2 radius", "information" if st2 != "valence lost" else "valence lost", "no usable j=0 split; mass not adopted")
                else:
                    I1s, Ir2s, share2, rsea2 = sea_note(sig)
                    info("AT-2", "AT-2 j=0 sea+PV share of I[1]", "M/m_p = 1/3, box j=0", share2, "diagnostic",
                         "sea+PV-only r^2 %s fm^2; AT-1 sea+PV share %s; neither mass is selected" % (nstr(rsea2 * fm2(a2["M_over_mp"]), 6), nstr(share, 6)))
                    info("AT-2", "AT-2 j=0 r_V^2 (fm^2)", "information only", (Ir2s / I1s) * fm2(a2["M_over_mp"]), "diagnostic", "M/m_p 0.4581682005 stays a diagnostic. H-40 E = 3.41 M is not adopted")
                    rec("AT-2", "AT-2 mass choice", "not adopted", "neither mass is selected; the sigma-model mass is not installed")
if not any(r_[0] == "GATE" for r_ in rows):
    rec("GATE", "record rows of the 91", "unchanged", "z-only; 88/91 since owner record commit b99fc29")
with open(a.out, "w", encoding="utf-8", newline="\n") as o:
    o.write("# generated by tools/score_2026_10_02at.py under audit/FREEZE_2026-10-02at (hashed before the run)\n#section\tname\tinputs\tvalue\tcentral\tsigma\tz\tverdict\trel\tclass\tnote\n")
    for r_ in rows: o.write("\t".join(str(x_) for x_ in r_) + "\n")
print("done", len(rows))
