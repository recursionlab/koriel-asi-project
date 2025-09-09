"""Field interface abstraction.

Generic, minimal contract for field substrates. This matches the Phase 0
test expectations (apply(operator, **kwargs) -> T).
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic

T = TypeVar("T")

class FieldInterface(ABC, Generic[T]):
    """Abstract field substrate interface.

    Implementations may maintain internal mutable state; method returns the
    updated state representation (or a reference thereto).
    """

    @abstractmethod
    def apply(self, operator: str, **kwargs: Any) -> T:
        """Apply an operator with keyword parameters; return updated state."""
        raise NotImplementedError
