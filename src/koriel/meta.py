"""Meta-module for self-modification logic.

This module contains the meta-level consciousness operations that
allow the system to modify its own behavior and structure.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class ModificationEvent:
    """Record of a self-modification event."""
    timestamp: float
    modification_type: str
    parameters_changed: Dict[str, Any]
    reason: str
    success: bool

class SelfModificationEngine:
    """Engine for controlled self-modification of consciousness parameters."""
    
    def __init__(self, safety_threshold: float = 0.1):
        self.safety_threshold = safety_threshold
        self.modification_history: List[ModificationEvent] = []
        self.allowed_modifications = {
            'field_parameters': self._modify_field_parameters,
            'evolution_rate': self._modify_evolution_rate,
            'observation_frequency': self._modify_observation_frequency
        }
        
    def propose_modification(self, field_state: Dict[str, Any], 
                           performance_metrics: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """Propose a modification based on current field state and performance."""
        
        # Simple heuristic: if energy is too high, reduce evolution rate
        if performance_metrics.get('energy', 0) > 1.5:
            return {
                'type': 'evolution_rate',
                'change': -0.1,
                'reason': 'High energy detected, reducing evolution rate'
            }
            
        # If complexity is stagnating, increase observation frequency  
        if performance_metrics.get('complexity_change', 0) < 0.01:
            return {
                'type': 'observation_frequency', 
                'change': 0.1,
                'reason': 'Low complexity change, increasing observation frequency'
            }
            
        return None
        
    def apply_modification(self, modification: Dict[str, Any], 
                         target_object: Any) -> bool:
        """Apply a proposed modification with safety checks."""
        
        mod_type = modification.get('type')
        if mod_type not in self.allowed_modifications:
            return False
            
        # Safety check: don't make changes larger than threshold
        change = modification.get('change', 0)
        if abs(change) > self.safety_threshold:
            return False
            
        try:
            success = self.allowed_modifications[mod_type](modification, target_object)
            
            event = ModificationEvent(
                timestamp=np.random.random(),  # placeholder
                modification_type=mod_type,
                parameters_changed=modification,
                reason=modification.get('reason', 'No reason provided'),
                success=success
            )
            self.modification_history.append(event)
            
            return success
            
        except Exception:
            return False
            
    def _modify_field_parameters(self, modification: Dict[str, Any], target: Any) -> bool:
        """Modify field-level parameters."""
        # Implementation depends on target field structure
        return True
        
    def _modify_evolution_rate(self, modification: Dict[str, Any], target: Any) -> bool:
        """Modify evolution rate parameters."""
        if hasattr(target, 'dt'):
            current_dt = target.dt
            new_dt = current_dt + modification.get('change', 0)
            if 0.0001 < new_dt < 0.01:  # Safety bounds
                target.dt = new_dt
                return True
        return False
        
    def _modify_observation_frequency(self, modification: Dict[str, Any], target: Any) -> bool:
        """Modify observation frequency parameters."""
        # Implementation would depend on how observation frequency is controlled
        return True
        
    def get_modification_summary(self) -> Dict[str, Any]:
        """Get summary of all modifications made."""
        total_mods = len(self.modification_history)
        successful_mods = sum(1 for mod in self.modification_history if mod.success)
        
        mod_types = defaultdict(int)
        for mod in self.modification_history:
            mod_types[mod.modification_type] += 1
            
        return {
            'total_modifications': total_mods,
            'successful_modifications': successful_mods,
            'success_rate': successful_mods / max(total_mods, 1),
            'modification_types': dict(mod_types),
            'recent_modifications': self.modification_history[-5:] if self.modification_history else []
        }

class MetaConsciousnessMonitor:
    """Monitor for meta-level consciousness processes."""
    
    def __init__(self):
        self.meta_observations = []
        self.recursion_depth = 0
        self.max_recursion_depth = 10
        
    def observe_observation(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Meta-observation: observe the act of observing."""
        self.recursion_depth += 1
        
        if self.recursion_depth > self.max_recursion_depth:
            # Prevent infinite recursion
            self.recursion_depth -= 1
            return {'meta_observation': 'recursion_limited'}
            
        meta_obs = {
            'observation_timestamp': observation.get('timestamp', 0),
            'observation_complexity': len(str(observation)),
            'recursion_depth': self.recursion_depth,
            'meta_patterns': self._detect_meta_patterns(observation)
        }
        
        self.meta_observations.append(meta_obs)
        self.recursion_depth -= 1
        
        return meta_obs
        
    def _detect_meta_patterns(self, observation: Dict[str, Any]) -> List[str]:
        """Detect patterns in the observation itself."""
        patterns = []
        
        # Simple pattern detection
        if 'energy' in observation and observation.get('energy', 0) > 1.0:
            patterns.append('high_energy_observation')
            
        if 'complexity' in observation and observation.get('complexity', 0) > 2.0:
            patterns.append('complex_observation')
            
        return patterns