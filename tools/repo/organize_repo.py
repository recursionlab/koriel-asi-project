"""Repo organization helper.

Conservative tool to inspect the repository and suggest (or perform) small structural
cleanup actions:

- Find small/top-level/trivial Python scripts that could be moved to tools/legacy/
- Compare top-level imports against declared dependencies in requirements.txt and pyproject.toml
- Run a syntax/compile check and report files with syntax errors

This script is intentionally non-destructive by default. Pass --apply to move suggested
files into `tools/legacy/`.

Usage:
    python tools/repo/organize_repo.py --summary
    python tools/repo/organize_repo.py --apply  # will move candidate files
"""

from __future__ import annotations

import argparse
import ast
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
EXCLUDE_DIRS = {
    "venv",
    ".venv",
    ".git",
    "__pycache__",
    "artifacts",
    "checkpoints",
    "docs",
    "tests",
    "benchmarks",
    "data",
}
LEGACY_DIR = REPO_ROOT / "tools" / "legacy"


def list_top_level_py(repo_root: Path) -> List[Path]:
    files: List[Path] = []
    for p in repo_root.iterdir():
        if p.is_file() and p.suffix == ".py":
            # skip some known meta files
            if p.name in {"setup.py", "run.py", "manage.py"}:
                continue
            files.append(p)
        # consider scripts/ and examples/ too
    return sorted(files)


def is_trivial_script(
    path: Path, max_kb: int = 40, max_defs: int = 3
) -> Tuple[bool, str]:
    """Heuristic: small file (<= max_kb KB) with few function/class defs and a main guard.
    Returns (is_trivial, reason).
    """
    try:
        size_kb = path.stat().st_size / 1024
    except OSError:
        return False, "stat-failed"

    try:
        src = path.read_text(encoding="utf8")
    except Exception:
        return False, "read-failed"

    has_main = "if __name__" in src

    try:
        tree = ast.parse(src)
    except Exception:
        return False, "syntax-error"

    defs = sum(
        isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        for n in ast.walk(tree)
    )

    if size_kb <= max_kb and defs <= max_defs and has_main:
        return True, f"size={size_kb:.1f}KB defs={defs} main=True"

    return False, f"size={size_kb:.1f}KB defs={defs} main={has_main}"


def parse_requirements(repo_root: Path) -> Set[str]:
    reqs = set()
    for fname in ("requirements.txt", "requirements-min.txt"):
        f = repo_root / fname
        if not f.exists():
            continue
        for ln in f.read_text(encoding="utf8").splitlines():
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            # take package name before any extras/version spec
            pkg = (
                ln.split(";")[0].split("==")[0].split("<=")[0].split(">=")[0].split()[0]
            )
            pkg = pkg.split("[")[0]
            if pkg:
                reqs.add(pkg.lower())
    # Also look at pyproject.toml for a [tool.poetry.dependencies] or [project.dependencies]
    pyproject = repo_root / "pyproject.toml"
    if pyproject.exists():
        try:
            text = pyproject.read_text(encoding="utf8")
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("[tool.poetry.dependencies]") or line.startswith(
                    "[project.dependencies]"
                ):
                    # crude: collect following non-bracket, non-empty lines until next [
                    continue
                # naive match for lines like "requests = "^2.0"" or "requests = "2.0"
                if "=" in line and not line.startswith("["):
                    key = line.split("=", 1)[0].strip().strip('"')
                    if key and not key.startswith("_"):
                        reqs.add(key.lower())
        except Exception:
            pass

    return reqs


