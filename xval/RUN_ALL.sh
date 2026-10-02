#!/usr/bin/env bash
# FSOT 2.1 cross-validation — run every layer that is runnable on this box, print a summary.
# Usage: ./RUN_ALL.sh [--fresh] [--only hub|siblings] [--skip-isabelle] [--skip-xproof] [--with-runner]
#   --fresh         re-clone hub + siblings instead of fetch/reset (keeps nothing; Lean cache re-downloads)
#   --skip-xproof   skip the hub's long multiprover run (run_cross_proof_verification.py)
#   --with-runner   also run scripts/fsot_verification_runner.py (needs Windows-only external corpora; see README)
# Local only: never pushes, never comments. Heavy layers run one at a time, niced, with a RAM watchdog.
set -u
XV=${XV:-$HOME/fsot-xval}
. "$XV/toolchains/env.sh"
FRESH=0; ONLY=all; SKIP_XPROOF=0; WITH_RUNNER=0; SKIP_ISA=0
while [ $# -gt 0 ]; do case "$1" in
  --fresh) FRESH=1;; --only) ONLY="$2"; shift;; --skip-xproof) SKIP_XPROOF=1;;
  --with-runner) WITH_RUNNER=1;; --skip-isabelle) SKIP_ISA=1;; *) echo "unknown arg $1"; exit 2;; esac; shift; done
STAMP=$(date +%Y%m%d-%H%M%S); OUT="$XV/runs/$STAMP"; mkdir -p "$OUT"
SUMMARY="$OUT/summary.tsv"; printf 'layer\tstatus\tseconds\tdetail\n' > "$SUMMARY"
export MIN_AVAIL_MB=${MIN_AVAIL_MB:-4000}   # guarded.sh kills+retries a layer if MemAvailable drops below this
export LEAN_NUM_THREADS=${LEAN_NUM_THREADS:-4}
export ISABELLE_BUILD_OPTIONS="threads=${ISA_THREADS:-2}"
T0=$(date +%s)

