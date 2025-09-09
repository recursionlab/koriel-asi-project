"""Shim: presence_certificate moved to `koriel.core.evaluation.presence`.

This file keeps backward compatibility for imports that do `from src.presence import presence_certificate`.
Prefer importing from `koriel.core.evaluation.presence` going forward.
"""

import sys
import os
# Ensure koriel module can be found
sys.path.insert(0, os.path.dirname(__file__))
from koriel.core.evaluation.presence import presence_certificate  # re-export

