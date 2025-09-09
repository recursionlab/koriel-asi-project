from typing import Any, Dict
from koriel.core.engine_protocol import EngineProtocol

class DummyEngine(EngineProtocol):
    def __init__(self) -> None:
        self._counter = 0
        self._seed: int | None = None
        self._closed = False

    def initialize(self, seed: int | None = None) -> None:  # type: ignore[override]
        self._seed = seed
        self._counter = 0

    def step(self, n: int = 1) -> None:  # type: ignore[override]
        assert not self._closed, "Engine closed"
        for _ in range(n):
            self._counter += 1

    def snapshot(self) -> Dict[str, Any]:  # type: ignore[override]
        return {"counter": self._counter, "seed": self._seed}

    def close(self) -> None:  # type: ignore[override]
        self._closed = True


def test_dummy_engine_cycle_determinism():
    e1 = DummyEngine()
    e1.initialize(seed=42)
    e1.step(3)
    snap1 = e1.snapshot()

    e2 = DummyEngine()
    e2.initialize(seed=42)
    e2.step(3)
    snap2 = e2.snapshot()

    assert snap1 == snap2
    assert snap1["counter"] == 3
