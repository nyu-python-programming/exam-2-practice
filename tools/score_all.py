#!/usr/bin/env python3
"""
score_all.py -- instructor-side AI-likelihood scorer for Exam #2.

Runs on the GRADER'S machine, in batch over a parent directory whose
subdirectories are each a student's cloned submission (fetched with all
branches, so the `autosave` snapshot stream is present).

    python3 tools/score_all.py ./submissions/ \
        --telemetry telemetry.csv \
        --baseline baseline_manifest.json \
        --private-tests tests_private \
        --out report_out

It produces, in the output directory:
  * index.html        -- cohort dashboard, sorted by descending AI-likelihood
  * risk_report.csv   -- the same data, machine-readable
  * reports/<handle>.html -- per-student detail (open only Reds/Ambers)

Design principles (see the plan):
  * Convergence, not single-signal: Red requires >= 2 independent high/medium
    signals. A lone soft signal can never reach Red.
  * Fault TOLERANCE, not resistance: no signal is mandatory. Missing data never
    aborts. Optional-absent is neutral; a missing *required* input (no autosave
    stream though the watcher was required) is itself a risk signal. Low
    evidence coverage routes to manual review, never auto-Green.
  * The score is a triage / likelihood indicator, NOT a verdict.

Standard library only.
"""

import argparse
import csv
import html
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# --------------------------------------------------------------------------- #
# Tunables (calibrate on a dry run against known-honest samples)
# --------------------------------------------------------------------------- #

BIG_INSERT_LINES = 25          # a single snapshot adding >= this many lines = burst
HEARTBEAT_GAP_SECONDS = 300    # gap in the snapshot stream that looks like "watcher off"
MIN_SNAPSHOTS_EXPECTED = 3     # fewer than this on a multi-hour exam is suspicious
RECON_OK_FRACTION = 0.60       # >= this fraction of final code seen incrementally is fine
SIMILARITY_FLAG = 0.80         # normalized cross-submission similarity to flag
LOW_COVERAGE = 0.34            # below this fraction of inputs -> force manual review

POINTS = {"high": 40, "medium": 25, "low": 10, "info": 0}

PROBLEM_FILES = ["problem_1.py", "problem_2.py", "problem_3.py", "problem_4.py"]

JSON_IN_MSG = re.compile(r"\{.*\}", re.DOTALL)


# --------------------------------------------------------------------------- #
# git helpers (operate on a given repo dir; never raise to the caller)
# --------------------------------------------------------------------------- #

def git(repo, args):
    """Run git in `repo`; return (ok, stdout)."""
    try:
        r = subprocess.run(["git", "-C", str(repo), *args],
                           capture_output=True, text=True, check=False)
        return r.returncode == 0, (r.stdout or "")
    except Exception:
        return False, ""


def autosave_ref(repo):
    for ref in ("refs/heads/autosave", "refs/remotes/origin/autosave",
                "autosave", "origin/autosave"):
        ok, _ = git(repo, ["rev-parse", "--verify", "--quiet", ref])
        if ok:
            return ref
    return None


def origin_url(repo):
    ok, out = git(repo, ["remote", "get-url", "origin"])
    return out.strip() if ok else ""


def git_author(repo):
    ok, out = git(repo, ["log", "-1", "--format=%an <%ae>"])
    return out.strip() if ok else ""


# --------------------------------------------------------------------------- #
# Snapshot-stream parsing
# --------------------------------------------------------------------------- #

def parse_ts(ts):
    try:
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


def read_snapshots(repo):
    """Return a list of snapshot metadata dicts (oldest first), or []."""
    ref = autosave_ref(repo)
    if not ref:
        return []
    ok, out = git(repo, ["log", "--format=%H%x1f%B%x1e", ref])
    if not ok:
        return []
    snaps = []
    for chunk in out.split("\x1e"):
        chunk = chunk.strip()
        if not chunk:
            continue
        commit, _, body = chunk.partition("\x1f")
        m = JSON_IN_MSG.search(body)
        if not m:
            continue
        try:
            meta = json.loads(m.group(0))
        except json.JSONDecodeError:
            continue
        meta["commit"] = commit.strip()
        snaps.append(meta)
    snaps.reverse()  # oldest first
    return snaps


