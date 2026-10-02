# True balanced-ternary arithmetic on binary hardware

`include/fsot/ternary.hpp` is a header-only, freestanding balanced-ternary number system. Every value is
stored as balanced trits {−1, 0, +1}. Every arithmetic step (add, carry, multiply, divide, compare,
round) is a ternary operation, run trit-parallel on two bit-planes. The binary CPU executes the ternary
gate logic. No binary integer or floating-point unit computes the values. Binary integers appear only
as indices, trit counts and power-of-3 exponents, and at explicit I/O boundaries (`from_binary`,
`to_double` for printing).

Before this, the FSOT repos stored trits but computed in binary: trit labels on top of `double`/`f32`
math (see INVENTORY §2). This is the first path where the FSOT core is evaluated with ternary
arithmetic doing the math.

## Types
| type | what | ops |
|---|---|---|
| `BigT<W>` | 64·W-trit balanced-ternary integer (plane P = +1 trits, plane N = −1 trits) | add (ternary full adder + carry loop), neg (swap planes), sub, cmp (MSB-first lexicographic), shl/shr by 3^k (shr = round-to-nearest), mul (radix-27 windows, 13 precomputed multiples), rounded long division (q_i ∈ {−1,0,+1} chosen by comparison, adds only) |
| `TWord<N>` (`Tryte`=9, `Word27`, `Word40`) | N-trit machine word, wraps mod 3^N with an overflow flag | + − × ÷ (rounded), compare, shifts |
| `BTFloat<P>` (`BT40`, `BT72`, `BT110`) | P-trit mantissa × 3^e | + − × correctly rounded (balanced truncation = nearest); ÷ faithful; `sqrt`, `exp`, `log`, `sin`, `cos`, `pow`, `floor`, `fabs`; constants π (Machin), e, ln 3 computed in ternary |

The range reduction is ternary-native:
- `exp(x)`: x = k·ln3 + r. Dividing r by 3^8 is an exact exponent move. A Taylor series follows, then 8 cubings (e^{3t} = (e^t)³).
- `log(x)`: x = m·3^k is read straight off the exponent. Then 2·atanh((m−1)/(m+1)) + k·ln3.
- `sin`/`cos`: reduce mod 2π, divide by 3^6, then apply the triple-angle formulas. The cosine is carried as the versine u = 1−cos, with u(3t) = u(3−2u)², so relative precision does not decay.
- `ln 3 = 2·atanh(1/3) + 2·atanh(1/5)`. The powers of 1/3 are exact trit shifts.

Kernels run at P+16 trits and round once to P.

## Results: FSOT core evaluated in balanced ternary (`Engine<BTFloat<P>>`)
Golden source: `golden/golden_AEB2AD.tsv` (mpmath dps = 50, pinned authority). The 168 values cover all
28 constants plus every domain's look, C, S and the c(72) Ledger B correction. The relative error is
computed in ternary from the golden decimal strings (`tests/test_ternary.cpp`, ctest `ternary`).

| type | ≈ bits | max rel. error, 168 values | max rel. error, 35 S | tolerance in CI |
|---|---:|---:|---:|---:|
| `BTFloat<40>` | 63.4 | 2.5e−17 (BETA) | 1.6e−18 | 1e−16 |
| `BTFloat<72>` | 114 | 1.2e−32 (BETA) | 8.0e−34 | 1e−31 |
| `BTFloat<110>` | 174 | 9.5e−50 (BETA) | 8.6e−51 | 1e−48 |

BETA = exp(−(π^π + e − 1)) has an argument of −37.6, so its condition number is about 38. That is why it
is the worst value at every precision. The binary types show the same effect.
For the same 35 S, the binary paths reach: double 1.1e−15, long double 4.2e−19, `__float128` 7.5e−34,
169-bit 1.6e−50. Ternary at 72 trits (114 bits) matches `__float128` (113 bits). Ternary at 110 trits
matches mpmath's 50 digits. Example: S_cosm(BT110) = −5.02377318176147818681778899140587445673264670e−1;
golden −5.0237731817614781868177889914058744567326467089208e−1.

Word arithmetic tests: an exhaustive 5-trit table (59,049 pairs × add/sub/mul/div/cmp + overflow flag),
4.0 M tryte pairs, 200 k random 40-trit pairs, and 20 k double-width 64×64-trit products against `__int128`.

## Speed (8 vCPU Xeon, GCC 14 -O3 -march=native; `build/bench_ternary`)
| workload | binary | ternary | ratio |
|---|---:|---:|---:|
| Engine build + 35 S, ~64-bit | long double 39 µs | BT40 18.2 ms | 470× slower |
| Engine build + 35 S, ~113-bit | `__float128` 340 µs | BT72 52.5 ms | 154× |
| Engine build + 35 S, ≥169-bit | cpp_bin_float<169> 2.69 ms | BT110 89 ms | 33× |
| 40-trit word add vs int64 add | 0.50 ns | 5.4 ns | 11× |
| 40-trit word mul vs int64 mul | 0.58 ns | 342 ns | 590× |
| 40-trit word div vs int64 div | 3.1 ns | 112 ns | 36× |
| 169-bit vs 110-trit x·y+z | 74 ns | 796 ns | 11× |
| 169-bit vs 110-trit y/(x+z) | 197 ns | 4.3 µs | 22× |
| 169-bit vs 110-trit exp(−x) | 9.5 µs | 112 µs | 12× |

Interpretation: the binary CPU runs ternary arithmetic at about 1/10 to 1/30 the speed of software
multi-precision binary arithmetic at equal precision, and roughly 500× slower than native hardware
words. That is the expected cost of emulating a carry chain in a different radix with no ternary ALU.
The results are as precise as the binary paths at matched precision. Python mpmath takes 4.93 ms for
the 35 S at 50 digits. BT110 takes 89 ms for the full engine build plus all 35 S.

Not optimized yet (next steps): a radix-9 multiplier for short words (the 13-multiple table dominates
`TWord` mul), Newton reciprocal for division, caching sin/cos pairs (the engine asks for both
separately), and a tryte-at-a-time lookup adder.

## Freestanding
`ternary.hpp` includes only `<cstdint>`, `<bit>` and `<type_traits>`. `tests/freestanding_check.cpp` is
compiled with `-ffreestanding -fno-exceptions -fno-rtti -fno-threadsafe-statics`. It computes ALPHA =
ln π/(e·φ¹³) in balanced ternary and a Word27 expression. The object has **zero undefined symbols**: no
libc, libm, heap, exception or guard calls. CTest `freestanding_symbols` enforces this. That makes it the
starting point for the bare-metal demo (milestone 3).
