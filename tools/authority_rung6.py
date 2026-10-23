"""Pinned FSOT authority (vendor/fsot_compute.py, SHA in AUTHORITY_PIN.json) plus the owner-approved canonical
rung for Quantum_Mechanics.

Owner decision, Damian Palumbo, 2026-10-23 10:44 EDT: "Yes, make rung 6 canonical for QM". Evidence: QM's
continuous rung 5*5^{1/19} = 5.442 is the nest rung nearest a rounding tie; QM was read at two rungs in one build
(pins D5, OD-2 records D6); the 408-run fold-swap test (TRACER dialin/swap/foldswap.tsv) found QM->D6 gains 2 rows
and loses none (111/135, 91/91). The C++ rung rule (include/fsot/engine.hpp, core.hpp derived_D_eff) carries the same rule.

The authority file is NOT modified: its bytes are SHA-verified, then one line is inserted into derived_D_eff in memory,
before DOMAINS / S_QUANT are built, so every downstream value (pins, closed forms, Ledger A/B) uses rung 6.
"""
from __future__ import annotations
import hashlib, importlib.util, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = "    G = len(NEST_GENERATIONS)\n    if G < 2:\n        return 25\n    for g, group in enumerate(NEST_GENERATIONS):\n"
RULE = "    if name == \"Quantum_Mechanics\":\n        return 6  # canonical rung 6 (owner decision 2026-10-23, see tools/authority_rung6.py)\n"


def install(path) -> tuple[object, str]:
    path = Path(path)
    raw = path.read_bytes(); sha = hashlib.sha256(raw).hexdigest().upper()
    pin = json.loads((ROOT / "AUTHORITY_PIN.json").read_text())
    if sha != pin["authority_sha256"]:
        sys.exit(f"PIN MISMATCH: {sha[:6]} != {pin['pin_prefix']}")
    src = raw.decode("utf-8").replace("\r\n", "\n")  # authority is stored with CRLF line ends
    if src.count(ANCHOR) != 1:
        sys.exit("authority_rung6: derived_D_eff anchor not found exactly once")
    src = src.replace(ANCHOR, RULE + ANCHOR)
    spec = importlib.util.spec_from_loader("fsot_compute", loader=None, origin=str(path))
    mod = importlib.util.module_from_spec(spec); mod.__file__ = str(path)
    sys.modules["fsot_compute"] = mod
    exec(compile(src, str(path), "exec"), mod.__dict__)
    assert mod.DOMAINS["Quantum_Mechanics"].D_eff == 6
    try:  # the hub adapter (scripts/fsot_canonical_adapter.py) caches its own authority load; hand it this one
        import fsot_canonical_adapter as ca
        ca._MOD, ca._MOD_PATH = mod, path
    except ImportError:
        pass
    return mod, sha
