"""Engine protocol abstraction.

LEGACY MIGRATION NOTE:
New engine implementations must conform to this protocol.
Existing monolithic orchestration logic will be decomposed progressively.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Protocol, Mapping

class EngineProtocol(ABC):
    """Abstract engine interface for orchestrating cognition cycles.

    Responsibilities:
    - initialize(): prepare internal state/resources
    - step(): advance the system N cycles
    - snapshot(): produce a serializable state bundle for inspection/persistence
    - close(): release resources
    """

    @abstractmethod
    def initialize(self, config: Mapping[str, Any] | None = None) -> None:  # noqa: D401
        """Initialize engine with optional configuration mapping."""
        raise NotImplementedError

    @abstractmethod
    def step(self, n: int = 1) -> None:
        """Advance the engine by n cycles (default 1)."""
        raise NotImplementedError

    @abstractmethod
    def snapshot(self) -> Mapping[str, Any]:
        """Return a lightweight serializable snapshot of current engine state."""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """Release any held resources (files, network handles, threads)."""
        raise NotImplementedError
