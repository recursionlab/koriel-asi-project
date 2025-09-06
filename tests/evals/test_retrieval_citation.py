from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from koriel_asi.tools.retrieval import Retrieval  # noqa: E402

def test_retrieval_returns_snippet_and_citation(tmp_path):
    doc = tmp_path / "demo.md"
    doc.write_text(
        "Koriel ASI system architecture.\n"
        "Planner -> Actor -> Verifier loop with retrieval and python_exec.\n"
        "Safety gates and evals are required before scaling.\n",
        encoding="utf-8",
    )
    r = Retrieval(roots=[str(doc)]).run(query="Koriel ASI", top_k=3)
    assert r.get("ok") is True
    hits = r.get("hits", [])
    assert hits, "No hits returned"
    h0 = hits[0]
    assert "path" in h0 and h0["path"].endswith("demo.md")
    assert "snippet" in h0 and "koriel asi" in h0["snippet"].lower()