# --------------------------------------------------------------------------- #
# A signal accumulator per student
# --------------------------------------------------------------------------- #

class Report:
    def __init__(self, handle, repo):
        self.handle = handle
        self.repo = repo
        self.signals = []          # list of dicts: key, severity, evidence
        self.inputs = {}           # input name -> present|neutral-absent|expected-missing
        self.issues = []           # data-quality notes
        self.details = {}          # freeform per-section detail for the HTML report

    def add(self, key, severity, evidence):
        self.signals.append({"key": key, "severity": severity, "evidence": evidence})

    def mark(self, name, status):
        self.inputs[name] = status

    def note(self, msg):
        self.issues.append(msg)

    # --- scoring -------------------------------------------------------------
    def coverage(self):
        if not self.inputs:
            return 0.0
        present = sum(1 for v in self.inputs.values() if v == "present")
        return present / len(self.inputs)

    def score(self):
        return min(100, sum(POINTS[s["severity"]] for s in self.signals))

    def strong_count(self):
        return sum(1 for s in self.signals if s["severity"] in ("high", "medium"))

    def tier(self):
        strong = self.strong_count()
        low = sum(1 for s in self.signals if s["severity"] == "low")
        if strong >= 2:
            t = "RED"
        elif strong == 1 or low >= 2:
            t = "AMBER"
        else:
            t = "GREEN"
        # Low evidence coverage must never auto-clear to Green.
        if t == "GREEN" and self.coverage() < LOW_COVERAGE:
            t = "AMBER"
            self.add("low-coverage", "low",
                     "Too little evidence available to clear this submission "
                     "confidently -- manual review recommended.")
        return t

    def top_reasons(self, n=3):
        order = {"high": 0, "medium": 1, "low": 2, "info": 3}
        ranked = sorted(self.signals, key=lambda s: order[s["severity"]])
        return [s["evidence"] for s in ranked[:n]]


# --------------------------------------------------------------------------- #
# Feature extractors -- each guarded; missing data never aborts
# --------------------------------------------------------------------------- #

def feat_cadence_and_burst(rep, snaps, cohort_median_active):
    if not snaps:
        rep.mark("autosave_stream", "expected-missing")
        rep.add("no-autosave", "medium",
                "No autosave snapshot stream found, though the watcher was "
                "required -- work may have been done with the watcher off.")
        return None
    rep.mark("autosave_stream", "present")

    times = [parse_ts(s.get("ts")) for s in snaps]
    times = [t for t in times if t]
    active_min = None
    if len(times) >= 2:
        active_min = (max(times) - min(times)).total_seconds() / 60.0
        rep.details["active_minutes"] = round(active_min, 1)
        rep.details["snapshots"] = len(snaps)

    if len(snaps) < MIN_SNAPSHOTS_EXPECTED:
        rep.add("thin-stream", "medium",
                f"Only {len(snaps)} snapshot(s) recorded -- too few for a "
                "multi-hour exam; the watcher likely was not running normally.")

    # Heartbeat / activity gaps.
    gaps = []
    for a, b in zip(times, times[1:]):
        secs = (b - a).total_seconds()
        if secs >= HEARTBEAT_GAP_SECONDS:
            gaps.append((a, b, secs))
    if gaps:
        biggest = max(g[2] for g in gaps) / 60.0
        rep.details["gaps"] = [(g[0].isoformat(), g[1].isoformat(), int(g[2]))
                               for g in gaps]
        rep.add("heartbeat-gap", "low",
                f"{len(gaps)} gap(s) in the autosave stream (largest "
                f"{biggest:.0f} min) -- watcher stopped, then resumed.")

    # Burst / paste detection. Prefer the largest single-poll jump (robust to
    # several edits being bundled into one snapshot); fall back to total added
    # for snapshots produced before that field existed.
    def burst_size(s):
        v = s.get("max_poll_added")
        return int(v) if v is not None else int(s.get("added", 0))

    bursts = [s for s in snaps if burst_size(s) >= BIG_INSERT_LINES]
    if bursts:
        biggest = max(burst_size(s) for s in bursts)
        rep.details["bursts"] = [
            {"ts": s.get("ts"), "added": burst_size(s),
             "removed": s.get("removed"), "files": s.get("files", []),
             "commit": s.get("commit")}
            for s in bursts
        ]
        sev = "high" if biggest >= 2 * BIG_INSERT_LINES else "medium"
        rep.add("paste-burst", sev,
                f"{len(bursts)} large insertion(s); biggest added {biggest} "
                "lines in a single ~minute snapshot (pasted, not typed).")

    # Fast-finish outlier vs cohort.
    if active_min is not None and cohort_median_active:
        if active_min < 0.35 * cohort_median_active:
            rep.add("fast-finish", "low",
                    f"Active editing time {active_min:.0f} min is far below the "
                    f"cohort median ({cohort_median_active:.0f} min).")
    return active_min


