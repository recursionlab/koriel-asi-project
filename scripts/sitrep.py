#!/usr/bin/env python3
"""Simple sitrep (situation report) script"""

import json
import os
import sys
from pathlib import Path

def main():
    """Generate a situation report of the repository state"""
    root = Path(__file__).resolve().parents[1]
    
    # Basic file counts
    src_files = len(list((root / "src").rglob("*.py"))) if (root / "src").exists() else 0
    test_files = len(list((root / "tests").rglob("*.py"))) if (root / "tests").exists() else 0
    script_files = len(list((root / "scripts").rglob("*.py"))) if (root / "scripts").exists() else 0
    
    # Check for key config files
    has_makefile = (root / "Makefile").exists()
    has_pyproject = (root / "pyproject.toml").exists()
    has_requirements = (root / "requirements.txt").exists()
    
    # Check manifesto/updates directory
    updates_dir = root / "manifesto" / "updates"
    update_files = len(list(updates_dir.rglob("*"))) if updates_dir.exists() else 0
    
    report = {
        "repository": "koriel-asi-project",
        "files": {
            "src_python": src_files,
            "test_python": test_files,
            "script_python": script_files
        },
        "config": {
            "has_makefile": has_makefile,
            "has_pyproject": has_pyproject,
            "has_requirements": has_requirements
        },
        "manifesto_updates": {
            "exists": updates_dir.exists(),
            "file_count": update_files
        }
    }
    
    print("=== KORIEL ASI PROJECT SITREP ===")
    print(f"Source files: {src_files}")
    print(f"Test files: {test_files}")
    print(f"Script files: {script_files}")
    print(f"Manifesto updates available: {update_files}")
    print(f"Configuration complete: {has_makefile and has_pyproject and has_requirements}")
    print()
    print("JSON report:")
    print(json.dumps(report, indent=2))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())