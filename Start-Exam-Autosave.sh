#!/bin/bash
# Linux launcher -- run this to start exam autosave (or double-click and choose
# "Run in Terminal"). Keep the window it opens OPEN for the whole exam.

cd "$(dirname "$0")" || exit 1

echo "Starting exam autosave..."

if command -v python3 >/dev/null 2>&1; then
    python3 .automations/autosave.py
elif command -v python >/dev/null 2>&1; then
    python .automations/autosave.py
else
    echo
    echo "ERROR: Python is not installed or not on your PATH."
    echo "Install Python 3, then run this file again."
fi

echo
read -r -p "Autosave has stopped. Press Enter to close..."
