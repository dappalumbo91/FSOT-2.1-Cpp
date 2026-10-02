#!/usr/bin/env python3
"""Collect DATED EVIDENCE for the evidence-tier report (docs/EVIDENCE_TIERS.md) from the hub's git history
and freeze/prereg files, at AUTHORITY_PIN.json "ledger_b_data_commit". Facts only; the classification
itself is done in C++ (include/fsot/host/tiers.hpp) so the rules live in one place.

Writes golden/tier_evidence_<commit8>.json:
  freezes[]: file, claimed date, explicit hash (if any) and the earliest commit whose version of the file
             already carried that hash (git pickaxe), pin, and what the freeze covers.
  cpp_freezes[]: this repo's freezes/*.json (apps/fsot_freeze_domain), dated by the first commit of THIS repo
             whose version of the file carries selection_sha256; per-row hashes for re-derivation in C++.
  benchmark_files{}: first commit that added data/<name> (--full-history --no-renames) and its date, and the
             last commit touching it.
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(hub: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(hub), *args], capture_output=True, text=True, check=True).stdout


def first_commit_with(hub: Path, path: str, needle: str | None) -> tuple[str | None, str | None]:
    if needle:
        out = git(hub, "log", "--full-history", "--reverse", "--format=%H %cI", "-S", needle, "--", path).split("\n")
    else:
        out = git(hub, "log", "--full-history", "--reverse", "--format=%H %cI", "--", path).split("\n")
    out = [l for l in out if l.strip()]
    if not out:
        return None, None
    h, d = out[0].split()
    return h, d


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hub", required=True)
    a = ap.parse_args()
    hub = Path(a.hub)
    pin = json.loads((ROOT / "AUTHORITY_PIN.json").read_text())
    head = git(hub, "rev-parse", "HEAD").strip()
    if head != pin["ledger_b_data_commit"]:
        print(f"hub HEAD {head} != ledger_b_data_commit", file=sys.stderr)
        return 2
    freezes = []
    # 1. domain table freeze (explicit sha256 of the 35-row DomainConfig table)
    p = "data/domain_table_freeze.json"
    d = json.loads((hub / p).read_text())
    c, cd = first_commit_with(hub, p, d["domain_table_sha256"])
    freezes.append({"id": "domain_table_freeze", "file": p, "claimed_date": d["freeze_date"], "pin_prefix": d["pin_prefix"],
                    "hash_field": "domain_table_sha256", "hash": d["domain_table_sha256"],
                    "hash_first_commit": c, "hash_first_commit_date": cd, "covers": "core_domain_table",
                    "ids": [r["domain"] for r in d["domains"]]})
    # 2. Ledger A freeze (dated, expressions verbatim, no explicit hash)
    p = "predictions/LEDGER_A_FREEZE.yaml"
    txt = (hub / p).read_text()
    m = re.search(r"generated_at:\s*(\S+)", txt)
    c, cd = first_commit_with(hub, p, None)
    freezes.append({"id": "ledger_a_freeze", "file": p, "claimed_date": m.group(1) if m else None,
                    "pin_prefix": re.search(r"^pin:\s*(\S+)", txt, re.M).group(1), "hash_field": None, "hash": None,
                    "hash_first_commit": None, "hash_first_commit_date": None, "file_first_commit": c, "file_first_commit_date": cd,
                    "covers": "ledger_a", "ids": re.findall(r"^\s*- id:\s*(\S+)", txt, re.M)})
    # 3. ToE prereg freeze (bundle hash over listed files, frozen at another pin)
    p = "predictions/toe_prereg_freeze.json"
    d = json.loads((hub / p).read_text())
    c, cd = first_commit_with(hub, p, d.get("bundle_sha256"))
    pinm = re.search(r"Pin ([0-9A-F]{6})", d.get("discipline", ""))
    freezes.append({"id": "toe_prereg_freeze", "file": p, "claimed_date": d.get("frozen_at"), "pin_prefix": pinm.group(1) if pinm else None,
                    "hash_field": "bundle_sha256", "hash": d.get("bundle_sha256"), "hash_first_commit": c, "hash_first_commit_date": cd,
                    "covers": "toe_sector_predictions", "ids": [s["id"] for s in d.get("sector_predictions", [])]})
    # 4. Pre-registered predictions manifest (dated per entry, no hash)
    p = "predictions/preregistered_predictions_manifest.yaml"
    txt = (hub / p).read_text()
    ids = re.findall(r"^\s*- id:\s*(PRED-\d+)", txt, re.M)
    dates = re.findall(r"^\s*registered_at:\s*\"?([0-9-]+)", txt, re.M)
    c, cd = first_commit_with(hub, p, None)
    freezes.append({"id": "preregistered_predictions_manifest", "file": p, "claimed_date": min(dates) if dates else None,
                    "pin_prefix": None, "hash_field": None, "hash": None, "hash_first_commit": None, "hash_first_commit_date": None,
                    "file_first_commit": c, "file_first_commit_date": cd, "covers": "prereg_ids", "ids": ids})
    # benchmark files: first-add and last-change commits
    files = {}
    log = git(hub, "log", "--full-history", "--no-renames", "--reverse", "--diff-filter=A", "--format=C %H %cI", "--name-only", "--", "data/")
    cur = None
    for line in log.splitlines():
        if line.startswith("C "):
            _, h, dt = line.split()
            cur = (h, dt)
        elif line.endswith("_benchmark.json") and line.startswith("data/") and "/" not in line[5:]:
            files.setdefault(line[5:], {"first_added_commit": cur[0], "first_added_date": cur[1]})
    log = git(hub, "log", "--full-history", "--no-renames", "--format=C %H %cI", "--name-only", "--", "data/")
    seen = set()
    for line in log.splitlines():
        if line.startswith("C "):
            _, h, dt = line.split()
            cur = (h, dt)
        elif line[5:] in files and line[5:] not in seen:
            seen.add(line[5:])
            files[line[5:]]["last_changed_commit"], files[line[5:]]["last_changed_date"] = cur
    present = {q.name for q in (hub / "data").glob("*_benchmark.json")}
    files = {k: v for k, v in sorted(files.items()) if k in present}
    missing = sorted(present - files.keys())
    # 5. freezes written by this repo's apps/fsot_freeze_domain (freezes/*.json), dated by THIS repo's git
    cpp_freezes = []
    for q in sorted((ROOT / "freezes").glob("*.json")):
        d = json.loads(q.read_text())
        rel = q.relative_to(ROOT).as_posix()
        c, cd = first_commit_with(ROOT, rel, d["selection_sha256"])
        cpp_freezes.append({"id": "cpp:" + rel, "file": "FSOT-2.1-Cpp/" + rel, "claimed_date": d["freeze_date"],
                            "pin_prefix": d["pin_prefix"], "hash_field": "selection_sha256", "hash": d["selection_sha256"],
                            "hash_first_commit": c, "hash_first_commit_date": cd, "covers": "domain_rows",
                            "rows": {r["domain"]: r["row_sha256"] for r in d["domains"]}})
    out = {"hub_commit": head, "freezes": freezes, "cpp_freezes": cpp_freezes, "benchmark_files": files, "benchmark_files_without_add_commit": missing}
    dst = ROOT / "golden" / f"tier_evidence_{head[:8]}.json"
    dst.write_text(json.dumps(out, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    print(f"wrote {dst.relative_to(ROOT)}: {len(freezes)} hub freezes, {len(cpp_freezes)} cpp freezes, {len(files)} benchmark files dated, {len(missing)} undated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
