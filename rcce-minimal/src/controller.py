"""Shim: RCCEController moved to `koriel.core.evaluation.rcce_controller`.

This file keeps backward compatibility for scripts that import
`rcce-minimal.src.controller.RCCEController`. Prefer importing from
`koriel.core.evaluation.rcce_controller` going forward.
"""

import sys
import os
# Add the main src directory to path to find koriel module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from koriel.core.evaluation.rcce_controller import RCCEController  # re-export
