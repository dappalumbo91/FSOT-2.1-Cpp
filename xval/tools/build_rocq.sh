#!/usr/bin/env bash
export OPAMROOT=${XV:-$HOME/fsot-xval}/toolchains/opam OPAMJOBS=3
opam switch create rocq ocaml-base-compiler.5.3.0 -y && \
opam repo add rocq-released https://rocq-prover.org/opam/released --switch rocq -y && \
opam install -y --switch rocq rocq-core.9.0.1 rocq-stdlib coq-interval
