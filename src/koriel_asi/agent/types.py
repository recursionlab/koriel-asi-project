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
