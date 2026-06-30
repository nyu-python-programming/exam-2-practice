#!/usr/bin/env python3
"""
make_baseline.py -- generate the canonical instrumentation baseline manifest.

Run this once on the pristine exam template BEFORE distributing it. It records
the SHA-256 of every instrumentation file. tools/score_all.py uses the manifest
to flag any submission whose instrumentation files were modified or stripped.

    python3 tools/make_baseline.py  > baseline_manifest.json
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Files that must be byte-identical to the template in every submission.
INSTRUMENTATION = [
    ".automations/autosave.py",
    ".automations/give-student-credit.py",
    ".claude/settings.json",
    ".cursor/hooks.json",
    ".github/hooks/hooks.json",
    ".github/workflows/event-logger.yml",
    ".githooks/commit-msg",
    ".vscode/tasks.json",
    "Start-Exam-Autosave.command",
    "Start-Exam-Autosave.bat",
    "Start-Exam-Autosave.sh",
]


def main():
    manifest = {}
    missing = []
    for rel in INSTRUMENTATION:
        path = ROOT / rel
        if path.exists():
            manifest[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            missing.append(rel)
    if missing:
        print(f"# warning: not found: {', '.join(missing)}", file=sys.stderr)
    json.dump(manifest, sys.stdout, indent=2, sort_keys=True)
    print()


if __name__ == "__main__":
    main()
