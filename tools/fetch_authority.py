#!/usr/bin/env python3
"""Download vendor/fsot_compute.py from FSOT-2.1-Lean at the pinned commit and verify its SHA-256.

Usage: python tools/fetch_authority.py [--out authority/fsot_compute.py]
Exit 2 on SHA mismatch. Never edits the file.
"""
import argparse, hashlib, json, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "authority" / "fsot_compute.py"))
    a = ap.parse_args()
    pin = json.loads((ROOT / "AUTHORITY_PIN.json").read_text())
    data = urllib.request.urlopen(pin["raw_url"], timeout=60).read()
    sha = hashlib.sha256(data).hexdigest().upper()
    if sha != pin["authority_sha256"]:
        print(f"PIN MISMATCH: got {sha[:6]}, expected {pin['pin_prefix']}", file=sys.stderr)
        return 2
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True); out.write_bytes(data)
    print(f"authority {pin['pin_prefix']} @ {pin['hub_commit'][:8]} -> {out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
