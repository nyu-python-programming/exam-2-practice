#!/usr/bin/env python3
"""
Exam autosave watcher  --  DO NOT MODIFY THIS FILE.

This program automatically saves your exam work to GitHub every few seconds so
that, if your computer crashes or your internet drops, your progress is never
lost. It is REQUIRED to be running for the whole exam. Keep its window open.

It is also part of how your instructor confirms the integrity of submissions.
By running it (as the exam instructions require) you acknowledge this; see the
exam policy / honor pledge in the README.

What it does, in plain terms:
  * every few seconds it checks whether your files changed;
  * when they do (and at least once a minute regardless) it takes a snapshot of
    your work and pushes it to a separate branch named "autosave" on GitHub;
  * it shows you a green RUNNING banner so you can confirm at a glance that your
    work is being saved, and a loud red message if a save ever fails.

It does NOT touch your normal git branch, your commits, or your staged files --
snapshots live entirely on the separate "autosave" branch and are built with a
temporary index, so your ordinary "commit and push when done" workflow is
unaffected.

Run it with the double-click launcher for your operating system
(Start-Exam-Autosave.command / .bat / .sh) or with:  python3 .automations/autosave.py
"""

import hashlib
import hmac
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
CONFIG_PATH = HERE / "config.json"
# Local-only bookkeeping. Set under the .git directory at runtime so it is never
# part of the working tree (never snapshotted) and never copied with the repo.
STATE_PATH = HERE / ".autosave_state.json"
INDEX_PATH = HERE / ".autosave_index"

AUTOSAVE_BRANCH = "autosave"
POLL_SECONDS = 3            # how often we look for changes
DEBOUNCE_SECONDS = 4        # snapshot once typing has settled for this long
MAX_DEBOUNCE_SECONDS = 20   # ...but force a snapshot if edits stay dirty this long
HEARTBEAT_SECONDS = 60      # snapshot at least this often, even with no changes
PUSH_RETRY_SECONDS = 10     # retry cadence after a failed push

# Directories / files we never snapshot.
EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", ".vscode", ".idea",
                "node_modules", ".mypy_cache", ".venv", "venv"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".log", ".tmp"}
EXCLUDE_NAMES = {".DS_Store", ".autosave_state.json"}

# ANSI colors (kept simple; degrade to no-color if unsupported).
RESET, BOLD = "\033[0m", "\033[1m"
GREEN, RED, YELLOW, CYAN = "\033[32m", "\033[31m", "\033[33m", "\033[36m"


def _enable_ansi():
    """Best-effort enable of ANSI colors on Windows 10+ consoles."""
    if os.name != "nt":
        return True
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004 on the std output handle
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        return True
    except Exception:
        return False


ANSI = _enable_ansi()


def c(text, color):
    return f"{color}{text}{RESET}" if ANSI else text


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #

def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def git(args, env=None, check=True, _input=None):
    """Run a git command in the project root; return stdout (stripped)."""
    result = subprocess.run(
        ["git", *args],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        input=_input,
        env=env,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({result.returncode}): "
            f"{(result.stderr or result.stdout).strip()}"
        )
    return (result.stdout or "").strip()


def init_storage():
    """Place state/index files inside the .git dir (never in the working tree)."""
    global STATE_PATH, INDEX_PATH
    try:
        base = Path(git(["rev-parse", "--absolute-git-dir"]))
    except Exception:
        base = HERE
    STATE_PATH = base / "autosave_state.json"
    INDEX_PATH = base / "autosave_index"


def total_lines():
    """Total newline count across tracked files -- used to size per-poll jumps."""
    total = 0
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for name in files:
            if name in EXCLUDE_NAMES or Path(name).suffix in EXCLUDE_SUFFIXES:
                continue
            try:
                with open(Path(root) / name, "rb") as f:
                    total += f.read().count(b"\n")
            except OSError:
                continue
    return total


def self_hash():
    try:
        return hashlib.sha256(Path(__file__).resolve().read_bytes()).hexdigest()
    except OSError:
        return "unknown"


def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def signing_secret(config):
    """
    Per-repo signing secret used to HMAC each snapshot so the server can detect
    forged / replayed heartbeats. Distributed per-repo (e.g. via GitHub
    Classroom). Falls back to a repo-derived value so the watcher still runs and
    signs consistently even if a secret was not injected -- note that a fallback
    secret is weaker (it is derivable), which the grading tool accounts for.
    """
    secret = (config or {}).get("signing_secret")
    if secret:
        return str(secret).encode("utf-8")
    try:
        origin = git(["remote", "get-url", "origin"], check=False)
    except Exception:
        origin = ""
    return hashlib.sha256(f"autosave::{origin}".encode("utf-8")).hexdigest().encode("utf-8")


def load_state():
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {"seq": 0}


def save_state(state):
    try:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except OSError:
        pass


# --------------------------------------------------------------------------- #
# Working-tree change detection
# --------------------------------------------------------------------------- #