# ---- layer runner: setsid + nice + RAM watchdog; log to $OUT/<name>.log ----
run() {  # run <name> <workdir> <cmd...>  -> tools/guarded.sh (nice, RAM watchdog kills whole tree, retries)
  local name="$1" wd="$2"; shift 2
  local log="$OUT/$name.log" s=$(date +%s)
  ( cd "$wd" && "$XV/tools/guarded.sh" "$log" "$@" ); LAST_RC=$?
  LAST_SECS=$(( $(date +%s) - s )); LAST_LOG="$log"
}
rec() { printf '%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" >> "$SUMMARY"; printf '  %-38s %-5s %5ss  %s\n' "$1" "$2" "$3" "$4"; }
pf() { [ "$1" = 0 ] && echo PASS || echo FAIL; }
skip() { rec "$1" SKIP 0 "$2"; }

sync_repo() {  # sync_repo <dir> <github-name>
  local d="$1" r="$2"
  if [ $FRESH = 1 ] || [ ! -d "$d/.git" ]; then rm -rf "$d"; git clone -q "https://github.com/dappalumbo91/$r" "$d"
  else git -C "$d" fetch -q origin && git -C "$d" reset -q --hard origin/HEAD && git -C "$d" clean -qfdx -e .lake -e dist-newstyle -e target -e .zig-cache -e zig-out -e build; fi
}

echo "FSOT cross-validation run $STAMP  (logs: $OUT)"
# ======================= HUB: FSOT-2.1-Lean =======================
if [ "$ONLY" != siblings ]; then
  H="$XV/hub"; sync_repo "$H" FSOT-2.1-Lean
  echo "hub commit: $(git -C "$H" log -1 --format='%h %cd' --date=iso)" | tee "$OUT/hub_commit.txt"
  PY="$XV/venv/bin/python"

  # H0 pin: vendor/fsot_compute.py must hash to AEB2AD (never edited by this script)
  sha=$(sha256sum "$H/vendor/fsot_compute.py" | cut -c1-6 | tr a-f A-F)
  [ "$sha" = AEB2AD ] && rec hub.pin_AEB2AD PASS 0 "sha256 prefix $sha" || rec hub.pin_AEB2AD FAIL 0 "sha256 prefix $sha (expected AEB2AD)"

  # H1 CI job margin-and-toe
  run hub.ci.margin_audit "$H" "$PY" scripts/audit_all_benchmark_margins.py
  d=$("$PY" -c "import json;m=json.load(open('$H/data/benchmark_margin_audit.json'));n=int(m.get('benchmark_file_count') or 0);f=int(m.get('green_gate_fail_count',-1));print(f'green {n-f}/{n} fail={f}');exit(0 if f==0 else 1)" 2>&1); r=$?
  [ $LAST_RC = 0 ] && [ $r = 0 ] && rec hub.ci.margin_audit PASS $LAST_SECS "$d" || rec hub.ci.margin_audit FAIL $LAST_SECS "$d rc=$LAST_RC"
  run hub.ci.tier_scalar_soft "$H" "$PY" scripts/build_tier_scalar_precision_closure.py
  d=$("$PY" -c "import json;s=json.load(open('$H/data/tier_scalar_precision_closure.json'));print('closed',s.get('closed'),'fails',s.get('tier_scalar_fail_count'))" 2>&1)
  rec hub.ci.tier_scalar_soft "$( [ $LAST_RC = 0 ] && echo PASS || echo SOFT)" $LAST_SECS "$d (non-blocking in CI)"
  run hub.ci.toe_gap "$H" "$PY" scripts/build_toe_gap_closure.py
  d=$("$PY" -c "import json;e=json.load(open('$H/data/toe_gap_closure_report.json'))['evaluation'];c=e.get('criteria') or {};p=sum(1 for v in c.values() if v.get('pass'));print(f\"LabelA={e.get('label_A_empirical_framework')} LabelB={e.get('label_B_classical_toe')} criteria {p}/{len(c)}\");exit(0 if e.get('label_A_empirical_framework') and e.get('label_B_classical_toe') else 1)" 2>&1); r=$?
  [ $LAST_RC = 0 ] && [ $r = 0 ] && rec hub.ci.toe_gap PASS $LAST_SECS "$d" || rec hub.ci.toe_gap FAIL $LAST_SECS "$d"

  # H2 CI job scientific-catalog-smt
  run hub.ci.smt2_catalog_z3 "$H" "$PY" scripts/run_smt2_catalog.py
  rec hub.ci.smt2_catalog_z3 $(pf $LAST_RC) $LAST_SECS "z3 $(z3 --version | awk '{print $3}'): $(tr '\n' ' ' < "$LAST_LOG" | cut -c1-60)"
  run hub.ci.export_obligations "$H" "$PY" scripts/export_cross_proof_obligations.py
  rec hub.ci.export_obligations $(pf $LAST_RC) $LAST_SECS "$(grep -o '([0-9]* obligations)' "$LAST_LOG" | head -1)"

  # H3 CI job publication-smoke
  for s in build_fsot_domain_navigator_db build_contested_observables_closure audit_parameter_count; do
    run hub.ci.$s "$H" "$PY" scripts/$s.py; rec hub.ci.$s $(pf $LAST_RC) $LAST_SECS "$(tail -n 2 "$LAST_LOG" | tr '\n' ' ' | cut -c1-90)"
  done

  # H4 Lean: Mathlib cache + build EVERY FSOT module (default target only reaches ~11 modules)
  run hub.lean.cache_get "$H" lake exe cache get
  rec hub.lean.cache_get $(pf $LAST_RC) $LAST_SECS "Mathlib oleans for $(cat "$H/lean-toolchain")"
  ( cd "$H" && find FSOT -name '*.lean' | sed 's#\.lean$##; s#/#.#g' | sort ) > "$OUT/lean_modules.txt"
  nmod=$(wc -l < "$OUT/lean_modules.txt")
  run hub.lean.build_all "$H" lake build $(cat "$OUT/lean_modules.txt") FSOT2_0_Compute
  ns=$(grep -c "declaration uses 'sorry'" "$LAST_LOG"); ne=$(grep -c '^error' "$LAST_LOG")
  nax=$(grep -rnE '^\s*axiom ' "$H/FSOT" --include=*.lean | wc -l)
  rec hub.lean.build_all $(pf $LAST_RC) $LAST_SECS "$nmod modules + exe; $(grep -o 'Build completed successfully ([0-9]* jobs)' "$LAST_LOG"); errors=$ne sorry=$ns axioms=$nax"

  # H5 multiprover: Lean->Python->Coq->Isabelle->Rust->F*->QEMU (+SMT bulk, TLA+, hardware_bare_metal)
  if [ $SKIP_XPROOF = 1 ]; then skip hub.xproof "--skip-xproof"
  else
    [ $SKIP_ISA = 1 ] && export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v Isabelle | paste -sd:)
    run hub.xproof "$H" "$PY" scripts/run_cross_proof_verification.py
    "$PY" "$XV/tools/summarize_xproof.py" "$H" > "$OUT/hub.xproof.summary.txt" 2>&1
    while IFS=$'\t' read -r k st dt; do rec "hub.xproof.$k" "$st" - "$dt"; done < <(grep -P '^\S+\t' "$OUT/hub.xproof.summary.txt")
    rec hub.xproof $(pf $LAST_RC) $LAST_SECS "$(grep '^OVERALL' "$OUT/hub.xproof.summary.txt" | cut -c9-)"
    . "$XV/toolchains/env.sh"
  fi
  if [ $WITH_RUNNER = 1 ]; then
    run hub.verification_runner "$H" "$PY" scripts/fsot_verification_runner.py
    rec hub.verification_runner $(pf $LAST_RC) $LAST_SECS "$(sed -n '/=== Summary ===/,$p' "$LAST_LOG" | grep -c 'FAIL:') FAIL items; $(grep -c 'missing\|not found\|No such file' "$LAST_LOG") missing-path messages (Windows C:/I:/D: corpora); see README"
  else skip hub.verification_runner "needs external corpora on I:/C: (SMILES lab, unified DB, KB, CNC Exp1.csv); --with-runner to try"; fi
  echo "tracked files rewritten by hub generators: $(git -C "$H" status --short | wc -l) (scratch clone; never pushed)" | tee -a "$OUT/hub_commit.txt"
