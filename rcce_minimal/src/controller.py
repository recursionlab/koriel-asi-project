"""Shim: re-export RCCEController from koriel.core.evaluation for legacy imports."""
import sys
import os

# Temporarily add the main src directory to find koriel module  
_original_path = sys.path[:]
try:
    _src_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
    if _src_path not in sys.path:
        sys.path.insert(0, _src_path)
    from koriel.core.evaluation.rcce_controller import RCCEController
finally:
    # Restore original path to avoid affecting other imports
    sys.path[:] = _original_path
    # But keep the import available
    if 'koriel.core.evaluation.rcce_controller' in sys.modules:
        RCCEController = sys.modules['koriel.core.evaluation.rcce_controller'].RCCEController
