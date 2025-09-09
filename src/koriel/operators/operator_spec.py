"""Specification for field operators."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class OperatorSpec:
    """Declarative description of an operator."""

    name: str
    description: str
    params: Optional[Mapping[str, Any]] = None
