#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

PYTHON_EXE="${PROJECT_ROOT}/.venv-content-tool/bin/python"
PYTHONW_EXE="${PROJECT_ROOT}/.venv-content-tool/bin/pythonw"
MODEL_ROOT="${PROJECT_ROOT}/scripts/content_tool/models/ocr"
TK_OVERLAY_ROOT="${PROJECT_ROOT}/.venv-content-tool/_tk-overlay"
USE_CONSOLE=0

if [[ "${1:-}" == "--console" ]]; then
  USE_CONSOLE=1
  shift
fi

if [[ ! -x "${PYTHON_EXE}" ]]; then
  echo "[ERROR] Python interpreter not found:"
  echo "        ${PYTHON_EXE}"
  echo
  echo "Create environment first:"
  echo "  python3 -m venv .venv-content-tool"
  echo "  ./.venv-content-tool/bin/python -m pip install kraken"
  exit 1
fi

export REVELATION_KRAKEN_MODELS_ROOT="${MODEL_ROOT}"
export REVELATION_KRAKEN_MODEL="${MODEL_ROOT}"

# Support environments where tkinter is unavailable system-wide
# by using a local deb-extracted overlay inside .venv-content-tool.
if [[ -d "${TK_OVERLAY_ROOT}" ]]; then
  PYTHON_MM="$("${PYTHON_EXE}" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  TK_PY_ROOT="${TK_OVERLAY_ROOT}/usr/lib/python${PYTHON_MM}"
  TK_DYNLOAD_ROOT="${TK_PY_ROOT}/lib-dynload"
  TK_LIB_ROOT="${TK_OVERLAY_ROOT}/usr/lib"
  TK_ARCH_LIB_ROOT="${TK_OVERLAY_ROOT}/usr/lib/x86_64-linux-gnu"
  TK_LIBRARY_ROOT="${TK_OVERLAY_ROOT}/usr/share/tcltk/tk8.6"
  TCL_LIBRARY_ROOT="/usr/share/tcltk/tcl8.6"

  if [[ -d "${TK_PY_ROOT}" ]]; then
    export PYTHONPATH="${TK_PY_ROOT}:${TK_DYNLOAD_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
  fi
  if [[ -d "${TK_ARCH_LIB_ROOT}" || -d "${TK_LIB_ROOT}" ]]; then
    export LD_LIBRARY_PATH="${TK_ARCH_LIB_ROOT}:${TK_LIB_ROOT}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
  fi
  if [[ -d "${TK_LIBRARY_ROOT}" ]]; then
    export TK_LIBRARY="${TK_LIBRARY_ROOT}"
  fi
  if [[ -d "${TCL_LIBRARY_ROOT}" ]]; then
    export TCL_LIBRARY="${TCL_LIBRARY_ROOT}"
  fi
fi

cd "${PROJECT_ROOT}"
set +e
if [[ "${USE_CONSOLE}" == "1" ]]; then
  "${PYTHON_EXE}" -m scripts.content_tool "$@"
else
  if [[ -x "${PYTHONW_EXE}" ]]; then
    "${PYTHONW_EXE}" -m scripts.content_tool "$@"
  else
    "${PYTHON_EXE}" -m scripts.content_tool "$@"
  fi
fi
EXIT_CODE=$?
set -e

if [[ "${EXIT_CODE}" -ne 0 ]]; then
  echo
  echo "content_tool exited with code ${EXIT_CODE}."
fi

exit "${EXIT_CODE}"
