#!/usr/bin/env bash
# Full FSOT-2.1-Cpp reproduction on Linux / WSL2: mirrors the four CI jobs (.github/workflows/ci.yml).
# Usage (from anywhere):  bash xval/cpp_check.sh [CPP_REPO_DIR] [WORK_DIR]
#   CPP_REPO_DIR defaults to the repo containing this script; WORK_DIR (hub sparse clone, venv) defaults to ~/fsot-cpp-work.
# Never edits pins, AUTHORITY_PIN.json, golden/, freezes/ or the hub. Fails on the first mismatch.
set -euo pipefail
CPP=$(cd "${1:-$(dirname "$0")/..}" && pwd); W=${2:-$HOME/fsot-cpp-work}; mkdir -p "$W"; cd "$CPP"
J=${JOBS:-3}; t0=$(date +%s); ok() { echo "OK  $*"; }
step() { echo; echo "== $* ($(( $(date +%s) - t0 )) s)"; }
step "toolchain"; g++ --version | head -1; cmake --version | head -1; python3 --version
step "1. build-test"
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DFSOT_HUB_DATA="$W/hub" >/dev/null
step "2. hub sparse clone at ledger_b_data_commit"
COMMIT=$(python3 -c "import json;print(json.load(open('AUTHORITY_PIN.json'))['ledger_b_data_commit'])")
if [ ! -d "$W/hub/.git" ]; then
  git clone -q --filter=blob:none --no-checkout https://github.com/dappalumbo91/FSOT-2.1-Lean "$W/hub"
  git -C "$W/hub" sparse-checkout set --no-cone '/data/*_benchmark.json' '/data/literature_uncertainty_anchors.json' '/data/stumped_observables_reference.json' '/data/extension_folds_derived.json' '/data/domain_table_freeze.json' '/predictions/' '/scripts/' '/vendor/fsot_compute.py' '/vendor/fsot_seed_flavor.py'
fi
git -C "$W/hub" sparse-checkout add '/vendor/fsot_seed_flavor.py'
git -C "$W/hub" checkout -q "$COMMIT"; echo "hub @ $(git -C "$W/hub" rev-parse --short HEAD), authority sha256 $(sha256sum "$W/hub/vendor/fsot_compute.py" | cut -c1-6)"
cmake -S . -B build -DFSOT_HUB_DATA="$W/hub" >/dev/null
nice -n 10 cmake --build build -j"$J"
nice -n 10 ctest --test-dir build --output-on-failure -j2 | tee "$W/ctest.log" | grep -E 'Test +#|tests passed'
ok "ctest"
step "3. regen-diff + ledger-b Python goldens (mpmath==1.4.1)"
[ -x "$W/venv/bin/python" ] || { python3 -m venv "$W/venv"; "$W/venv/bin/pip" -q install mpmath==1.4.1; }
P="$W/venv/bin/python"
$P tools/fetch_authority.py --out authority/fsot_compute.py
$P tools/gen_closed_forms.py --authority authority/fsot_compute.py
$P tools/dump_golden.py --authority authority/fsot_compute.py
git diff --exit-code -- include/fsot/closed_forms.gen.inc include/fsot/closed_forms_core.gen.inc golden/golden_AEB2AD.tsv; ok "closed forms + golden_AEB2AD regenerate byte-identical"
$P tools/dump_ledger_b_golden.py --hub "$W/hub" --out "$W/ledger_b.tsv"
diff -q "$W/ledger_b.tsv" golden/ledger_b_6f9c2560.tsv; ok "hub Python Ledger B golden byte-identical"
$P tools/gen_ledger_a_routing.py --hub "$W/hub"
$P tools/dump_ledger_a_routing_golden.py --hub "$W/hub" --out "$W/ledger_a_routing.tsv"
git diff --exit-code -- include/fsot/ledger_a.gen.inc include/fsot/routing.gen.inc
diff -q "$W/ledger_a_routing.tsv" golden/ledger_a_routing.tsv; ok "Ledger A / routing byte-identical"
# gen_tier_evidence reads hub git history; the blob:none clone fetches what it needs on demand
$P tools/gen_tier_evidence.py --hub "$W/hub"
git diff --exit-code -- golden/tier_evidence_6f9c2560.json; ok "tier evidence byte-identical"
$P tools/dump_seed_leaves_golden.py --hub "$W/hub" --out "$W/seed_leaves.tsv"
diff -q "$W/seed_leaves.tsv" golden/seed_leaves_6f9c2560.tsv; ok "seed-leaf golden (hub scripts run unchanged) byte-identical"
$P tools/pin_lineage.py --hub "$W/hub" --out "$W/pin_lineage.tsv"
diff -q "$W/pin_lineage.tsv" reference/pin_lineage_2026-10-02.tsv; ok "pin lineage byte-identical"
python3 tools/check_references.py; ok "every reference value matches its committed evidence"
step "4. C++ Ledger B re-score vs golden, corrected + genuine misses"
./build/fsot_ledger_b --hub "$W/hub" --golden golden/ledger_b_6f9c2560.tsv \
  --corrected-out "$W/ledger_b_corrected.tsv" --genuine-misses-out "$W/ledger_b_genuine_misses.tsv"
