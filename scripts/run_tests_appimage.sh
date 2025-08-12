#!/usr/bin/env bash
# Run pytest using the Python & libs embedded in the extracted FreeCAD AppImage.
# Falls back to normal python if the AppImage tree is missing.
set -euo pipefail

# Ensure Qt can run headlessly in CI/containers
export QT_QPA_PLATFORM=${QT_QPA_PLATFORM:-offscreen}
export QT_PLUGIN_PATH=${QT_PLUGIN_PATH:-}
export XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR:-/tmp}

APPROOT="$(dirname "${BASH_SOURCE[0]}")/../squashfs-root"
APPROOT="$(realpath "$APPROOT")"
PYBIN="$APPROOT/usr/bin/python"
SITEPKG="$APPROOT/usr/lib/python3.11/site-packages"
ADDON_ROOT="$(realpath "$(dirname "${BASH_SOURCE[0]}")/..")"

if [[ ! -x "$PYBIN" ]]; then
  echo "[INFO] AppImage python not found at $PYBIN. Falling back to system python." >&2
  python -m pytest -q "$@"
  exit $?
fi

export PYTHONPATH="$SITEPKG:$ADDON_ROOT/freecad_ai_addon:${PYTHONPATH:-}"

echo "[INFO] Using AppImage Python: $PYBIN" >&2
echo "[INFO] PYTHONPATH: $PYTHONPATH" >&2

# Install pytest if missing inside AppImage env (non-destructive; will go to user site)
if ! "$PYBIN" -c "import pytest" 2>/dev/null; then
  echo "[INFO] Installing pytest into user site-packages for AppImage python" >&2
  "$PYBIN" -m pip install --user --quiet pytest pytest-asyncio anyio
fi

# Default to full test suite if no args
if [[ $# -eq 0 ]]; then
  set -- tests
fi

"$PYBIN" -m pytest -v --tb=short "$@"
