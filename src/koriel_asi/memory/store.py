from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Fact:
    key: str
    value: Any
    ts: float
    ttl: float  # seconds


class MemoryStore:
    """Simple in-process KV with TTL."""

    def __init__(self) -> None:
        self._facts: Dict[str, Fact] = {}

    def put(self, key: str, value: Any, ttl: float = 3600.0) -> None:
        self._facts[key] = Fact(key=key, value=value, ts=time.time(), ttl=ttl)

    def get(self, key: str) -> Optional[Any]:
        f = self._facts.get(key)
        if not f:
            return None
        if time.time() - f.ts > f.ttl:
            self._facts.pop(key, None)
            return None
        return f.value

    def all_valid(self) -> List[Fact]:
        now = time.time()
        out: List[Fact] = []
        for k, f in list(self._facts.items()):
            if now - f.ts <= f.ttl:
                out.append(f)
            else:
                self._facts.pop(k, None)
        return out
