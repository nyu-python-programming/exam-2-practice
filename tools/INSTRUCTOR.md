# Instructor guide — AI-integrity system for Exam #2 (practice)

This is the **practice exam**, wired with the same AI-integrity system as the real Exam #2 so the whole pipeline (autosave stream, editor-agent telemetry, hidden tests, scorer) can be exercised end-to-end before the graded exam. Everything below applies identically to the real exam.

This exam ships with a layered system to **detect** (not prevent) generative-AI use, code sharing, and tampering, and to give you defensible, convergence-gated evidence for review. Nothing here auto-accuses anyone: the scorer produces a **review-priority triage**, and a RED still warrants a short oral check before any conclusion.

## Components

| Piece                                                                       | Where it runs                  | What it gives you                                                                                     |
| --------------------------------------------------------------------------- | ------------------------------ | ----------------------------------------------------------------------------------------------------- |
| `.automations/autosave.py` + `Start-Exam-Autosave.*`                        | student machine (required)     | continuous, HMAC-signed work snapshots on an `autosave` branch → paste/burst, cadence, reconciliation |
| `.automations/give-student-credit.py` + `.claude`/`.cursor`/`.github/hooks` | student editor                 | direct "an AI agent edited files" telemetry → `telemetry.csv`                                         |
| `.github/workflows/event-logger.yml`                                        | GitHub (server-side)           | un-disableable push/PR log                                                                            |
| `tests_private/`                                                            | your machine                   | hidden edge-case suite that catches solutions tuned only to the visible tests                         |
| `tools/score_all.py`                                                        | your machine                   | the AI-likelihood dashboard + per-student reports                                                     |
| `tools/make_baseline.py`                                                    | your machine, pre-distribution | the instrumentation hash manifest                                                                     |

## Before the exam

1. **Inject a per-repo signing secret.** Each student repo needs a unique value in
   `signing_secret` of `.automations/config.json`. The watcher and the hook both read it;
   if it is left as the placeholder they fall back to a weaker repo-derived secret (still
   consistent, but forgeable), so injecting real secrets is recommended.

   **Automatic injection (recommended).** `.github/workflows/inject-secret.yml` ships in
   the template and self-injects the first time GitHub Classroom creates each student repo
   (the initial push). It derives the per-repo secret as
   `HMAC_SHA256(MASTER_SECRET, <owner/repo>)` and commits it into `config.json`. Because
   the value is _derived_ rather than random, you keep **no `repo → secret` map** — you
   recompute any repo's secret at grading time from the same master + repo name.

   One-time setup: create an **organization** Actions secret named `MASTER_SIGNING_SECRET`
   (Org → Settings → Secrets and variables → Actions → New organization secret), scoped to
   the repositories Classroom creates. Org-level secrets reach every Classroom-generated
   repo, which is what lets the workflow self-inject without per-repo manual work. If the
   org secret is absent, the workflow no-ops and the watcher uses its weaker fallback.

   Note: GitHub Classroom has no native per-repo-secret feature; the first-push workflow is
   how you hook "on acceptance." Any secret stored in the repo is, by design, readable by
   that student — so this never stops a student from signing _their own_ forged heartbeats;
   it stops cross-repo forgery/replay and lets you verify a stream matches its issued
   secret.

2. **Generate the baseline manifest** from the pristine template:
   ```
   python3 tools/make_baseline.py > baseline_manifest.json
   ```
   Keep `baseline_manifest.json` on your side (do **not** ship it to students).
3. **Hold back the hidden tests.** `tests_private/` must **not** be distributed. Keep
   only the visible `tests/` in the student template.
4. **Set the Actions secret** `COMMIT_LOG_API` (and `signing_secret` handling) as needed
   for `event-logger.yml`.

## After the exam — score the cohort

1. Clone every submission into one parent directory, **with all branches** so the
   `autosave` stream comes along:
   ```
   mkdir submissions && cd submissions
   # for each student repo URL:
   git clone <url> <handle>
   git -C <handle> fetch origin '+refs/heads/*:refs/remotes/origin/*'
   ```
2. Export the hook telemetry from the Apps Script to `telemetry.csv` (tab-separated, with
   columns: `date  repository  username  email  tool  event  machine  machine_user
hook_integrity`).
3. **Regenerate the secrets map** from your master secret (no map was kept — the secrets
   are derived). This recomputes each repo's `HMAC_SHA256(MASTER_SECRET, <owner/repo>)`,
   keyed by clone URL the way `score_all.py` expects:
   ```
   MASTER_SECRET='<your MASTER_SIGNING_SECRET value>' \
       python3 tools/derive_secrets.py ./submissions/ > repo_secrets.json
   ```
   (Skip this if you didn't use the auto-injection workflow; the scorer just runs without
   HMAC verification.)
4. Run the scorer:
   ```
   python3 tools/score_all.py ./submissions/ \
       --telemetry telemetry.csv \
       --baseline baseline_manifest.json \
       --secrets repo_secrets.json \
       --private-tests tests_private \
       --out report_out
   ```
   (Every flag is optional — missing inputs degrade gracefully and are noted; they never
   abort the run.)
5. Open `report_out/index.html` — the cohort dashboard, sorted by AI-likelihood. Open a
   per-student report only for 🔴/🟡 rows. Each report shows the cadence timeline, the
   exact paste/burst diffs (with `git show <sha>` to inspect), agent-hook events, tamper
   flags, hidden-test results, and similarity matches.

## How to read a score

- The score is a **triage indicator, not a verdict.** RED = ≥2 independent
  high/medium-reliability signals converged; a lone soft signal can never reach RED.
- **Coverage** shows how much evidence was available. A low-coverage row is **not**
  auto-cleared to GREEN — it routes to manual review (can't-assess ≠ clean).
- For any RED, the recommended next step is a **2–3 minute oral check** ("walk me through
  line 12 of your code"). That is what converts suspicion into proof.

## Tunables

Thresholds live at the top of `tools/score_all.py` (`BIG_INSERT_LINES`,
`HEARTBEAT_GAP_SECONDS`, `RECON_OK_FRACTION`, `SIMILARITY_FLAG`, `LOW_COVERAGE`, …).
Calibrate them on a dry run against a few known-honest submissions before grading for
real, to keep the false-positive rate where you want it.
