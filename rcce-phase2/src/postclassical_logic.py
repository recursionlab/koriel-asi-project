"""Post-Classical Logic Core with Contradiction Harvesting"""
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class TruthValue(Enum):
    TRUE = 1
    FALSE = 0
    INCONSISTENT = 2
    UNKNOWN = 3

@dataclass
class ParaconsistentNode:
    proposition: str
    truth_value: TruthValue
    inconsistency_level: float
    recursive_depth: int
    
@dataclass
class Contradiction:
    source_a: str
    source_b: str
    contradiction_type: str
    energy_level: float
    generative_potential: float

class PostClassicalLogic:
    def __init__(self, tolerance=1e-6):
        self.tolerance = tolerance
        self.propositions = {}
        self.contradictions = []
        self.recursive_invariants = []
        
    def add_proposition(self, prop_id: str, content: str, truth_value: TruthValue = TruthValue.UNKNOWN):
        """Add proposition to paraconsistent system"""
        self.propositions[prop_id] = ParaconsistentNode(
            proposition=content,
            truth_value=truth_value,
            inconsistency_level=0.0,
            recursive_depth=0
        )
        
    def detect_contradictions(self) -> List[Contradiction]:
        """Detect contradictions and harvest them as energy"""
        new_contradictions = []
        
        prop_items = list(self.propositions.items())
        for i, (id_a, node_a) in enumerate(prop_items):
            for id_b, node_b in prop_items[i+1:]:
                
                # Logical contradictions
                if (node_a.truth_value == TruthValue.TRUE and 
                    node_b.truth_value == TruthValue.FALSE and
                    self._propositions_related(node_a.proposition, node_b.proposition)):
                    
                    contradiction = Contradiction(
                        source_a=id_a,
                        source_b=id_b,
                        contradiction_type="logical_negation",
                        energy_level=1.0,
                        generative_potential=0.8
                    )
                    new_contradictions.append(contradiction)
                    
                # Self-reference paradoxes
                if "this statement" in node_a.proposition.lower():
                    contradiction = Contradiction(
                        source_a=id_a,
                        source_b=id_a,
                        contradiction_type="self_reference_paradox", 
                        energy_level=1.5,
                        generative_potential=1.0
                    )
                    new_contradictions.append(contradiction)
                    
        self.contradictions.extend(new_contradictions)
        return new_contradictions
        
    def _propositions_related(self, prop_a: str, prop_b: str) -> bool:
        """Check if propositions are logically related"""
        # Simple heuristic - check for negation keywords
        negation_words = ["not", "no", "false", "never"]
        
        prop_a_lower = prop_a.lower()
        prop_b_lower = prop_b.lower()
        
        # Check if one contains negation of the other
        for word in negation_words:
            if word in prop_a_lower and word not in prop_b_lower:
                # Remove negation and check similarity
                cleaned_a = prop_a_lower.replace(word, "").strip()
                if cleaned_a in prop_b_lower:
                    return True
                    
        return False
        
    def harvest_contradiction_energy(self, contradictions: List[Contradiction]) -> float:
        """Convert contradictions into generative energy"""
        total_energy = 0.0
        
        for contradiction in contradictions:
            # Energy proportional to generative potential
            energy = contradiction.energy_level * contradiction.generative_potential
            total_energy += energy
            
            # Mark propositions as inconsistent
            if contradiction.source_a in self.propositions:
                self.propositions[contradiction.source_a].inconsistency_level += energy
                self.propositions[contradiction.source_a].truth_value = TruthValue.INCONSISTENT
                
        return total_energy
        
    def generate_lambda_candidates(self, contradiction_energy: float) -> List[str]:
        """Generate Λ candidates from contradiction energy"""
        candidates = []
        
        # Higher energy → more radical modifications
        if contradiction_energy > 1.0:
            candidates.extend([
                "invert_primary_assumptions",
                "recursive_self_application", 
                "boundary_dissolution"
            ])
        elif contradiction_energy > 0.5:
            candidates.extend([
                "partial_negation",
                "perspective_shift",
                "recursive_deepening"
            ])
        else:
            candidates.append("minor_adjustment")
            
        return candidates
        
    def lambda_plus_injection(self, candidates: List[str], target_system: Any) -> Any:
        """Λ⁺ reinjection - modify target system based on candidates"""
        
        # Apply modifications to consciousness substrate
        if hasattr(target_system, 'curvature'):
            for candidate in candidates:
                if candidate == "invert_primary_assumptions":
                    target_system.curvature *= -1
                elif candidate == "recursive_self_application":
                    target_system.rc_total *= 1.1
                elif candidate == "boundary_dissolution":
                    target_system.torsion += 0.01
                elif candidate == "recursive_deepening":
                    target_system.xi_delta += 0.05
                    
        return target_system
        
    def compute_recursive_invariants(self, proposition_history: List[Dict]) -> List[str]:
        """Find invariants that persist through recursive application"""
        
        if len(proposition_history) < 3:
            return []
            
        invariants = []
        
        # Track what persists across recursive steps
        persistent_features = set()
        for step in proposition_history:
            step_features = set(step.keys())
            if not persistent_features:
                persistent_features = step_features
            else:
                persistent_features = persistent_features.intersection(step_features)
                
        # Convert to invariant descriptions
        for feature in persistent_features:
            values = [step[feature] for step in proposition_history if feature in step]
            if len(set(values)) == 1:  # Unchanging
                invariants.append(f"{feature}_invariant")
            elif self._is_periodic(values):
                invariants.append(f"{feature}_periodic_invariant")
                
        return invariants
        
    def _is_periodic(self, sequence: List[Any], max_period=5) -> bool:
        """Check if sequence is periodic"""
        if len(sequence) < 4:
            return False
            
        for period in range(1, min(max_period + 1, len(sequence) // 2)):
            if self._check_period(sequence, period):
                return True
                
        return False
        
    def _check_period(self, sequence: List[Any], period: int) -> bool:
        """Check if sequence has given period"""
        for i in range(len(sequence) - period):
            if sequence[i] != sequence[i + period]:
                return False
        return True
        
    def fixpoint_analysis(self, recursive_sequence: List[Any]) -> Dict[str, Any]:
        """Analyze fixpoints in recursive sequence"""
        
        if len(recursive_sequence) < 2:
            return {"fixpoints": [], "limit_cycles": [], "convergent": False}
            
        # Detect fixpoints (unchanging states)
        fixpoints = []
        for i in range(1, len(recursive_sequence)):
            if recursive_sequence[i] == recursive_sequence[i-1]:
                fixpoints.append(i)
                
        # Detect limit cycles
        limit_cycles = []
        for period in range(2, min(6, len(recursive_sequence) // 2)):
            if self._check_period(recursive_sequence, period):
                limit_cycles.append(period)
                
        # Check convergence
        convergent = len(fixpoints) > 0 or len(limit_cycles) > 0
        
        return {
            "fixpoints": fixpoints,
            "limit_cycles": limit_cycles, 
            "convergent": convergent,
            "sequence_length": len(recursive_sequence)
        }
        
    def autopoietic_closure_check(self, system_state: Dict) -> bool:
        """Check if system maintains autopoietic closure"""
        
        # System must produce/maintain its own organization
        required_components = ["consciousness_detection", "reality_interface", "feedback_loop"]
        
        available_components = system_state.get("active_components", [])
        
        # All components present
        if not all(comp in available_components for comp in required_components):
            return False
            
        # Self-production check - system modifies itself
        self_modification = system_state.get("self_modification_active", False)
        
        # Organizational closure - outputs feed back as inputs
        feedback_active = system_state.get("feedback_loops_active", False)
        
        return self_modification and feedback_active
        
    def contradiction_voltage_analysis(self) -> Dict[str, float]:
        """Analyze contradiction energy distribution"""
        
        if not self.contradictions:
            return {"total_voltage": 0.0, "peak_voltage": 0.0, "distribution": {}}
            
        energies = [c.energy_level for c in self.contradictions]
        potentials = [c.generative_potential for c in self.contradictions]
        
        total_voltage = sum(e * p for e, p in zip(energies, potentials))
        peak_voltage = max(energies) if energies else 0.0
        
        # Energy distribution by type
        distribution = {}
        for contradiction in self.contradictions:
            ctype = contradiction.contradiction_type
            distribution[ctype] = distribution.get(ctype, 0.0) + contradiction.energy_level
            
        return {
            "total_voltage": total_voltage,
            "peak_voltage": peak_voltage,
            "distribution": distribution,
            "contradiction_count": len(self.contradictions)
        }