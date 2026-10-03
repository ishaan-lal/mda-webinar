#!/usr/bin/env bash
# Runs once when the snapshot is built (on `mda deploy` or `mda dev`), not per
# conversation. Everything it leaves on disk is in every new thread's sandbox.
#
# Only tooling goes here. The repo is cloned per thread by
# middleware/checkout.py, so a snapshot never holds a stale copy of it.
# Never write secrets to disk here.
set -euo pipefail

# git, to clone and diff the repo. Node, for `node --check` on JavaScript.
missing=()
command -v git  >/dev/null 2>&1 || missing+=(git)
command -v node >/dev/null 2>&1 || missing+=(nodejs)
if [ ${#missing[@]} -gt 0 ]; then
  apt-get update
  apt-get install -y --no-install-recommends "${missing[@]}"
fi

mkdir -p /workspace
