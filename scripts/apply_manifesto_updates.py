#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPDATES = ROOT / "manifesto" / "updates"


def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd or ROOT, text=True, capture_output=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def copy_tree(src: Path, dst: Path, dry: bool):
    copied = []
    for p in src.rglob("*"):
        if p.is_dir():
            continue
        rel = p.relative_to(src)
        target = dst / rel
        if not dry:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
        copied.append(str(rel))
    return copied


def apply_patches(patches_dir: Path, dry: bool):
    applied, failed = [], []
    for patch in sorted(patches_dir.rglob("*.patch")) + sorted(
        patches_dir.rglob("*.diff")
    ):
        if dry:
            applied.append(patch.name)
            continue
        code, out, err = run(
            ["git", "apply", "--whitespace=fix", "--reject", str(patch)]
        )
        (applied if code == 0 else failed).append(
            {"file": str(patch), "code": code, "stderr": err}
        )
    return applied, failed


def main():
    ap = argparse.ArgumentParser(description="Apply manifesto/updates to repo.")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not UPDATES.exists():
        print(f"[updates] directory missing: {UPDATES}", file=sys.stderr)
        return 2

    summary = {"copied": {}, "patches": {"applied": [], "failed": []}}

    # 1) Apply *.patch/*.diff if present
    applied, failed = apply_patches(UPDATES, args.dry_run)
    summary["patches"]["applied"] = applied
    summary["patches"]["failed"] = failed

    # 2) Conventional folders
    conventions = {
        "files": ROOT,  # arbitrary files mirrored to repo root
        "workflows": ROOT / ".github" / "workflows",  # YAML workflows
        "requirements": ROOT,  # requirement files
        "docs": ROOT / "docs",  # docs
        "scripts": ROOT / "scripts",  # scripts
        "src": ROOT / "src",  # source drops
        "tests": ROOT / "tests",  # tests
    }
    for name, dest in conventions.items():
        src = UPDATES / name
        if src.exists():
            copied = copy_tree(src, dest, args.dry_run)
            summary["copied"][name] = copied

    # 3) Optional manifest.json to drive targeted copies
    manifest = UPDATES / "manifest.json"
    if manifest.exists():
        try:
            spec = json.loads(manifest.read_text(encoding="utf-8"))
            for entry in spec.get("copies", []):
                s = ROOT / entry["src"]
                d = ROOT / entry["dst"]
                if not args.dry_run:
                    d.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(s, d)
            summary["manifest"] = spec
        except Exception as e:
            summary["manifest_error"] = str(e)

    # 4) Basic sanity commands post-apply (skipped on dry-run)
    if not args.dry_run:
        run(["python", "-m", "scripts.validate_operators"])
        # Run tests but don't fail the script if tests fail (as there may be unrelated test issues)
        code, _, _ = run(["pytest", "-q", "--maxfail=1", "--disable-warnings"])
        summary["tests_exit_code"] = code

    print(json.dumps(summary, indent=2))
    return 0 if not summary["patches"]["failed"] else 3


if __name__ == "__main__":
    sys.exit(main())
