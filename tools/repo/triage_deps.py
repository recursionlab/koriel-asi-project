"""Triage declared dependencies vs. imports.

Find imports across the repo, classify whether each import is provided by the
repo (internal) or likely external, and list candidates not declared in
requirements/pyproject.

Usage: python tools/repo/triage_deps.py
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, Set

REPO_ROOT = Path(__file__).resolve().parents[2]


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
            pkg = (
                ln.split(";")[0].split("==")[0].split("<=")[0].split(">=")[0].split()[0]
            )
            pkg = pkg.split("[")[0]
            if pkg:
                reqs.add(pkg.lower())
    # naive pyproject parse
    pyproject = repo_root / "pyproject.toml"
    if pyproject.exists():
        try:
            text = pyproject.read_text(encoding="utf8")
            for line in text.splitlines():
                line = line.strip()
                if "=" in line and not line.startswith("["):
                    key = line.split("=", 1)[0].strip().strip('"')
                    if key and not key.startswith("_"):
                        reqs.add(key.lower())
        except Exception:
            pass
    return reqs


def collect_imports(repo_root: Path) -> Set[str]:
    imports: Set[str] = set()
    for p in repo_root.rglob("*.py"):
        if ".venv" in str(p) or "site-packages" in str(p):
            continue
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
    return imports


def classify_imports(repo_root: Path, imports: Set[str]) -> Dict[str, str]:
    classes: Dict[str, str] = {}
    # build set of internal modules (top-level dirs and py files)
    internal = set()
    for p in repo_root.iterdir():
        if p.is_dir():
            internal.add(p.name)
        elif p.is_file() and p.suffix == ".py":
            internal.add(p.stem)
    # also consider src/ and packages inside
    src_dir = repo_root / "src"
    if src_dir.exists():
        for p in src_dir.iterdir():
            if p.is_dir() or p.suffix == ".py":
                internal.add(p.name if p.is_dir() else p.stem)

    for imp in sorted(imports):
        if imp in internal:
            classes[imp] = "internal"
        else:
            classes[imp] = "external_candidate"
    return classes


def main() -> int:
    repo_root = REPO_ROOT
    declared = parse_requirements(repo_root)
    imports = collect_imports(repo_root)
    classes = classify_imports(repo_root, imports)

    external_candidates = sorted(
        [k for k, v in classes.items() if v == "external_candidate"]
    )
    missing = [k for k in external_candidates if k.lower() not in declared]

    print("Declared dependencies (summary):")
    for d in sorted(declared):
        print("  -", d)

    print("\nExternal import candidates (not internal):")
    for e in external_candidates[:200]:
        print("  -", e)

    print("\nLikely missing (not in declared dependencies):")
    for m in missing[:200]:
        print("  -", m)

    print(
        "\nNote: some names may be stdlib or misclassified; review before adding to requirements."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
