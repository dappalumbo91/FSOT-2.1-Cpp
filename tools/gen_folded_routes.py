#!/usr/bin/env python3
"""Generate golden/folded_routes.tsv from the dial-in ledger (read-only).

Every PASS/INCLUDE leaf of /workspace/refine_bots/tracer/STATUS.tsv whose results.tsv carries a (pred, obs, sigma)
triple becomes one row. `live` names the C++ function that recomputes pred inside the engine
(tests/test_folded_routes.cpp asserts pred_live == pred_recorded and re-scores z). Excluded by rule:
anything scoring V_ud / g_A as its target ((l) exclusions). §43.5vt (G_F) was a HOOK row until Damian t994u
(2026-11-11 1:00 PM EST) folded it flagged SM_PARITY_REFINE_LATER (ruling t992u sha8 c65ff89d): vt_rows() emits the
carried route P2 and the documented alternate P1 from out_vt_*/results.tsv; they are re-derived live by
fold::vt::Chain (include/fsot/fold/vt_gf.hpp).
IRONOUT-2 (parent steering 2026-11-11 1:55 PM EST, Tracer vv FOLD f66b7985 / vw FOLD ce51de78): the CARRIED G_F route is
now §43.5vv P3 (remainder unresummed) with §43.5vw P3's corrected Delta_R^V (tau_n 878.4325396 s); vt P2 and vt P1 stay
as documented alternates. vvw_rows() emits them from out_vv_*/results.tsv and out_vw_*/results.tsv (re-derived live by
fold::vt::Chain with Hooks::vv_p3 + Hooks::tau_vk_override; coefficients golden/vv_vw_package.tsv). tau_n primary =
pdgLive 878.3 +- 0.4 s; PDG 2024 878.4 +- 0.5, UCNtau and Pattie are secondary rows.
Usage: tools/gen_folded_routes.py [TRACER_DIR] > golden/folded_routes.tsv
       tools/gen_folded_routes.py --vt-only TRACER_DIR golden/folded_routes.tsv   (replace only the vt HOOK/rows; the
       other rows stay pinned to the ledger sha in the header, so unrelated new leaves are not folded silently)"""
import csv, hashlib, io, re, sys
from pathlib import Path
VT_ONLY = len(sys.argv) > 1 and sys.argv[1] == "--vt-only"
if VT_ONLY: sys.argv.pop(1)
T = Path(sys.argv[1] if len(sys.argv) > 1 else "/workspace/refine_bots/tracer")
VT_DIR = "dialin/out_vt_tau_n_gf_z2_mu_consistent_dr2_completion"
VT_ID = "43.5vt-TAU_N_GF_Z2_MU_CONSISTENT_DR2_COMPLETION_INVENT_EXTEND"
FLAG = "SM_PARITY_REFINE_LATER"
def vt_rows():
    f = T / VT_DIR / "results.tsv"; src = f"{VT_DIR}/results.tsv@{hashlib.sha256(f.read_bytes()).hexdigest()[:8]}"
    out = []; rows = [l.split("\t") for l in f.read_text().splitlines()[1:] if l.strip()]
    gate = "Gate A PASS (tau_n), G_F Gate A FAIL / Gate B ACCEPT-AT-SM-PARITY (t992u c65ff89d)"
    for route, role in (("P2", "ALTERNATE P2 C1+C2+C3+C5mu+C6 (no C7; carried until IRONOUT-2, replaced by vv P3 + vw P3)"), ("P1", "ALTERNATE P1 C1+C2+C3+C5mu+C6+C7 (documented, not carried)")):
        for r in rows:
            if r[0] != route: continue
            if r[1] == "tau_n_s":
                g = "UCNtau" if r[3].startswith("UCN") else "Pattie"
                out.append([VT_ID, f"tau_n_s {g} [{route}]", r[2], r[4], r[5], r[6], f"{role} · {gate} · {FLAG}", f"vt:tau_n_{route}", src])
            elif r[1] == "chi2_over_N":
                gf = re.search(r"G_F,vt=([0-9.e+-]+)", r[8]).group(1)
                # obs/sigma: reference/published_2026-10-02.tsv:129 G_F_GeVm2 (CODATA 2022), the engine's own G_F reference row
                out.append([VT_ID, f"G_F_GeVm2 [{route}]", gf, "1.1663787e-5", "6e-12", "", f"{role} · {gate} · {FLAG}", f"vt:G_F_{route}", src])
    return out
