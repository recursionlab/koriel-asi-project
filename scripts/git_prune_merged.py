#!/usr/bin/env python3
"""
Prune remote branches on origin for PRs that are already merged.

Usage:
  python3 scripts/git_prune_merged.py           # dry-run (prints what it would delete)
  python3 scripts/git_prune_merged.py --execute # actually deletes branches on origin

Safety:
- Skips default branch (main) and protected prefix patterns.
- Skips branches that correspond to OPEN or DRAFT PRs.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Set


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True)


def gh_json(args: list[str]):
    proc = run(["gh", *args])
    if proc.returncode != 0:
        return []
    try:
        return json.loads(proc.stdout)
    except Exception:
        return []


def get_remote_branches() -> Set[str]:
    proc = run(["git", "branch", "-r"])
    if proc.returncode != 0:
        return set()
    names: Set[str] = set()
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        # lines like: origin/feature/x
        if line.startswith("origin/"):
            names.add(line[len("origin/") :])
    return names


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--execute", action="store_true", help="Actually delete branches on origin"
    )
    ap.add_argument(
        "--protect-prefix",
        action="append",
        default=["main", "release/", "ops/sync-"],
        help="Protected branch prefixes (won't delete)",
    )
    args = ap.parse_args(argv)

    remote_branches = get_remote_branches()

    # Collect merged PR head branches
    merged = gh_json(
        [
            "pr",
            "list",
            "--state",
            "merged",
            "--limit",
            "200",
            "--json",
            "number,headRefName,baseRefName,updatedAt",
        ]
    )
    open_prs = gh_json(
        [
            "pr",
            "list",
            "--state",
            "open",
            "--limit",
            "200",
            "--json",
            "number,headRefName",
        ]
    )

    open_heads = {pr.get("headRefName") for pr in open_prs if isinstance(pr, dict)}
    merged_heads = {pr.get("headRefName") for pr in merged if isinstance(pr, dict)}

    candidates = []
    for head in sorted(merged_heads):
        if not head:
            continue
        if head in open_heads:
            continue
        # Only delete if remote branch exists
        if head not in remote_branches:
            continue
        protected = any(head == p or head.startswith(p) for p in args.protect_prefix)
        if protected:
            continue
        candidates.append(head)

    if not candidates:
        print("No merged PR remote branches to prune.")
        return 0

    print("Candidates to delete on origin (merged PRs, not open):")
    for name in candidates:
        print(f"  - {name}")

    if not args.execute:
        print("\nDry-run only. Re-run with --execute to delete.")
        return 0

    # Execute deletions
    failed: list[str] = []
    for name in candidates:
        proc = run(["git", "push", "origin", "--delete", name])
        if proc.returncode != 0:
            failed.append(name)
            sys.stderr.write(proc.stderr)
    if failed:
        print("Some deletions failed:", ", ".join(failed))
        return 1
    print("Deleted:")
    for name in candidates:
        print(f"  - {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
