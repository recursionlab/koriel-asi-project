#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True)


def sh(cmd: list[str]) -> str:
    p = run(cmd)
    if p.returncode != 0:
        return ""
    return p.stdout.strip()


def gh_json(args: list[str]):
    p = run(["gh", *args])
    if p.returncode != 0:
        return None
    try:
        return json.loads(p.stdout)
    except Exception:
        return None


def ensure_dir(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


def report_for_pr(pr_num: int, update_clean: bool, base: str = "origin/main") -> list[str]:
    lines: list[str] = []
    meta = gh_json(["pr", "view", str(pr_num), "--json", "headRefName,title,state,mergeStateStatus"]) or {}
    head = (meta or {}).get("headRefName") or ""
    title = (meta or {}).get("title") or ""
    state = (meta or {}).get("state") or ""
    merge_state = (meta or {}).get("mergeStateStatus") or ""
    lines.append(f"## PR #{pr_num}: {title}")
    lines.append(f"- State: {state} :: Mergeability: {merge_state}")
    if not head:
        lines.append("- Error: no headRefName")
        lines.append("")
        return lines
    lines.append(f"- Branch: {head}")

    # Prepare local temp branch tracking remote
    rem = f"origin/{head}"
    run(["git", "fetch", "origin", head, "--quiet"])  # best-effort
    temp = f"tmp/pr-{pr_num}-reconcile"
    # Create/reset temp branch at remote head
    if run(["git", "show-ref", "--verify", f"refs/heads/{temp}"]).returncode == 0:
        run(["git", "branch", "-D", temp])
    if run(["git", "checkout", "-q", "-b", temp, rem]).returncode != 0:
        lines.append(f"- Error: unable to checkout {rem}")
        lines.append("")
        return lines

    # Attempt non-committing merge of base
    m = run(["git", "merge", "--no-commit", "--no-ff", base])
    if m.returncode != 0:
        # Conflicts likely; list U files
        u = sh(["git", "diff", "--name-only", "--diff-filter=U"]).splitlines()
        if u:
            lines.append("- Conflicts:")
            lines += [f"  - {name}" for name in sorted(set(u))]
        else:
            lines.append("- Merge failed; conflicts likely, but no U files listed (manual rebase may be required).")
        run(["git", "merge", "--abort"])  # cleanup
        run(["git", "checkout", "-q", "-"])
        run(["git", "branch", "-D", temp])
        lines.append("")
        return lines

    # No conflicts: finalize commit and maybe push
    run(["git", "commit", "-m", f"chore: merge {base} into {head}"])
    if update_clean:
        run(["git", "push", "origin", f"{temp}:{head}"])
        lines.append("- Clean merge with main applied and pushed.")
    else:
        lines.append("- Clean merge with main possible (no conflicts).")
    # Cleanup
    run(["git", "checkout", "-q", "-"])
    run(["git", "branch", "-D", temp])
    lines.append("")
    return lines


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("prs", nargs="*", type=int, help="PR numbers to evaluate")
    ap.add_argument("--update-clean", action="store_true", help="Push a merge of main into PR branches that merge cleanly")
    ap.add_argument("--output", default="artifacts/ci_smoke/merge_conflicts.md")
    args = ap.parse_args(argv)

    # If none provided, default to open DIRTY PRs
    prs: list[int] = args.prs
    if not prs:
        data = gh_json(["pr", "list", "--state", "open", "--limit", "200", "--json", "number,mergeStateStatus"]) or []
        prs = [d.get("number") for d in data if isinstance(d, dict) and d.get("mergeStateStatus") == "DIRTY"]

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = ["# Merge conflict report", ""]
    for pr_num in prs:
        try:
            lines += report_for_pr(int(pr_num), update_clean=args.update_clean)
        except Exception as e:
            lines += [f"## PR #{pr_num}", f"- Error: {e}", ""]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
