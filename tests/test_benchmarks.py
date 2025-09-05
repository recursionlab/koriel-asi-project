import json
import subprocess
import sys
from pathlib import Path


def test_mmlu_cli(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    cmd = [sys.executable, "-m", "benchmarks.run", "--suite", "mmlu"]
    subprocess.check_call(cmd, cwd=repo_root)
    log_dir = repo_root / "logs" / "benchmarks"
    json_file = log_dir / "mmlu.json"
    assert json_file.exists(), "metrics file not created"
    data = json.loads(json_file.read_text())
    assert data.get("accuracy") == 0.5