def feat_reconciliation(rep, snaps):
    """Fraction of final problem-file code that ever appeared incrementally."""
    if not snaps:
        rep.mark("reconciliation", "expected-missing")
        return
    rep.mark("reconciliation", "present")

    # All non-trivial lines that ever appeared in any snapshot, per file.
    seen = defaultdict(set)
    for s in snaps:
        commit = s.get("commit")
        if not commit:
            continue
        for path in PROBLEM_FILES:
            ok, content = git(rep.repo, ["show", f"{commit}:{path}"])
            if not ok:
                continue
            for line in content.splitlines():
                stripped = line.strip()
                if len(stripped) > 3 and not stripped.startswith("#"):
                    seen[path].add(stripped)

    total = matched = 0
    unreconciled_files = []
    for path in PROBLEM_FILES:
        final = Path(rep.repo) / path
        if not final.exists():
            continue
        final_lines = [ln.strip() for ln in final.read_text(
            encoding="utf-8", errors="replace").splitlines()
            if len(ln.strip()) > 3 and not ln.strip().startswith("#")]
        if not final_lines:
            continue
        present = sum(1 for ln in final_lines if ln in seen[path])
        total += len(final_lines)
        matched += present
        frac = present / len(final_lines)
        if frac < RECON_OK_FRACTION:
            unreconciled_files.append((path, frac))

    if total:
        overall = matched / total
        rep.details["reconciliation"] = round(overall, 2)
        if overall < RECON_OK_FRACTION:
            rep.add("reconciliation-gap", "high",
                    f"Only {overall*100:.0f}% of final code appeared "
                    "incrementally in snapshots -- the rest materialized at the "
                    "end (watcher bypassed / pasted outside it).")
        elif unreconciled_files:
            names = ", ".join(f"{p} ({f*100:.0f}%)" for p, f in unreconciled_files)
            rep.add("partial-reconciliation", "low",
                    f"Some files have low incremental provenance: {names}.")


def feat_seq_integrity(rep, snaps, secret):
    """Sequence monotonicity + (optional) HMAC verification."""
    if not snaps:
        return
    seqs = [int(s.get("seq", 0)) for s in snaps]
    if seqs != sorted(seqs) or len(set(seqs)) != len(seqs):
        rep.add("seq-anomaly", "medium",
                "Snapshot sequence numbers are non-monotonic or duplicated -- "
                "the autosave history may have been rewritten/force-pushed.")

    if secret is None:
        rep.mark("hmac", "neutral-absent")
        return
    rep.mark("hmac", "present")
    bad = 0
    import hmac as _hmac
    import hashlib as _hashlib
    for s in snaps:
        sig = s.get("sig")
        if not sig:
            continue
        payload = {k: s[k] for k in s
                   if k not in ("sig", "commit")}
        expect = _hmac.new(secret, json.dumps(payload, sort_keys=True).encode(),
                          _hashlib.sha256).hexdigest()
        if expect != sig:
            bad += 1
    if bad:
        rep.add("hmac-fail", "high",
                f"{bad} snapshot(s) failed HMAC verification -- forged or "
                "tampered autosave entries.")


