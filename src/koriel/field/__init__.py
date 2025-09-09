"""Field substrate package (Phase 0 scaffold).

Provides compatibility re-exports for legacy test imports while Phase 0
decomposition proceeds. New code should prefer abstract interfaces.
"""
from .field_interface import FieldInterface  # noqa: F401
from .state import FieldState  # noqa: F401

# Re-export legacy concrete symbols from the explicitly named legacy module.
from ..field_legacy_impl import SimpleQuantumField, FieldObservation, PatternMemory  # noqa: F401

__all__ = [
	"FieldInterface",
	"FieldState",
	"SimpleQuantumField",
	"FieldObservation",
	"PatternMemory",
]


def __getattr__(name: str):
	"""Emit deprecation guidance when legacy symbols are accessed.

	This helps callers notice the migration path without breaking runtime.
	"""
	legacy_names = {"SimpleQuantumField", "FieldObservation", "PatternMemory"}
	if name in legacy_names:
		import warnings
		warnings.warn(
			f"Accessing legacy symbol koriel.field.{name} — this symbol is deprecated and will be moved; see ADR-0003.",
			DeprecationWarning,
			stacklevel=2,
		)
		return globals()[name]
	raise AttributeError(name)