# FSOT-2.1-Cpp

[![CI](https://github.com/dappalumbo91/FSOT-2.1-Cpp/actions/workflows/ci.yml/badge.svg)](https://github.com/dappalumbo91/FSOT-2.1-Cpp/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

A C++20 port of the **FSOT 2.1** computational engine, plus a balanced-ternary (trinary) core.
The authority stays in the hub, **[FSOT-2.1-Lean](https://github.com/dappalumbo91/FSOT-2.1-Lean)**:
`vendor/fsot_compute.py` at pin **AEB2AD**. This repo reproduces that file's numbers in C++, golden-checks
every value against it, and runs it 2–2900× faster depending on the precision you pick.

The law is S = K(T1 + T2 + T3), built from five seeds (π, e, φ, γ, Catalan G) with zero free parameters:
D_eff comes from the 20-generation nest, look/hits/observed are named fold laws, and the Ledger B
amplitude is f = ALPHA.

## What is ported (v0.1)
- All of `fsot_compute.py`: seeds, layer-1/2 constants, the 24-input scalar law, nest → D_eff, the fold laws,
  the 35 domain scalars, all 26 closed-form sections (368 rows: waves 1–10, validation, leptons,
  dynamical systems, neural, consciousness, homeostasis, soliton/STDP, cross-species, trinary, predictions,
  chemistry), and the Ledger B correction c = m(1 + |S|·ALPHA).
- Trinary core (`include/fsot/trit.hpp`) with the same semantics as the trit code in
  [FSOT-Genetics](https://github.com/dappalumbo91/FSOT-Genetics) / [fsot-neuron-zig](https://github.com/dappalumbo91/fsot-neuron-zig) (Zig T1 packing, Rust codon packing),
  [FSOT-GPU](https://github.com/dappalumbo91/FSOT-GPU) / [FSOT-Quantum](https://github.com/dappalumbo91/FSOT-Quantum) (code {0,1,2}, collapse at C_EFF·P_VAR, consensus similarity, H/CX/Bell analogs).
  It adds bit-sliced 32-trit word ops and a 27-trit balanced-ternary integer.
- The FSOTB 27-opcode / 25-register VM core from [FSOT-Reality-OS](https://github.com/dappalumbo91/FSOT-Reality-OS) (`include/fsot/fsotb_vm.hpp`).
  Its EVAL_PANEL reads the live 35-domain nest.

- **Ledger B / benchmark-margin re-scorer** (`include/fsot/host/ledger_b.hpp`, `apps/fsot_ledger_b.cpp`): a C++ port of
  the hub's `benchmark_margin_lib.analyze_benchmark` (scalar/classifier/structural classification, literature-aware
  error, contested rows, gates) plus a re-score of every Ledger B record with the live law. Over all 478
  `data/*_benchmark.json` files at hub commit 6f9c2560, it is **bit-identical to the hub's Python**: 13,841 of 13,841 golden lines,
  477 active / 477 green, 140,088 routed Ledger B records. Runtime is 6.5 s, vs about 6 s for Python, and is dominated by JSON parsing.
- **Balanced-ternary arithmetic** (`include/fsot/ternary.hpp`, see [docs/TERNARY.md](docs/TERNARY.md)): trit/tryte words and a
  balanced-ternary floating-point type. Ternary operations do the actual math. `Engine<BTFloat<110>>` evaluates the whole
  FSOT core in ternary and matches the 50-digit golden to 9.5e-50. The header is freestanding: no heap, exceptions, iostream or libm.
- **Ledger A emit and property routing** (`include/fsot/host/ledger_a.hpp`): bit-identical to the hub Python.
- **Corrected modes** for the audit findings. Parity stays the default and is golden-tested.
  - `fsot_ledger_b --corrected-out` and `fsot_report --corrected`: see "Fixed in C++" in [docs/AUDIT_LOG.md](docs/AUDIT_LOG.md).
- **Evidence tiers** for every gated record and domain ([docs/EVIDENCE_TIERS.md](docs/EVIDENCE_TIERS.md)).
- **A look-elsewhere count** ([docs/LOOK_ELSEWHERE.md](docs/LOOK_ELSEWHERE.md)).
- **A full citation/DOI pass** (`tools/check_citations.py`).
- **Bare metal:** a freestanding `CoreEngine` (`include/fsot/core.hpp`) and an x86_64 kernel. It boots under QEMU and prints, over serial, the 35 domain S and all 368 closed-form rows (26 sections), computed in balanced ternary ([docs/BARE_METAL.md](docs/BARE_METAL.md)).
- **`predict_closed_form`:** CLI for any closed-form row in the freestanding ternary core (`--section`, `--name`, `--digits`, `--trits 40|72|110`, `--corrected`, `--tsv`, `--list-sections`).
- **Freezes:** `fsot_freeze_domain` writes and verifies dated SHA-256 freezes of the live mapping against AEB2AD. The tiers count them per row ([docs/FREEZES.md](docs/FREEZES.md)). New post-freeze public data is tracked in [docs/PROMOTION_WATCH.md](docs/PROMOTION_WATCH.md).
- **Precision pass:** the 188 genuine-prediction misses are split into data handling and formula, with the data-handling causes fixed in corrected mode ([docs/PRECISION_M3.md](docs/PRECISION_M3.md)).
- Specs and audit: [docs/TRIT_SPEC.md](docs/TRIT_SPEC.md) (canonical trit wire format + codon mapping, cross-repo
  mismatches, and the status of fixes T-1 to T-5 in the other repos) and [docs/AUDIT_LOG.md](docs/AUDIT_LOG.md) (neutral rigor log with evidence).

Header-only: `#include "fsot/engine.hpp"`, then `fsot::Engine<double> e; e.domain_scalar("Thermodynamics");`.

## Build (verified on Linux: Debian, GCC 14.2, CMake 4.4, Boost 1.83; CI on ubuntu-latest)
```bash
sudo apt-get install -y libboost-dev nlohmann-json3-dev ninja-build   # Boost: 169-bit type; nlohmann: Ledger B tool (both optional)
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build
ctest --test-dir build --output-on-failure           # golden, trit, ternary, freestanding tests
# Ledger B re-scorer against a hub checkout at AUTHORITY_PIN.json ledger_b_data_commit:
./build/fsot_ledger_b --hub /path/to/FSOT-2.1-Lean --golden golden/ledger_b_6f9c2560.tsv
./build/bench_ternary                                # ternary vs binary results + speed
./build/fsot_report                                  # full report at authority precision
./build/bench_cpp                                    # timings
```
Requirements: a C++20 compiler and CMake ≥ 3.20. Boost headers (Boost Software License) and GCC libquadmath are optional.
Nothing paid.

## How the golden tests tie to the authority
1. `AUTHORITY_PIN.json` records the hub commit `d127c07e`, the raw URL, and SHA-256 `AEB2ADAD…AAC170` of `vendor/fsot_compute.py`.
2. `tools/fetch_authority.py` downloads that exact file and refuses to continue if the SHA doesn't match.
3. `tools/gen_closed_forms.py` checks the SHA again, then translates the authority's closed-form sections from the Python AST
   into `include/fsot/closed_forms.gen.inc`. No number is typed by hand. The few Python-only loops are hand snippets
   bound to a hash of the exact source statement, so if the authority edits one of them, generation fails instead of drifting.
4. `tools/dump_golden.py` runs the authority with mpmath at mp.dps = 50 and writes `golden/golden_AEB2AD.tsv`:
   643 checks covering every constant, every domain's D_eff/hits/observed/look/C/S, Ledger B corrections, all 368 rows,
   and the 5 % pass counts.
5. `tests/test_golden.cpp` compares the C++ engine to the golden file at every available number type.
   CI's `regen-diff` job repeats steps 2–4 and fails if the generated files differ from what's committed.

When the hub moves its pin, update `AUTHORITY_PIN.json`, run `cmake --build build --target fsot_regen`
(configure with `-DFSOT_AUTHORITY=<path>`), and commit the regenerated files together.

## Precision (vs the 50-digit golden, 643 checks, all pass)
| Number type | Max relative deviation | Excluding the one cancellation row¹ | Rounded to double = `float(mpmath)` |
|---|---|---|---|
| `double` | 1.2e-12 | 1.1e-14 | 265/536 (others within a few ulp) |
| `long double` (x87 80-bit) | 5.6e-15 | 4.8e-18 | — |
| `__float128` | 2.4e-30 | 4.8e-33 | **536/536** |
| Boost `cpp_bin_float<169 bits>` (same precision as mpmath dps 50) | 1.9e-46 | 1.8e-49 | **536/536** |

¹ `Chain_consistency_%` subtracts two nearly equal ratios, so it magnifies rounding.
Example: S_thermo = 0.93638756406297475802… (169-bit), and 0.9363875640629747 when rounded to double, matching Python exactly.

## Precision against published uncertainties (z ≤ 1 gate)
`apps/fsot_precision` scores every physics prediction with z = |value − central|/σ ≤ 1. σ comes from PDG 2024, CODATA 2022 and AME2020
(`reference/published_2026-10-02.tsv`; every entry is checked against committed evidence by `tools/check_references.py`). The gate is configured
once, in `include/fsot/host/precision_gate.hpp`. The legacy 2 % check and ppm are reported next to it.

**Current gate (FREEZE_2026-10-02bg):** **91/91 pass z ≤ 1** (90/91 pinned only; frozen-pending column 91/91; 89/89 with H0 and τ_n deferred; 89/91 under 2 %). The Higgs/W record row is leaf m_H_MeV / leaf m_W_MeV = 1.55729801381558, z 0.3681, on the low side of 1.55781070360287 ± 0.00139275. The domain scalar stays in the report at record 0. OD-2 still supplies Ω_Λ and σ_8. The CKM Jarlskog record row is A²λ⁶η̄ = 3.13591416718917×10⁻⁵, z 0.1224, flat error 0.510%. G/π⁹ stays in the report with record 0. The deuteron moment record row is `(G⁴+Poof)(1+α²(1+1/(4π²)))` = 0.857438231894115, z 0.7299. `sin²θ₂₃` and `δ_CP` still fail 2 % and pass z. N_eff and the baryon-to-photon ratio stay on their closed forms. Median record ppm is 74.13. Worst record ppm is 34691 (`δ_CP`). A fresh `fsot_precision` run matches [audit/precision_2026-10-02.md](audit/precision_2026-10-02.md) byte for byte. The dated paragraphs below keep the count each round printed. All 50 hub seed leaves (`include/fsot/host/seed_leaves.hpp`) pass. [docs/PRECISION_REPORT.md](docs/PRECISION_REPORT.md) opens with the 2026-10-02b snapshot (85/91, Γ_Z/M_Z, deuteron binding, and μ_d still open in that snapshot) and ends with the bg section.
2026-10-06bh (`audit/FREEZE_2026-10-02bh.md`): l̄₁ = −0.15209 (z 0.413) and l̄₂ = 4.24299 (z 0.570) from the KSRF rho D-wave at the physical pion mass. The precision gate is not rebuilt. The one-loop F_π stays 92.887 MeV. The two-loop insertion still needs l̄₃, which is outside its bar, and k_F, which is not fixed.
2026-10-06: the leaf-curvature light tadpole in `include/fsot/host/axial_residue.hpp` is 92.672790938 MeV, z 3.631 against the lifetime center. It misses. The one-loop truncation stays 92.8866215097 MeV. The precision gate is not rebuilt.

2026-10-06: the catalog half of `owner-decisions-2026-10-02i` is evaluated in `include/fsot/host/catalog_leaves.hpp` and locked by `catalog_leaves_pass`. Thirteen leaves pass on the AEB2AD seeds: Al, Cl, Si, P, S, Ar, and K first ionization; methane, ammonia, and ethanol boiling points; the NaCl lattice energy; olive-oil viscosity; and the cyclohexane cryoscopic constant. The Γ_Z/M_Z catalog leaf was already the record row `leaf:Gamma_Z/M_Z`. The authority pin stays AEB2AD. Quantum_Mechanics keeps its derived depth. Calcium, hydrogen, CO₂ sublimation, deuteron binding, and the deuteron moment stay on their bare formulas. The 91 are not rescored.

2026-10-06: the water-to-air sound ratio from the T2 lab suite is evaluated in `include/fsot/host/fluid_lab.hpp` and locked by `fluid_lab_pass`. It is `(e+φ)(1−α/(1+C_eff cos θ_S))` against 1482.4/343.2, with the bar the quadrature of half a printed tenth on each speed. Diatomic γ = 7/5 and the US 1976 scale height R T/(μ g) equal their comparisons by construction and are not installed. The 91 are not rescored.
Post-hoc refinements are frozen as tier frozen-pending in [docs/freezes/REFINEMENTS_2026-10-02.md](docs/freezes/REFINEMENTS_2026-10-02.md) and
[docs/freezes/REFINEMENTS_2026-10-02b.md](docs/freezes/REFINEMENTS_2026-10-02b.md) (committed before scoring) and are never counted as confirmed.
A pre-registered train/test search for class-level dressing rules (docs/freezes/PROTOCOL_2026-10-02c.md, REFINEMENTS_2026-10-02c.md; 539 patterns, 5 classes) accepted **no** rule; see PRECISION_REPORT §2026-10-02c.
2026-10-02d re-derivations (docs/freezes/DERIVATIONS_2026-10-02d.md): Γ_Z built from partial widths, plus new rows Γ_W, τ_μ, τ_τ, μ_n, μ_t, μ_h and a two-nucleon μ_d, all frozen before scoring. None passes. The G_F-normalised rows fail because Damian's seed v = 58.24 GeV; see PRECISION_REPORT §2026-10-02d.
2026-10-02e (docs/freezes/DERIVATIONS_2026-10-02e.md): seed v fixed to its documented relation. On the primary on-shell scheme G_F is −3.6 % (tree level, no Δr), so Γ_Z/M_Z is still open. The new α_s(m_τ) and BR(τ→eνν̄) rows pass (frozen-pending).
2026-10-02f (docs/freezes/DERIVATIONS_2026-10-02f.md): Δr built from FSOT leaves (FSOT-only hadronic H1: 0.0296; with PDG Δα_had H2: 0.0332). G_F is −0.66 % (H1), Γ_Z/M_Z z 11.2, still open. The lost-route search across all repositories found no route for μ_n, μ_t, f_π, P_D, Δr or α(M_Z).
2026-10-02g (docs/freezes/DERIVATIONS_2026-10-02g.md): LEPTOP effective Z couplings in Γ_Z. The pre-declared PDG-input validation **failed** (Γ_Z 2.49592 vs SM 2.4940 ± 0.0009), so nothing is confirmed. FSOT H1: Γ_Z/M_Z z 8.0, still open; see PRECISION_REPORT §2026-10-02g.

2026-10-02h (audit/FREEZE_2026-10-02h.md): each miss was traced to its first break step, then diagnosed and branched. GZ-1 (complete Δr + Freitas Γ_Z) passes its PDG-input validations but fails with FSOT's own Δα_had (z 3.84). No FSOT-native Δα_had route exists yet. Counts are unchanged at 85/91 confirmed; see PRECISION_REPORT §2026-10-02h.

2026-10-02i (audit/OWNER_DECISIONS_2026-10-02i.md): owner decisions OD-1 (score the Δm² ratio against Δm²21/Δm²31) and OD-2 (Quantum_Mechanics D_eff = 6, the pre-2026-09-11 value), added as labelled owner-decision rows next to the pinned rows. The gate is **87/91 confirmed** (85/91 pinned only).

2026-10-02i (audit/FREEZE_2026-10-02i.md): two light-hadron routes (constituent-quark m_ρ, quark–hadron-duality Δα_had) fail their PDG-input validations, so no FSOT-native hadron sector exists yet. GZ-1 with the duality Δα_had gives Γ_Z/M_Z z 0.68 (frozen-pending, not confirmed).

2026-10-02j (audit/FREEZE_2026-10-02j.md): walk-down from FSOT's absolute scale to the strong sector. Λ^(5) from the FSOT α_s(M_Z) is 209.5 MeV vs FLAG 213(8) (z 0.43, validated method; not one of the 91 rows). No FSOT-native f_π, g_A or g_πNN: the NDA and quark-model routes fail their validations, and GMOR and Goldberger–Treiman validate but lack FSOT inputs. Hence the KSRF/Δα and deuteron chains were not run, and the gate stays at 87/91.

2026-10-02k (audit/FREEZE_2026-10-02k.md): θ_S = sin(ψ_con η_eff) has no known physical counterpart. The pion, kaon, D, W, Z, H and nuclear-binding leaves are pure numbers read in MeV and are not tied to the m_e anchor; the missing factor contains the SI-defined value of e. F_π (91.8 MeV) and g_πNN (12.92) come out only as hybrids with lattice ratios. m_ρ by lowest-meson dominance misses its 1 % gate, so the Δα and deuteron chains were not run. The gate stays at 87/91.

2026-10-02l (audit/FREEZE_2026-10-02l.md): the pion and kaon were treated as pseudo-Goldstone bosons (leading-order chiral perturbation theory plus Dashen's EM term), using FSOT's quark-mass ratios and its π± and K± leaves. The held-out K⁰ comes out at 497.597 MeV against 497.611(13) (−0.003 %). The π⁰ and η miss by about 3 %, the known limit of leading order. GMOR gives m_ud 3.60 MeV and m_s 99.7 MeV, but only as hybrids. A frozen D_eff → unit map (3 families, trained on π±, B(²H) and T_CMB) puts 0 of 10 held-out leaves within 2 %. The scale factor each leaf needs is set by the SI unit it is read in, not by its domain. The gate stays at 87/91.

2026-10-02m (audit/FREEZE_2026-10-02m.md): an FSOT-only pion decay constant, F = m_p/(2√3π) = 86.22 MeV, from the quark-level sigma model with N_c = 3. It is within 0.55 % of the chiral-limit value. The π⁰ from the electromagnetic sum rule comes out at 134.40 MeV (−0.43 %) and the K⁰ via Q at +0.13 %. The η and η′ fail. D_eff/S does not organize the m_e-multiple ratios. The gate stays at 87/91.

2026-10-02n (audit/FREEZE_2026-10-02n.md): an FSOT-only physical F_π of 90.51 MeV (−1.7 %), from the NLO step with l̄₄ = N_c in the quark-level sigma model. A valence chiral-quark-soliton g_A of 1.178 (−7.7 %) misses its 2 % gate, so the Δα → Γ_Z/M_Z chain stays gated off. The leading-order deuteron radius misses by 23 % (no effective range). D_eff maps on one reference leaf per domain fail. The gate stays at 87/91. The physical meaning, units path and status of every quantity are in docs/PHYSICAL_MAP.md.

2026-10-02o (audit/FREEZE_2026-10-02o.md): a full-Dirac-sea chiral quark soliton (Kahana–Ripka basis, Pauli–Villars) at M = m_p/3 is unbound (E = 3.41 M). Its leading-order g_A^(0) = 0.742 misses by 42 % without the 1/N_c rotational term, and Δ−N = 177 MeV misses by 40 %, so the Δα → Γ_Z/M_Z chain stays gated off. A one-pion-exchange deuteron with FSOT g_πNN gives r_d −4.1 %, Q_d −14 % and η −7.3 %. SU(6) μ_n (−2.7 %) and μ_d (+3.8 %) fail, and so does l̄₄ = 1 + ln(M_Q²/M_π²) (F_π −2.3 %). The gate stays at 87/91.

2026-10-02p (audit/FREEZE_2026-10-02p.md): adding the 1/N_c rotational term gives a soliton g_A of 1.1755 (−7.8 %). The Δα chain stays gated off. Soliton magnetic moments come out high (μ_p +17 %, μ_n +31 %). The one-loop linear-sigma-model l̄₄ = 4.66 gives an FSOT-only F_π of 92.89 MeV (+0.89 %, agrees). The DP instanton χ_top is +24 % high. The own-physics T_CMB is +0.25 % (z 11). The gate stays at 87/91.

2026-10-02q (audit/FREEZE_2026-10-02q.md): adding the physical pion mass to the soliton gives μ_p = 2.766 (−0.96 %) and μ_n = −1.926 (+0.67 %). These are not confirmed because the validation run was cut by the time box. g_A = 1.391 (+9.1 %) and Δ−N = 190 MeV both fail, and the soliton is still unbound at M = m_p/3. The gate stays at 87/91.

2026-10-02r (audit/FREEZE_2026-10-02r.md): round q's validation, run late, passed for g_A, μ_p and μ_n, so the soliton μ_p (−0.96 %, z 3.3e7) and μ_n (+0.67 %, z 2.8e4) were reported as agreeing under a 2 % gate. That gate does not count (z rule, round u), and the values are not basis-stable (round t). μ_d = 0.808 (−5.7 %) fails. Tracing χ_top showed the unquenched Λ^(3) had been fed into a pure-gauge instanton chain; with quenched Λ^(0) = 0.772 Λ^(3) (FLAG), χ^{1/4} = 177 MeV (−4.5 %, z 1.46, a miss). The η (−7.6 %) and η′ (+5.8 %) now point at the LO U(3)+WV matrix. The gate stays at 87/91.

2026-10-02s (audit/FREEZE_2026-10-02s.md): the g_A shift comes from adding the physical pion mass, not from the basis cap. The Dirac-sea axial sum goes from 0.011 to 0.156 and g_A^(1) rises 22 %; the fix is still open. η/η′ at next order (FKS): η = 538.4 MeV (−1.7 %, z 557, a miss), η′ = 882.6 MeV (−7.9 %, fails), with χ as the remaining step. The gate stays at 87/91.

2026-10-02s2 (audit/FREEZE_2026-10-02s2.md, owner directive): nothing hybrid counts. Results built on lattice, FLAG or fit inputs (χ_top, η/η′, GMOR quark masses, the J-1 external-threshold Λ's) are now listed as scaffolding and never counted. With FSOT-only quark thresholds, Λ^(4) = 292.07 MeV and Λ^(3) = 334.43 MeV, both within 1σ of FLAG. Λ^(0)/Λ^(3) is an open derivation that needs a pure-gauge hadronic scale leaf. The gate stays at 87/91.

2026-10-02t (audit/FREEZE_2026-10-02t.md): FSOT's gluon-condensate pin fixes the instanton density, giving χ^{1/4} = 200.1 MeV (+8.0 %, z 2.6, a miss under the z rule) from FSOT inputs only. The leading-order η′ fails (+20 %). At K 12 the massive soliton gives g_A +12.3 %, μ_p −5.4 % and μ_n −6.2 %, so the round-q/r K 8 μ agreement is not basis-stable and is withdrawn. The gate stays at 87/91.

2026-10-02u (audit/FREEZE_2026-10-02u.md, u2): only z ≤ 1 counts now, and earlier percentage-gate "passes" are re-labelled as misses. The K 14 soliton run did not finish inside the cap. Routing Λ^(0)/Λ^(3) through FSOT (trace anomaly at fixed vacuum energy) gives 0.837 and χ^{1/4} = 190.3 MeV (z 0.88); this route was chosen after round t and is disclosed as provisional. The g_A ordering derivation is still open. The gate stays at 87/91.

2026-10-02v (audit/FREEZE_2026-10-02v.md): the soliton now runs to K 16 with a windowed scan (validated against round t to 3.8e-10). The pre-registered K 14–16 extrapolation misses for g_A (1.502, z 5.6) and Δ−N (180.8 MeV, z 41). μ_p and μ_n come out at z ≈ 1 only because the K 16 jump inflates the theory uncertainty; the K sequence does not converge, so these are not counted as evidence. FSOT F_K/F_π = 1.273 (z 38; the L4 = 0 step fails) and FKS η/η′ = 574/951 MeV both miss. Every PHYSICAL_MAP row now carries a reference type (measured / model-computed / lattice-computed / scheme-dependent / contested). The gate stays at 87/91.

2026-10-02w (audit/FREEZE_2026-10-02w.md): the μ oscillation across K is numerical. The valence level and the moment of inertia are K-stable, and only the μ_V^(0) sea sum moves, through a non-decaying high-grand-spin tail. Δ−N fails at the soliton quark mass M = m_p/3, where the valence inertia alone is too large; an M = 420 MeV run gives 296.7 MeV. A J-dependent (rotating) profile lowers Δ−N further. FSOT scalar saturation derives L4 = 0 and gives F_K/F_π = 1.506 (miss). χ is now scored only through the η/η′ observables (WV combination +25 %, miss). The gate stays at 87/91 (85/89 with H0 and τ_n deferred).

2026-10-02x (audit/FREEZE_2026-10-02x.md): an energy cutoff does not converge the μ sea sum, so μ is not rescored. The instanton-vacuum gap equation with FSOT's own instanton density gives the soliton quark mass M(0) = 346 MeV, but Δ−N rises only to 200 MeV because the frozen setup ties F to M. The Γ_Z/M_Z physics route already sits at z 0.68; it is insensitive to the failing Δα_had step and is blocked by external parametrisation inputs (an owner decision). The gate stays at 87/91.

2026-10-02y (audit/FREEZE_2026-10-02y.md): with the soliton in proton units and F held at FSOT's chiral value, (M_Δ−M_N)/m_p = 0.244 (229 MeV, K-stable) and g_A = 1.48; both miss. Putting the heavy-quark thresholds of the duality route at the quark pole masses recovers 58 % of the Δα_had deficit, but its validation still fails. The FSOT-only one-loop chain gives Γ_Z/M_Z 0.02717 (z 7.7), with the next divergence in the higher-order Δr. The round-i Freitas/ACFW chain is scaffolding. The gate stays at 87/91.

2026-10-02z (audit/FREEZE_2026-10-02z.md): the soliton inertia stays at or above 2.1/M at every size, because a smaller valence part is made up by the sea. Δ−N therefore tracks the absolute quark mass ratio M/m_p = 0.369, which is the diverging step; nothing was rescored. With the higher-order Δr terms (resummation, O(αα_s²), O(G_F²m_t⁴)), Γ_Z/M_Z moves from z 7.7 to z 5.0, still a miss. A direct radiation-density route gives T_CMB = 2.7434 K (+0.66 %, information only). The gate stays at 87/91.
2026-10-02aa (audit/FREEZE_2026-10-02aa.md): reading the condensate pin in proton units lowers M/m_p to 0.346, which moves Δ−N further from the measurement (z 47); the KSRF light-quark Δα_had undershoots (validation fails), so Γ_Z/M_Z is at z 6.7; the FSOT pins offer no T_CMB route that avoids H0. The gate stays at 87/91.
2026-10-02ab (audit/FREEZE_2026-10-02ab.md): the DP variational instanton size gives R/ρ̄ = 2.47 and M/m_p = 0.458, so Δ−N comes out at z 10.9 (edge minimum) and g_A at z 171, both misses; the deuteron central-force trace is unbound until the tensor force is added; T_CMB has no anchor inside FSOT. The gate stays at 87/91.
2026-10-02ac (audit/FREEZE_2026-10-02ac.md): with the wide soliton window Δ−N is at z 8.0 and g_A at z 202 (the rotational term is 0.634); the tensor-OPE deuteron with a soliton-size form factor binds 4.0 MeV on OPE alone but is unbound once σ and ω are added; the FSOT matter-to-baryon ratio is 6.37. The gate stays at 87/91.
2026-10-02ad (audit/FREEZE_2026-10-02ad.md): PV-regularising the sea part of the time-ordered rotational term gives g_A = 1.2845 (z 7.0, +0.7 %); with the soliton σ coupling, OPE+σ binds the deuteron at 7.5 MeV but ω unbinds it; T_CMB from the FSOT age is 2.7285 K (z 5.0, +0.11 %). The gate stays at 87/91.
2026-10-02ae (audit/FREEZE_2026-10-02ae.md): PV-regularising the rotational μ terms gives μ_p 2.197 and μ_n −1.596 at K 14, but they move about 3 % from K 12, so μ is not scored; g_A at K 14 is 1.2911 (z 2.3) and Δ−N z 4.7; the ω Dirac form factor still leaves the deuteron unbound; the T_CMB trace shows the FSOT cosmology pins aren't mutually consistent (closure 0.99816). The gate stays at 87/91.
2026-10-02af (audit/FREEZE_2026-10-02af.md): the μ_V^(0) grand-spin decomposition shows the K 12→14 drift is a common box-size rescaling (box tied to K), not a pion tail, so μ is still not scored; the deuteron with ω tensor/spin-orbit and σ spin-orbit potentials is still unbound; a self-consistent flat FSOT cosmology branch gives T_CMB 2.725739 K (z 0.40; η-route circularity flagged) and h 0.6745 (H0 pin −1.45 %, audit finding). Totals unchanged at 87/91.
2026-10-02ag (audit/FREEZE_2026-10-02ag.md): FSOT η = Poof¹¹/(πγ) uses no T_CMB, so the round-af T_CMB is an FSOT derivation (proposed record route for the hub). With the box and cutoff decoupled from K, μ_p, μ_n, g_A and Δ−N converge and all miss (z 21.9, 9.4, 1.56, 6.1); μ still depends on the cutoff (4–5 %). In the deuteron, the ω central term over-repels by 37× the binding. Totals unchanged at 87/91.
2026-10-02ah (audit/FREEZE_2026-10-02ah.md): the μ cutoff dependence is entirely in the μ_V^(0) sea sum, which oscillates with kmax (2.81/2.64/2.90 at kmax 12/14/16) after a 90 % PV cancellation, so μ is not scored. The full valence + PV-sea scalar charge (12.1) is not kmax-stable (3.0 %), so it is not adopted. Totals unchanged at 87/91.
2026-10-02ai (audit/FREEZE_2026-10-02ai.md): a two-subtraction PV scheme (FSOT F + condensate pin) stabilises the scalar charge but fails the energy tolerance (−3.7 %) and leaves the μ_V^(0) kmax oscillation (a basis effect), so μ is not scored; the σ-projected scalar charge is not kmax-stable, so it is not adopted. Totals unchanged at 87/91.
2026-10-02aj (audit/FREEZE_2026-10-02aj.md): evaluating μ_V^(0) and the σ charge from regularised local densities reproduces the matrix-element sums exactly; the kmax oscillation sits in the interior density, so μ is not scored and the σ charge is not adopted. Totals unchanged at 87/91.
2026-10-02ak (audit/FREEZE_2026-10-02ak.md): the μ_V^(0) sea oscillation is confirmed to follow the shell count (kmax·D). A smooth spectral convergence factor stabilises the sums but shifts the energy by +10 % against the sharp values, so validation fails and μ and the σ charge are not scored. Totals unchanged at 87/91.

2026-10-03 (adoption of the 2026-10-02ah T_CMB section): the CMB record row is the η route, n_γ0 = ω_b ρ_c,100 / (m_p η), T_0 = (π² n_γ0 / (2ζ(3)))^{1/3} ħc/k_B = 2.72573880197729 K against FIRAS 2.7255(6), z 0.398. ω_b is wave1|Omega_b_h2 and η is wave10|eta_baryon_photon. The closed form φ² + P_base·|S_cosm| remains in the report as the superseded row. The gate is **88/91 confirmed** (86/91 pinned only; the frozen-pending column is 88/91; 86/89 with H0 and τ_n deferred). Caveat: the observed η the formula was compared to is itself inferred with T_CMB³ (target choice, not an input). The same flat branch gives h 0.674541, against the H0 pin by −1.448%, Ω_Λ by +0.408%, Ω_m by −0.299% and Ω_r by +0.327%. The pin set sums to 0.99816.

2026-10-02al (audit/FREEZE_2026-10-02al.md): averaging the single-PV sums over one radial-shell period passes validation at kmax 12, but the kmax-14 level did not finish within the 10-min cap, so μ is not scored. The averaged σ charge still moves 4.2 % between kmax 12 and 14, so it is not adopted. The core-SHA CTest no longer needs `sh` on Windows. Totals 88/91 (86/91 pinned only, 86/89 with H0 and τ_n deferred), after the owner's record commit b99fc29 adopted the η T_CMB route. Round al changes no record row.

2026-10-02am (audit/FREEZE_2026-10-02am.md): under the owner's operational budget change, the kmax-14 shell-average samples run as one detached resumable job (still running; μ is scored when it finishes). Δα_had from the soliton-radius ρ mass with lowest-meson-dominance duality couplings fails its PDG-input validation (−6.5 %; Γ_ee(ρ) 4.4 keV vs 7.04), so G_F and Γ_Z/M_Z (z 6.1) stay misses. Totals 88/91 (b99fc29).

2026-10-02an (audit/FREEZE_2026-10-02an.md): the Γ_ee(ρ) shortfall was traced through a two-FESR f_ρ. α_s and the finite ρ width raise it from 4.38 to 5.40 keV (PDG 7.04); the remaining factor 1.30 points at a gluon-condensate term FSOT does not yet supply. Δα_had still fails validation, and Γ_Z/M_Z stays a miss (z 5.7). The kmax-14 job has 3 of 4 samples. Totals 88/91 (b99fc29).

2026-10-02ao (audit/FREEZE_2026-10-02ao.md): the kmax-14 shell average finished and validates, but μ_p and μ_n still move 2.4 % and 3.3 % between kmax 12 and 14, so they are not scored. Adding the gluon condensate to the vector sum rule raises Γ_ee(ρ) to 5.66 keV (PDG 7.04); Δα_had still fails validation, and Γ_Z/M_Z stays a miss (z 5.6). Totals 88/91 (b99fc29).

2026-10-02ap (audit/FREEZE_2026-10-02ap.md): the soliton's isovector charge radius comes out at r_V² 1.004 fm² against 0.822 fm² from the proton and neutron radii (+22 %), so the form-factor route to f_ρ breaks at its first step. After the break, for information: ρ pole 533 MeV, f_ρ 146 MeV, Γ_ee 8.9 keV. A new additive kmax-16 rule is frozen and its job is running. Totals 88/91 (b99fc29).

2026-10-02aq (audit/FREEZE_2026-10-02aq.md): with shell averaging, the soliton isovector radius is 1.004 fm² at both kmax 12 and 14 (stable to 0.05 %), so the 22 % excess is physical. It comes from the regularised Dirac sea (31 % of the isovector charge, at 1.85 fm²); the valence level alone gives 0.62 fm². Nothing is rescored. Totals 88/91 (b99fc29).

2026-10-02ar (audit/FREEZE_2026-10-02ar.md): the self-consistent profile at the scoring cutoff (K 14, D 14, kmax 12, mix 0.2) is still moving after the locked 40 steps (dtheta 0.005632, E/M 2.21557). The j=0 radius on that unfinished profile is 1.05233 fm², 4.777% from the DPP value, so it stays information. The M = m_p/3 sea check stays unstarted. Totals 88/91 (b99fc29).

2026-10-02as (audit/FREEZE_2026-10-02as.md): taking the whole force-balance step, the gap jumps to 0.194 and then orbits between about 0.19 and 0.008. Sixty full passes end at dtheta 0.0255. The j=0 radius on that orbit point is 1.12163 fm², information. The sea check stays unstarted. Totals 88/91 (b99fc29).

2026-10-02at (audit/FREEZE_2026-10-02at.md): half of the force-balance step shrinks the gap once, from 0.00552 to 0.00524, and the next pass opens it to 0.194. Two hundred passes then orbit about every nine passes and end at dtheta 0.02238. The j=0 radius on that orbit point is 1.14252 fm², information. The sea check stays unstarted. Totals 88/91 (b99fc29).

2026-10-02au (audit/FREEZE_2026-10-02au.md): re-entering the solver with the original 0.2 damper closes the gap for four passes, from 0.00552 to 0.00519, and the fifth pass opens it to 0.194. Four hundred passes orbit and end at dtheta 0.02223. The j=0 radius on that orbit point is 1.15100 fm², information. The sea check stays unstarted. Totals 88/91 (b99fc29).

2026-10-05: the Lean catalog on `owner-decisions-2026-10-02i` at `7e106a5` reads Γ_Z/M_Z as `(φ⁵/e⁶)(1−α/φ)` = 0.02736580363935934, 0.029 uncertainties low of `2.4955/91.1880`. The engine formula stays `φ⁵/e⁶` and stays a miss. The C++ record row stays that bare law. Totals 88/91 (b99fc29). The same catalog pass records Al, Cl, Si, P, S, Ar, and K first ionization, the methane, ammonia, and ethanol boiling leaves, and the NaCl lattice leaf. Calcium, hydrogen, CO₂ sublimation, deuteron binding, and the deuteron moment stay on their bare formulas.

2026-10-02av (audit/FREEZE_2026-10-02av.md): one continuous call of the 0.2 damper, budget 400, from the DPP, matches the 40-step close through step 39 and keeps closing through step 43 (dtheta 0.00519). Step 44 opens the gap to 0.194. Four hundred steps end at dtheta 0.02018. The j=0 radius on that point is 1.15018 fm², information. The sea check stays unstarted. Totals 88/91 (b99fc29).

2026-10-05 (audit/FREEZE_2026-10-02aw.md): the Γ_Z/M_Z record row is the Lean catalog leaf `(φ⁵/e⁶)(1−α/φ)` = 0.0273658036393593 against `2.4955/91.1880`, z 0.02916. The bare seed stays in the report as the superseded row. The gate is **89/91 confirmed** (87/91 pinned only; the frozen-pending column is 89/91; 87/89 with H0 and τ_n deferred). Deuteron binding and the deuteron moment stay on their bare formulas.

2026-10-05 (audit/FREEZE_2026-10-02ax.md): the deuteron binding record row is `(√e/e+φ)(1+α³·e³/φ⁵)` = 2.22456621408218 MeV against the AME2020 mass excess 2.224566229 MeV, z 0.0339. The bare sum stays in the report as the superseded row. The mass-excess quotient names `e³/φ⁵` as the nearest short product; the next one, `φ+φ⁻³`, is 1.49118 times farther. The gate is **90/91 confirmed** (88/91 pinned only; the frozen-pending column is 90/91; 88/89 with H0 and τ_n deferred). The deuteron moment stays on `G⁴+Poof`. The Lean engine file stays the bare sum.

2026-10-05 (audit/FREEZE_2026-10-02ay.md): the deuteron moment record row is `(G⁴+Poof)(1+α²(1+1/(4π²)))` = 0.857438231894115 against CODATA 2022 0.8574382335(22), z 0.7299. The same algebra is `1+α²+(α/(2π))²`. The bare sum stays in the report as the superseded row. The α² quotient names that weight after the named-seed window came back empty. Two closer stacks, `α²+α³(π+γ²)` and `α²+α³(π+1/3)`, use a second power and are not the record. The gate is **91/91 confirmed** (89/91 pinned only; the frozen-pending column is 91/91; 89/89 with H0 and τ_n deferred; 89/91 at 2%). The Lean engine file stays `G⁴+Poof`.

2026-10-05 (audit/FREEZE_2026-10-02az.md): the step-44 gap of 0.19380 rad sits at r = 0.9063/M (r/D = 0.0647, 0.416 fm). The edge past 0.75 D peaks at 1.65e-5 rad, inside the 0.001 rad tolerance. 231 of 1500 bins exceed 0.05 rad, all of them interior. The tolerance and the mixer were left as they are. The 22% isovector-radius excess stays its own miss. Totals stay 91/91. The sea check stays unstarted.

2026-10-05 (audit/FREEZE_2026-10-02ba.md): the DPP isovector radius at M = m_p/3, same x_DPP, box j=0, is 1.58254 fm². The committed j=0 value at the diagnostic mass is 1.00435 fm². Holding that shape fixed would give 1.89749 fm². The recomputed pion cloud shrinks r M² by 0.834, and the fm radius is 1.58254. The regularised sea holds 25.4% of the isovector charge, at 2.872 fm², against 31.3% at 1.853 fm² on the committed profile. M = m_p/3 stays off the record. Round o already has that soliton unbound at E = 3.41 M. Totals stay 91/91.

2026-10-05 (audit/FREEZE_2026-10-02bb.md): the same diagnostic DPP, after the solver's edge tail, misses stationarity by 0.17212 rad at r = 0.3976/M (0.1825 fm). That is the committed step-0 gap, reproduced exactly. The bare Dirac sea and the Pauli-Villars sea each hold about half of the scalar and pseudoscalar densities and cancel at 99.29% and 98.97%. What remains of the sea is the same size as the valence. The meson constant from the chiral-limit F moves that angle by 0.00311 rad. The step-44 site, 0.416 fm, is only 0.0317 rad off on this profile. Nothing is installed. Totals stay 91/91.

## Benchmarks (8-vCPU x86-64, GCC 14 -O3 -march=native; Python 3.13 + mpmath, dps 50)
| Workload | Python mpmath | double | long double | __float128 | 169-bit |
|---|---|---|---|---|---|
| Engine init (constants + nest + cached S) | 6.66 ms | 2.4 µs | 5.8 µs | 38 µs | 343 µs |
| 35 domain scalars | 4.93 ms | 2.0 µs (2460×) | 24.8 µs (199×) | 261 µs (19×) | 1.97 ms (2.5×) |
| All 26 sections (368 rows) | 5.05 ms | 39.6 µs (128×) | 55.4 µs (91×) | 217 µs (23×) | 1.61 ms (3.1×) |
| One S evaluation | 108 µs | 37 ns (2900×) | 510 ns | 7.4 µs (15×) | 54 µs (2.0×) |

| Ternary: consensus similarity, 4096 × 256 trits | Time |
|---|---|
| FSOT-GPU `trinary.py` (pure Python) | 58.1 ms |
| C++ lane loop | 4.94 ms (12×) |
| C++ bit-packed, 32 trits/u64 + popcount | 29 µs (~2000×) |

Details are in [docs/BENCHMARKS.md](docs/BENCHMARKS.md). `__float128` is the practical sweet spot: 33 digits, and it reproduces Python's doubles exactly.

## Windows / MSVC caveat
MSVC has no `__float128`, and its `long double` is the same as `double`. On MSVC the CMake script builds the
`double` and 169-bit Boost types only (get Boost headers from vcpkg: `boost-multiprecision boost-math`).
Use the 169-bit type when you need values that match Python exactly. MinGW-w64 GCC does support `__float128`. Damian reproduced the MSVC build on MSVC 19.44 (2026-10-02). The portability fixes are listed in docs/AUDIT_LOG.md H-33, and CI job `build-test-msvc` (windows-latest, blocking since 2026-10-02j, H-35) builds it and checks that the precision report is byte-identical. Windows steps are in docs/REPRODUCE.md §1.

Full reproduction guide (WSL2 recommended on Windows, with expected outputs for every check): [docs/REPRODUCE.md](docs/REPRODUCE.md).
One-shot Linux/WSL2 check of all four CI jobs: `bash xval/cpp_check.sh`.

## Roadmap (from [docs/PORT_PLAN.md](docs/PORT_PLAN.md))
1. ~~Ledger B panel re-scorer~~ (milestone 1) · ~~Ledger A emit + property routing~~ (milestone 2)
2. ~~Closed-form sections in the freestanding core; `predict_closed_form` CLI; freezes; trit fixes T-1 to T-5~~ (milestone 3)
3. Trinary syntax rows, opcode registry loader, wire-format FSOTB loader — 1–2 days
4. Extend the codegen to the hub's pure-math modules (seed_flavor, gr_sm, matter_antimatter, uniqueness_confinement, ckm_pmns, complex_interaction) — 1–2 weeks
5. Numeric kernels (nse3d, path_sum, dynamics) — about 1 week
6. Data panels and gauntlet modules — 3–4 weeks
7. Python binding (pybind11) and a CUDA bridge for ternary attention; a C++ replay alongside the hub's multiprover — about 1 week

A survey of the engine and of every trinary implementation is in [docs/INVENTORY.md](docs/INVENTORY.md).

## Layout
| Path | What |
|---|---|
| `include/fsot/engine.hpp` | engine, templated on the number type |
| `include/fsot/closed_forms.gen.inc` | generated sections (do not edit) |
| `include/fsot/real.hpp` | number-type shim (double / long double / __float128 / Boost 169-bit) |
| `include/fsot/trit.hpp`, `fsotb_vm.hpp` | trinary core, FSOTB VM |
| `include/fsot/ternary.hpp`, `core.hpp` | balanced-ternary arithmetic, freestanding core |
| `include/fsot/host/` | Ledger A/B, routing, tiers, Python-semantics helpers (host only) |
| `include/fsot/closed_forms_core.gen.inc` | generated freestanding closed-form sections (do not edit) |
| `kernel/` | x86_64 bare-metal QEMU demo |
| `freezes/` | dated SHA-256 freezes (`fsot_freeze_domain`) |
| `audit/` | citation pass, look-elsewhere, precision (M3) and promotion-watch outputs |
| `tools/` | pinned fetch, codegen, golden export |
| `golden/golden_AEB2AD.tsv` | golden values |
| `tests/`, `bench/`, `apps/` | tests, benchmarks, report CLI |

## License and citation
Apache License 2.0. Copyright 2026 Damian Arthur Palumbo. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
Citation metadata is in [CITATION.cff](CITATION.cff).
