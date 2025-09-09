"""Field interface abstraction.

Defines the minimal contract for state-transforming field substrates.
Legacy field implementations will be incrementally adapted to conform.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Protocol, Mapping

class FieldInterface(ABC):
    """Abstract field substrate interface.

    apply(): perform an operator-driven transformation on a field state.
    Implementations may mutate internal buffers or return new state objects.
    """

    @abstractmethod
    def apply(self, operator: str, state: Any, params: Mapping[str, Any] | None = None) -> Any:
        """Apply an operator to the given state with optional parameters.
        Returns the updated/new state representation.
        """
        raise NotImplementedError
