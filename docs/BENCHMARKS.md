# Benchmarks — C++ port vs Python authority (box: 8 vCPU x86_64, g++ 14.2 -O3 -march=native)

Python: `vendor/fsot_compute.py` (pin AEB2AD), mpmath 1.4.1, mp.dps=50, CPython 3.13.
(gmpy2 backend measured too: no faster for these sizes, 5.5 ms vs 4.9 ms for 35 domains.)
Run: `./build/bench_cpp` and `python bench/bench_py.py <authority> <FSOT-GPU/fsot_lib/trinary.py>`.

| Workload | Python mpmath | double | long double (x87 80-bit) | __float128 | cpp_bin_float<169> (= mpmath precision) |
|---|---|---|---|---|---|
| Engine init (all constants + 35-domain nest + cached S) | 6.66 ms* | 2.4 µs (2700x) | 5.8 µs (1150x) | 38 µs (176x) | 343 µs (19x) |
| 35 domain scalars | 4.93 ms | 2.0 µs (2460x) | 24.8 µs (199x) | 261 µs (19x) | 1.97 ms (2.5x) |
| All 26 closed-form sections (368 rows) | 5.05 ms | 39.6 µs (128x) | 55.4 µs (91x) | 217 µs (23x) | 1.61 ms (3.1x) |
| One S = K(T1+T2+T3) evaluation | 108 µs | 37 ns (2900x) | 510 ns (212x) | 7.4 µs (15x) | 54 µs (2.0x) |

\* includes re-exec of the module (source compile), the natural Python cold-start.

Ternary (4096 vectors × 256 trits, consensus similarity, code format {0,1,2}):

| Implementation | Time | vs Python |
|---|---|---|
| FSOT-GPU `trinary.py` `trit_similarity_codes` (pure Python) | 58.1 ms | 1x |
| C++ lane loop (same algorithm) | 4.94 ms | 11.8x |
| C++ bit-packed (32 trits/u64, popcount) | 29 µs | ~2000x |

Accuracy at each type (vs 50-digit golden, 643 checks). Max relative deviation, all rows /
excluding the one cancellation row `Chain_consistency_%` (difference of two near-equal ratios):
double 1.2e-12 / 1.1e-14; long double 5.6e-15 / 4.8e-18; __float128 2.4e-30 / 4.8e-33;
cpp_bin_float<169> 1.9e-46 / 1.8e-49. __float128 and mp169 results rounded to double are
bit-identical to `float(mpmath)` for 536/536 real-valued rows (plain double: 265/536, within a few ulp).

## Balanced-ternary vs binary (milestone 1)
See [TERNARY.md](TERNARY.md) for the full table (`build/bench_ternary`). In short: Engine build + 35 S takes BT110 89 ms vs cpp_bin_float<169> 2.69 ms, BT72 52 ms vs `__float128` 0.34 ms, and BT40 18 ms vs long double 0.039 ms, at matched precision.

## Ledger B re-scorer
`fsot_ledger_b` over 478 benchmark files (~197 MB JSON) takes 6.5 s, vs about 6 s for `tools/dump_ledger_b_golden.py`. Both are dominated by JSON parsing. The output is byte-identical.
