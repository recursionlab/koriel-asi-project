import os
import shutil
import sys
from pathlib import Path

import pytest

# Ensure project root is on sys.path so tests can import the `src` package
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


@pytest.fixture
def temp_workdir(tmp_path, monkeypatch):
    """Create an isolated working directory with required config files."""
    config_src = Path(ROOT) / "config"
    shutil.copytree(config_src, tmp_path / "config")
    monkeypatch.chdir(tmp_path)
    return tmp_path
