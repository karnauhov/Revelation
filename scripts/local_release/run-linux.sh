#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/../.."
exec python3 scripts/local_release/linux_bootstrap.py "$@"
