#!/bin/sh
# Runs balance_book.py in a private venv with openpyxl (created on first use).
# The venv lives in the user cache, never in the game repo or system Python.
set -e
VENV="${GD_TOOLKIT_VENV:-${XDG_CACHE_HOME:-$HOME/.cache}/gd-toolkit/venv}"
if ! "$VENV/bin/python" -c "import openpyxl" 2>/dev/null; then
  echo "gd-toolkit: setting up $VENV (one time)…" >&2
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install --quiet --disable-pip-version-check "openpyxl>=3.1,<4"
fi
exec "$VENV/bin/python" "$(dirname "$0")/balance_book.py" "$@"
