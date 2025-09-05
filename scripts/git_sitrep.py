#!/usr/bin/env python3
"""
Generate a concise Git/PR status report to help manage branches and pull requests.
Writes artifacts/ci_smoke/git_sitrep.md with:
- Current repo/branch summary
- Local branches and their upstream/ahead-behind
- Remote branches
- PRs (open + merged) with state, head->base, draft, merge state
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run(cmd: list[str], check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def git(*args: str) -> str:
    out = run(["git", *args]).stdout
    return out.strip()


def gh_json(args: list[str]) -> list[dict] | dict:
    proc = run(["gh", *args])
    if proc.returncode != 0:
        return []
    try:
        return json.loads(proc.stdout)
    except Exception:
        return []


def ahead_behind(branch: str, upstream: str) -> tuple[int, int] | None:
    if not upstream:
        return None
    proc = run(["git", "rev-list", "--left-right", "--count", f"{branch}...{upstream}"])
    if proc.returncode != 0:
        return None
    s = proc.stdout.strip()
    if not s:
        return None
    try:
        behind_str, ahead_str = s.split()
        # left is commits only in branch (ahead), right in upstream (behind) depending on order
        # For branch...upstream, output is: left=only in branch, right=only in upstream
        left, right = map(int, (behind_str, ahead_str))
        return (left, right)
    except Exception:
        return None


def main() -> int:
    repo = git("rev-parse", "--show-toplevel")
    if not repo:
        print("Not a git repository", file=sys.stderr)
        return 1
    cwd = Path(repo)
    artifacts = cwd / "artifacts" / "ci_smoke"
    artifacts.mkdir(parents=True, exist_ok=True)
    out_file = artifacts / "git_sitrep.md"

    current_branch = git("rev-parse", "--abbrev-ref", "HEAD")
    head = git("rev-parse", "--short", "HEAD")
    remote_url = git("config", "--get", "remote.origin.url")
    try:
        run(["git", "fetch", "--all", "--prune", "--quiet"])  # best-effort
    except Exception:
        pass

    # Local branches with upstream and ahead/behind
    local_branches = []
    for line in git("for-each-ref", "--format=%(refname:short)\t%(upstream:short)", "refs/heads").splitlines():
        if not line.strip():
            continue
        name, *rest = line.split("\t")
        upstream = rest[0] if rest else ""
        ab = ahead_behind(name, upstream) if upstream else None
        local_branches.append({"name": name, "upstream": upstream, "ahead_behind": ab})

    # Remote branches
    remote_branches = [rb.strip() for rb in git("branch", "-r").splitlines() if rb.strip()]

    # PRs via gh (open + closed)
    pr_fields = [
        "number",
        "state",
        "isDraft",
        "headRefName",
        "baseRefName",
        "mergeStateStatus",
        "title",
        "updatedAt",
        "url",
    ]
    pr_data = gh_json(["pr", "list", "--state", "all", "--limit", "200", "--json", ",".join(pr_fields)])
    if not isinstance(pr_data, list):
        pr_data = []

    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    lines = []
    lines.append(f"# Git/PR Sitrep\n")
    lines.append(f"Generated: {ts} (UTC)\n")
    lines.append(f"Repo: {cwd.name}\n")
    lines.append(f"Remote: {remote_url}\n")
    lines.append(f"Current branch: {current_branch} ({head})\n")

    lines.append("\n## Local branches\n")
    for b in sorted(local_branches, key=lambda x: (x["name"] != current_branch, x["name"])):
        ab = b["ahead_behind"]
        ab_str = ""
        if ab is not None:
            ab_str = f" [ahead {ab[0]}, behind {ab[1]}]"
        star = "* " if b["name"] == current_branch else "  "
        lines.append(f"{star}{b['name']} -> {b['upstream'] or '(no upstream)'}{ab_str}")

    lines.append("\n## Remote branches (origin)\n")
    for rb in remote_branches:
        if not rb.startswith("origin/"):
            continue
        lines.append(f"- {rb}")

    lines.append("\n## Pull Requests\n")
    if not pr_data:
        lines.append("No PR data (gh may not be authenticated).")
    else:
        # Sort: open first, then by updated desc
        def pr_sort_key(pr: dict) -> tuple:
            state_rank = 0 if pr.get("state") == "OPEN" else (1 if pr.get("state") == "MERGED" else 2)
            return (state_rank, pr.get("updatedAt", ""))

        for pr in sorted(pr_data, key=pr_sort_key):
            number = pr.get("number")
            state = pr.get("state")
            draft = pr.get("isDraft")
            head_ref = pr.get("headRefName")
            base_ref = pr.get("baseRefName")
            merge_state = pr.get("mergeStateStatus")
            title = pr.get("title")
            url = pr.get("url")
            lines.append(f"- #{number} [{state}{' DRAFT' if draft else ''}] {head_ref} -> {base_ref} :: {merge_state} :: {title} :: {url}")

    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
