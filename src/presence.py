"""Shim: presence_certificate moved to `koriel.core.evaluation.presence`.

This file keeps backward compatibility for imports that do `from src.presence import presence_certificate`.
Prefer importing from `koriel.core.evaluation.presence` going forward.
"""

from koriel.core.evaluation.presence import presence_certificate  # re-export

