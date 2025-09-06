#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from typing import List


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True)


def gh_json(args: list[str]):
    p = run(["gh", *args])
    if p.returncode != 0:
        return []
    try:
        return json.loads(p.stdout)
    except Exception:
        return []


def gh_ok(args: list[str]) -> bool:
    return run(["gh", *args]).returncode == 0


PREFIXES = ("copilot/", "codex/", "probe/", "ops/", "adopt/")


def label_and_comment(pr: dict, trigger_sitrep: bool = False) -> None:
    num = pr.get("number")
    head = pr.get("headRefName") or ""
    title = pr.get("title") or ""
    author = pr.get("author", {}).get("login") or ""

    is_agent = head.startswith(PREFIXES) or "bot" in author.lower()
    if is_agent:
        gh_ok(["pr", "edit", str(num), "--add-label", "agent"])  # label as agent
        # perm-probe detection: head starts with probe/ or title contains perm-probe
        if head.startswith("probe/") or "perm-probe" in title.lower():
            gh_ok(["pr", "edit", str(num), "--add-label", "perm-probe"])
            gh_ok(["pr", "edit", str(num), "--add-label", "automerge"])  # merge on green
    # Post guidance comment
    gh_ok([
        "pr",
        "comment",
        str(num),
        "--body",
        "Commands: /sitrep, /label <name>, /automerge, /adopt",
    ])
    # Optionally trigger sitrep
    if trigger_sitrep:
        gh_ok(["pr", "comment", str(num), "--body", "/sitrep"])  # kicks workflow


def main(argv: list[str]) -> int:
    prs = gh_json(["pr", "list", "--state", "open", "--limit", "50", "--json", "number,headRefName,state,mergeStateStatus,title,author"])
    if not isinstance(prs, list):
        print("No PR data or gh not authenticated")
        return 1
    # Label, comment, and trigger sitrep for first 2 agent PRs
    count = 0
    for pr in prs:
        label_and_comment(pr, trigger_sitrep=(count < 2))
        if (pr.get("headRefName") or "").startswith(PREFIXES):
            count += 1
    print(f"Processed {len(prs)} PRs; triggered sitrep on {min(count,2)} agent PRs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
