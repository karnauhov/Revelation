@echo off
REM =============================================================================
REM 1) Read .env from project root and set environment variables
REM 2) Launch VS Code in the same shell so that VS Code inherits these env vars
REM
REM Usage:
REM   start_vscode.bat
REM
REM Explanation:
REM   - We expect a file ".env" in the project root containing lines like:
REM       SUPABASE_URL=https://your-project.supabase.co
REM       SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
REM   - This script will parse each KEY=VALUE and do:
REM       set KEY=VALUE
REM   - Then it will run "code ." so that VS Code sees those variables.
REM   - In launch.json, you can refer to them as ${env:SUPABASE_URL}, etc.
REM =============================================================================

REM 1) If .env exists, read line by line "KEY=VALUE"
if not exist ".env" (
  echo Error: .env file not found in project root.
  popd
  exit /b 1
)

for /f "usebackq tokens=1* delims==" %%A in (".env") do (
  set "%%A=%%B"
)

REM 2) Launch VS Code in the same environment
echo Launching VS Code with SUPABASE_URL and SUPABASE_KEY set...
code .

popd
