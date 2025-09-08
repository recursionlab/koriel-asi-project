# tests/test_ab.py
import json
from pathlib import Path

from src.ab import main


def test_ab(temp_workdir):
    main()
    p = Path("logs/ab_summary.json")
    assert p.exists(), "ab_summary.json missing"
    j = json.loads(p.read_text())
    for k in ["RC_slope_diff_mean", "Loss_slope_diff_mean", "Ups_rate_diff_mean"]:
        v = j.get(k, None)
        assert isinstance(v, (int, float)), "CI fields not numeric"