VV_DIR = "dialin/out_vv_tau_n_gf_dr_two_loop_remainder_completion"
VW_DIR = "dialin/out_vw_tau_n_drv_gamma_w_box_bjsr_interpolator"
VV_ID = "43.5vv-TAU_N_GF_DR_TWO_LOOP_REMAINDER_COMPLETION_INVENT_EXTEND"
VW_ID = "43.5vw-TAU_N_DRV_GAMMA_W_BOX_BJSR_INTERPOLATOR_INVENT_EXTEND"
TAU_GATES = (("pdgLive", "878.3", "0.4", "PRIMARY world average"), ("PDG2024", "878.4", "0.5", "secondary"),
             ("UCNtau", "877.82", "0.287445647", "secondary"), ("Pattie", "877.7", "0.761577311", "secondary"))
def vvw_rows():
    fv = T / VV_DIR / "results.tsv"; fw = T / VW_DIR / "results.tsv"
    sv = f"{VV_DIR}/results.tsv@{hashlib.sha256(fv.read_bytes()).hexdigest()[:8]}"; sw = f"{VW_DIR}/results.tsv@{hashlib.sha256(fw.read_bytes()).hexdigest()[:8]}"
    rv = [l.split("\t") for l in fv.read_text().splitlines()[1:] if l.strip()]; rw = [l.split("\t") for l in fw.read_text().splitlines()[1:] if l.strip()]
    t_vw = next(r[2] for r in rw if r[0] == "P3" and r[1] == "tau_n_s"); t_vv = next(r[2] for r in rv if r[0] == "P3" and r[1] == "tau_n_s")
    gf = re.search(r"G_F ([0-9.e+-]+);", next(r[9] for r in rv if r[0] == "P3" and r[1] == "tau_mu_ps")).group(1)
    gate = "G_F Gate A FAIL (tau_mu) / Gate B ACCEPT-AT-SM-PARITY (t992u c65ff89d, amend 50cd28b1); Gate B threshold vs world average 1.583 s"
    role = "CARRIED vv P3 G_F (remainder unresummed) + vw P3 Delta_R^V (3-loop alpha_g1 BjSR; engine gammaW box overstated +0.343 alpha/pi)"
    out = []
    for g, o, sg, pr in TAU_GATES:
        z = f"{(float(t_vw) - float(o)) / float(sg):.6g}"
        out.append([VW_ID, f"tau_n_s {g} [vvP3+vwP3]", t_vw, o, sg, z, f"{role} · tau_n {pr} · {gate} · {FLAG}", "vvw:tau_n", sw])
    out.append([VV_ID, "G_F_GeVm2 [vvP3, no W-prop term]", gf, "1.1663787e-5", "6e-12", "", f"Tracer's vv P3 G_F as filed (Delta r without 3m_mu^2/5M_W^2) · {gate} · {FLAG}", "vvw:G_F_noW", sv])
    # IRONOUT-2 (Tracer check of 1f0192f): the carried G_F carries the W-propagator term in Delta r (PDG eq.(10.9) fn.3, MuLan
    # convention): G_F = G_F,noW (1 + 3 m_mu^2/(5 M_W^2))^(1/2) with the engine m_mu, M_W leaves; C++ value (fold::vt::Chain::solve)
    out.append([VV_ID, "G_F_GeVm2 [vvP3 + W-prop in Delta r]", "1.16689453394674e-5", "1.1663787e-5", "6e-12", "", f"{role} · W-propagator term in Delta r (+0.5185 ppm, IRONOUT-2 C++) · {gate} · {FLAG}", "vvw:G_F", "fsot_cpp:include/fsot/fold/vt_gf.hpp Chain::solve (Hooks::w_prop_dr)"])
    z = f"{(float(t_vv) - 878.3) / 0.4:.6g}"
    out.append([VV_ID, "tau_n_s pdgLive [vvP3 only]", t_vv, "878.3", "0.4", z, f"ALTERNATE vv P3 without the vw Delta_R^V correction · {gate} · {FLAG}", "vvw:tau_n_vvP3", sv])
    return out
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
if VT_ONLY:
    gold = Path(sys.argv[2]); keep = [l for l in gold.read_text().splitlines() if not (l.startswith("HOOK\t43.5vt") or l.startswith((VT_ID, VV_ID, VW_ID)))]
    keep[0] = re.sub(r"\tvt=.*$", "", keep[0]) + f"\tvt={VT_DIR}/results.tsv (t994u)\tvvw={VV_DIR}+{VW_DIR} (IRONOUT-2)"
    sys.stdout.write("\n".join(keep + ["\t".join(r) for r in vvw_rows() + vt_rows()]) + "\n"); sys.exit(0)
for rid, p in sorted(last.items()):
    st, note = p[1].upper(), p[2]
    if rid.startswith(("43.5vt", "43.5vv", "43.5vw")): continue
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
for r in vvw_rows() + vt_rows(): print("\t".join(r), file=out)
sys.stdout.write(out.getvalue())
