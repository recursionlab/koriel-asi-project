"""Operator specification dataclass.

Represents a declarative description of an operator made available to the engine.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass(slots=True)
class OperatorSpec:
    name: str
    arity: int
    deterministic: bool = True
    safety_tags: Optional[List[str]] = field(default=None)

    def __post_init__(self) -> None:  # basic validation
        if self.arity < 0:
            raise ValueError("arity must be non-negative")
