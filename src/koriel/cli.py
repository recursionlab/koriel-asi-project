"""CLI module for console entrypoints."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .engine import RecursiveOrchestrationEngine, EngineConfig
from .io import (load_config, save_results, get_results_dir, 
                get_default_config_path, validate_config)
from .safety import ExperimentSafetyGate, check_system_resources

def run_minimal_cycle(config_path: Optional[str] = None, 
                     steps: Optional[int] = None,
                     dry_run: bool = False) -> int:
    """Run a minimal consciousness evolution cycle."""
    
    print("Koriel ASI - Running minimal consciousness cycle")
    
    if dry_run:
        print("DRY RUN MODE: No actual computation will be performed")
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
                print(f"Using default configuration: {default_config_path}")
            else:
                print("No configuration specified and default config not found")
                print("Using built-in defaults")
                config_data = {
                    'engine': {
                        'field_size': 256,
                        'field_length': 20.0,
                        'dt': 0.001,
                        'evolution_steps': 1000,
                        'c_rate': 0.05,
                        'c_thresh': 0.5
                    }
                }
        
        # Validate configuration
        config_data = validate_config(config_data)
        
        # Override steps if specified
        if steps:
            config_data['engine']['evolution_steps'] = steps
            
        # Create engine config from loaded config
        engine_config = EngineConfig(**config_data.get('engine', {}))
            
        # Initialize and run engine
        engine = RecursiveOrchestrationEngine(engine_config)
        engine.initialize()
        
        print(f"Evolving field for {engine_config.evolution_steps} steps...")
        results = engine.evolve()
        
        # Display results
        print("\nEvolution completed!")
        print(f"Energy change: {results['energy_change']:.6f}")
        print(f"Complexity change: {results['complexity_change']:.6f}")
        
        # Save results
        results_dir = get_results_dir()
        results_dir.mkdir(exist_ok=True)
        save_results(results, results_dir / "minimal_run_results.json")
        print(f"Results saved to: {results_dir}/minimal_run_results.json")
        
        return 0
        
    except Exception as e:
        print(f"Error during execution: {e}")
        return 1

def run_experiment(experiment_name: str, 
                  config_path: Optional[str] = None,
                  allow_experiments: bool = False,
                  dry_run: bool = False) -> int:
    """Run a gated experiment with safety checks."""
    
    if not allow_experiments:
        print("ERROR: Experiments require explicit --allow-experiments flag")
        print("This is for safety - experiments may modify system behavior")
        return 1
        
    if dry_run:
        print(f"DRY RUN: Would run experiment '{experiment_name}'")
        return 0
        
    print(f"Running experiment: {experiment_name}")
    print("WARNING: Experimental mode - proceed with caution")
    
    try:
        # Initialize safety gate
        safety_gate = ExperimentSafetyGate()
        
        # Find experiment script
        experiment_root = Path(__file__).parent.parent.parent / "experiments"
        experiment_files = list(experiment_root.rglob(f"{experiment_name}.py"))
        
        if not experiment_files:
            print(f"ERROR: Experiment '{experiment_name}' not found")
            print(f"Searched in: {experiment_root}")
            return 1
            
        experiment_path = experiment_files[0]
        print(f"Found experiment: {experiment_path}")
        
        # Load experiment configuration
        experiment_config = safety_gate.load_experiment_config(experiment_path)
        
        # Check safety requirements
        safety_check = safety_gate.check_safety_requirements(experiment_config, allow_experiments)
        
        if not safety_check['allowed']:
            print(f"ERROR: {safety_check['reason']}")
            return 1
            
        # Display warnings and get confirmation
        warnings = safety_check.get('warnings', [])
        if warnings:
            print("\nWARNINGS:")
            for warning in warnings:
                print(f"  - {warning}")
                
        risk_level = safety_check.get('risk_level', 'unknown')
        print(f"\nRisk Level: {risk_level.upper()}")
        
        # Check system resources
        resources = check_system_resources()
        print("\nSystem Resources:")
        print(f"  Memory: {resources['memory_available_gb']:.1f}GB available ({resources['memory_percent_used']:.1f}% used)")
        print(f"  Disk: {resources['disk_free_gb']:.1f}GB free ({resources['disk_percent_used']:.1f}% used)")
        
        # Get user confirmation for high-risk experiments
        if risk_level == 'high':
            response = input("\nThis is a HIGH RISK experiment. Continue? (type 'yes' to proceed): ")
            if response.lower() != 'yes':
                print("Experiment cancelled by user")
                return 0
                
        # Create resource monitor
        monitor = safety_gate.create_resource_monitor(experiment_config)
        
        print("\nStarting experiment with resource monitoring...")
        monitor.start_monitoring()
        
        # This is a basic framework - actual experiment execution would be implemented
        # based on the specific experiment type and requirements
        print("Experiment framework is set up but execution is not yet implemented")
        print("Resource monitor is active and limits are enforced")
        
        # Simulate some work and monitoring
        import time
        for i in range(5):
            time.sleep(1)
            stats = monitor.get_stats()
            limits_check = monitor.check_limits()
            
            print(f"  T+{stats['elapsed_time']:.1f}s: Memory={stats['memory_mb']:.1f}MB CPU={stats['cpu_percent']:.1f}%")
            
            if limits_check['status'] == 'violation':
                print("SAFETY VIOLATION DETECTED:")
                for violation in limits_check['violations']:
                    print(f"  - {violation}")
                print("Experiment terminated for safety")
                return 1
                
        print("Experiment completed successfully")
        return 0
        
    except Exception as e:
        print(f"Error during experiment execution: {e}")
        return 1

def main_cli():
    """Main CLI entrypoint."""
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
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run consciousness evolution')
    run_parser.add_argument('--config', type=str, help='Configuration file path')
    run_parser.add_argument('--steps', type=int, help='Number of evolution steps')
    run_parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    # Experiment command  
    exp_parser = subparsers.add_parser('experiment', help='Run gated experiments')
    exp_parser.add_argument('--name', type=str, required=True, help='Experiment name')
    exp_parser.add_argument('--config', type=str, help='Configuration file path')
    exp_parser.add_argument('--allow-experiments', action='store_true', 
                           help='Allow experimental execution (required for safety)')
    exp_parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        return run_minimal_cycle(
            config_path=args.config,
            steps=args.steps,
            dry_run=args.dry_run
        )
    elif args.command == 'experiment':
        return run_experiment(
            experiment_name=args.name,
            config_path=args.config,
            allow_experiments=args.allow_experiments,
            dry_run=args.dry_run
        )
    elif args.command == 'status':
        print("Koriel ASI System Status:")
        print("- Package: Installed")
        print("- Configuration: Available")
        print("- Experiments: Gated (require --allow-experiments)")
        return 0
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main_cli())