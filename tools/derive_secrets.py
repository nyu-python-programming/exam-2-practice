#!/usr/bin/env python3
"""
Regenerate the repo -> signing-secret map for score_all.py's --secrets flag.

Each student repo's signing secret is *derived*, not random:

    secret = HMAC_SHA256(MASTER_SECRET, "<owner>/<repo>")

where "<owner>/<repo>" is the slug GitHub Actions exposed as $GITHUB_REPOSITORY
when .github/workflows/inject-secret.yml self-injected the value on the first
push. Because it is derived, there is no map to keep around: this script
recomputes every repo's secret from the one master secret plus each clone's
origin URL.

score_all.py keys the secrets map by `git remote get-url origin` (the full clone
URL), so that is what we emit as the key; the value is the HMAC over the slug.

Usage:
    MASTER_SECRET='<org master secret>' \
        python3 tools/derive_secrets.py ./submissions/ > repo_secrets.json
"""
import hashlib
import hmac
import json
import os
import re
import subprocess
import sys


def slug_from_url(url):
    """Extract '<owner>/<repo>' (no .git) from an https or ssh clone URL."""
    m = re.search(r"[:/]([^/:]+/[^/:]+?)(?:\.git)?/?$", url)
    return m.group(1) if m else None


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: MASTER_SECRET=... derive_secrets.py <submissions-dir>")
    master = os.environ.get("MASTER_SECRET")
    if not master:
        sys.exit("set MASTER_SECRET (the org-level MASTER_SIGNING_SECRET value)")
    master = master.encode("utf-8")

    root = sys.argv[1]
    out = {}
    for handle in sorted(os.listdir(root)):
        repo = os.path.join(root, handle)
        if not os.path.isdir(os.path.join(repo, ".git")):
            continue
        try:
            url = subprocess.check_output(
                ["git", "-C", repo, "remote", "get-url", "origin"],
                text=True,
            ).strip()
        except subprocess.CalledProcessError:
            print(f"warn: no origin for {handle}, skipping", file=sys.stderr)
            continue
        slug = slug_from_url(url)
        if not slug:
            print(f"warn: cannot parse slug from {url}, skipping", file=sys.stderr)
            continue
        out[url] = hmac.new(master, slug.encode("utf-8"), hashlib.sha256).hexdigest()

    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
