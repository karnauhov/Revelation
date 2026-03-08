@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"

set "PYTHON_EXE=%PROJECT_ROOT%\.venv-content-tool\Scripts\python.exe"
set "PYTHONW_EXE=%PROJECT_ROOT%\.venv-content-tool\Scripts\pythonw.exe"
set "MODEL_ROOT=%PROJECT_ROOT%\scripts\content_tool\models\ocr"
set "USE_CONSOLE=0"

if /I "%~1"=="--console" (
    set "USE_CONSOLE=1"
    shift
)

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python interpreter not found:
    echo         %PYTHON_EXE%
    echo.
    echo Create environment first:
    echo   python -m venv .venv-content-tool
    echo   .\.venv-content-tool\Scripts\python.exe -m pip install kraken
    pause
    exit /b 1
)

set "REVELATION_KRAKEN_MODELS_ROOT=%MODEL_ROOT%"
set "REVELATION_KRAKEN_MODEL=%MODEL_ROOT%"

pushd "%PROJECT_ROOT%"
if "%USE_CONSOLE%"=="1" (
    "%PYTHON_EXE%" -m scripts.content_tool %*
) else (
    "%PYTHONW_EXE%" -m scripts.content_tool %*
)
set "EXIT_CODE=%ERRORLEVEL%"
popd

if not "%EXIT_CODE%"=="0" (
    echo.
    echo content_tool exited with code %EXIT_CODE%.
    pause
)

exit /b %EXIT_CODE%
