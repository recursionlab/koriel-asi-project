"""Minimal MMLU benchmark stub used for tests."""

from __future__ import annotations

from typing import Callable, Dict

from .base import BenchmarkSuite, register_suite


@register_suite("mmlu")
class MMLUSuite(BenchmarkSuite):
    """Tiny MMLU subset returning a deterministic accuracy of 0.5."""

    def evaluate(self, model_fn: Callable[[str, list[str]], str]) -> Dict[str, float]:
        questions = [
            ("q1", ["A", "B"], "A"),
            ("q2", ["A", "B"], "B"),
        ]
        correct = 0
        for q, choices, answer in questions:
            pred = model_fn(q, choices)
            if pred == answer:
                correct += 1
        acc = correct / len(questions)
        return {"accuracy": acc}
