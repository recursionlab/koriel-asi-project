Here are the CI workflow and a second eval. Paste as-is.

```
File: .github/workflows/ci.yml
```

```yaml
name: ci
on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install deps
        run: |
          python -m pip install -U pip
          # project deps if present
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          # dev tools
          pip install pytest coverage ruff black mypy

      - name: Lint (non-blocking)
        run: |
          ruff check . || true
          black --check . || true
          mypy src || true

      - name: Tests with coverage
        run: |
          coverage run -m pytest -q
          coverage xml

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-xml
          path: coverage.xml
          if-no-files-found: ignore
```

```
File: tests/evals/test_retrieval_citation.py
```

```python
from pathlib import Path
import sys

# Ensure src on path for "src/" layout without installing
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from koriel_asi.tools.retrieval import Retrieval  # noqa: E402


def test_retrieval_returns_snippet_and_citation(tmp_path):
    # Seed a local doc
    doc = tmp_path / "demo.md"
    text = (
        "Koriel ASI system architecture.\n"
        "Planner → Actor → Verifier loop with retrieval and python_exec.\n"
        "Safety gates and evals are required before scaling.\n"
    )
    doc.write_text(text, encoding="utf-8")

    # Point retriever at this file and query
    r = Retrieval(roots=[str(doc)]).run(query="Koriel ASI", top_k=3)
    assert r.get("ok") is True
    hits = r.get("hits", [])
    assert hits, "No hits returned"

    h0 = hits[0]
    # Citation via file path
    assert "path" in h0 and h0["path"].endswith("demo.md")
    # Snippet contains query context (case-insensitive ok)
    assert "snippet" in h0 and "koriel asi" in h0["snippet"].lower()
```

Run:

```
PYTHONPATH=src pytest -q
```
