# Owner decisions 2026-10-02i (Damian Palumbo, 2026-10-02 18:10 EDT)

Recorded and hashed before the precision gate was rescored. These are the owner's explicit theory decisions, not tuning. No formula, constant, f, gate, pin (AEB2AD, D1D38A), frozen value, existing freeze or prereg (TOE-PREREG-20260909) is edited, and `vendor/fsot_compute.py` is untouched.

## OD-1: reference object of the neutrino ratio row is Δm²21/Δm²31
- **Row:** `pin:wave4|Dm2_21/Dm2_32`, formula γ³·Poof (unchanged; value 0.0295170114802864).
- **Decision:** score against Δm²21/Δm²31 for normal ordering, with Δm²31 = Δm²32 + Δm²21, using PDG 2024 (Δm²21 = 7.53(18)e-5 eV², Δm²32 = 2.455(28)e-3 eV², NO; rpp2024-sum-leptons). This gives 0.0297593(765), with exact propagation for a/(a+b) and uncorrelated inputs.
- **Rationale and evidence:** the hub's own `scripts/atmospheric_neutrino_seed_check.py` names the seed's atmospheric splitting dm2_31, while the record row used PDG's Δm²32 (round-h trace, audit/trace_2026-10-02h.tsv). The same comparison was frozen as DM-R1 in FREEZE_2026-10-02h (eee8141) and scored z 0.317 (audit/score_2026-10-02h.tsv).
- **C++ application:** a new record row `od1:wave4|Dm2_21/Dm2_31` carries the same pinned value against the new reference key `dm2_21_over_dm2_31`. The old row is kept with record=0, still scored against Δm²32 and still carrying C-DM-1.

## OD-2: Quantum_Mechanics D_eff = 6 (undo hub 3c74a180 / pin FE23A2 for this domain)
- **Provenance:**
  - QM D_eff was assigned 6 in pin D1D38A (hub 012e5c64, 2026-08-04, `DomainConfig("Quantum_Mechanics", 6, ...)`) and in pin 3090BC (hub ba6a8288, 2026-09-11 15:19:52 -0400; `data/domain_table_freeze.json` D_eff 6).
  - Hub commit 3c74a180 (2026-09-11 15:28:37 -0400, "Derive D_eff from nest generations; rebuild Ledger B under f=ALPHA. Pin FE23A2") replaced the assigned D_eff of every domain with round(5·5^{g/(G-1)}). For QM (generation 1) that gives 5.
  - Pins 3FBCE5 and AEB2AD inherit 5.
- **Decision:** QM D_eff = 6 (the pre-Sept-11 value). Every other domain keeps its derived D_eff.
- **Rationale and evidence:**
  - With D_eff 5, m_H/m_W = S_quant(1+ψ_con) = 1.5508368, z 5.01. With D_eff 6 it is 1.5591474, z 0.96, matching the 3090BC lineage value exactly.
  - S_quant is one shared quantity, so the decision applies to every record row that uses it: m_H/m_W, Omega_Lambda and sigma_8. Their D_eff-6 values equal the 3090BC lineage column: 0.6846092 and 0.8109399.
  - Applying it to m_H/m_W alone would be inconsistent, so it is applied to all three. Omega_Lambda and sigma_8 pass under both values.
- **How the owner-decision rows differ from the pin:**
  - They are computed by the same C++ Engine (mp169, parity mode), with one change: the Quantum_Mechanics DomainConfig.D_eff is set to 6 before S_QUANT is evaluated.
  - S_quant(D_eff 6) = 0.9552893401 (hub scalar_from_fold, D_eff=6); S_quant(pin, D_eff 5) = 0.9501974701.
  - Pin parity (C++ vs pinned Python AEB2AD/D1D38A) is still checked on the unmodified Engine. The pinned rows stay in the gate with record=0 and their pinned values.
- **C++ application:** new route `owner` (rows `od2:...`, record=1); the pinned rows `pin:wave3|m_H/m_W`, `pin:wave2|Omega_Lambda` and `pin:wave2|sigma_8` are kept with record=0.

## Gate convention
Owner-decision rows are counted in the record set and labelled `owner-decision` in the gate output. The pinned-only count (no owner decisions) is printed alongside.
