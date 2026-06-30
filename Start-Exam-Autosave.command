#!/bin/bash
# macOS launcher -- double-click this file in Finder to start exam autosave.
# Keep the window it opens OPEN for the whole exam.

# Move to the folder that contains this launcher (the exam repo root).
cd "$(dirname "$0")" || exit 1

echo "Starting exam autosave..."

# Prefer python3, fall back to python.
if command -v python3 >/dev/null 2>&1; then
    python3 .automations/autosave.py
elif command -v python >/dev/null 2>&1; then
    python .automations/autosave.py
else
    echo
    echo "ERROR: Python is not installed or not on your PATH."
    echo "Install Python 3, then double-click this file again."
fi

echo
read -r -p "Autosave has stopped. Press Enter to close this window..."
