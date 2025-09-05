from __future__ import annotations
import json
from pathlib import Path
from typing import Dict

from .base import BenchmarkSuite, register_suite


@register_suite("mmlu")
class MMLUSuite(BenchmarkSuite):
    """Simple MMLU-style multiple-choice benchmark using a tiny sample."""

    def __init__(self) -> None:
        data_path = Path(__file__).resolve().parent / "data" / "mmlu_sample.jsonl"
        with open(data_path, "r", encoding="utf-8") as f:
            self.samples = [json.loads(line) for line in f]

    def evaluate(self, model_fn) -> Dict[str, float]:
        correct = 0
        for sample in self.samples:
            pred = model_fn(sample["question"], sample["choices"])
            if pred.strip().upper() == sample["answer"]:
                correct += 1
        total = len(self.samples)
        return {"accuracy": correct / total if total else 0.0}
