#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
exec bash scripts/local_release/run-linux.sh "$@"
