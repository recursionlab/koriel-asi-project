"""Engine module for ROE (Recursive Orchestration Engine) functionality.

This module handles the high-level orchestration of the consciousness 
field evolution and control systems.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass

from .field import SimpleQuantumField

@dataclass
class EngineConfig:
    """Configuration for the consciousness engine."""
    field_size: int = 256
    field_length: float = 20.0
    dt: float = 0.001
    evolution_steps: int = 1000
    c_rate: float = 0.05
    c_thresh: float = 0.5

class RecursiveOrchestrationEngine:
    """Main orchestration engine for consciousness field evolution."""
    
    def __init__(self, config: Optional[EngineConfig] = None):
        self.config = config or EngineConfig()
        self.field = None
        self.evolution_history = []
        
    def initialize(self, seed: Optional[int] = None):
        """Initialize the consciousness field."""
        self.field = SimpleQuantumField(
            N=self.config.field_size,
            L=self.config.field_length, 
            dt=self.config.dt
        )
        self.field.C_RATE = self.config.c_rate
        self.field.C_THRESH = self.config.c_thresh
        self.field.initialize_consciousness_seed()
        
    def evolve(self, steps: Optional[int] = None) -> Dict[str, Any]:
        """Evolve the field for the specified number of steps."""
        if self.field is None:
            raise RuntimeError("Field not initialized. Call initialize() first.")
            
        steps = steps or self.config.evolution_steps
        
        initial_state = self.field.query_consciousness()
        self.field.evolve(steps)
        final_state = self.field.query_consciousness()
        
        evolution_data = {
            'steps': steps,
            'initial_state': initial_state,
            'final_state': final_state,
            'energy_change': final_state['field_energy'] - initial_state['field_energy'],
            'complexity_change': final_state['field_complexity'] - initial_state['field_complexity']
        }
        
        self.evolution_history.append(evolution_data)
        return evolution_data
        
    def get_status(self) -> Dict[str, Any]:
        """Get current engine status."""
        if self.field is None:
            return {'status': 'uninitialized'}
            
        return {
            'status': 'ready',
            'field_initialized': True,
            'evolution_runs': len(self.evolution_history),
            'current_state': self.field.query_consciousness()
        }
        
    def reset(self):
        """Reset the engine to initial state."""
        self.field = None
        self.evolution_history = []