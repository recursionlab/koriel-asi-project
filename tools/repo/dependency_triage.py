"""Dependency triage helper.

Classify imports found across the repository into:
- internal: module/package present in the repo tree
- installed: importlib can find it in the current environment
- missing: neither internal nor importable (candidate for requirements)

Usage:
    python tools/repo/dependency_triage.py
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import List, Set

REPO_ROOT = Path(__file__).resolve().parents[2]


def collect_imports(search_paths: List[Path]) -> Set[str]:
    imports = set()
    for p in search_paths:
        try:
            text = p.read_text(encoding="utf8")
        except Exception:
            continue
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("import "):
                parts = line.split()
                if len(parts) >= 2:
                    imports.add(parts[1].split(".")[0])
            elif line.startswith("from "):
                parts = line.split()
                if len(parts) >= 4:
                    imports.add(parts[1].split(".")[0])
    return imports


def is_internal(module: str, repo_root: Path) -> bool:
    # check for a top-level package or module file in the repo
    mod_py = repo_root / (module + ".py")
    mod_pkg = repo_root / module
    return mod_py.exists() or mod_pkg.exists()


def is_importable(module: str) -> bool:
    try:
        spec = importlib.util.find_spec(module)
        return spec is not None
    except Exception:
        return False


def main() -> int:
    search_paths = [
        p
        for p in REPO_ROOT.rglob("*.py")
        if "venv" not in str(p) and ".venv" not in str(p)
    ]
    imports = collect_imports(search_paths)

    internal = []
    installed = []
    missing = []

    for mod in sorted(imports):
        if is_internal(mod, REPO_ROOT):
            internal.append(mod)
        elif is_importable(mod):
            installed.append(mod)
        else:
            missing.append(mod)

    print("Dependency triage report:\n")
    print(f"Total unique imports scanned: {len(imports)}\n")
    print("Internal modules (present in repo):")
    for m in internal:
        print("  -", m)
    print("\nImportable (installed in environment):")
    for m in installed:
        print("  -", m)
    print("\nPotential missing external packages (candidates to add to requirements):")
    for m in missing:
        print("  -", m)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
