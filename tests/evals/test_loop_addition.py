import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from koriel_asi.agent.loop import run_once  # noqa: E402


def test_add_two_numbers():
    res = run_once("add 2 and 3")
    assert res.ok, f"Verifier failed: {res.notes}"
    out = "".join(step.get("stdout", "") for step in res.steps)
    assert "5" in out, f"Unexpected output: {out!r}"
