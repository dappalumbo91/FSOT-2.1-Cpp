#!/usr/bin/env python3
"""Dump golden values from the FSOT authority (vendor/fsot_compute.py) to TSV.

Verifies the authority SHA-256 against AUTHORITY_PIN.json first. Every value is
written with 50 significant digits (mpmath mp.dps = 50, prec = 169 bits).
Format: one record per line, tab-separated:  key  name  value
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONSTS = ["PI", "E", "PHI", "GAMMA", "G_CAT", "ALPHA", "PSI_CON", "ETA_EFF", "BETA", "GAMMA_C",
          "OMEGA", "THETA_S", "POOF", "C_EFF", "A_BLEED", "P_VAR", "B_IN", "A_IN", "SUCTION",
          "CHAOS", "P_BASE", "P_NEW", "C_FACTOR", "K", "C_COSM", "S_COSM", "S_QUANT", "S_CHEM"]
SECTIONS = [
    "wave1", "validation_suite", "wave2", "wave3", "wave4", "wave5", "wave6", "wave7",
    "wave8", "wave9", "wave10", "lepton_ratios", "dynamical_systems", "neural_architecture",
    "consciousness_model", "homeostasis", "soliton_stdp", "cross_species", "trinary",
    "predictions", "chemistry_ionization", "chemistry_electronegativity",
    "chemistry_bond_lengths", "chemistry_bond_energies", "chemistry_molecular", "chemistry_radii",
]


def load(path: Path):
    sha = hashlib.sha256(path.read_bytes()).hexdigest().upper()
    pin = json.loads((ROOT / "AUTHORITY_PIN.json").read_text())
    if sha != pin["authority_sha256"]:
        sys.exit(f"PIN MISMATCH: {sha[:6]} != {pin['pin_prefix']}")
    spec = importlib.util.spec_from_file_location("fsot_compute", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["fsot_compute"] = mod
    spec.loader.exec_module(mod)
    return mod, sha


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--authority", required=True)
    ap.add_argument("--out", default=str(ROOT / "golden" / "golden_AEB2AD.tsv"))
    a = ap.parse_args()
    mod, sha = load(Path(a.authority))
    mp = mod.mp
    s = lambda v: mp.nstr(v, 50, strip_zeros=False, min_fixed=1, max_fixed=0)
    lines = [f"#pin\t{sha}\t{mp.prec}"]
    for c in CONSTS:
        lines.append(f"const\t{c}\t{s(getattr(mod, c))}")
    for name, d in mod.DOMAINS.items():
        lines.append(f"domain.D_eff\t{name}\t{d.D_eff}")
        lines.append(f"domain.hits\t{name}\t{d.hits}")
        lines.append(f"domain.observed\t{name}\t{int(d.observed)}")
        lines.append(f"domain.look\t{name}\t{s(d.delta_psi)}")
        lines.append(f"domain.C\t{name}\t{s(d.C)}")
        lines.append(f"domain.S\t{name}\t{s(mod.domain_scalar(name))}")
        lines.append(f"correct72\t{name}\t{s(mod.mpf(72) * (1 + abs(mod.domain_scalar(name)) * mod.ALPHA))}")
    total = passed = 0
    for sec in SECTIONS:
        for i, r in enumerate(getattr(mod, sec)()):
            lines.append(f"sec.{sec}.{i}\t{r.name}\t{s(r.computed)}")
            if r.measured is not None and r.measured != 0:
                total += 1
                if float(abs(r.computed - r.measured) / abs(r.measured) * 100) < 5.0:
                    passed += 1
    lines.append(f"summary.total\t-\t{total}")
    lines.append(f"summary.pass5\t-\t{passed}")
    Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {a.out}: {len(lines)} lines, pin {sha[:6]}, {total} targets, {passed} within 5%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