def tree_fingerprint():
    """
    Cheap fingerprint of the working tree (path -> mtime/size) so we can tell
    when something changed without invoking git on every poll.
    """
    fp = {}
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for name in files:
            if name in EXCLUDE_NAMES or Path(name).suffix in EXCLUDE_SUFFIXES:
                continue
            path = Path(root) / name
            try:
                st = path.stat()
                fp[str(path)] = (int(st.st_mtime), st.st_size)
            except OSError:
                continue
    return fp


# --------------------------------------------------------------------------- #
# Snapshotting (build a commit on the autosave branch via a temp index)
# --------------------------------------------------------------------------- #

def autosave_parent():
    sha = git(["rev-parse", "--verify", "--quiet", f"refs/heads/{AUTOSAVE_BRANCH}"],
              check=False)
    return sha or None


def make_snapshot(state, secret, reason, max_poll_added=0):
    """
    Capture the full working tree as a commit on refs/heads/autosave without
    touching the student's real index or branch. Returns the metadata dict, or
    None if nothing changed since the last snapshot.

    max_poll_added is the largest single-poll line jump observed since the last
    snapshot -- a robust paste signal that does not get diluted when several
    edits are bundled into one snapshot.
    """
    tmp_index = INDEX_PATH
    env = os.environ.copy()
    env["GIT_INDEX_FILE"] = str(tmp_index)
    try:
        # Build a fresh index from the current working tree.
        git(["read-tree", "--empty"], env=env)
        git(["add", "-A"], env=env)
        tree = git(["write-tree"], env=env)
    finally:
        try:
            tmp_index.unlink()
        except OSError:
            pass

    parent = autosave_parent()

    # Skip if the tree is identical to the last snapshot (and this isn't the
    # first heartbeat establishing the branch).
    if parent:
        parent_tree = git(["rev-parse", f"{parent}^{{tree}}"], check=False)
        if parent_tree == tree and reason == "change":
            return None

    # Compute what changed vs the previous snapshot.
    added = removed = 0
    files = []
    if parent:
        numstat = git(["diff", "--numstat", parent, tree], check=False)
        for line in numstat.splitlines():
            parts = line.split("\t")
            if len(parts) == 3:
                a, r, fname = parts
                added += int(a) if a.isdigit() else 0
                removed += int(r) if r.isdigit() else 0
                files.append(fname)

    seq = int(state.get("seq", 0)) + 1
    payload = {
        "v": 1,
        "seq": seq,
        "ts": now_iso(),
        "reason": reason,
        "tree": tree,
        "parent": parent,
        "added": added,
        "removed": removed,
        "max_poll_added": max_poll_added,
        "files": files,
        "self_hash": self_hash(),
    }
    payload["sig"] = hmac.new(
        secret, json.dumps(payload, sort_keys=True).encode("utf-8"), hashlib.sha256
    ).hexdigest()

    message = "autosave #{seq}\n\n{json}".format(
        seq=seq, json=json.dumps(payload, sort_keys=True)
    )

    parent_args = ["-p", parent] if parent else []
    commit = git(["commit-tree", tree, *parent_args], _input=message)
    git(["update-ref", f"refs/heads/{AUTOSAVE_BRANCH}", commit])

    state["seq"] = seq
    save_state(state)
    payload["commit"] = commit
    return payload


def push_autosave():
    git(["push", "origin", f"{AUTOSAVE_BRANCH}:{AUTOSAVE_BRANCH}"])


# --------------------------------------------------------------------------- #
# Pre-flight self-test (plain-English PASS/FAIL, including a real test push)
# --------------------------------------------------------------------------- #

def preflight(secret):
    print(c("\nChecking your setup...\n", BOLD))
    ok = True

    def line(passed, label, detail=""):
        nonlocal ok
        mark = c("[OK]", GREEN) if passed else c("[X]", RED)
        print(f"  {mark} {label}" + (f"  {c(detail, YELLOW)}" if detail else ""))
        ok = ok and passed

    def warn(label, detail=""):
        print(f"  {c('[!]', YELLOW)} {label}"
              + (f"  {c(detail, YELLOW)}" if detail else ""))

    line(True, f"Python found ({sys.version.split()[0]})")

    try:
        git(["--version"])
        line(True, "Git is installed")
    except Exception:
        line(False, "Git is installed", "Install Git, then restart this window.")
        return False

    try:
        git(["rev-parse", "--git-dir"])
        line(True, "You are inside your exam repository")
    except Exception:
        line(False, "You are inside your exam repository",
             "Open this from your cloned exam folder.")
        return False

    # The hard requirement is a working *local* save: the autosave branch is the
    # evidence stream and is built with local git only, so it works with no
    # network and no remote. We never abort on a missing remote or a failed
    # upload -- snapshots are kept locally and can be collected/verified later.
    try:
        state = load_state()
        snap = make_snapshot(state, secret, reason="preflight")
        line(True, "Local autosave works",
             f"snapshot #{(snap or {}).get('seq', '?')} saved on this computer")
    except Exception as exc:
        line(False, "Local autosave FAILED")
        print()
        print(c(f"  PROBLEM: could not record a snapshot locally. Details: {exc}",
                RED + BOLD))
        return False

    # Uploading to GitHub is best-effort -- never fatal.
    origin = git(["remote", "get-url", "origin"], check=False)
    if not origin:
        warn("No GitHub remote -- saving locally only",
             "snapshots stay on this computer; hand in the repo to share them.")
        return True

    try:
        push_autosave()
        line(True, "Connected to GitHub (test save uploaded)",
             f"snapshot #{(snap or {}).get('seq', '?')} pushed")
    except Exception as exc:
        warn("Could not upload to GitHub -- saving locally and will keep retrying",
             str(exc))
        warn("If this is your exam repo, push once in VS Code to log in, then "
             "restart this window.")

    return True


