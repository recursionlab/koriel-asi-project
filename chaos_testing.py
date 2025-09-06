"""
Chaos testing utilities for KORIEL ASI Project.

Implements controlled failure injection for testing system resilience.
"""

import random
import numpy as np
from typing import Dict, Any, Optional, Callable
from pathlib import Path
import json
import logging


class ChaosConfig:
    """Configuration for chaos testing parameters."""
    
    def __init__(self):
        self.perturbation_rate = 0.1  # Probability of perturbation per operation
        self.noise_amplitude = 0.05   # Amplitude of noise to add
        self.drop_rate = 0.02         # Probability of dropping sections
        self.enabled = False          # Master chaos toggle
        
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'ChaosConfig':
        """Create config from dictionary."""
        chaos_config = cls()
        for key, value in config.items():
            if hasattr(chaos_config, key):
                setattr(chaos_config, key, value)
        return chaos_config


class ChaosEngine:
    """Engine for controlled chaos injection."""
    
    def __init__(self, config: ChaosConfig, seed: Optional[int] = None):
        self.config = config
        self.rng = np.random.Generator(np.random.PCG64(seed or 42))
        self.operations_count = 0
        self.perturbations_applied = 0
        self.logger = logging.getLogger(__name__)
        
    def should_apply_chaos(self) -> bool:
        """Determine if chaos should be applied this operation."""
        if not self.config.enabled:
            return False
            
        self.operations_count += 1
        return self.rng.random() < self.config.perturbation_rate
    
    def perturb_cover(self, cover_data: Any) -> Any:
        """Apply controlled perturbation to cover data."""
        if not self.should_apply_chaos():
            return cover_data
            
        self.perturbations_applied += 1
        self.logger.debug(f"Applying cover perturbation (#{self.perturbations_applied})")
        
        if isinstance(cover_data, (list, tuple)):
            # Randomly shuffle some elements
            data = list(cover_data)
            if len(data) > 1:
                # Swap two random elements
                i, j = self.rng.choice(len(data), 2, replace=False)
                data[i], data[j] = data[j], data[i]
            return type(cover_data)(data)
        
        elif isinstance(cover_data, dict):
            # Add noise to numeric values
            result = cover_data.copy()
            for key, value in result.items():
                if isinstance(value, (int, float)):
                    noise = self.rng.normal(0, self.config.noise_amplitude)
                    result[key] = value + noise
            return result
            
        return cover_data
    
    def drop_section(self, sections: list) -> list:
        """Randomly drop sections from a list."""
        if not self.should_apply_chaos():
            return sections
            
        if not sections:
            return sections
            
        # Decide how many sections to drop
        max_drops = max(1, int(len(sections) * self.config.drop_rate))
        num_drops = self.rng.integers(0, max_drops + 1)
        
        if num_drops == 0:
            return sections
            
        self.perturbations_applied += 1
        self.logger.debug(f"Dropping {num_drops} sections (#{self.perturbations_applied})")
        
        # Randomly select sections to drop
        indices_to_drop = set(self.rng.choice(len(sections), min(num_drops, len(sections)), replace=False))
        return [section for i, section in enumerate(sections) if i not in indices_to_drop]
    
    def add_noisy_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Add bounded noise to numeric metrics."""
        if not self.should_apply_chaos():
            return metrics
            
        result = metrics.copy()
        noise_applied = False
        
        for key, value in result.items():
            if isinstance(value, (int, float)) and self.rng.random() < 0.3:  # 30% chance per metric
                noise = self.rng.normal(0, self.config.noise_amplitude)
                # Bound the noise to prevent extreme values
                bounded_noise = np.clip(noise, -0.1, 0.1)
                result[key] = value + bounded_noise
                noise_applied = True
        
        if noise_applied:
            self.perturbations_applied += 1
            self.logger.debug(f"Applied noisy metrics (#{self.perturbations_applied})")
            
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get chaos engine statistics."""
        return {
            "operations_count": self.operations_count,
            "perturbations_applied": self.perturbations_applied,
            "perturbation_rate": (self.perturbations_applied / max(1, self.operations_count)),
            "config": {
                "enabled": self.config.enabled,
                "perturbation_rate": self.config.perturbation_rate,
                "noise_amplitude": self.config.noise_amplitude,
                "drop_rate": self.config.drop_rate,
            }
        }


