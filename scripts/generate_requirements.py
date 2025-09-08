"""Generate requirements.txt from pyproject.toml dependencies."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    pyproject_path = ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text())
    dependencies = data.get("project", {}).get("dependencies", [])

    req_lines = ["# Auto-generated from pyproject.toml; do not edit by hand."]
    req_lines.extend(dependencies)

    (ROOT / "requirements.txt").write_text("\n".join(req_lines) + "\n")
    print("requirements.txt generated from pyproject.toml")


if __name__ == "__main__":
    main()
