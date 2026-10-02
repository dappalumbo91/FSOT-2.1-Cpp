#!/usr/bin/env bash
# Idempotent toolchain install for FSOT cross-validation (Linux or WSL2 Ubuntu/Debian, no GPU needed).
# Default root: $HOME/fsot-xval (override with XV=...). Copy this xval/ folder there first.
set -u
XV=${XV:-$HOME/fsot-xval}; T=$XV/toolchains; mkdir -p $T/bin $XV/logs
need() { ! command -v "$1" >/dev/null 2>&1; }
# 0) base build tools (C++ repo + Rust/Lean builds)
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -q git curl xz-utils build-essential python3-venv cmake ninja-build libboost-dev nlohmann-json3-dev binutils
[ -x "$HOME/.cargo/bin/cargo" ] || command -v cargo >/dev/null || { curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal; }
# 1) apt: z3 4.13.3, cvc5, Coq 8.20 + Interval, Java 21 (TLC), QEMU, GHC/cabal
if need z3 || need cvc5 || need java || need qemu-system-x86_64 || need ghc || need cabal; then
  sudo apt-get update -q && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --fix-missing \
    z3 cvc5 default-jre-headless qemu-system-x86 ghc cabal-install
fi
# 2) elan + Lean toolchain (hub pins leanprover/lean4:v4.31.0; Chua pins v4.33.1, fetched on demand)
[ -x "$HOME/.elan/bin/elan" ] || { curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -o $T/elan-init.sh && sh $T/elan-init.sh -y --default-toolchain leanprover/lean4:v4.31.0; }
# 3) TLA+ tools
[ -f $T/tla2tools.jar ] || curl -sSfL -o $T/tla2tools.jar https://github.com/tlaplus/tlaplus/releases/download/v1.8.0/tla2tools.jar
printf '#!/bin/sh\nexec java -XX:+UseParallelGC -Xmx1g -cp %s/tla2tools.jar tlc2.TLC "$@"\n' "$T" > $T/bin/tlc; chmod +x $T/bin/tlc
# 4) F* (version named in hub scripts)
[ -x $T/fstar/bin/fstar.exe ] || (cd $T && curl -sSfL -O https://github.com/FStarLang/FStar/releases/download/v2026.07.05/fstar-v2026.07.05-Linux-x86_64.tar.gz && tar xzf fstar-v2026.07.05-Linux-x86_64.tar.gz && rm -f fstar-v2026.07.05-Linux-x86_64.tar.gz)
# 5) Isabelle2025-2 (Linux bundle; hub docs reference 2025-2)
[ -d $T/Isabelle2025-2 ] || (cd $T && curl -sSfL -o isa.tgz https://isabelle.in.tum.de/website-Isabelle2025-2/dist/Isabelle2025-2_linux.tar.gz && tar xzf isa.tgz && rm -f isa.tgz)
# 6) Zig 0.15.2 (neuron-zig / Genetics zig twin)
[ -x $T/zig-x86_64-linux-0.15.2/zig ] || (cd $T && curl -sSfL https://ziglang.org/download/0.15.2/zig-x86_64-linux-0.15.2.tar.xz | tar xJ)
ln -sf $T/zig-x86_64-linux-0.15.2/zig $T/bin/zig
# z3 shim: apt z3 4.13.3 (what F* expects) ahead of pip z3-solver
ln -sf /usr/bin/z3 $T/bin/z3; ln -sf /usr/bin/z3 $T/bin/z3-4.13.3
# Idris2 0.8.0 built from source on Chez Scheme (neuron-idris twin)
if [ ! -x $T/idris2/bin/idris2 ]; then
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y chezscheme bsdextrautils
  [ -d $T/Idris2-0.8.0 ] || (cd $T && curl -sSfL https://github.com/idris-lang/Idris2/archive/refs/tags/v0.8.0.tar.gz | tar xz)
  $XV/tools/guarded.sh $XV/logs/idris2_build.log $XV/tools/build_idris2.sh
fi
ln -sf $T/idris2/bin/idris2 $T/bin/idris2
# 7) Python venvs (hub clone needed for requirements.txt)
[ -d $XV/hub/.git ] || git clone -q https://github.com/dappalumbo91/FSOT-2.1-Lean $XV/hub
[ -x $XV/venv/bin/python ] || { /usr/bin/python3 -m venv $XV/venv && $XV/venv/bin/pip install -q -r $XV/hub/requirements.txt z3-solver scipy; }
[ -x $XV/venv-sib/bin/python ] || { /usr/bin/python3 -m venv $XV/venv-sib && $XV/venv-sib/bin/pip install -q "torch>=2.1.0" --index-url https://download.pytorch.org/whl/cpu && $XV/venv-sib/bin/pip install -q "numpy>=1.24" "pandas>=2.0" "mpmath>=1.3" matplotlib; }
echo SETUP_DONE_BASE
# 8) Rocq 9.0 via opam (Debian's coq 8.20 lacks the `Stdlib` prefix the hub's .v files import).
#    Own OCaml 5.3.0 compiler in the switch: ocaml-system mixes in Debian OCaml libs and breaks the build.
export OPAMROOT=$T/opam
if [ ! -x $OPAMROOT/rocq/bin/coqc ]; then
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y opam pkg-config libgmp-dev
  [ -d $OPAMROOT ] || opam init --bare -n --disable-sandboxing -q
  $XV/tools/guarded.sh $XV/logs/opam_rocq.log $XV/tools/build_rocq.sh
fi
# 9) Isabelle heap for the hub session parent (one-time, ~15 min at threads=2)
mkdir -p ~/.isabelle/Isabelle2025-2/etc
[ -f ~/.isabelle/Isabelle2025-2/etc/settings ] || printf 'ML_OPTIONS="--minheap 500 --maxheap 3000"\nISABELLE_TOOL_JAVA_OPTIONS="$ISABELLE_TOOL_JAVA_OPTIONS -Xmx1g"\n' > ~/.isabelle/Isabelle2025-2/etc/settings
$XV/tools/guarded.sh $XV/logs/isa_heap.log $T/Isabelle2025-2/bin/isabelle build -b -o threads=2 HOL-Decision_Procs
echo SETUP_DONE_ALL
