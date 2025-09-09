# Branch management and cleanup policy

Purpose
-------
This document records the lightweight branch naming and cleanup policy the team will follow to keep the repository tidy and avoid accidental cruft.

Goals
-----
- Make it easy to find active work and remove stale branches.
- Ensure safe recoverability (tags / backups) before any destructive cleanup.
- Keep PRs and branches aligned: branch per task/PR, short-lived, descriptive names.

Branch naming (recommended prefixes)
-----------------------------------
- main — default stable branch
- chore/ — chore work: dependency bumps, infra, CI maintenance
- feat/ or feature/ — new features or experiments
- fix/ — bugfixes
- docs/ — documentation-only changes
- refactor/ — code reorganizations
- codex/ — automated codex/copilot-generated work (review & squash)
- copilot/ — interactive copilot branches (should be short‑lived)
- probe/perm-* — permission/probe branches (ephemeral)

Lifecycle & cleanup rules
-------------------------
1. Tag before bulk cleanup
   - Create an annotated tag at HEAD and push it before deleting remote branches.
     This provides an easy rollback point: `git tag -a pre-cleanup-YYYYMMDD-HHMM -m "pre-cleanup"` and `git push origin --tags`.

2. Delete only merged branches
   - Prefer deleting remote branches that are already merged into `main`.
   - Use `git fetch --prune` then audit with `git branch -r --merged origin/main` to locate merged branches.

3. Keep active PR branches
   - Do NOT delete branches that have open PRs under review unless you also intend to close the PR.

4. Stale/old branches
   - If a branch is unmerged but hasn't had activity for >30 days, open a PR or ping the author; if the author is unavailable, consider archiving or deleting following a short notice window.

5. Local housekeeping
   - Developers should delete local feature branches after merge: `git branch -d my/branch`.
   - Use `git fetch --prune` to remove stale remote-tracking branches.

6. Emergency restore
   - To restore a deleted branch from a tag or commit: `git checkout -b <branch> <tag-or-commit>` then `git push -u origin <branch>`.

Commands cheat-sheet
--------------------
- Tag current HEAD and push tags (safe rollback):

```bash
git tag -a pre-cleanup-$(date +%Y%m%d-%H%M%S) -m "pre-cleanup snapshot"
git push origin --tags
```

- Prune stale remote-tracking refs:

```bash
git fetch --prune
```

- List remote branches merged into origin/main:

```bash
git fetch origin
git branch -r --merged origin/main | sed 's|origin/||'
```

- Delete a remote branch (careful):

```bash
git push origin --delete <branch-name>
```

- Delete a local branch:

```bash
git branch -d <branch-name>    # safe: refuses unmerged
git branch -D <branch-name>    # force delete
```

Policy for automated branches (copilot / codex / probe)
------------------------------------------------------
- Automated generator branches (prefixes `copilot/`, `codex/`, `probe/`) should be ephemeral. If accepted, their PR should be merged then the branch deleted. If rejected, they should be deleted after review. Keep a short retention window (48–72 hours) for review.

Governance and responsibilities
-------------------------------
- Branch owners are responsible for closing or deleting their branches after merge.
- The repo maintainers may periodically run a cleanup sweep for long‑stale branches following the policy above.

Questions or exceptions
-----------------------
If you are unsure whether to delete a branch, open an issue or mention the branch in the team channel and wait 24–48 hours for objections before deleting.

## Cleanup log

- 2025-09-09: Performed remote-branch cleanup. Created rollback tag `pre-cleanup-20250909-043640` before deletions. Removed merged `codex/*`, `copilot/*`, `experiments/burn-test`, and `probe/perm-17506442896` branches from `origin` after owner confirmation. Remaining unmerged branches were left intact and owners were notfied.