def feat_baseline(rep, baseline):
    """Compare committed instrumentation files to the canonical baseline."""
    if not baseline:
        rep.mark("baseline", "neutral-absent")
        return
    rep.mark("baseline", "present")
    import hashlib as _hashlib
    mismatched, missing = [], []
    for relpath, expected in baseline.items():
        f = Path(rep.repo) / relpath
        if not f.exists():
            missing.append(relpath)
            continue
        actual = _hashlib.sha256(f.read_bytes()).hexdigest()
        if actual != expected:
            mismatched.append(relpath)
    if missing:
        rep.add("instrumentation-stripped", "high",
                "Required instrumentation file(s) missing: "
                + ", ".join(missing) + ".")
    if mismatched:
        rep.add("instrumentation-modified", "high",
                "Instrumentation file(s) modified vs baseline: "
                + ", ".join(mismatched) + ".")


def feat_telemetry(rep, tel_rows, baseline):
    """Editor-agent hook events joined on repository (fallback identity)."""
    if tel_rows is None:
        rep.mark("telemetry", "neutral-absent")
        return
    rep.mark("telemetry", "present")
    if not tel_rows:
        return  # no agent events for this student == neutral
    tools = sorted({r.get("tool", "?") for r in tel_rows})
    events = len(tel_rows)
    rep.details["telemetry"] = [
        {k: r.get(k, "") for k in ("date", "tool", "event", "machine",
                                   "machine_user")}
        for r in tel_rows
    ]
    rep.add("agent-edits", "high",
            f"{events} AI-agent edit event(s) recorded "
            f"({', '.join(tools)}) -- direct evidence an agent edited files.")

    # Identity mismatch: telemetry identity vs git author.
    author = git_author(rep.repo).lower()
    tel_emails = {r.get("email", "").lower() for r in tel_rows if r.get("email")}
    if author and tel_emails and not any(e and e in author for e in tel_emails):
        rep.add("identity-mismatch", "low",
                "Telemetry identity does not match the repo's git author "
                f"({author}).")

    # Telemetry-side instrumentation integrity (lazy-tamperer tripwire).
    if baseline:
        for r in tel_rows:
            hi = r.get("hook_integrity", "")
            if hi and "missing" in hi:
                rep.add("hook-missing-runtime", "medium",
                        "Hook integrity report shows a missing instrumentation "
                        "file at run time.")
                break


# --------------------------------------------------------------------------- #
# Cross-cohort features
# --------------------------------------------------------------------------- #

def normalize_code(text):
    """Crude identifier/whitespace normalization so light refactors still match."""
    text = re.sub(r"#.*", "", text)
    text = re.sub(r'"""[\s\S]*?"""', "", text)
    text = re.sub(r"'''[\s\S]*?'''", "", text)
    toks = re.findall(r"[A-Za-z_]\w*|[^\s\w]", text)
    out = []
    for t in toks:
        if t.isidentifier() and t not in KEYWORDS:
            out.append("V")          # collapse all identifiers to a placeholder
        else:
            out.append(t)
    return out


KEYWORDS = {"def", "return", "if", "elif", "else", "while", "for", "in", "and",
            "or", "not", "is", "True", "False", "None", "import", "from", "with",
            "as", "try", "except", "finally", "break", "continue", "pass",
            "print", "input", "int", "str", "float", "open", "range", "len"}


