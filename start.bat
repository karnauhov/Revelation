@echo off

if not exist ".env" (
  echo Error: .env file not found in project root.
  popd
  exit /b 1
)

for /f "usebackq tokens=1* delims==" %%A in (".env") do (
  set "%%A=%%B"
)

echo Launching VS Code with SUPABASE_URL and SUPABASE_KEY set...
start "" code .

popd
exit /b 0
