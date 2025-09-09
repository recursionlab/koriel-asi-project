from __future__ import annotations
from dataclasses import dataclass

__all__ = ["FieldState"]

@dataclass
class FieldState:
    """Phase 0 extracted pure data structure for field snapshot metadata.

    Invariant: Side-effect free. Extended only via ADR-governed changes.
    Migration origin: legacy quantum_consciousness_field.py (conceptual).
    """
    step_index: int = 0
    energy: float = 0.0