def shingles(tokens, k=5):
    return {tuple(tokens[i:i + k]) for i in range(len(tokens) - k + 1)}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def cohort_similarity(reports):
    """
    Pairwise normalized similarity over concatenated problem files. Because all
    correct solutions to the same small spec converge, a high *absolute*
    similarity is normal -- so we flag only a pair that is a clear *outlier*
    above the cohort's own similarity distribution (far more alike than typical
    pairs are). This keeps false positives down on convergent exam answers.
    """
    sigs = {}
    for rep in reports:
        toks = []
        for path in PROBLEM_FILES:
            f = Path(rep.repo) / path
            if f.exists():
                toks += normalize_code(f.read_text(encoding="utf-8",
                                                   errors="replace"))
        sigs[rep.handle] = shingles(toks)

    handles = list(sigs)
    pair = {}
    allvals = []
    for i, h in enumerate(handles):
        for j in range(i + 1, len(handles)):
            g = handles[j]
            s = jaccard(sigs[h], sigs[g])
            pair[(h, g)] = pair[(g, h)] = s
            allvals.append(s)

    # Outlier threshold from the cohort's own distribution.
    thresh = SIMILARITY_FLAG
    if allvals:
        sv = sorted(allvals)
        p75 = sv[min(len(sv) - 1, int(0.75 * len(sv)))]
        thresh = max(SIMILARITY_FLAG, p75 + 0.10)

    for h in handles:
        rep = next(r for r in reports if r.handle == h)
        rep.mark("similarity", "present" if sigs[h] else "neutral-absent")
        best, best_with = 0.0, None
        for g in handles:
            if g == h:
                continue
            s = pair.get((h, g), 0.0)
            if s > best:
                best, best_with = s, g
        rep.details["max_similarity"] = (round(best, 2), best_with)
        # Require enough distinctive shingles so tiny solutions don't false-match.
        if best >= thresh and best_with and len(sigs[h]) >= 8:
            rep.add("high-similarity", "medium",
                    f"{best*100:.0f}% normalized code similarity to "
                    f"'{best_with}' -- a clear outlier above the cohort "
                    "(survives variable renaming).")


def cohort_collusion(reports, telemetry_by_repo):
    """Same machine+machine_user across different repositories."""
    machine_to_repos = defaultdict(set)
    repo_to_handle = {}
    for rep in reports:
        url = origin_url(rep.repo)
        repo_to_handle[url] = rep.handle
        for r in telemetry_by_repo.get(url, []):
            key = (r.get("machine", ""), r.get("machine_user", ""))
            if any(key):
                machine_to_repos[key].add(url)
    for key, repos in machine_to_repos.items():
        if len(repos) > 1:
            handles = sorted(repo_to_handle.get(u, u) for u in repos)
            for rep in reports:
                if origin_url(rep.repo) in repos:
                    others = [h for h in handles if h != rep.handle]
                    rep.add("shared-machine", "medium",
                            f"Same machine/OS-user ({key[0]}/{key[1]}) also "
                            f"used by: {', '.join(others)}.")


def feat_hidden_tests(rep, private_tests):
    if not private_tests:
        rep.mark("hidden_tests", "neutral-absent")
        return
    rep.mark("hidden_tests", "present")
    # The private suite lives outside the student repo; put the repo on the path
    # so `from problem_1 import *` resolves to the submission's code.
    env = os.environ.copy()
    env["PYTHONPATH"] = str(rep.repo) + os.pathsep + env.get("PYTHONPATH", "")
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
             str(Path(private_tests).resolve())],
            cwd=str(rep.repo), capture_output=True, text=True, check=False,
            timeout=120, env=env,
        )
        if r.returncode != 0:
            tail = (r.stdout or "").strip().splitlines()[-1:] or [""]
            rep.add("hidden-test-fail", "medium",
                    "Fails the hidden test suite though visible tests may pass "
                    f"(shallow / tuned-to-visible): {tail[0]}")
    except Exception as exc:
        rep.mark("hidden_tests", "neutral-absent")
        rep.note(f"hidden tests could not run: {exc}")


# --------------------------------------------------------------------------- #
# Telemetry loading
# --------------------------------------------------------------------------- #

