"""Benchmark suite registration utilities."""

# Import suites so that they register themselves via decorators
from . import mmlu  # noqa: F401
from .base import BenchmarkSuite, get_suite, register_suite

__all__ = ["BenchmarkSuite", "get_suite", "register_suite"]
