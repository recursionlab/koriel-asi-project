import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
src_path = root / "src"

# Ensure /src is importable as top-level package path (koriel, etc.).
if src_path.exists():
    p = str(src_path)
    if p not in sys.path:
        sys.path.insert(0, p)

# Also allow imports that may still reference the repository root (legacy 'src.' patterns)
rp = str(root)
if rp not in sys.path:
    sys.path.append(rp)
