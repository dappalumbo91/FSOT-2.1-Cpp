#!/usr/bin/env python3
"""Closed-form values of every physics row under the five vendor/fsot_compute.py pins that the hub
carried between 2026-08-04 and 2026-09-14 (read-only `git show` from a FSOT-2.1-Lean clone; nothing
in the hub or vendor/ is modified).  Writes reference/pin_lineage_2026-10-02.tsv, which supplies the
"historical" column of docs/PRECISION_REPORT.md for closed-form rows.

usage: python tools/pin_lineage.py --hub /path/to/FSOT-2.1-Lean [--out reference/pin_lineage_2026-10-02.tsv]
"""
import argparse, hashlib, importlib.util, os, subprocess, sys, tempfile

PINS = [  # (pin prefix, hub commit, commit date, subject)
    ("D1D38A", "012e5c64", "2026-08-04", "Restore D1D38A authority"),
    ("3090BC", "ba6a8288", "2026-09-11", "Replace decimal knobs with pi identities; f_domain=ALPHA"),
    ("FE23A2", "3c74a180", "2026-09-11", "Derive D_eff from nest generations"),
    ("3FBCE5", "ebd48320", "2026-09-14", "Derive observed, species, baryon/DM chemistry rung"),
    ("AEB2AD", "d127c07e", "2026-09-14", "Name interpretation C; nest D in APPLY. Pin AEB2AD"),
]
SECTIONS = ["wave1", "validation_suite", "wave2", "wave3", "wave4", "wave5", "wave7", "wave8", "wave9",
            "wave10", "lepton_ratios", "predictions"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hub", required=True)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "reference", "pin_lineage_2026-10-02.tsv"))
    a = ap.parse_args()
    vals, shas = {}, {}
    order = []
    with tempfile.TemporaryDirectory() as td:
        for pin, commit, _, _ in PINS:
            src = subprocess.run(["git", "-C", a.hub, "show", f"{commit}:vendor/fsot_compute.py"], check=True,
                                 capture_output=True).stdout
            sha = hashlib.sha256(src).hexdigest().upper()
            if not sha.startswith(pin):
                sys.exit(f"{commit}: vendor/fsot_compute.py sha256 {sha[:6]} != pin {pin}")
            shas[pin] = sha
            p = os.path.join(td, f"fc_{pin}.py")
            open(p, "wb").write(src)
            spec = importlib.util.spec_from_file_location(f"fc_{pin}", p)
            m = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = m
            spec.loader.exec_module(m)
            for sec in SECTIONS:
                fn = getattr(m, sec, None)
                if fn is None:
                    continue
                for r in fn():
                    key = f"{sec}|{r.name}"
                    if key not in vals:
                        vals[key] = {}
                        order.append(key)
                    vals[key][pin] = repr(float(r.computed))
    with open(a.out, "w") as f:
        f.write("# closed-form values per hub pin (tools/pin_lineage.py); sha256: " +
                " ".join(f"{p}={shas[p]}" for p, *_ in PINS) + "\n")
        f.write("# commits: " + " ".join(f"{p}={c}({d})" for p, c, d, _ in PINS) + "\n")
        f.write("#row\t" + "\t".join(p for p, *_ in PINS) + "\n")
        for k in order:
            f.write(k + "\t" + "\t".join(vals[k].get(p, "") for p, *_ in PINS) + "\n")
    print(f"wrote {a.out}: {len(order)} rows x {len(PINS)} pins")

if __name__ == "__main__":
    main()
