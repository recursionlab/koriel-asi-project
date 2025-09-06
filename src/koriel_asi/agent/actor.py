from __future__ import annotations

from typing import Any, Dict, List, Protocol

from .types import Plan


class Tool(Protocol):
    def run(self, **kwargs: Any) -> Dict[str, Any]: ...


class Actor:
    """Executes plan steps via provided tools dict."""

    def __init__(self, tools: Dict[str, Tool]) -> None:
        self.tools = tools

    def execute(self, plan: Plan) -> List[Dict[str, Any]]:
        outputs: List[Dict[str, Any]] = []
        for step in plan.steps:
            tool = self.tools.get(step.tool)
            if not tool:
                outputs.append({"tool": step.tool, "error": "unknown_tool"})
                continue
            try:
                res = tool.run(**step.args)
                res.setdefault("tool", step.tool)
                outputs.append(res)
            except Exception as e:
                outputs.append({"tool": step.tool, "error": str(e)})
        return outputs
