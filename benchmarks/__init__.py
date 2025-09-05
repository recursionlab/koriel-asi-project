"""Benchmark suite registry and utilities."""
from .base import BenchmarkSuite, register_suite, get_suite

# Import suites so they register with the registry when package is imported.
from . import mmlu as _mmlu  # noqa: F401

__all__ = ["BenchmarkSuite", "register_suite", "get_suite"]
