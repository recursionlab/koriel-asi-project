"""RCCE (Recursive Coherence and Consciousness Engine) package."""

from .controller import compute_rcce_metrics, ethical_guard  # noqa: F401
from .observer import ObserverState, control_step  # noqa: F401

__all__ = [
    "compute_rcce_metrics",
    "ethical_guard",
    "ObserverState",
    "control_step",
]

