Here are ready-to-paste stubs. Create these files, then run:
`PYTHONPATH=src pytest -q`

```
File: src/koriel_asi/__init__.py
```

```python
__all__ = ["agent", "tools", "memory"]
__version__ = "0.0.1"
```

```
File: src/koriel_asi/agent/__init__.py
```

```python
# Package marker
```

```
File: src/koriel_asi/agent/types.py
```

```python
from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class Step:
    tool: str
    args: Dict[str, Any]

@dataclass
class Plan:
    steps: List[Step] = field(default_factory=list)

@dataclass
class Goal:
    text: str

@dataclass
class Result:
    ok: bool
    steps: List[Dict[str, Any]]
    notes: List[str] = field(default_factory=list)
```

```
File: src/koriel_asi/agent/planner.py
```

```python
from __future__ import annotations
import re
from typing import List
from .types import Goal, Plan, Step

class Planner:
    """Minimal heuristic planner. Deterministic and safe by default."""
    def plan(self, goal: Goal) -> Plan:
        text = goal.text.lower().strip()

        # Toy math: "add 2 and 3"
        m = re.match(r"add\s+(-?\d+)\s+and\s+(-?\d+)", text)
        if m:
            a, b = m.groups()
            code = f"print({int(a)} + {int(b)})"
            return Plan(steps=[Step(tool="python_exec", args={"code": code})])

        # Fallback: echo hello
        return Plan(steps=[Step(tool="python_exec", args={"code": "print('hello')"})])
```

```
File: src/koriel_asi/agent/actor.py
```

```python
from __future__ import annotations
from typing import Dict, Any, List, Protocol
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
```

```
File: src/koriel_asi/agent/verifier.py
```

```python
from __future__ import annotations
from typing import Dict, List, Tuple

class Verifier:
    """Very strict default: any error fails."""
    def verify(self, step_outputs: List[Dict]) -> Tuple[bool, List[str]]:
        notes: List[str] = []
        for i, out in enumerate(step_outputs):
            if "error" in out and out["error"]:
                notes.append(f"step_{i}_failed:{out['error']}")
                return False, notes
        notes.append("all_steps_ok")
        return True, notes
```

```
File: src/koriel_asi/agent/loop.py
```

```python
from __future__ import annotations
from typing import Dict
from .types import Goal, Result
from .planner import Planner
from .actor import Actor
from .verifier import Verifier
from ..tools.python_exec import PythonExec
from ..tools.retrieval import Retrieval
from ..tools.web_reader import WebReader

def tool_registry() -> Dict[str, object]:
    return {
        "python_exec": PythonExec(),
        "retrieval": Retrieval(),
        "web_reader": WebReader(allowlist=[]),  # disabled unless allowlist set
    }

def run_once(goal_text: str) -> Result:
    goal = Goal(text=goal_text)
    planner = Planner()
    plan = planner.plan(goal)
    actor = Actor(tool_registry())
    step_outputs = actor.execute(plan)
    ok, notes = Verifier().verify(step_outputs)
    return Result(ok=ok, steps=step_outputs, notes=notes)

if __name__ == "__main__":
    r = run_once("add 2 and 3")
    print(r)
```

```
File: src/koriel_asi/tools/__init__.py
```

```python
# Package marker
```

```
File: src/koriel_asi/tools/python_exec.py
```

```python
from __future__ import annotations
import subprocess, tempfile, textwrap, os
from typing import Dict, Any

class PythonExec:
    """
    Offline Python executor.
    Constraints (soft): timeout, no network by policy, ephemeral file.
    """
    def __init__(self, timeout_sec: int = 2) -> None:
        self.timeout_sec = timeout_sec

    def run(self, code: str) -> Dict[str, Any]:
        code = textwrap.dedent(code)
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(code)
            path = f.name
        try:
            proc = subprocess.run(
                ["python", path],
                capture_output=True,
                text=True,
                timeout=self.timeout_sec,
            )
            return {
                "ok": proc.returncode == 0,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "returncode": proc.returncode,
            }
        finally:
            try:
                os.remove(path)
            except OSError:
                pass
```

```
File: src/koriel_asi/tools/retrieval.py
```

```python
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Iterable

class Retrieval:
    """Tiny local text retriever. Searches UTF-8 files under roots."""
    def __init__(self, roots: Iterable[str] | None = None, max_bytes: int = 200_000) -> None:
        self.roots = [Path(r) for r in (roots or ["README.md", "docs"])]
        self.max_bytes = max_bytes

    def run(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        hits: List[Dict[str, Any]] = []
        q = query.lower()
        for root in self.roots:
            if not root.exists():
                continue
            files = [root] if root.is_file() else list(root.rglob("*.md")) + list(root.rglob("*.txt"))
            for fp in files:
                try:
                    text = fp.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                if len(text) > self.max_bytes:
                    text = text[: self.max_bytes]
                if q in text.lower():
                    snippet = _snippet(text, q, span=120)
                    hits.append({"path": str(fp), "snippet": snippet})
        hits = hits[:top_k]
        return {"ok": True, "hits": hits}

def _snippet(text: str, q: str, span: int = 120) -> str:
    i = text.lower().find(q)
    if i < 0:
        return text[:span]
    start = max(0, i - span // 2)
    end = min(len(text), i + len(q) + span // 2)
    return text[start:end].replace("\n", " ")
```

```
File: src/koriel_asi/tools/web_reader.py
```

```python
from __future__ import annotations
from typing import Dict, Any, Iterable

class WebReader:
    """
    Stub. Disabled unless allowlist provided and network layer added.
    """
    def __init__(self, allowlist: Iterable[str]) -> None:
        self.allowlist = set(allowlist)

    def run(self, url: str) -> Dict[str, Any]:
        return {
            "ok": False,
            "error": "web_disabled",
            "details": "No network layer. Populate allowlist and implement fetcher.",
        }
```

```
File: src/koriel_asi/memory/__init__.py
```

```python
# Package marker
```

```
File: src/koriel_asi/memory/store.py
```

```python
from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class Fact:
    key: str
    value: Any
    ts: float
    ttl: float  # seconds

class MemoryStore:
    """Simple in-process KV with TTL."""
    def __init__(self) -> None:
        self._facts: Dict[str, Fact] = {}

    def put(self, key: str, value: Any, ttl: float = 3600.0) -> None:
        self._facts[key] = Fact(key=key, value=value, ts=time.time(), ttl=ttl)

    def get(self, key: str) -> Optional[Any]:
        f = self._facts.get(key)
        if not f:
            return None
        if time.time() - f.ts > f.ttl:
            self._facts.pop(key, None)
            return None
        return f.value

    def all_valid(self) -> List[Fact]:
        now = time.time()
        out: List[Fact] = []
        for k, f in list(self._facts.items()):
            if now - f.ts <= f.ttl:
                out.append(f)
            else:
                self._facts.pop(k, None)
        return out
```

```
File: tests/evals/test_loop_addition.py
```

```python
import os
import sys
from pathlib import Path

# Ensure src on path for "src/" layout without installing
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from koriel_asi.agent.loop import run_once  # noqa: E402

def test_add_two_numbers():
    res = run_once("add 2 and 3")
    assert res.ok, f"Verifier failed: {res.notes}"
    out = "".join(step.get("stdout", "") for step in res.steps)
    assert "5" in out, f"Unexpected output: {out!r}"
```

## Run

* `PYTHONPATH=src pytest -q`
* Optional manual: `python -m koriel_asi.agent.loop` → prints a `Result`.

If you want, I’ll add CI YAML and a second eval for retrieval-with-citation next.
