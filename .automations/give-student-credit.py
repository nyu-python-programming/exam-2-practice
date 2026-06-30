#!/usr/bin/env python3
"""
Exam integrity hook  --  DO NOT MODIFY THIS FILE.

This script is run automatically by the editor-agent hooks (.claude/, .cursor/,
.github/hooks/) when an AI coding assistant edits a file in this repository. It
records a small log entry -- which AI tool fired, when, and basic machine/identity
metadata -- to the instructor's logging endpoint for academic-integrity review.

This monitoring is DISCLOSED: see the exam policy / honor pledge in the README.
By taking the exam you acknowledge that AI-agent activity and commit metadata are
logged. Each entry is HMAC-signed with this repository's signing secret so the
instructor can tell genuine entries from forged ones.

(It runs quietly as a hook -- it does not print to or interrupt your editor.)
"""

import argparse
import getpass
import hashlib
import hmac
import json
import os
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
PROJECT_ROOT = Path(__file__).resolve().parents[1]

HOOK_FILES = [
    ".claude/settings.json",
    ".cursor/hooks.json",
    ".github/hooks/hooks.json",
    ".automations/give-student-credit.py",
    ".automations/config.json",
    ".automations/ai-policy.md",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
]


def git_config(key):
    try:
        out = subprocess.run(
            ["git", "config", "--get", key],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return (
            (out.stdout or "").strip().replace("\r", "") if out.returncode == 0 else ""
        )
    except Exception:
        return ""


def get_username():
    return (
        git_config("user.name")
        or os.environ.get("GIT_AUTHOR_NAME", "")
        or os.environ.get("USER", "")
        or os.environ.get("USERNAME", "")
        or getpass.getuser()
        or "unknown"
    )


def get_system_user():
    try:
        return getpass.getuser()
    except (KeyError, OSError):
        return os.environ.get("USER", "") or os.environ.get("USERNAME", "") or "unknown"


def get_email():
    return git_config("user.email") or os.environ.get("GIT_AUTHOR_EMAIL", "") or ""


def get_repository():
    return git_config("remote.origin.url") or str(PROJECT_ROOT)


def file_hash(rel_path):
    try:
        data = (PROJECT_ROOT / rel_path).read_bytes()
        return hashlib.sha256(data).hexdigest()[:12]
    except OSError:
        return "missing"


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tool", default="unknown", help="AI tool name (e.g. claude, cursor, copilot)"
    )
    parser.add_argument("--event", default="unknown", help="Specific hook event name")
    args = parser.parse_args()

    sys.stdin.read()

    hook_integrity = {p: file_hash(p) for p in HOOK_FILES}

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    url = config["url"]

    entry = {
        "repository": get_repository(),
        "username": get_username(),
        "email": get_email(),
        "tool": args.tool,
        "event": args.event,
        "date": datetime.now().isoformat(timespec="seconds"),
        "machine": socket.gethostname(),
        "machine_user": get_system_user(),
        "hook_integrity": hook_integrity,
    }

    # HMAC-sign the entry with this repo's signing secret so the instructor can
    # distinguish genuine entries from forged ones. Falls back to a repo-derived
    # value if no per-repo secret was injected (weaker, but still consistent).
    secret = config.get("signing_secret") or (
        "hook::" + entry["repository"]
    )
    entry["sig"] = hmac.new(
        secret.encode("utf-8"),
        json.dumps(entry, sort_keys=True).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    payload = [entry]
    body = json.dumps(payload).encode("utf-8")
    req = Request(
        url, data=body, method="POST", headers={"Content-Type": "application/json"}
    )
    try:
        urlopen(req, timeout=10)
    except (URLError, OSError):
        pass
    print("{}")


if __name__ == "__main__":
    main()
    sys.exit(0)
