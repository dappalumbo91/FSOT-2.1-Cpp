#!/usr/bin/env python3
"""Python baseline: vendor/fsot_compute.py (mpmath, dps=50) and FSOT-GPU trinary.py."""
import importlib.util, json, random, sys, time
from pathlib import Path

auth = Path(sys.argv[1]); trin = Path(sys.argv[2]) if len(sys.argv) > 2 else None

def t(f, min_s=1.0):
    n = 1
    while True:
        t0 = time.perf_counter()
        for _ in range(n): f()
        dt = time.perf_counter() - t0
        if dt >= min_s: return dt / n
        n *= 2

def load():
    spec = importlib.util.spec_from_file_location("fsot_compute_b", auth)
    m = importlib.util.module_from_spec(spec); sys.modules["fsot_compute_b"] = m; spec.loader.exec_module(m); return m

t_init = t(load, 2.0)
m = load()
SECS = ["wave1","validation_suite","wave2","wave3","wave4","wave5","wave6","wave7","wave8","wave9","wave10",
        "lepton_ratios","dynamical_systems","neural_architecture","consciousness_model","homeostasis","soliton_stdp",
        "cross_species","trinary","predictions","chemistry_ionization","chemistry_electronegativity",
        "chemistry_bond_lengths","chemistry_bond_energies","chemistry_molecular","chemistry_radii"]
t_dom = t(lambda: sum(m.domain_scalar(n) for n in m.DOMAINS))
t_sec = t(lambda: sum(len(getattr(m, s)()) for s in SECS))
si = m.ScalarInput(D_eff=m.mpf(12), observed=True)
t_one = t(lambda: m.compute_scalar(si))
print(json.dumps({"type": "python mpmath dps50", "engine_init_s": t_init, "domains35_s": t_dom, "sections_all_s": t_sec, "one_scalar_s": t_one}))
if trin:
    sys.modules.setdefault("fsot_lib", type(sys)("fsot_lib"))
    seeds = type(sys)("fsot_lib.seeds"); seeds.COLLAPSE_THRESHOLD = 0.9174663774653723; sys.modules["fsot_lib.seeds"] = seeds
    spec = importlib.util.spec_from_file_location("trinary_b", trin); tr = importlib.util.module_from_spec(spec); spec.loader.exec_module(tr)
    rnd = random.Random(1); NV, DIM = 4096, 256
    A = [[rnd.randint(0, 2) for _ in range(DIM)] for _ in range(NV)]; B = [[rnd.randint(0, 2) for _ in range(DIM)] for _ in range(NV)]
    t_sim = t(lambda: sum(tr.trit_similarity_codes(A[v], B[v]) for v in range(NV)), 2.0)
    print(json.dumps({"type": "python trinary.py", "similarity_4096x256_s": t_sim}))
