#!/usr/bin/env python3
"""Run FSOT-2.1-Neural `run_language_loop.py --verify-only` with the SMILES Lab dataset
found at a local path, without editing the Neural repo.

chemical_codon.SMILES_JSON_CANDIDATES only lists two Windows paths (I:\\ archive, C:\\ Desktop)
and has no env override, so this wrapper puts $FSOT_SMILES_DATASET (default:
$XV/data/ (default ~/fsot-xval/data/)FSOT_SMILES_Lab_Dataset.json, the public copy vendored in
FSOT-2.1-Lean/vendor/smiles/) at the front of that list in-process, then runs the script."""
import os, runpy, sys
from pathlib import Path
neural = Path(sys.argv[1] if len(sys.argv) > 1 else str(Path(os.environ.get("XV", Path.home() / "fsot-xval")) / "siblings/FSOT-2.1-Neural")).resolve()
ds = Path(os.environ.get("FSOT_SMILES_DATASET", str(Path(os.environ.get("XV", Path.home() / "fsot-xval")) / "data/FSOT_SMILES_Lab_Dataset.json")))
os.chdir(neural); sys.path.insert(0, str(neural))
import fsot_nuron.chemical_codon as cc
cc.SMILES_JSON_CANDIDATES.insert(0, ds)
sys.argv = ["run_language_loop.py", "--verify-only"]
runpy.run_path(str(neural / "run_language_loop.py"), run_name="__main__")
