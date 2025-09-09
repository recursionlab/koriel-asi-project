"""Minimal Operator Registry scaffold (Phase 0).

Purpose: provide a central place for operator metadata without changing operator
implementation semantics. This is intentionally small and conservative.
"""
from dataclasses import dataclass, field
from typing import Dict, Optional, List


@dataclass
class OperatorEntry:
    name: str
    category: Optional[str] = None
    arity: int = 0
    deterministic: bool = True
    safety_tags: List[str] = field(default_factory=list)


class OperatorRegistry:
    """In-memory registry for operator metadata. Phase 0: no persistence."""

    def __init__(self) -> None:
        self._entries: Dict[str, OperatorEntry] = {}

    def register(self, entry: OperatorEntry) -> None:
        if entry.name in self._entries:
            raise KeyError(f"Operator already registered: {entry.name}")
        self._entries[entry.name] = entry

    def get(self, name: str) -> Optional[OperatorEntry]:
        return self._entries.get(name)

    def list(self) -> List[OperatorEntry]:
        return list(self._entries.values())