def load_chaos_config(config_file: Optional[Path] = None) -> ChaosConfig:
    """Load chaos configuration from file."""
    if config_file is None:
        config_file = Path("config") / "chaos.json"
    
    if not config_file.exists():
        # Create default config
        default_config = ChaosConfig()
        config_file.parent.mkdir(exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump({
                "enabled": False,
                "perturbation_rate": 0.1,
                "noise_amplitude": 0.05,
                "drop_rate": 0.02
            }, f, indent=2)
        return default_config
    
    with open(config_file, 'r') as f:
        config_data = json.load(f)
    
    return ChaosConfig.from_dict(config_data)


def create_chaos_engine(seed: Optional[int] = None) -> ChaosEngine:
    """Create chaos engine with loaded configuration."""
    config = load_chaos_config()
    return ChaosEngine(config, seed)


# Property fuzzers for testing
class PropertyFuzzer:
    """Base class for property-based fuzzing."""
    
    def __init__(self, seed: Optional[int] = None):
        self.rng = np.random.Generator(np.random.PCG64(seed or 123))
    
    def generate_formula(self) -> str:
        """Generate random mathematical formula for testing."""
        operators = ['+', '-', '*', '/', '**']
        variables = ['x', 'y', 'z', 'a', 'b']
        constants = ['1', '2', '3.14', '0.5']
        
        # Simple binary operation
        left = self.rng.choice(variables + constants)
        op = self.rng.choice(operators)
        right = self.rng.choice(variables + constants)
        
        return f"({left} {op} {right})"
    
    def generate_cover(self, size: int = 10) -> list:
        """Generate random cover for testing."""
        return [
            {
                "id": i,
                "weight": self.rng.random(),
                "data": self.rng.integers(0, 100, 5).tolist()
            }
            for i in range(size)
        ]
    
    def generate_clause(self) -> Dict[str, Any]:
        """Generate random logic clause for testing."""
        predicates = ['P', 'Q', 'R', 'S']
        operators = ['AND', 'OR', 'NOT', 'IMPLIES']
        
        return {
            "type": "clause",
            "predicate": self.rng.choice(predicates),
            "operator": self.rng.choice(operators),
            "arguments": self.rng.integers(0, 10, self.rng.integers(1, 4)).tolist()
        }


def run_chaos_drill(drill_name: str, test_function: Callable, iterations: int = 10) -> Dict[str, Any]:
    """
    Run a chaos drill with multiple iterations.
    
    Args:
        drill_name: Name of the drill
        test_function: Function to test (should return success/failure)
        iterations: Number of iterations to run
        
    Returns:
        Dictionary with drill results
    """
    chaos_engine = create_chaos_engine()
    chaos_engine.config.enabled = True
    
    results = {
        "drill_name": drill_name,
        "iterations": iterations,
        "successes": 0,
        "failures": 0,
        "errors": [],
        "chaos_stats": None
    }
    
    for i in range(iterations):
        try:
            success = test_function(chaos_engine)
            if success:
                results["successes"] += 1
            else:
                results["failures"] += 1
        except Exception as e:
            results["failures"] += 1
            results["errors"].append(f"Iteration {i}: {str(e)}")
    
    results["chaos_stats"] = chaos_engine.get_stats()
    results["success_rate"] = results["successes"] / iterations
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="KORIEL ASI Chaos Testing")
    parser.add_argument("--demo", action="store_true", help="Run chaos demo")
    parser.add_argument("--enable", action="store_true", help="Enable chaos in config")
    parser.add_argument("--disable", action="store_true", help="Disable chaos in config")
    parser.add_argument("--stats", action="store_true", help="Show chaos stats")
    
    args = parser.parse_args()
    
    if args.enable:
        config_file = Path("config") / "chaos.json"
        config_file.parent.mkdir(exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump({"enabled": True, "perturbation_rate": 0.1, "noise_amplitude": 0.05, "drop_rate": 0.02}, f, indent=2)
        print("✓ Chaos testing enabled")
    
    elif args.disable:
        config_file = Path("config") / "chaos.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
            config["enabled"] = False
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        print("✓ Chaos testing disabled")
    
    elif args.demo:
        # Demo chaos functionality
        logging.basicConfig(level=logging.DEBUG)
        
        chaos_engine = create_chaos_engine(seed=42)
        chaos_engine.config.enabled = True
        
        print("=== Chaos Testing Demo ===")
        
        # Test cover perturbation
        cover = [{"id": i, "weight": i * 0.1} for i in range(5)]
        print(f"Original cover: {cover}")
        perturbed = chaos_engine.perturb_cover(cover)
        print(f"Perturbed cover: {perturbed}")
        
        # Test section dropping
        sections = [f"section_{i}" for i in range(10)]
        print(f"\nOriginal sections: {sections}")
        dropped = chaos_engine.drop_section(sections)
        print(f"After dropping: {dropped}")
        
        # Test metric noise
        metrics = {"accuracy": 0.95, "loss": 0.1, "count": 100}
        print(f"\nOriginal metrics: {metrics}")
        noisy = chaos_engine.add_noisy_metrics(metrics)
        print(f"Noisy metrics: {noisy}")
        
        print(f"\nChaos stats: {json.dumps(chaos_engine.get_stats(), indent=2)}")
        
    elif args.stats:
        config = load_chaos_config()
        print("Chaos Configuration:")
        print(f"  Enabled: {config.enabled}")
        print(f"  Perturbation Rate: {config.perturbation_rate}")
        print(f"  Noise Amplitude: {config.noise_amplitude}")
        print(f"  Drop Rate: {config.drop_rate}")
    
    else:
        parser.print_help()