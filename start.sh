#!/usr/bin/env bash

set -e

if [ -f ".env" ]; then
  set -o allexport
  # shellcheck disable=SC1091
  source ".env"
  set +o allexport
else
  echo "Error: .env file not found in project root."
  exit 1
fi

echo "Launching VS Code with SUPABASE_URL and SUPABASE_KEY exported..."
nohup code . >/dev/null 2>&1 &

exit 0
