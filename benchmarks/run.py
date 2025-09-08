from __future__ import annotations

import argparse
import json
import logging
import os
from typing import Any

from . import get_suite


def dummy_model(question: str, choices: list[str]) -> str:
    """A trivial model that always selects option A."""
    return "A"


def setup_logging(suite: str) -> str:
    log_dir = os.path.join("logs", "benchmarks")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{suite}.log")
    logging.basicConfig(filename=log_file, level=logging.INFO, format="%(message)s")
    return log_dir


def main(argv: list[str] | None = None) -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Run a benchmark suite")
    parser.add_argument("--suite", required=True, help="Name of the benchmark suite")
    args = parser.parse_args(argv)

    log_dir = setup_logging(args.suite)
    logging.info("running suite %s", args.suite)

    suite_cls = get_suite(args.suite)
    suite = suite_cls()
    metrics = suite.evaluate(dummy_model)

    logging.info("metrics %s", metrics)
    out_path = os.path.join(log_dir, f"{args.suite}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f)

    print(json.dumps(metrics))
    return metrics


if __name__ == "__main__":
    main()
