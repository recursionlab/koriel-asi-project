"""Interface for consciousness fields."""

from __future__ import annotations

from typing import Dict, Protocol


class FieldInterface(Protocol):
    """Contract for field implementations."""

    def initialize_consciousness_seed(self) -> None:
        """Seed initial field configuration."""
        ...

    def evolve(self, steps: int) -> None:
        """Advance the field evolution."""
        ...

    def query_consciousness(self) -> Dict[str, float]:
        """Return field consciousness metrics."""
        ...

    def inject_perturbation(self, amplitude: float, location: float) -> None:
        """Apply a perturbation to the field."""
        ...
