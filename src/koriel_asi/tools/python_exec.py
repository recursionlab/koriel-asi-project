from __future__ import annotations
import subprocess, tempfile, textwrap, os
from typing import Dict, Any

class PythonExec:
    """Offline Python executor."""
    def __init__(self, timeout_sec: int = 2) -> None:
        self.timeout_sec = timeout_sec

    def run(self, code: str) -> Dict[str, Any]:
        code = textwrap.dedent(code)
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(code)
            path = f.name
        try:
            proc = subprocess.run(
                ["python", path],
                capture_output=True,
                text=True,
                timeout=self.timeout_sec,
            )
            return {
                "ok": proc.returncode == 0,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "returncode": proc.returncode,
            }
        finally:
            try: os.remove(path)
            except OSError: pass
