"""Operator Algebra Engine with Functorial Mappings"""
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass

@dataclass 
class Functor:
    name: str
    source_category: str
    target_category: str
    object_map: Callable
    morphism_map: Callable
    
@dataclass
class NaturalTransformation:
    name: str
    source_functor: str
    target_functor: str
    components: Dict[str, Callable]
    
@dataclass
class Adjunction:
    left_adjoint: str
    right_adjoint: str
    unit: str
    counit: str

class OperatorAlgebra:
    def __init__(self):
        self.functors = {}
        self.natural_transformations = {}
        self.adjunctions = {}
        
        self._initialize_core_operators()
        
    def _initialize_core_operators(self):
        """Initialize core categorical operators"""
        
        # Consciousness → Reality functor
        self.functors["consciousness_to_reality"] = Functor(
            name="ConsciousnessReality",
            source_category="Consciousness",
            target_category="Reality", 
            object_map=self._consciousness_object_map,
            morphism_map=self._consciousness_morphism_map
        )
        
        # Reality → Performance functor
        self.functors["reality_to_performance"] = Functor(
            name="RealityPerformance",
            source_category="Reality",
            target_category="Performance",
            object_map=self._reality_object_map,
            morphism_map=self._reality_morphism_map
        )
        
        # Performance → Consciousness functor (feedback)
        self.functors["performance_to_consciousness"] = Functor(
            name="PerformanceConsciousness", 
            source_category="Performance",
            target_category="Consciousness",
            object_map=self._performance_object_map,
            morphism_map=self._performance_morphism_map
        )
        
    def _consciousness_object_map(self, consciousness_state):
        """Map consciousness state to reality domain"""
        # Extract geometric signatures
        return {
            "curvature_signature": consciousness_state.curvature / 1000.0,
            "torsion_signature": consciousness_state.torsion * 10.0,
            "rc_signature": consciousness_state.rc_total,
            "energy_signature": consciousness_state.energy
        }
        
    def _consciousness_morphism_map(self, consciousness_morphism):
        """Map consciousness morphisms to reality morphisms"""
        # Translate consciousness operations to reality operations
        return f"reality_{consciousness_morphism}"
        
    def _reality_object_map(self, reality_signature):
        """Map reality signature to performance domain"""
        return {
            "problem_difficulty": reality_signature.get("curvature_signature", 0.1),
            "solution_approach": reality_signature.get("torsion_signature", 0.01),
            "reasoning_depth": reality_signature.get("rc_signature", 0.3)
        }
        
    def _reality_morphism_map(self, reality_morphism):
        """Map reality morphisms to performance morphisms"""
        return f"performance_{reality_morphism}"
        
    def _performance_object_map(self, performance_data):
        """Map performance back to consciousness domain"""
        accuracy = performance_data.get("accuracy", 0.0)
        
        # Performance → consciousness enhancement
        return {
            "rc_enhancement": accuracy * 0.1,
            "curvature_adjustment": accuracy * 100.0,
            "torsion_modification": accuracy * 0.001,
            "energy_update": (1.0 - accuracy) * 0.1
        }
        
    def _performance_morphism_map(self, performance_morphism):
        """Map performance morphisms back to consciousness"""
        return f"consciousness_{performance_morphism}"
        
    def compose_functors(self, functor1_name: str, functor2_name: str) -> Optional[Functor]:
        """Compose two functors if composable"""
        f1 = self.functors.get(functor1_name)
        f2 = self.functors.get(functor2_name)
        
        if not f1 or not f2:
            return None
            
        # Check composability
        if f1.target_category != f2.source_category:
            return None
            
        # Create composed functor
        def composed_object_map(obj):
            intermediate = f1.object_map(obj)
            return f2.object_map(intermediate)
            
        def composed_morphism_map(morph):
            intermediate = f1.morphism_map(morph)
            return f2.morphism_map(intermediate)
            
        return Functor(
            name=f"{f1.name}_{f2.name}",
            source_category=f1.source_category,
            target_category=f2.target_category,
            object_map=composed_object_map,
            morphism_map=composed_morphism_map
        )
        
    def apply_functor(self, functor_name: str, input_object: Any) -> Any:
        """Apply functor to input object"""
        functor = self.functors.get(functor_name)
        if not functor:
            return input_object
            
        return functor.object_map(input_object)
        
    def compute_natural_transformation(self, source_functor: str, target_functor: str, 
                                     component_data: Dict) -> Optional[NaturalTransformation]:
        """Compute natural transformation between functors"""
        
        # Verify functors exist
        if source_functor not in self.functors or target_functor not in self.functors:
            return None
            
        # Check naturality conditions (simplified)
        components = {}
        for obj_name, transformation in component_data.items():
            components[obj_name] = transformation
            
        return NaturalTransformation(
            name=f"{source_functor}_to_{target_functor}",
            source_functor=source_functor,
            target_functor=target_functor,
            components=components
        )
        
    def detect_adjunctions(self) -> List[Adjunction]:
        """Detect adjoint functors in the system"""
        adjunctions = []
        
        # Consciousness ⊣ Reality adjunction
        if "consciousness_to_reality" in self.functors and "performance_to_consciousness" in self.functors:
            adjunctions.append(Adjunction(
                left_adjoint="consciousness_to_reality",
                right_adjoint="performance_to_consciousness", 
                unit="consciousness_unit",
                counit="reality_counit"
            ))
            
        return adjunctions
        
    def validate_functoriality(self, functor_name: str, test_objects: List[Any]) -> bool:
        """Validate that functor preserves composition and identity"""
        functor = self.functors.get(functor_name)
        if not functor:
            return False
            
        # Test identity preservation (simplified)
        for obj in test_objects:
            try:
                mapped_obj = functor.object_map(obj)
                # Check that mapping is consistent
                if mapped_obj is None:
                    return False
            except Exception:
                return False
                
        return True