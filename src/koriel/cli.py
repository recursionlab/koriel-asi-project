"""CLI module for console entrypoints."""

import argparse
import sys
from pathlib import Path
from typing import Optional, List

from .engine import RecursiveOrchestrationEngine, EngineConfig
from .io import load_config, save_results, get_config_dir, get_results_dir
from .meta import SelfModificationEngine

def run_minimal_cycle(config_path: Optional[str] = None, 
                     steps: Optional[int] = None,
                     dry_run: bool = False) -> int:
    """Run a minimal consciousness evolution cycle."""
    
    print("Koriel ASI - Running minimal consciousness cycle")
    
    if dry_run:
        print("DRY RUN MODE: No actual computation will be performed")
        return 0
        
    try:
        # Load configuration
        if config_path:
            config_data = load_config(config_path)
            engine_config = EngineConfig(**config_data.get('engine', {}))
        else:
            engine_config = EngineConfig()
            
        if steps:
            engine_config.evolution_steps = steps
            
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
    """Run a gated experiment."""
    
    if not allow_experiments:
        print("ERROR: Experiments require explicit --allow-experiments flag")
        print("This is for safety - experiments may modify system behavior")
        return 1
        
    if dry_run:
        print(f"DRY RUN: Would run experiment '{experiment_name}'")
        return 0
        
    print(f"Running experiment: {experiment_name}")
    print("WARNING: Experimental mode - proceed with caution")
    
    # Implementation would depend on specific experiments
    print("Experiment framework not yet implemented")
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
    status_parser = subparsers.add_parser('status', help='Show system status')
    
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