# --------------------------------------------------------------------------- #
# Banner / heartbeat display
# --------------------------------------------------------------------------- #

def banner(saves, last_save, status_line):
    bar = "=" * 52
    print()
    print(c(bar, GREEN))
    print(c("    EXAM AUTOSAVE IS RUNNING", GREEN + BOLD))
    print(c("    Keep this window OPEN until you finish & submit.", GREEN))
    print(c(f"    Last save: {last_save}", GREEN))
    print(c(f"    Saves so far: {saves}", GREEN))
    if status_line:
        print(c(f"    {status_line}", YELLOW))
    print(c(bar, GREEN))


# --------------------------------------------------------------------------- #
# Main loop
# --------------------------------------------------------------------------- #

def main():
    # Make console output crash-proof on any platform/codepage (notably legacy
    # Windows consoles or redirected stdout): prefer UTF-8, and never raise on a
    # character the terminal can't encode -- replace it instead.
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    print(c(BOLD + "\n  Exam Autosave Watcher" + RESET, CYAN))
    print(c("  (keep this window open for the entire exam)\n", CYAN))

    config = load_config()
    secret = signing_secret(config)
    init_storage()

    if not preflight(secret):
        print(c("\n  Autosave is NOT running. Fix the problem above and "
                "re-launch.\n", RED + BOLD))
        try:
            input("  Press Enter to close this window...")
        except EOFError:
            pass
        return 1

    state = load_state()
    saves = int(state.get("seq", 0))
    last_save = now_iso()
    has_remote = bool(git(["remote", "get-url", "origin"], check=False))
    banner(saves, last_save,
           "" if has_remote else "Saving locally (no GitHub remote).")

    last_fp = tree_fingerprint()
    pending_since = None     # when the current dirty streak began
    last_change = None       # most recent detected change
    last_heartbeat = time.monotonic()
    push_backoff_until = 0.0
    prev_lines = total_lines()
    max_poll_added = 0       # biggest single-poll line jump since last snapshot

    def commit_and_push(reason):
        nonlocal saves, last_save, push_backoff_until, max_poll_added
        snap = make_snapshot(state, secret, reason=reason,
                             max_poll_added=max_poll_added)
        if snap is None:
            return
        max_poll_added = 0
        # The local snapshot is the evidence -- count it as a save whether or not
        # it uploads, so the autosave branch keeps growing for later diff checks.
        saves = snap["seq"]
        last_save = snap["ts"]

        if not has_remote:
            banner(saves, last_save, "Saving locally (no GitHub remote).")
            return

        try:
            push_autosave()
            push_backoff_until = 0.0
            banner(saves, last_save, "")
        except Exception as exc:
            push_backoff_until = time.monotonic() + PUSH_RETRY_SECONDS
            banner(saves, last_save,
                   f"Saved locally; upload to GitHub failed -- will retry. ({exc})")

    try:
        while True:
            time.sleep(POLL_SECONDS)
            now = time.monotonic()

            # Retry a failed push as soon as the backoff elapses.
            if push_backoff_until and now >= push_backoff_until:
                commit_and_push("retry")

            fp = tree_fingerprint()
            if fp != last_fp:
                last_fp = fp
                last_change = now
                if pending_since is None:
                    pending_since = now  # start a new dirty streak
                # Track the biggest single-poll insertion (a paste appears as a
                # large jump within one ~3s poll; typing adds only a few lines).
                cur_lines = total_lines()
                jump = cur_lines - prev_lines
                prev_lines = cur_lines
                if jump > max_poll_added:
                    max_poll_added = jump

            # Snapshot when typing has settled OR the streak has run long enough
            # (so sustained, continuous editing still gets periodic snapshots).
            if pending_since is not None and (
                (now - last_change) >= DEBOUNCE_SECONDS
                or (now - pending_since) >= MAX_DEBOUNCE_SECONDS
            ):
                pending_since = None
                last_change = None
                commit_and_push("change")
                last_heartbeat = now

            # Heartbeat snapshot so idle vs. stopped is distinguishable.
            if (now - last_heartbeat) >= HEARTBEAT_SECONDS:
                last_heartbeat = now
                commit_and_push("heartbeat")
    except KeyboardInterrupt:
        print(c("\n  Autosave stopped. Remember to commit & push your final "
                "work in VS Code.\n", YELLOW + BOLD))
        return 0


if __name__ == "__main__":
    sys.exit(main())
