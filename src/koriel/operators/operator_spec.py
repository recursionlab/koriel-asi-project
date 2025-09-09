"""Operator specification dataclass.

Represents a declarative description of an operator made available to the engine.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass(slots=True)
class OperatorSpec:
    name: str
    category: str
    arity: int = 0
    deterministic: bool = True
    safety_tags: Optional[List[str]] = field(default=None)

    def __post_init__(self) -> None:  # basic validation
        if not self.name or len(self.name) > 128:
            raise ValueError("invalid operator name")
        if not self.category:
            raise ValueError("category required")
        if self.arity < 0:
            raise ValueError("arity must be non-negative")
