"""Protocol for orchestration engines."""

from __future__ import annotations

from typing import Any, Dict, Optional, Protocol


class EngineProtocol(Protocol):
    """Expected interface for engine implementations."""

    def initialize(self, seed: Optional[int] = None) -> None:
        """Prepare the engine state."""
        ...

    def evolve(self, steps: Optional[int] = None) -> Dict[str, Any]:
        """Advance the engine and return evolution data."""
        ...

    def get_status(self) -> Dict[str, Any]:
        """Report current engine status."""
        ...

    def reset(self) -> None:
        """Return the engine to its initial state."""
        ...