def load_telemetry(path):
    """Return (rows_by_repo, rows_by_email) or (None, None) if unavailable."""
    if not path or not Path(path).exists():
        return None, None
    by_repo = defaultdict(list)
    by_email = defaultdict(list)
    try:
        with open(path, newline="", encoding="utf-8", errors="replace") as f:
            # The export is tab-separated.
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                row = {(k or "").strip(): (v or "").strip()
                       for k, v in row.items()}
                if row.get("repository"):
                    by_repo[row["repository"]].append(row)
                if row.get("email"):
                    by_email[row["email"].lower()].append(row)
    except Exception:
        return None, None
    return by_repo, by_email


def telemetry_for(repo_url, author, by_repo, by_email):
    if by_repo is None:
        return None
    rows = list(by_repo.get(repo_url, []))
    if not rows and author and by_email:
        for email, erows in by_email.items():
            if email in author.lower():
                rows += erows
    return rows


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #

TIER_COLOR = {"RED": "#c0392b", "AMBER": "#e67e22", "GREEN": "#27ae60"}
TIER_EMOJI = {"RED": "🔴", "AMBER": "🟡", "GREEN": "🟢"}


def render_dashboard(reports, out_dir):
    rows = sorted(reports, key=lambda r: r.score(), reverse=True)
    cells = []
    for r in rows:
        tier = r.tier()
        reasons = "<br>".join(html.escape(x) for x in r.top_reasons()) or "&mdash;"
        cells.append(
            f"<tr>"
            f"<td><a href='reports/{html.escape(r.handle)}.html'>"
            f"{html.escape(r.handle)}</a></td>"
            f"<td style='text-align:center;font-weight:bold'>{r.score()}</td>"
            f"<td style='text-align:center'>{TIER_EMOJI[tier]} "
            f"<b style='color:{TIER_COLOR[tier]}'>{tier}</b></td>"
            f"<td style='text-align:center'>{int(r.coverage()*100)}%</td>"
            f"<td>{reasons}</td>"
            f"</tr>"
        )
    page = f"""<!doctype html><meta charset=utf-8>
<title>Exam #2 -- AI-likelihood dashboard</title>
<style>
body{{font:14px system-ui,Arial;margin:24px;color:#222}}
table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #ddd;padding:8px;vertical-align:top}}
th{{background:#f4f4f4;text-align:left}}
tr:hover{{background:#fafafa}}
.note{{color:#666;max-width:60em}}
</style>
<h1>Exam #2 &mdash; AI-likelihood dashboard</h1>
<p class=note>Ranked by review priority. The score is a <b>triage indicator,
not a verdict</b>: a <b>RED</b> means &ge;2 independent signals converged and a
2&ndash;3 minute oral check is recommended before any conclusion. Coverage shows
how much evidence was available; a low-coverage row was <b>not</b> auto-cleared.</p>
<table>
<tr><th>Student</th><th>Score</th><th>Tier</th><th>Coverage</th>
<th>Top reasons</th></tr>
{''.join(cells)}
</table>
<p class=note>{len(reports)} submissions scored.</p>
"""
    (Path(out_dir) / "index.html").write_text(page, encoding="utf-8")


