from __future__ import annotations
from typing import Dict, Any, Iterable

class WebReader:
    """Stub. Disabled unless allowlist + fetcher added."""
    def __init__(self, allowlist: Iterable[str]) -> None:
        self.allowlist = set(allowlist)

    def run(self, url: str) -> Dict[str, Any]:
        return {"ok": False, "error": "web_disabled", "details": "no network layer"}
