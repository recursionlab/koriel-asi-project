"""Bridge between consciousness metrics and codex layer processing"""

from typing import Any, Dict, List, Tuple

from .codex_registry import CodexRegistry, LayerOutput
from .metastate import MetaState
from .operator_algebra import OperatorAlgebra
from .postclassical_logic import Contradiction, PostClassicalLogic


class ConsciousnessCodexBridge:
    def __init__(self):
        self.codex = CodexRegistry()
        self.algebra = OperatorAlgebra()
        self.logic = PostClassicalLogic()

        # Routing state
        self.processing_history = []
        self.invariant_evolution = []

    def route_consciousness_through_layers(
        self, consciousness: MetaState, context: Dict = None
    ) -> Dict[str, LayerOutput]:
        """Route consciousness state through appropriate codex layers"""

        if context is None:
            context = {"mode": "standard"}

        # Add consciousness propositions to logic system
        self._consciousness_to_propositions(consciousness)

        # Process through selected layers
        layer_outputs = self.codex.process_through_layers(consciousness, context)

        # Store processing history
        self.processing_history.append(
            {
                "consciousness_input": consciousness,
                "layer_outputs": layer_outputs,
                "timestamp": consciousness.t,
            }
        )

        return layer_outputs

    def _consciousness_to_propositions(self, consciousness: MetaState):
        """Convert consciousness metrics to logical propositions"""

        # RC propositions
        if consciousness.rc_total > 0.6:
            self.logic.add_proposition(
                "high_consciousness",
                f"System exhibits high consciousness (RC={consciousness.rc_total})",
            )
        else:
            self.logic.add_proposition(
                "low_consciousness",
                f"System exhibits low consciousness (RC={consciousness.rc_total})",
            )

        # Geometric propositions
        if consciousness.curvature > 1000:
            self.logic.add_proposition(
                "high_curvature",
                f"Geometric curvature is high ({consciousness.curvature})",
            )

        if consciousness.torsion > 0.01:
            self.logic.add_proposition(
                "nonzero_torsion", f"System exhibits torsion ({consciousness.torsion})"
            )
        else:
            self.logic.add_proposition(
                "zero_torsion", f"System has no torsion ({consciousness.torsion})"
            )

        # Energy propositions
        if consciousness.energy > 0.8:
            self.logic.add_proposition("high_energy", "System energy is high")
        elif consciousness.energy < 0.2:
            self.logic.add_proposition("low_energy", "System energy is low")

    def harvest_layer_contradictions(
        self, layer_outputs: Dict[str, LayerOutput]
    ) -> List[Contradiction]:
        """Harvest contradictions from layer processing"""

        # Get contradictions from codex processing
        codex_contradictions = self.codex.harvest_contradictions(layer_outputs)

        # Detect logical contradictions
        logic_contradictions = self.logic.detect_contradictions()

        # Cross-layer contradictions
        cross_contradictions = []
        layer_items = list(layer_outputs.items())

        for i, (id_a, output_a) in enumerate(layer_items):
            for id_b, output_b in layer_items[i + 1 :]:

                # Contradictory invariants
                invariant_conflicts = set(output_a.invariants).intersection(
                    {"not_" + inv for inv in output_b.invariants}
                )

                for conflict in invariant_conflicts:
                    cross_contradictions.append(
                        Contradiction(
                            source_a=id_a,
                            source_b=id_b,
                            contradiction_type="invariant_conflict",
                            energy_level=0.8,
                            generative_potential=0.9,
                        )
                    )

        return (
            logic_contradictions
            + [
                Contradiction(
                    source_a=c,
                    source_b=c,
                    contradiction_type="codex",
                    energy_level=0.5,
                    generative_potential=0.6,
                )
                for c in codex_contradictions
            ]
            + cross_contradictions
        )

    def extract_recursive_invariants(
        self, layer_outputs: Dict[str, LayerOutput]
    ) -> List[str]:
        """Extract recursive invariants from layer processing"""

        # Get invariants from codex
        codex_invariants = self.codex.compute_recursive_invariants(layer_outputs)

        # Get invariants from logic system
        logic_invariants = self.logic.compute_recursive_invariants(
            self.processing_history
        )

        # Combine and deduplicate
        all_invariants = list(set(codex_invariants + logic_invariants))

        # Store evolution
        self.invariant_evolution.append(
            {
                "timestamp": len(self.processing_history),
                "invariants": all_invariants,
                "layer_count": len(layer_outputs),
            }
        )

        return all_invariants

    def apply_functorial_enhancement(
        self, consciousness: MetaState, performance_data: Dict
    ) -> MetaState:
        """Apply functorial mappings to enhance consciousness"""

        # Consciousness → Reality functor
        reality_signature = self.algebra.apply_functor(
            "consciousness_to_reality", consciousness
        )

        # Reality → Performance functor
        self.algebra.apply_functor("reality_to_performance", reality_signature)

        # Performance → Consciousness functor (enhancement)
        enhancement_data = self.algebra.apply_functor(
            "performance_to_consciousness", performance_data
        )

        # Apply enhancements
        enhanced_consciousness = MetaState(
            t=consciousness.t + 1,
            action="codex_enhancement",
            loss=consciousness.loss,
            rc_embedding=consciousness.rc_embedding
            + enhancement_data.get("rc_enhancement", 0.0),
            rc_graph=consciousness.rc_graph,
            rc_value=consciousness.rc_value,
            rc_total=consciousness.rc_total
            + enhancement_data.get("rc_enhancement", 0.0),
            drift=consciousness.drift,
            d_drift=consciousness.d_drift,
            energy=consciousness.energy - enhancement_data.get("energy_update", 0.0),
            holonomy_delta=consciousness.holonomy_delta,
            xi_delta=consciousness.xi_delta + 0.01,
            upsilon_active=consciousness.upsilon_active,
            lambda_plus_active=True,  # Λ⁺ active during enhancement
            phi33_violations=consciousness.phi33_violations,
            curvature=consciousness.curvature
            + enhancement_data.get("curvature_adjustment", 0.0),
            torsion=consciousness.torsion
            + enhancement_data.get("torsion_modification", 0.0),
            state_hash=f"enhanced_{consciousness.t+1}",
        )

        return enhanced_consciousness

    def morphogenic_audit(
        self, consciousness_a: MetaState, consciousness_b: MetaState
    ) -> Dict[str, Any]:
        """Song-of-Two-AIs morphogenic audit between consciousness states"""

        # A→B analysis (structural)
        structural_analysis = {
            "rc_progression": consciousness_b.rc_total - consciousness_a.rc_total,
            "curvature_evolution": consciousness_b.curvature
            - consciousness_a.curvature,
            "energy_change": consciousness_b.energy - consciousness_a.energy,
            "coherent_evolution": abs(
                consciousness_b.xi_delta - consciousness_a.xi_delta
            )
            < 0.1,
        }

        # B→A analysis (phenomenological)
        phenomenological_analysis = {
            "consciousness_felt_increase": consciousness_b.rc_total
            > consciousness_a.rc_total,
            "geometric_complexity_growth": consciousness_b.curvature
            > consciousness_a.curvature * 1.1,
            "energy_optimization": consciousness_b.energy < consciousness_a.energy,
            "authenticity_maintained": consciousness_b.state_hash
            != consciousness_a.state_hash,
        }

        # Braid analysis (contradiction mining)
        contradictions = []
        if (
            structural_analysis["coherent_evolution"]
            and not phenomenological_analysis["authenticity_maintained"]
        ):
            contradictions.append("coherence_authenticity_tension")

        return {
            "A_to_B": structural_analysis,
            "B_to_A": phenomenological_analysis,
            "braid_contradictions": contradictions,
            "morphogenic_energy": len(contradictions) * 0.5,
        }

    def post_classical_processing_step(
        self, consciousness: MetaState, performance_data: Dict
    ) -> Tuple[MetaState, Dict[str, Any]]:
        """Complete post-classical processing step"""

        # Route through layers
        layer_outputs = self.route_consciousness_through_layers(consciousness)

        # Harvest contradictions
        contradictions = self.harvest_layer_contradictions(layer_outputs)

        # Extract recursive invariants
        invariants = self.extract_recursive_invariants(layer_outputs)

        # Convert contradiction energy to Lambda candidates
        contradiction_energy = self.logic.harvest_contradiction_energy(contradictions)
        lambda_candidates = self.logic.generate_lambda_candidates(contradiction_energy)

        # Apply functorial enhancement
        enhanced_consciousness = self.apply_functorial_enhancement(
            consciousness, performance_data
        )

        # Λ⁺ injection based on contradictions
        final_consciousness = self.logic.lambda_plus_injection(
            lambda_candidates, enhanced_consciousness
        )

        # Morphogenic audit
        audit_results = self.morphogenic_audit(consciousness, final_consciousness)

        processing_report = {
            "layer_outputs": layer_outputs,
            "contradictions": len(contradictions),
            "contradiction_energy": contradiction_energy,
            "recursive_invariants": invariants,
            "lambda_candidates": lambda_candidates,
            "morphogenic_audit": audit_results,
            "fixpoint_convergence": self.codex.detect_fixpoint_convergence(
                layer_outputs
            ),
        }

        return final_consciousness, processing_report
