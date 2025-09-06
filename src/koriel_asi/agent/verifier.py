from __future__ import annotations
from typing import Dict, List, Tuple

class Verifier:
    """Any error fails."""
    def verify(self, step_outputs: List[Dict]) -> Tuple[bool, List[str]]:
        notes: List[str] = []
        for i, out in enumerate(step_outputs):
            if out.get("error"):
                notes.append(f"step_{i}_failed:{out['error']}")
                return False, notes
        notes.append("all_steps_ok")
        return True, notes
