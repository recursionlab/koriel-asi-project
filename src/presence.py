"""Shim: presence_certificate moved to `koriel.core.evaluation.presence`.

This file keeps backward compatibility for imports that do `from src.presence import presence_certificate`.
Prefer importing from `koriel.core.evaluation.presence` going forward.
"""

import sys
import os

# Temporarily add current directory to find koriel module
_original_path = sys.path[:]
try:
    _src_path = os.path.dirname(__file__)
    if _src_path not in sys.path:
        sys.path.insert(0, _src_path)
    from koriel.core.evaluation.presence import presence_certificate  # re-export
finally:
    # Restore original path to avoid affecting other imports
    sys.path[:] = _original_path
    # But keep the import available
    if 'koriel.core.evaluation.presence' in sys.modules:
        presence_certificate = sys.modules['koriel.core.evaluation.presence'].presence_certificate

