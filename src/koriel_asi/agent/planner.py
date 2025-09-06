from __future__ import annotations

import re

from .types import Goal, Plan, Step


class Planner:
    """Minimal heuristic planner."""

    def plan(self, goal: Goal) -> Plan:
        text = goal.text.lower().strip()
        m = re.match(r"add\s+(-?\d+)\s+and\s+(-?\d+)", text)
        if m:
            a, b = m.groups()
            code = f"print({int(a)} + {int(b)})"
            return Plan(steps=[Step(tool="python_exec", args={"code": code})])
        return Plan(steps=[Step(tool="python_exec", args={"code": "print('hello')"})])
