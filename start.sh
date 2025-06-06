#!/usr/bin/env bash
# =============================================================================
# 1) Load environment variables from .env
# 2) Launch VS Code in the same shell so that VS Code inherits these env vars
#
# Usage:
#   ./start_vscode.sh
#
# Explanation:
#   - We assume a file ".env" in the project root with lines like:
#       SUPABASE_URL=https://your-project.supabase.co
#       SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
#   - This script will export every KEY=VALUE from .env into the current shell.
#   - Then it will run "code ." so that VS Code sees those variables.
#   - In launch.json, you can use ${env:SUPABASE_URL}, etc.
# =============================================================================

set -e

# 1) If .env exists, export every KEY=VALUE line
if [ -f ".env" ]; then
  set -o allexport
  # shellcheck disable=SC1091
  source ".env"
  set +o allexport
else
  echo "Error: .env file not found in project root."
  exit 1
fi

# 2) Now launch VS Code in the same shell environment
echo "Launching VS Code with SUPABASE_URL and SUPABASE_KEY exported..."
code .
