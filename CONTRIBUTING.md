# Contributing to FSOT-2.1-Cpp

This repo is a C++20 port of the FSOT 2.1 engine. It reproduces numbers; it does not set them.

## Theory authority
- The authority is the hub, [FSOT-2.1-Lean](https://github.com/dappalumbo91/FSOT-2.1-Lean):
  `vendor/fsot_compute.py` at pin **AEB2AD** (commit and SHA-256 in [AUTHORITY_PIN.json](AUTHORITY_PIN.json)).
- Do not invent LECs, constants, exponents or fit parameters. Every coefficient must come from the
  pinned authority or a quantity the law already has.
- Do not edit `AUTHORITY_PIN.json`, any pin (AEB2AD, D1D38A), `golden/`, `freezes/`, or `*.gen.inc`
  files by hand. Do not tune tolerances or gate limits to make a check pass; a mismatch is a finding.
- Tip dial-in work is separate. Do not GO-MERGE tip dial-in leaves from satellite repos here without
  going through the Steward/Tracer path.

## Preferred changes
- Closed-form ports with golden or numeric checks against the authority.
- State provenance in the PR and in code comments: source repo + commit (and file/function).
- Regenerated outputs must come from the repo's tools (`tools/`), not hand edits.

## Opening a PR
1. Fork, or branch off `main`.
2. One concern per PR: a port, a fix, a doc change. Keep math changes and surface polish apart.
3. Describe what changed, why, the provenance, and which checks you ran.
4. Keep commits small with plain messages (`docs: ...`, `fix: ...`, `port: ...`).

## Tests and CI
Build and test locally first:

```bash
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build
ctest --test-dir build --output-on-failure
```

CI ([.github/workflows/ci.yml](.github/workflows/ci.yml)) must be green before merge. Jobs:
- `build-test` — Linux build; golden at every type, trit, balanced-ternary engine, freestanding symbols.
- `build-test-msvc` — Windows/MSVC build; precision report must be byte-identical to the Linux golden.
- `regen-diff` — fetches the pinned authority (SHA-checked), regenerates closed forms and goldens,
  and fails if they differ from the committed files.
- `ledger-b` — re-runs Ledger B, routing, tier evidence and freeze scoring with the hub's own Python
  at the pinned commits and diffs against the committed outputs.
- `bare-metal` — freestanding / bare-metal serial check.

A red job you did not expect is a finding: report the exact output rather than adjusting the check.
Full local reproduction steps are in [docs/REPRODUCE.md](docs/REPRODUCE.md).

## License
Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE). By contributing you agree your
contribution is licensed under the same terms. Citation metadata is in [CITATION.cff](CITATION.cff).

## Conduct
Be professional and specific. Critique numbers and code, not people. Report results as they are,
including misses.
