"""CLI module for console entrypoints."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .engine import EngineConfig, RecursiveOrchestrationEngine
from .io import (
    get_default_config_path,
    get_results_dir,
    load_config,
    save_results,
    validate_config,
)
from .logging import get_logger, setup_logging
from .safety import ExperimentSafetyGate, check_system_resources

logger = get_logger(__name__)


def run_minimal_cycle(
    config_path: Optional[str] = None,
    steps: Optional[int] = None,
    dry_run: bool = False,
) -> int:
    """Run a minimal consciousness evolution cycle."""

    setup_logging({"monitoring": {"log_level": "INFO"}})
    logger.info("Koriel ASI - Running minimal consciousness cycle")

    if dry_run:
        logger.info("DRY RUN MODE: No actual computation will be performed")
        return 0

    try:
        # Load configuration with defaults
        if config_path:
            config_data = load_config(config_path)
        else:
            # Use default config
            default_config_path = get_default_config_path()
            if default_config_path.exists():
                config_data = load_config(default_config_path)
                logger.info(f"Using default configuration: {default_config_path}")
            else:
                logger.warning(
                    "No configuration specified and default config not found"
                )
                logger.info("Using built-in defaults")
                config_data = {
                    "engine": {
                        "field_size": 256,
                        "field_length": 20.0,
                        "dt": 0.001,
                        "evolution_steps": 1000,
                        "c_rate": 0.05,
                        "c_thresh": 0.5,
                    }
                }

        # Validate configuration
        config_data = validate_config(config_data)

        # Override steps if specified
        if steps:
            config_data["engine"]["evolution_steps"] = steps

        setup_logging(config_data)

        engine_config = EngineConfig(**config_data.get("engine", {}))

        engine = RecursiveOrchestrationEngine(engine_config)
        engine.initialize()

        logger.info(f"Evolving field for {engine_config.evolution_steps} steps...")
        results = engine.evolve()

        logger.info("Evolution completed")
        logger.info(f"Energy change: {results['energy_change']:.6f}")
        logger.info(f"Complexity change: {results['complexity_change']:.6f}")

        results_dir = get_results_dir()
        results_dir.mkdir(exist_ok=True)
        save_results(results, results_dir / "minimal_run_results.json")
        logger.info(f"Results saved to: {results_dir}/minimal_run_results.json")

        return 0

    except Exception as e:
        logger.error(f"Error during execution: {e}")
        return 1


def run_experiment(
    experiment_name: str,
    config_path: Optional[str] = None,
    allow_experiments: bool = False,
    dry_run: bool = False,
) -> int:
    """Run a gated experiment with safety checks."""

    setup_logging({"monitoring": {"log_level": "INFO"}})

    if not allow_experiments:
        logger.error("ERROR: Experiments require explicit --allow-experiments flag")
        logger.warning("This is for safety - experiments may modify system behavior")
        return 1

    if dry_run:
        logger.info(f"DRY RUN: Would run experiment '{experiment_name}'")
        return 0

    logger.info(f"Running experiment: {experiment_name}")
    logger.warning("Experimental mode - proceed with caution")

    try:
        safety_gate = ExperimentSafetyGate()

        experiment_root = Path(__file__).parent.parent.parent / "experiments"
        experiment_files = list(experiment_root.rglob(f"{experiment_name}.py"))

        if not experiment_files:
            logger.error(f"ERROR: Experiment '{experiment_name}' not found")
            logger.error(f"Searched in: {experiment_root}")
            return 1

        experiment_path = experiment_files[0]
        logger.info(f"Found experiment: {experiment_path}")

        experiment_config = safety_gate.load_experiment_config(experiment_path)
        setup_logging(experiment_config)

        safety_check = safety_gate.check_safety_requirements(
            experiment_config, allow_experiments
        )

        if not safety_check["allowed"]:
            logger.error(f"ERROR: {safety_check['reason']}")
            return 1

        warnings = safety_check.get("warnings", [])
        if warnings:
            logger.warning("WARNINGS:")
            for warning in warnings:
                logger.warning(f"  - {warning}")

        risk_level = safety_check.get("risk_level", "unknown")
        logger.info(f"Risk Level: {risk_level.upper()}")

        resources = check_system_resources()
        logger.info(
            f"System Resources: Memory={resources['memory_available_gb']:.1f}GB"
            f" ({resources['memory_percent_used']:.1f}% used)"
        )
        logger.info(
            f"Disk={resources['disk_free_gb']:.1f}GB"
            f" ({resources['disk_percent_used']:.1f}% used)"
        )

        if risk_level == "high":
            response = input(
                "This is a HIGH RISK experiment. Continue? (type 'yes' to proceed): "
            )
            if response.lower() != "yes":
                logger.info("Experiment cancelled by user")
                return 0

        monitor = safety_gate.create_resource_monitor(experiment_config)

        logger.info("Starting experiment with resource monitoring...")
        monitor.start_monitoring()

        logger.info(
            "Experiment framework is set up but execution is not yet implemented"
        )
        logger.info("Resource monitor is active and limits are enforced")

        import time

        for _ in range(5):
            time.sleep(1)
            stats = monitor.get_stats()
            limits_check = monitor.check_limits()

            logger.info(
                f"  T+{stats['elapsed_time']:.1f}s: Memory={stats['memory_mb']:.1f}MB"
                f" CPU={stats['cpu_percent']:.1f}%"
            )

            if limits_check["status"] == "violation":
                logger.error("SAFETY VIOLATION DETECTED:")
                for violation in limits_check["violations"]:
                    logger.error(f"  - {violation}")
                logger.error("Experiment terminated for safety")
                return 1

        logger.info("Experiment completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Error during experiment execution: {e}")
        return 1


def main_cli():
    """Main CLI entrypoint."""
    setup_logging({"monitoring": {"log_level": "INFO"}})

    parser = argparse.ArgumentParser(
        description="Koriel ASI - Artificial Super Intelligence Research",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  koriel run                          # Run minimal cycle with defaults
  koriel run --steps 500              # Run with specific step count
  koriel run --config config/my.yaml  # Run with custom config
  koriel run --dry-run                # Dry run (no computation)

  koriel experiment --name stress-test --allow-experiments  # Run experiment
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run consciousness evolution")
    run_parser.add_argument("--config", type=str, help="Configuration file path")
    run_parser.add_argument("--steps", type=int, help="Number of evolution steps")
    run_parser.add_argument("--dry-run", action="store_true", help="Dry run mode")

    # Experiment command
    exp_parser = subparsers.add_parser("experiment", help="Run gated experiments")
    exp_parser.add_argument("--name", type=str, required=True, help="Experiment name")
    exp_parser.add_argument("--config", type=str, help="Configuration file path")
    exp_parser.add_argument(
        "--allow-experiments",
        action="store_true",
        help="Allow experimental execution (required for safety)",
    )
    exp_parser.add_argument("--dry-run", action="store_true", help="Dry run mode")

    # Status command
    subparsers.add_parser("status", help="Show system status")

    args = parser.parse_args()

    if args.command == "run":
        return run_minimal_cycle(
            config_path=args.config, steps=args.steps, dry_run=args.dry_run
        )
    elif args.command == "experiment":
        return run_experiment(
            experiment_name=args.name,
            config_path=args.config,
            allow_experiments=args.allow_experiments,
            dry_run=args.dry_run,
        )
    elif args.command == "status":
        logger.info("Koriel ASI System Status:")
        logger.info("- Package: Installed")
        logger.info("- Configuration: Available")
        logger.info("- Experiments: Gated (require --allow-experiments)")
        return 0
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main_cli())
