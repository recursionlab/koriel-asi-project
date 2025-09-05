from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, Dict, Type


class BenchmarkSuite(ABC):
    """Abstract base class for benchmark suites."""

    @abstractmethod
    def evaluate(self, model_fn: Callable[[str, list[str]], str]) -> Dict[str, float]:
        """Evaluate the provided model function.

        Args:
            model_fn: Function taking (question, choices) and returning a label.
        Returns:
            A dictionary of metric name to value.
        """
        raise NotImplementedError


_SUITE_REGISTRY: Dict[str, Type[BenchmarkSuite]] = {}


def register_suite(name: str) -> Callable[[Type[BenchmarkSuite]], Type[BenchmarkSuite]]:
    """Decorator to register a benchmark suite."""

    def decorator(cls: Type[BenchmarkSuite]) -> Type[BenchmarkSuite]:
        _SUITE_REGISTRY[name] = cls
        return cls

    return decorator


def get_suite(name: str) -> Type[BenchmarkSuite]:
    """Retrieve a registered benchmark suite by name."""

    if name not in _SUITE_REGISTRY:
        raise KeyError(f"Unknown benchmark suite: {name}")
    return _SUITE_REGISTRY[name]
