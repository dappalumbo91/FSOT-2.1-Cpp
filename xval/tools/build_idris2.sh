#!/usr/bin/env bash
set -e
cd ${XV:-$HOME/fsot-xval}/toolchains/Idris2-0.8.0
make bootstrap SCHEME=chezscheme PREFIX=${XV:-$HOME/fsot-xval}/toolchains/idris2 -j2
make install PREFIX=${XV:-$HOME/fsot-xval}/toolchains/idris2