def render_student(rep, out_dir):
    tier = rep.tier()
    parts = [f"""<!doctype html><meta charset=utf-8>
<title>{html.escape(rep.handle)} -- detail</title>
<style>
body{{font:14px system-ui,Arial;margin:24px;color:#222;max-width:60em}}
.badge{{font-size:20px;font-weight:bold;color:{TIER_COLOR[tier]}}}
code,pre{{background:#f6f6f6;padding:2px 4px;border-radius:3px}}
pre{{padding:10px;overflow:auto}}
.sig-high{{color:#c0392b}} .sig-medium{{color:#e67e22}} .sig-low{{color:#b8860b}}
h2{{border-bottom:1px solid #eee;padding-bottom:4px;margin-top:28px}}
</style>
<p><a href='../index.html'>&larr; back to dashboard</a></p>
<h1>{html.escape(rep.handle)}</h1>
<p class=badge>{TIER_EMOJI[tier]} {tier} &middot; score {rep.score()}/100
&middot; evidence coverage {int(rep.coverage()*100)}%</p>
"""]
    action = {"RED": "Recommended: 2&ndash;3 min oral check before any conclusion.",
              "AMBER": "Recommended: manual review.",
              "GREEN": "No action indicated."}[tier]
    parts.append(f"<p><b>Recommended action:</b> {action}</p>")

    parts.append("<h2>Signals</h2>")
    if rep.signals:
        parts.append("<ul>")
        for s in sorted(rep.signals,
                       key=lambda x: {"high": 0, "medium": 1, "low": 2,
                                      "info": 3}[x["severity"]]):
            parts.append(f"<li class='sig-{s['severity']}'><b>"
                        f"[{s['severity'].upper()}]</b> "
                        f"{html.escape(s['evidence'])}</li>")
        parts.append("</ul>")
    else:
        parts.append("<p>No signals triggered.</p>")

    d = rep.details
    parts.append("<h2>Cadence</h2>")
    parts.append(f"<p>Active editing time: "
                f"<b>{d.get('active_minutes','?')}</b> min over "
                f"<b>{d.get('snapshots','?')}</b> snapshots. "
                f"Incremental-provenance reconciliation: "
                f"<b>{d.get('reconciliation','?')}</b>. "
                f"Max similarity: <b>{d.get('max_similarity',('?',None))}</b>.</p>")

    if d.get("bursts"):
        parts.append("<h2>Paste/burst events</h2><table border=1 "
                    "cellpadding=5 style='border-collapse:collapse'>"
                    "<tr><th>time</th><th>+lines</th><th>files</th>"
                    "<th>inspect</th></tr>")
        for b in d["bursts"]:
            files = ", ".join(html.escape(x) for x in b.get("files", []))
            parts.append(f"<tr><td>{html.escape(str(b.get('ts')))}</td>"
                        f"<td>{b.get('added')}</td><td>{files}</td>"
                        f"<td><code>git show {b.get('commit','')[:10]}</code>"
                        f"</td></tr>")
        parts.append("</table>")

    if d.get("gaps"):
        parts.append("<h2>Activity gaps</h2><ul>")
        for a, b, secs in d["gaps"]:
            parts.append(f"<li>{html.escape(a)} &rarr; {html.escape(b)} "
                        f"({secs//60} min)</li>")
        parts.append("</ul>")

    if d.get("telemetry"):
        parts.append("<h2>AI-agent hook events</h2><table border=1 "
                    "cellpadding=5 style='border-collapse:collapse'>"
                    "<tr><th>date</th><th>tool</th><th>event</th>"
                    "<th>machine</th><th>os user</th></tr>")
        for e in d["telemetry"]:
            parts.append("<tr>" + "".join(
                f"<td>{html.escape(str(e.get(k,'')))}</td>"
                for k in ("date", "tool", "event", "machine", "machine_user")
            ) + "</tr>")
        parts.append("</table>")

    parts.append("<h2>Inspect the snapshot stream</h2>"
                "<pre>git -C &lt;clone&gt; log --oneline autosave\n"
                "git -C &lt;clone&gt; show &lt;commit&gt;:problem_1.py</pre>")

    if rep.issues:
        parts.append("<h2>Data issues</h2><ul>"
                    + "".join(f"<li>{html.escape(i)}</li>" for i in rep.issues)
                    + "</ul>")

    reports_dir = Path(out_dir) / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / f"{rep.handle}.html").write_text("".join(parts),
                                                     encoding="utf-8")


def render_csv(reports, out_dir):
    rows = sorted(reports, key=lambda r: r.score(), reverse=True)
    with open(Path(out_dir) / "risk_report.csv", "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["handle", "score", "tier", "coverage_pct",
                    "strong_signals", "top_reasons"])
        for r in rows:
            w.writerow([r.handle, r.score(), r.tier(),
                        int(r.coverage() * 100), r.strong_count(),
                        " | ".join(r.top_reasons())])


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #

