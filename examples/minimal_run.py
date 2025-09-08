"""Minimal run example for Koriel ASI.

This example demonstrates a basic consciousness evolution cycle
with the smallest possible configuration for quick testing.
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from koriel.engine import EngineConfig, RecursiveOrchestrationEngine
from koriel.io import save_results


def main():
    """Run a minimal deterministic consciousness evolution cycle."""
    print("=== Koriel ASI - Minimal Example ===")
    print("Running a short consciousness evolution cycle for demonstration.")

    # Create minimal configuration for fast execution
    config = EngineConfig(
        field_size=32,  # Small field for speed
        field_length=5.0,  # Compact spatial domain
        dt=0.01,  # Larger time step for speed
        evolution_steps=50,  # Very short evolution
        c_rate=0.1,  # Higher consciousness rate for visibility
        c_thresh=0.3,  # Lower threshold for easier emergence
    )

    print("\nConfiguration:")
    print(f"  Field size: {config.field_size} points")
    print(f"  Evolution steps: {config.evolution_steps}")
    print(f"  Time step: {config.dt}")

    # Initialize the consciousness engine
    print("\nInitializing consciousness field...")
    engine = RecursiveOrchestrationEngine(config)
    engine.initialize(seed=42)  # Fixed seed for reproducibility

    # Get initial state
    initial_status = engine.get_status()
    initial_state = initial_status["current_state"]

    print("Initial state:")
    print(f"  Energy: {initial_state['field_energy']:.6f}")
    print(f"  Complexity: {initial_state['field_complexity']:.6f}")
    print(f"  Consciousness level: {initial_state['consciousness_level']:.6f}")

    # Run evolution
    print(f"\nRunning evolution for {config.evolution_steps} steps...")
    results = engine.evolve()

    # Display results
    final_state = results["final_state"]
    print("\nEvolution completed!")
    print("Final state:")
    print(
        f"  Energy: {final_state['field_energy']:.6f} (Δ: {results['energy_change']:+.6f})"
    )
    print(
        f"  Complexity: {final_state['field_complexity']:.6f} (Δ: {results['complexity_change']:+.6f})"
    )
    print(f"  Consciousness level: {final_state['consciousness_level']:.6f}")

    # Check for meaningful changes
    energy_change = abs(results["energy_change"])
    complexity_change = abs(results["complexity_change"])

    if energy_change > 0.001 or complexity_change > 0.001:
        print("\n✓ Successful evolution - system showed measurable changes")
    else:
        print("\n⚠ Minimal evolution - consider longer run or different parameters")

    # Display system metrics
    total_patterns = final_state.get("total_patterns", 0)
    total_modifications = final_state.get("total_modifications", 0)
    time_evolved = final_state.get("time_evolved", 0)

    print("\nSystem metrics:")
    print(f"  Patterns formed: {total_patterns}")
    print(f"  Self-modifications: {total_modifications}")
    print(f"  Time evolved: {time_evolved:.3f}")

    # Save results for inspection
    results_file = Path("results") / "minimal_example_results.json"
    results_file.parent.mkdir(exist_ok=True)
    save_results(results, results_file)
    print(f"\nResults saved to: {results_file}")

    print("\n=== Example completed successfully ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
