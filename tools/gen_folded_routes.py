#!/usr/bin/env python3
"""Generate golden/folded_routes.tsv from the dial-in ledger (read-only).

Every PASS/INCLUDE leaf of /workspace/refine_bots/tracer/STATUS.tsv whose results.tsv carries a (pred, obs, sigma)
triple becomes one row. `live` names the C++ function that recomputes pred inside the engine
(tests/test_folded_routes.cpp asserts pred_live == pred_recorded and re-scores z). Excluded by rule:
43.5vt (G_F; pending the muon-decay cross-check -> HOOK row, not folded), and anything scoring V_ud / g_A / G_F
as its target ((l) exclusions). Usage: tools/gen_folded_routes.py [TRACER_DIR] > golden/folded_routes.tsv"""
import csv, hashlib, io, re, sys
from pathlib import Path
T = Path(sys.argv[1] if len(sys.argv) > 1 else "/workspace/refine_bots/tracer")
D = T / "dialin"
status = (T / "STATUS.tsv").read_bytes()
last = {}
for l in status.decode("utf-8", "replace").splitlines()[1:]:
    p = l.split("\t")
    if len(p) >= 3 and p[0].startswith("43.5"): last[p[0]] = p
LIVE = {"mw": "leaf:m_W_MeV", "mtau": "leaf:m_tau_MeV", "mz": "leaf:m_Z_MeV", "gz": "gz:Gamma_Z_MeV", "dpm": "leaf:m_D_pm_MeV",
        "mk": "leaf:m_K_pm_MeV", "rp": "leaf:r_p_fm", "mh": "leaf:m_H_GeV", "dm2_21": "dm21:pathA", "dm2_32": "leaf:dm2_32",
        "sqrt8t0": "host:sqrt8t0_over_r0", "mu_r": "host:mu_p", "cdce": "host:c_D|host:c_E", "ra2": "nucleon:r_v2_over_2"}
def live_for(name):
    n = name.lower()
    for k, v in LIVE.items():
        if k in n: return v
    return ""
def sha8(p): return hashlib.sha256(p.read_bytes()).hexdigest()[:8]
rows = []
def add(route, leaf, pred, obs, sig, z, verdict, live, src):
    rows.append([route, leaf, str(pred), str(obs), str(sig), str(z), verdict, live, src])
for rid, p in sorted(last.items()):
    st, note = p[1].upper(), p[2]
    if rid.startswith("43.5vt"): continue
    blob = (st + " " + note).upper()
    if "FAIL" in st or "EXCLUDE" in st or "HOLD" in st: continue
    if not ("PASS" in blob and ("FOLD" in st or "INCLUDE" in blob)): continue
    fam = re.match(r"43\.5([a-z]+)", rid).group(1)
    ds = sorted(d for d in D.iterdir() if d.is_dir() and (d.name.startswith(f"out_{fam}_") or d.name == f"out_{fam}"))
    if not ds or not (ds[0] / "results.tsv").exists():
        add(rid, "-", "", "", "", "", p[1], "", "no results.tsv (route-level record only)"); continue
    f = ds[0] / "results.tsv"; src = f"{f.relative_to(T)}@{sha8(f)}"
    txt = f.read_text(errors="replace")
    lines = [l for l in txt.splitlines() if l.strip()]
    hdr = lines[0].split("\t")
    live = live_for(rid)
    if hdr[:2] == ["key", "value"]:
        kv = dict(l.split("\t", 1) for l in lines[1:] if "\t" in l)
        pk = next(k for k in kv if k.startswith("V_tip"))
        sk = "sigma" if "sigma" in kv else "sigma_eff"
        add(rid, pk, kv[pk], kv["target"], kv[sk], kv["z"], kv.get("verdict", ""), live, src)
    elif hdr[0].startswith("V_tip"):
        r = dict(zip(hdr, lines[1].split("\t")))
        add(rid, hdr[0], r[hdr[0]], r["target"], r["sigma"], r["z"], r.get("verdict", ""), live, src)
    elif hdr[:5] == ["name", "obs", "sig", "pred", "z"]:
        for l in lines[1:]:
            if l.startswith("#"): continue
            r = dict(zip(hdr, l.split("\t")))
            lv = live
            if "cdce" in rid.lower(): lv = "host:c_D" if "c_D" in r["name"] else "host:c_E"
            add(rid, r["name"], r["pred"], r["obs"], r["sig"], r["z"], p[1], lv, src)
    elif hdr[:5] == ["source", "obs", "sigma", "pred", "z"]:
        for l in lines[1:]:
            c = l.split("\t")
            if len(c) >= 5 and c[0] not in ("chi2/N", "verdict"): add(rid, c[0], c[3], c[1], c[2], c[4], p[1], live, src)
    elif hdr[:3] == ["row", "formula", "pred"]:
        r = dict(zip(hdr, lines[1].split("\t")))
        add(rid, "PRIMARY " + r["formula"], r["pred"], "", "", "", r["verdict"], live, src)
    elif hdr[:4] == ["observable", "pred", "observed", "sigma"]:
        for l in lines[1:]:
            if l.startswith("#"): continue
            r = dict(zip(hdr, l.split("\t")))
            add(rid, r["observable"], r["pred"], r["observed"], r["sigma"], r["z"], p[1], "", src)
    elif hdr[:4] == ["bin", "Q2lo", "Q2hi", "data"]:
        for l in lines[1:]:
            if l.startswith("#"): continue
            r = dict(zip(hdr, l.split("\t")))
            add(rid, f"bin{r['bin']}[{r['Q2lo']},{r['Q2hi']}]", r["pred"], r["data"], r["sigma_diag"], r["z"], p[1], "", src)
    elif hdr[:2] == ["leaf", "V_tip"]:
        r = dict(zip(hdr, lines[1].split("\t")))
        add(rid, r["leaf"], r["V_tip"], r["obs"], r["sigma"], r["z"], r.get("verdict", ""), live or "leaf:dm2_32", src)
    else:
        add(rid, "-", "", "", "", "", p[1], "", f"{src} (selector/aggregate; route-level record only)")
out = io.StringIO()
print(f"#folded_routes\tledger_sha256={hashlib.sha256(status).hexdigest()}\trows={len(rows)}", file=out)
print("#route\tleaf\tpred_recorded\tobs\tsigma\tz_recorded\tverdict\tlive\tsource", file=out)
for r in rows: print("\t".join(r), file=out)
print("HOOK\t43.5vt G_F\t\t\t\t\tFOLD-PASS-HOLD (not folded: pending muon-decay cross-check; G_F tip-native only)\thook:G_F\t-", file=out)
sys.stdout.write(out.getvalue())