def discover_submissions(parent):
    subs = []
    for child in sorted(Path(parent).iterdir()):
        if child.is_dir() and (child / ".git").exists():
            subs.append(child)
    return subs


def load_baseline(path):
    if not path or not Path(path).exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def load_secrets(path):
    """Optional map: repository-url -> signing secret (for HMAC verification)."""
    if not path or not Path(path).exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Score student submissions for "
                                "likelihood of generative-AI use.")
    ap.add_argument("submissions", help="parent dir of per-student clones")
    ap.add_argument("--telemetry", help="telemetry.csv export from the hook API")
    ap.add_argument("--baseline", help="baseline_manifest.json of instrumentation hashes")
    ap.add_argument("--secrets", help="optional repo->signing-secret map for HMAC")
    ap.add_argument("--private-tests", help="path to tests_private/ to run")
    ap.add_argument("--out", default="report_out", help="output directory")
    args = ap.parse_args(argv)

    subs = discover_submissions(args.submissions)
    if not subs:
        print(f"No git submissions found under {args.submissions}", file=sys.stderr)
        return 2

    by_repo, by_email = load_telemetry(args.telemetry)
    baseline = load_baseline(args.baseline)
    secrets = load_secrets(args.secrets)
    private_tests = args.private_tests if (
        args.private_tests and Path(args.private_tests).exists()) else None

    reports = []
    snaps_by_handle = {}
    active_times = []

    # First pass: snapshots + per-student features that don't need the cohort.
    for repo in subs:
        handle = repo.name
        rep = Report(handle, repo)
        try:
            snaps = read_snapshots(repo)
        except Exception as exc:
            snaps = []
            rep.note(f"could not read snapshots: {exc}")
        snaps_by_handle[handle] = snaps
        reports.append(rep)

    # cohort median active time (from those with a usable stream)
    for rep in reports:
        snaps = snaps_by_handle[rep.handle]
        times = [parse_ts(s.get("ts")) for s in snaps]
        times = [t for t in times if t]
        if len(times) >= 2:
            active_times.append((max(times) - min(times)).total_seconds() / 60.0)
    cohort_median = (sorted(active_times)[len(active_times) // 2]
                     if active_times else None)

    # Second pass: full per-student scoring.
    for rep in reports:
        snaps = snaps_by_handle[rep.handle]
        url = origin_url(rep.repo)
        author = git_author(rep.repo)
        secret = None
        if secrets and url in secrets:
            secret = str(secrets[url]).encode("utf-8")

        for fn in (
            lambda: feat_cadence_and_burst(rep, snaps, cohort_median),
            lambda: feat_reconciliation(rep, snaps),
            lambda: feat_seq_integrity(rep, snaps, secret),
            lambda: feat_baseline(rep, baseline),
            lambda: feat_telemetry(
                rep, telemetry_for(url, author, by_repo, by_email), baseline),
            lambda: feat_hidden_tests(rep, private_tests),
        ):
            try:
                fn()
            except Exception as exc:
                rep.note(f"feature error: {exc}")

    # Cohort passes.
    try:
        cohort_similarity(reports)
    except Exception as exc:
        for rep in reports:
            rep.note(f"similarity error: {exc}")
    try:
        cohort_collusion(reports, by_repo or {})
    except Exception as exc:
        for rep in reports:
            rep.note(f"collusion error: {exc}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for rep in reports:
        render_student(rep, out)
    render_dashboard(reports, out)
    render_csv(reports, out)

    # Console summary.
    rows = sorted(reports, key=lambda r: r.score(), reverse=True)
    print(f"\nScored {len(reports)} submissions -> {out}/index.html\n")
    for r in rows:
        print(f"  {TIER_EMOJI[r.tier()]} {r.tier():5s} {r.score():3d}  "
              f"{r.handle}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
