from __future__ import annotations

from typing import Dict

from ..tools.python_exec import PythonExec
from ..tools.retrieval import Retrieval
from ..tools.web_reader import WebReader
from .actor import Actor
from .planner import Planner
from .types import Goal, Result
from .verifier import Verifier


def tool_registry() -> Dict[str, object]:
    return {
        "python_exec": PythonExec(),
        "retrieval": Retrieval(),
        "web_reader": WebReader(allowlist=[]),  # stubbed
    }


def run_once(goal_text: str) -> Result:
    goal = Goal(text=goal_text)
    plan = Planner().plan(goal)
    outputs = Actor(tool_registry()).execute(plan)
    ok, notes = Verifier().verify(outputs)
    return Result(ok=ok, steps=outputs, notes=notes)


if __name__ == "__main__":
    print(run_once("add 2 and 3"))
