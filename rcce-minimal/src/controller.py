"""Shim: RCCEController moved to `koriel.core.evaluation.rcce_controller`.

This file keeps backward compatibility for scripts that import
`rcce-minimal.src.controller.RCCEController`. Prefer importing from
`koriel.core.evaluation.rcce_controller` going forward.
"""

from koriel.core.evaluation.rcce_controller import RCCEController  # re-export
