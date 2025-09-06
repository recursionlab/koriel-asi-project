from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List


class Retrieval:
    """Search UTF-8 files under roots for a substring."""

    def __init__(
        self, roots: Iterable[str] | None = None, max_bytes: int = 200_000
    ) -> None:
        self.roots = [Path(r) for r in (roots or ["README.md", "docs"])]
        self.max_bytes = max_bytes

    def run(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        hits: List[Dict[str, Any]] = []
        q = query.lower()
        for root in self.roots:
            if not root.exists():
                continue
            files = (
                [root]
                if root.is_file()
                else list(root.rglob("*.md")) + list(root.rglob("*.txt"))
            )
            for fp in files:
                try:
                    text = fp.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                if len(text) > self.max_bytes:
                    text = text[: self.max_bytes]
                if q in text.lower():
                    snippet = _snippet(text, q, span=120)
                    hits.append({"path": str(fp), "snippet": snippet})
        return {"ok": True, "hits": hits[:top_k]}


def _snippet(text: str, q: str, span: int = 120) -> str:
    i = text.lower().find(q)
    if i < 0:
        return text[:span].replace("\n", " ")
    start = max(0, i - span // 2)
    end = min(len(text), i + len(q) + span // 2)
    return text[start:end].replace("\n", " ")