def get_top_level_imports(repo_root: Path, search_paths: List[Path]) -> Set[str]:
    imports: Set[str] = set()
    for p in search_paths:
        try:
            src = p.read_text(encoding="utf8")
        except Exception:
            continue
        try:
            tree = ast.parse(src)
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.add(n.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
    # filter out stdlib/common local names heuristically
    stdlib_like = {
        "os",
        "sys",
        "pathlib",
        "json",
        "typing",
        "ast",
        "subprocess",
        "shutil",
        "re",
        "math",
        "itertools",
        "collections",
        "datetime",
        "time",
        "logging",
        "glob",
        "inspect",
        "dataclasses",
    }
    return {name for name in imports if name and name not in stdlib_like}


def run_compile_check(repo_root: Path) -> List[str]:
    """Run python -m compileall and return files with syntax errors (if any)."""
    out = []
    try:
        proc = subprocess.run(
            ["python3", "-m", "compileall", "-q", str(repo_root)],
            capture_output=True,
            text=True,
        )
        # compileall writes errors to stderr; capture and parse lines with '...' pattern
        stderr = proc.stderr or proc.stdout
        for ln in (stderr or "").splitlines():
            if ln.strip():
                out.append(ln)
    except Exception as e:
        out.append(f"compile-check-failed: {e}")
    return out


def suggest_actions(repo_root: Path) -> Dict[str, List[str]]:
    suggestions: Dict[str, List[str]] = {}
    top_level = list_top_level_py(repo_root)
    trivial_files = []
    for p in top_level:
        trivial, reason = is_trivial_script(p)
        if trivial:
            trivial_files.append((p, reason))

    suggestions["move_to_legacy"] = [
        f"{p.relative_to(repo_root)} ({reason})" for p, reason in trivial_files
    ]

    # dependency check
    declared = parse_requirements(repo_root)
    search_paths = [
        p
        for p in repo_root.rglob("*.py")
        if "venv" not in str(p) and ".venv" not in str(p)
    ]
    imports = get_top_level_imports(repo_root, search_paths)
    missing = sorted([imp for imp in imports if imp.lower() not in declared])
    suggestions["declared_deps"] = sorted(declared)
    suggestions["top_level_imports"] = sorted(imports)
    suggestions["potential_missing_deps"] = missing

    # compile check
    syntax = run_compile_check(repo_root)
    suggestions["compile_issues"] = syntax

    return suggestions


def apply_moves(repo_root: Path, candidates: List[Path]) -> List[Tuple[Path, Path]]:
    moved: List[Tuple[Path, Path]] = []
    LEGACY_DIR.mkdir(parents=True, exist_ok=True)
    for p in candidates:
        dest = LEGACY_DIR / p.name
        try:
            shutil.move(str(p), str(dest))
            moved.append((p, dest))
        except Exception:
            continue
    return moved


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply moves (non-reversible) to tools/legacy/",
    )
    parser.add_argument(
        "--summary", action="store_true", help="Print a summary report (default)"
    )
    args = parser.parse_args(argv)

    repo_root = REPO_ROOT
    report = suggest_actions(repo_root)

    print("Repo organization report:\n")
    print("Candidate files to move to tools/legacy/ (heuristic):")
    for line in report.get("move_to_legacy", []):
        print("  -", line)

    print("\nDeclared dependencies (from requirements/pyproject):")
    for dep in report.get("declared_deps", [])[:200]:
        print("  -", dep)

    print("\nTop-level imports (non-stdlib heuristics):")
    for imp in report.get("top_level_imports", [])[:200]:
        print("  -", imp)

    print("\nPotential missing dependencies (imports not found in declared deps):")
    for m in report.get("potential_missing_deps", [])[:200]:
        print("  -", m)

    print("\nCompile/syntax check output (empty if no issues):")
    for ln in report.get("compile_issues", [])[:200]:
        print("  ", ln)

    if args.apply:
        # parse candidates again as Path objects
        top_level = list_top_level_py(repo_root)
        candidates = [p for p in top_level if is_trivial_script(p)[0]]
        if not candidates:
            print("\nNo candidates to move.")
            return 0
        print(f"\nApplying moves: moving {len(candidates)} files to {LEGACY_DIR}")
        moved = apply_moves(repo_root, candidates)
        for src, dst in moved:
            print(
                f"  moved {src.relative_to(repo_root)} -> {dst.relative_to(repo_root)}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
