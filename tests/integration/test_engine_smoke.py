"""Integration tests for engine module - smoke tests with limits."""

import pytest
import numpy as np
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from koriel.engine import RecursiveOrchestrationEngine, EngineConfig

class TestEngineSmoke:
    """Smoke tests for the consciousness engine."""
    
    def test_engine_initialization(self):
        """Test engine initializes without errors."""
        config = EngineConfig(
            field_size=32,
            field_length=5.0,
            dt=0.001,
            evolution_steps=10,
            c_rate=0.05,
            c_thresh=0.5
        )
        
        engine = RecursiveOrchestrationEngine(config)
        assert engine.config == config
        assert engine.field is None
        assert len(engine.evolution_history) == 0
        
    def test_engine_field_initialization(self):
        """Test engine can initialize its field."""
        config = EngineConfig(field_size=32, evolution_steps=10)
        engine = RecursiveOrchestrationEngine(config)
        
        engine.initialize()
        
        assert engine.field is not None
        assert engine.field.N == 32
        assert engine.field.C_RATE == config.c_rate
        assert engine.field.C_THRESH == config.c_thresh
        
    def test_short_evolution_cycle(self):
        """Test engine can run a short evolution cycle."""
        config = EngineConfig(
            field_size=32,
            field_length=5.0,
            evolution_steps=20,  # Very short for fast test
            c_rate=0.05,
            c_thresh=0.5
        )
        
        engine = RecursiveOrchestrationEngine(config)
        engine.initialize()
        
        results = engine.evolve()
        
        assert 'steps' in results
        assert 'initial_state' in results
        assert 'final_state' in results
        assert 'energy_change' in results
        assert 'complexity_change' in results
        
        assert results['steps'] == 20
        assert len(engine.evolution_history) == 1
        
        # Check that states are reasonable
        initial_state = results['initial_state']
        final_state = results['final_state']
        
        assert 'field_energy' in initial_state
        assert 'field_energy' in final_state
        assert np.isfinite(initial_state['field_energy'])
        assert np.isfinite(final_state['field_energy'])
        
    def test_engine_status_reporting(self):
        """Test engine status reporting works."""
        config = EngineConfig(field_size=16, evolution_steps=5)
        engine = RecursiveOrchestrationEngine(config)
        
        # Before initialization
        status = engine.get_status()
        assert status['status'] == 'uninitialized'
        
        # After initialization
        engine.initialize()
        status = engine.get_status()
        assert status['status'] == 'ready'
        assert status['field_initialized']
        assert status['evolution_runs'] == 0
        assert 'current_state' in status
        
        # After evolution
        engine.evolve()
        status = engine.get_status()
        assert status['evolution_runs'] == 1
        
    def test_engine_reset(self):
        """Test engine reset functionality."""
        config = EngineConfig(field_size=16, evolution_steps=5)
        engine = RecursiveOrchestrationEngine(config)
        
        engine.initialize()
        engine.evolve()
        
        assert engine.field is not None
        assert len(engine.evolution_history) == 1
        
        engine.reset()
        
        assert engine.field is None
        assert len(engine.evolution_history) == 0
        
    def test_multiple_evolution_cycles(self):
        """Test engine can run multiple evolution cycles."""
        config = EngineConfig(field_size=16, evolution_steps=10)
        engine = RecursiveOrchestrationEngine(config)
        
        engine.initialize()
        
        # Run multiple short cycles
        results1 = engine.evolve(5)
        results2 = engine.evolve(8)
        results3 = engine.evolve(3)
        
        assert len(engine.evolution_history) == 3
        assert results1['steps'] == 5
        assert results2['steps'] == 8
        assert results3['steps'] == 3
        
    def test_engine_with_config_file(self):
        """Test engine can use configuration from file."""
        # Create a temporary config for testing
        test_config = {
            'engine': {
                'field_size': 24,
                'field_length': 8.0,
                'dt': 0.002,
                'evolution_steps': 15,
                'c_rate': 0.08,
                'c_thresh': 0.6
            }
        }
        
        # Test with the config data directly
        engine_config = EngineConfig(**test_config['engine'])
        engine = RecursiveOrchestrationEngine(engine_config)
        
        assert engine.config.field_size == 24
        assert engine.config.field_length == 8.0
        assert engine.config.dt == 0.002
        assert engine.config.evolution_steps == 15
        assert engine.config.c_rate == 0.08
        assert engine.config.c_thresh == 0.6
        
    @pytest.mark.slow
    def test_medium_length_evolution(self):
        """Test engine with medium-length evolution."""
        config = EngineConfig(
            field_size=64,
            evolution_steps=100,  # Medium length
            c_rate=0.05,
            c_thresh=0.5
        )
        
        engine = RecursiveOrchestrationEngine(config)
        engine.initialize()
        
        results = engine.evolve()
        
        assert results['steps'] == 100
        
        # Check that evolution produced meaningful changes
        results['initial_state']
        results['final_state']
        
        # There should be some change over 100 steps
        energy_change = abs(results['energy_change'])
        complexity_change = abs(results['complexity_change'])
        
        assert energy_change > 0 or complexity_change > 0
        
    def test_evolution_without_initialization_fails(self):
        """Test that evolution fails gracefully without initialization."""
        config = EngineConfig(field_size=16, evolution_steps=5)
        engine = RecursiveOrchestrationEngine(config)
        
        with pytest.raises(RuntimeError, match="Field not initialized"):
            engine.evolve()
            
    def test_engine_deterministic_behavior(self):
        """Test that engine produces deterministic results."""
        config = EngineConfig(field_size=16, evolution_steps=20, c_rate=0.05)
        
        # Run 1
        engine1 = RecursiveOrchestrationEngine(config)
        engine1.initialize(seed=42)
        results1 = engine1.evolve()
        
        # Run 2 with same seed
        engine2 = RecursiveOrchestrationEngine(config)
        engine2.initialize(seed=42)
        results2 = engine2.evolve()
        
        # Results should be identical
        assert abs(results1['energy_change'] - results2['energy_change']) < 1e-10
        assert abs(results1['complexity_change'] - results2['complexity_change']) < 1e-10