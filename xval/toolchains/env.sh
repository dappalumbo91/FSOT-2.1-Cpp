# Source me: toolchain PATH for FSOT cross-validation on this box
export XV=${XV:-$HOME/fsot-xval}
[ -f "$HOME/.elan/env" ] && . "$HOME/.elan/env"
[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"
export PATH="$XV/venv/bin:$XV/toolchains/fstar/bin:$XV/toolchains/Isabelle2025-2/bin:$PATH"
export PATH="$XV/toolchains/bin:$PATH"   # z3 4.13.3 shim, tlc, zig, idris2 first
# Rocq 9.0 (opam switch "rocq": rocq-core 9.0.1 + rocq-stdlib + coq-interval) — hub .v files use `From Stdlib`
export OPAMROOT="$XV/toolchains/opam"
[ -x "$OPAMROOT/rocq/bin/coqc" ] && export PATH="$OPAMROOT/rocq/bin:$PATH"