fi

# ======================= SIBLINGS =======================
if [ "$ONLY" != hub ]; then
  S="$XV/siblings"; mkdir -p "$S"; PY="$XV/venv/bin/python"; PYS="$XV/venv-sib/bin/python"
  for r in FSOT-Chua-Circuit FSOT-Genetics FSOT-2.1-Neural fsot-neuron-zig fsot-neuron-haskell fsot-neuron-idris; do sync_repo "$S/$r" "$r"; done
  for r in FSOT-Chua-Circuit FSOT-Genetics; do
    sha=$(sha256sum "$S/$r/vendor/fsot_compute.py" | cut -c1-6 | tr a-f A-F)
    [ "$sha" = D1D38A ] && rec "$r.pin_D1D38A" PASS 0 "vendor sha $sha (sibling freeze pin)" || rec "$r.pin_D1D38A" FAIL 0 "vendor sha $sha"
  done

  # Chua: full gauntlet (lean v4.33.1, coq, z3, rust, TLC); Isabelle via current CLI
  run chua.cross_proof "$S/FSOT-Chua-Circuit" "$PY" verification/run_cross_proof.py
  rec chua.cross_proof $(pf $LAST_RC) $LAST_SECS "$(grep -c '^\[PASS\]' "$LAST_LOG") PASS / $(grep -c '^\[FAIL\]' "$LAST_LOG") FAIL; $(grep -o 'overall_ok=.*' "$LAST_LOG")"
  grep -q '^\[FAIL\] isabelle' "$LAST_LOG" && rec chua.cross_proof.isabelle_layer NOTE - "optional Isabelle layer reported FAIL (process_theories fallback added in Chua cecef94; see log)"
  if [ $SKIP_ISA = 0 ]; then
    run chua.isabelle_process_theories "$S/FSOT-Chua-Circuit/formal/isabelle" isabelle process_theories -l HOL -D . -O CircuitArray
    rec chua.isabelle_process_theories $(pf $LAST_RC) $LAST_SECS "CircuitArray.thy checked with current CLI"
  fi

  # Genetics
  G="$S/FSOT-Genetics"
  run genetics.lean_cache "$G" lake exe cache get; rec genetics.lean_cache $(pf $LAST_RC) $LAST_SECS "Mathlib cache"
  run genetics.verify_cross "$G" "$PY" scripts/verify_cross.py
  rec genetics.verify_cross $(pf $LAST_RC) $LAST_SECS "$(grep -c '^OK' "$LAST_LOG") OK / $(grep -c '^FAIL' "$LAST_LOG") FAIL"
  run genetics.cross_proof "$G" "$PY" verification/run_cross_proof.py
  rec genetics.cross_proof $(pf $LAST_RC) $LAST_SECS "$(grep -c '^\[PASS\]' "$LAST_LOG") PASS / $(grep -c '^\[FAIL\]' "$LAST_LOG") FAIL; $(grep -o 'overall_ok=.*' "$LAST_LOG")"
  run genetics.system_verify "$G" "$PY" scripts/system_verify.py
  rec genetics.system_verify $(pf $LAST_RC) $LAST_SECS "$(grep -o 'overall_ok=.*' "$LAST_LOG" | tail -1)"
  run genetics.cargo_check "$G" cargo check --workspace -q; rec genetics.cargo_check $(pf $LAST_RC) $LAST_SECS "Rust workspace"
  run genetics.haskell "$G/haskell" bash -c 'cabal build -v0 && cabal run -v0 fsot-genetics-check'
  rec genetics.haskell $(pf $LAST_RC) $LAST_SECS "$(grep -o 'ALL HASKELL GATES PASSED' "$LAST_LOG")"
  run genetics.zig_host "$G/zig" zig build host; rec genetics.zig_host $(pf $LAST_RC) $LAST_SECS "$(grep -o 'FSOT_STAGE_GENETICS_OK' "$LAST_LOG" | head -1)"

  # Neural (CPU torch)
  N="$S/FSOT-2.1-Neural"
  run neural.ci_smoke "$N" "$PYS" scripts/ci_smoke.py; rec neural.ci_smoke $(pf $LAST_RC) $LAST_SECS "$(tail -n 1 "$LAST_LOG")"
  # SMILES Lab dataset: public copy from FSOT-2.1-Lean/vendor/smiles (see data/SHA256SUMS); wrapper injects the path
  [ -f "$XV/data/FSOT_SMILES_Lab_Dataset.json" ] || cp "$XV/hub/vendor/smiles/FSOT_SMILES_Lab_Dataset.json" "$XV/data/" 2>/dev/null
  run neural.language_verify "$N" "$PYS" "$XV/tools/run_neural_language_verify.py" "$N"
  rec neural.language_verify $(pf $LAST_RC) $LAST_SECS "Morse/codon gates: $(grep -cE '(OK|exact|roundtrip): +True' "$LAST_LOG") True; SMILES $(grep -oE 'hit_rate: +[0-9.%]+' "$LAST_LOG" | tr -s ' ') median_err $(grep -oE 'median_error_pct: +[0-9.]+' "$LAST_LOG" | awk '{print $2}')"
  run neural.formal_lean "$N/formal" lake build; rec neural.formal_lean $(pf $LAST_RC) $LAST_SECS "$(grep -o 'Build completed.*' "$LAST_LOG")"

  # Language twins
  Z="$S/fsot-neuron-zig"
  run twin.zig.build "$Z" zig build -Doptimize=ReleaseFast; rec twin.zig.build $(pf $LAST_RC) $LAST_SECS "fsot_mind"
  run twin.zig.suite "$Z" ./zig-out/bin/fsot_mind suite
  rec twin.zig.suite $(pf $LAST_RC) $LAST_SECS "$(grep -cE ' PASS|_OK' "$LAST_LOG") PASS/_OK markers, $(grep -cE '\bFAIL\b' "$LAST_LOG") FAIL markers"
  HS="$S/fsot-neuron-haskell"
  run twin.haskell.build_test "$HS" bash -c 'cabal build -v0 all && cabal test -v0'
  rec twin.haskell.build_test $(pf $LAST_RC) $LAST_SECS "cabal test-suite"
  for c in selftest parity phase-a; do run twin.haskell.$c "$HS" cabal run -v0 fsot-mind -- $c
    rec twin.haskell.$c $(pf $LAST_RC) $LAST_SECS "$(grep -E 'PASS|_OK' "$LAST_LOG" | head -1 | xargs)"; done
  ID="$S/fsot-neuron-idris"
  run twin.idris.build "$ID" idris2 --build fsot-neuron-idris.ipkg; rec twin.idris.build $(pf $LAST_RC) $LAST_SECS "idris2 $(idris2 --version | awk '{print $NF}')"
  for c in scalpel phase-a; do run twin.idris.$c "$ID" ./build/exec/fsot-mind $c
    rec twin.idris.$c $(pf $LAST_RC) $LAST_SECS "$(grep -E 'PASS' "$LAST_LOG" | tail -1 | xargs)"; done
fi

# ======================= not runnable here =======================
skip esp32_hardware_harness "needs ESP32 board on CP210x serial port (physical hardware)"
skip FSOT-GPU/CUDA_panels "needs NVIDIA GPU (Lean priors for GPU panels still build above)"
skip FSOT-Qwen_training "LoRA/LLM training needs GPU; its cross-proof rows are copies of hub report"

TOTAL=$(( $(date +%s) - T0 ))
echo; echo "================ SUMMARY ($STAMP) ================"
awk -F'\t' '{printf "%-44s %-5s %6s  %s\n",$1,$2,$3,$4}' "$SUMMARY"
np=$(grep -cP '\tPASS\t' "$SUMMARY"); nf=$(grep -cP '\tFAIL\t' "$SUMMARY"); nsk=$(grep -cP '\tSKIP\t' "$SUMMARY")
echo "PASS=$np FAIL=$nf SKIP=$nsk  total ${TOTAL}s (~$((TOTAL/60)) min)"
echo "summary: $SUMMARY"
ln -sfn "$OUT" "$XV/runs/latest"
[ "$nf" = 0 ]
