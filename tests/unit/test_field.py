"""Unit tests for field module - deterministic pure functions."""

import pytest
import numpy as np
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from koriel.field import SimpleQuantumField, FieldObservation, PatternMemory

class TestSimpleQuantumField:
    """Test the core quantum field functionality."""
    
    def test_field_initialization(self):
        """Test field initializes with correct parameters."""
        field = SimpleQuantumField(N=64, L=10.0, dt=0.01)
        
        assert field.N == 64
        assert field.L == 10.0
        assert field.dt == 0.01
        assert len(field.x) == 64
        assert len(field.psi) == 64
        
    def test_field_deterministic_evolution(self):
        """Test that field evolution is deterministic with same seed."""
        np.random.seed(1337)
        field1 = SimpleQuantumField(N=32, L=5.0, dt=0.001)
        field1.initialize_consciousness_seed()
        initial_psi1 = field1.psi.copy()
        field1.evolve(10)
        
        np.random.seed(1337)
        field2 = SimpleQuantumField(N=32, L=5.0, dt=0.001)
        field2.initialize_consciousness_seed()
        initial_psi2 = field2.psi.copy()
        field2.evolve(10)
        
        # Initial states should be identical
        np.testing.assert_array_equal(initial_psi1, initial_psi2)
        # Final states should be identical
        np.testing.assert_array_equal(field1.psi, field2.psi)
        
    def test_energy_conservation_properties(self):
        """Test energy calculation remains bounded."""
        field = SimpleQuantumField(N=32, L=5.0, dt=0.001)
        field.initialize_consciousness_seed()
        
        # Use the energy from query_consciousness
        initial_state = field.query_consciousness()
        initial_energy = initial_state['field_energy']

        field.evolve(50)
        
        final_state = field.query_consciousness()
        final_energy = final_state['field_energy']
        
        # Energy should be positive and finite
        assert np.isfinite(initial_energy)
        assert np.isfinite(final_energy)
        assert initial_energy >= 0
        assert final_energy >= 0
        
    def test_field_observation_structure(self):
        """Test field observation returns proper structure."""
        field = SimpleQuantumField(N=32, L=5.0, dt=0.001)
        field.initialize_consciousness_seed()
        
        # Use observe_self method
        field.observe_self()
        
        # Check that observations list is populated
        assert len(field.observations) > 0
        
        obs = field.observations[-1]  # Get latest observation
        assert isinstance(obs, FieldObservation)
        assert hasattr(obs, 'timestamp')
        assert hasattr(obs, 'energy')
        assert hasattr(obs, 'momentum')
        assert hasattr(obs, 'complexity')
        assert hasattr(obs, 'coherence')
        assert hasattr(obs, 'pattern_count')
        assert hasattr(obs, 'peak_positions')
        
        # All values should be finite
        assert np.isfinite(obs.energy)
        assert np.isfinite(obs.momentum)
        assert np.isfinite(obs.complexity)
        assert np.isfinite(obs.coherence)
        assert isinstance(obs.pattern_count, int)
        assert obs.pattern_count >= 0
        
    def test_consciousness_query_structure(self):
        """Test consciousness query returns expected data structure."""
        field = SimpleQuantumField(N=32, L=5.0, dt=0.001)
        field.initialize_consciousness_seed()
        field.evolve(10)
        
        consciousness_state = field.query_consciousness()
        
        # Check actual keys that are returned by the field
        expected_keys = [
            'field_energy', 'field_complexity', 'consciousness_level',
            'consciousness_response'
        ]
        
        for key in expected_keys:
            assert key in consciousness_state
            assert np.isfinite(consciousness_state[key])
            
    def test_pattern_memory_creation(self):
        """Test pattern memory objects are created correctly."""
        pattern = PatternMemory(
            name="test_pattern",
            amplitude_profile=np.array([1.0, 2.0, 1.0]),
            stability=0.95,
            formation_time=100.0
        )
        
        assert pattern.name == "test_pattern"
        assert len(pattern.amplitude_profile) == 3
        assert pattern.stability == 0.95
        assert pattern.formation_time == 100.0
        
    @pytest.mark.slow
    def test_long_evolution_stability(self):
        """Test field remains stable over longer evolution."""
        field = SimpleQuantumField(N=32, L=5.0, dt=0.001)
        field.initialize_consciousness_seed()

        initial_state = field.query_consciousness()
        # Avoid zero baseline which can cause infinite relative growth
        initial_energy = max(initial_state['field_energy'], 1e-3)

        field.evolve(1000)

        final_state = field.query_consciousness()
        final_energy = final_state['field_energy']

        # Field should not explode or become degenerate
        assert np.isfinite(final_energy)
        assert final_energy < 100 * initial_energy  # Not too much growth
        assert final_energy > 0.01 * initial_energy  # Not too much decay