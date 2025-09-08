# src/metastate.py
import json
import hashlib
import numpy as np
from dataclasses import dataclass
from pathlib import Path
def digest_arr(a: np.ndarray) -> str:
    return hashlib.sha1(a.tobytes()).hexdigest()


@dataclass
class MetaState:
    t: int
    seed: int
    phase: float
    delta_xi: float
    upsilon: int
    ethics: int
    rc: float
    loss: float
    energy: float


class ShadowCodex:
    def __init__(self, path: str):
        self.p = Path(path)
        self.p.parent.mkdir(parents=True, exist_ok=True)
        if not self.p.exists():
            self.p.write_text("")

    def append(self, obj: dict):
        with self.p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
