#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]

ALLOWED_DIRS = {
    ".git", ".github", ".vscode", ".claude",
    "src", "tests", "docs", "scripts", "examples",
    "experiments", "research", "tools", "ops", "config",
    "prompts", "benchmarks", "demo", "spec", "conversations-pocket",
    "artifacts", "checkpoints", "logs", "rcce-minimal", "rcce-phase2",
    "node_modules",
}

ALLOWED_FILES = {
    "README.md", "LICENSE", "Makefile", "pyproject.toml", "setup.py",
    "requirements.txt", "requirements-min.txt", "package.json", ".gitignore",
    ".pre-commit-config.yaml", "QRFT_README.md",
}

EPHEMERAL_DIRS = {"__pycache__", ".pytest_cache"}
SENSITIVE_MODULES = {"consciousness_interface.py", "koriel_operator.py"}


def git_mv(src: Path, dst: Path) -> bool:
    dst.parent.mkdir(parents=True, exist_ok=True)
    res = subprocess.run(["git", "mv", str(src), str(dst)], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"git mv failed for {src} -> {dst}: {res.stderr.strip()}")
        return False
    return True


def suggest_destination(p: Path) -> Optional[Path]:
    name = p.name
    lower = name.lower()
    # Skip sensitive modules and quantum_* for manual refactor later
    if name in SENSITIVE_MODULES or lower.startswith("quantum_"):
        return None
    # Windows batch files
    if name.endswith('.bat'):
        return ROOT / "scripts" / "windows" / name
    # JSON reports
    if lower.endswith('.json'):
        if any(k in lower for k in ("report", "validation", "tinylm", "validator")):
            return ROOT / "artifacts" / name
        return ROOT / "experiments" / "results" / name
    # Markdown docs
    if lower.endswith('.md'):
        return ROOT / "docs" / name
    # Python tests or stress/validation scripts
    if lower.endswith('.py'):
        if re.search(r"(^test_|_test(s)?\.py$|tests?\b|stress|validation)", lower):
            return ROOT / "tests" / name
        if lower.startswith("run_") or lower.endswith("_demo.py") or "demo" in lower:
            return ROOT / "examples" / name
        # CLI/one-off tools
        if any(k in lower for k in ("inspect", "operator", "chat", "showcase")):
            return ROOT / "scripts" / name
        # default for .py scripts
        return ROOT / "scripts" / name
    # Fallback for misc text
    if lower.endswith(('.txt', '.csv')):
        return ROOT / "docs" / name
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Inventory root and propose tidy moves")
    ap.add_argument("--apply", action="store_true", help="Apply proposed moves using git mv")
    args = ap.parse_args()

    root_entries = sorted([e for e in ROOT.iterdir()])
    proposals: list[tuple[Path, Path]] = []
    for e in root_entries:
        if e.name.startswith('.') and e.name not in {'.github', '.vscode', '.claude'}:
            continue
        if e.is_dir():
            if e.name in ALLOWED_DIRS or e.name in EPHEMERAL_DIRS:
                continue
            # Unrecognized dir: suggest moving under docs/ or experiments/ depending on name
            target_base = ROOT / ("experiments" if any(k in e.name.lower() for k in ("data", "results", "exp")) else "docs")
            proposals.append((e, target_base / e.name))
            continue
        if e.name in ALLOWED_FILES:
            continue
        dest = suggest_destination(e)
        if dest is not None:
            proposals.append((e, dest))

    if not proposals:
        print("Root looks tidy. No proposals.")
        return 0

    print("Proposed moves (dry-run):")
    for src, dst in proposals:
        print(f"  - {src.relative_to(ROOT)} -> {dst.relative_to(ROOT)}")

    if not args.apply:
        print("\nRun with --apply to perform these moves (uses git mv). Review first.")
        return 0

    ok = True
    for src, dst in proposals:
        if not git_mv(src, dst):
            ok = False
    if ok:
        print("Applied all proposed moves. Review 'git status' and commit.")
        return 0
    else:
        print("Some moves failed. Resolve manually.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