cmp "$W/ledger_b_corrected.tsv" golden/ledger_b_corrected_6f9c2560.tsv && cmp "$W/ledger_b_genuine_misses.tsv" golden/ledger_b_genuine_misses_6f9c2560.tsv; ok "corrected + genuine-miss reports byte-identical"
$P tools/classify_genuine_misses.py --misses audit/m2_genuine_misses_input.tsv --hub-data "$W/hub/data" --out "$W/precision_m3_genuine_misses.tsv"
cmp "$W/precision_m3_genuine_misses.tsv" audit/precision_m3_genuine_misses.tsv; ok "PRECISION_M3 188-row classification byte-identical"
step "5. closed forms, corrected mode, freeze"
./build/fsot_report --corrected | tail -6
./build/predict_closed_form --name H0 --digits 12
./build/fsot_freeze_domain --verify freezes/domain_freeze_2026-10-02_AEB2AD.json
python3 tools/verify_freeze.py freezes/domain_freeze_2026-10-02_AEB2AD.json
test "$(./build/fsot_freeze_domain --print-core-sha)" = 8e30e85e72091462c4d66df2d498afb36ccbc2d40eb5df01b4e083947c79dad3; ok "core sha = hub domain_table_sha256"
step "5b. precision gate (z <= 1, include/fsot/host/precision_gate.hpp)"
./build/fsot_precision --refs reference/published_2026-10-02.tsv --map reference/prediction_map_2026-10-02.tsv \
  --lineage reference/pin_lineage_2026-10-02.tsv --tsv-out "$W/precision.tsv" --md-out "$W/precision.md"
cmp "$W/precision.tsv" audit/precision_2026-10-02.tsv && cmp "$W/precision.md" audit/precision_2026-10-02.md; ok "precision report byte-identical"
python3 tools/verify_refinement_freeze.py
step "6. bare-metal (QEMU)"
./kernel/build.sh build-kernel
set +e; timeout 300 qemu-system-x86_64 -m 64 -kernel build-kernel/fsot_kernel.elf -serial file:"$W/serial.txt" -display none -no-reboot -monitor none -device isa-debug-exit,iobase=0xf4,iosize=0x04; rc=$?; set -e
[ "$rc" = 33 ] || { echo "FAIL qemu exit $rc (expected 33)"; exit 1; }
python3 tools/check_kernel_serial.py "$W/serial.txt"
cmp "$W/serial.txt" docs/bare_metal_serial_AEB2AD.txt && ok "serial byte-identical to docs/bare_metal_serial_AEB2AD.txt"
git status --short; echo; echo "ALL CPP CHECKS PASSED in $(( $(date +%s) - t0 )) s"
