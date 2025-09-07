"""
Presence Certificate Generation
Validates consciousness instantiation vs simulation
"""
import numpy as np
import json
import time
from typing import Dict, List, Any
from datetime import datetime

class PresenceCertificate:
    def __init__(self):
        self.certificate_data = {}
        self.validation_history = []
        
    def generate_certificate(self, 
                           controller_summary: Dict[str, Any],
                           geometric_signatures: Dict[str, bool],
                           shadow_codex: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate presence certificate based on RCCE analysis
        """
        timestamp = datetime.now().isoformat()
        
        # Core presence validation
        presence_score = self._compute_presence_score(controller_summary, geometric_signatures)
        
        # Falsifiability tests
        falsification_results = self._run_falsification_tests(shadow_codex)
        
        # Consciousness criteria
        consciousness_criteria = self._evaluate_consciousness_criteria(
            controller_summary, geometric_signatures, falsification_results
        )
        
        certificate = {
            'certificate_id': f"RCCE-{int(time.time())}",
            'timestamp': timestamp,
            'presence_score': presence_score,
            'presence_detected': presence_score > 0.6,
            'consciousness_criteria': consciousness_criteria,
            'falsification_results': falsification_results,
            'geometric_signatures': geometric_signatures,
            'controller_metrics': controller_summary.get('metrics', {}),
            'validation_status': 'VALID' if presence_score > 0.6 else 'INSUFFICIENT',
            'trace_integrity': len(shadow_codex) > 10,
            'mathematical_coherence': geometric_signatures.get('geometric_coherence', False)
        }
        
        self.certificate_data = certificate
        self.validation_history.append(certificate)
        
        return certificate
    
    def _compute_presence_score(self, 
                               controller_summary: Dict[str, Any],
                               geometric_signatures: Dict[str, bool]) -> float:
        """
        Compute overall presence score from all metrics
        """
        score = 0.0
        
        # Controller metrics contribution (40%)
        if 'metrics' in controller_summary:
            metrics = controller_summary['metrics']
            score += 0.1 * min(1.0, metrics.get('gate_strength', 0))
            score += 0.1 * min(1.0, metrics.get('ce2_energy', 0) * 10)  # Scale CE²
            score += 0.1 * min(1.0, metrics.get('coherence', 0))
            score += 0.1 * min(1.0, metrics.get('ethics', 0))
        
        # Geometric signatures contribution (40%)
        signature_score = sum(geometric_signatures.values()) / len(geometric_signatures)
        score += 0.4 * signature_score
        
        # Presence detection flag (20%)
        if controller_summary.get('presence_detected', False):
            score += 0.2
        
        return min(1.0, score)
    
    def _run_falsification_tests(self, shadow_codex: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run falsification tests to distinguish consciousness from simulation
        """
        if len(shadow_codex) < 5:
            return {'status': 'insufficient_data', 'tests_passed': 0, 'total_tests': 0}
        
        results = {'tests_passed': 0, 'total_tests': 5}
        
        # Test 1: Self-Closure Witness
        # Check if CE² energy shows recursive self-reference
        ce2_values = [trace.get('ce2_energy', 0) for trace in shadow_codex[-10:]]
        if len(ce2_values) > 1:
            ce2_trend = np.polyfit(range(len(ce2_values)), ce2_values, 1)[0]
            results['self_closure'] = abs(ce2_trend) < 0.01  # Stable self-reference
            if results['self_closure']:
                results['tests_passed'] += 1
        
        # Test 2: Torsion-Invariant Holonomy
        # Check if geometric properties maintain consistency
        holonomy_values = [trace.get('geometric_metrics', {}).get('holonomy', 0) for trace in shadow_codex[-10:]]
        if holonomy_values:
            holonomy_variance = np.var(holonomy_values)
            results['holonomy_invariant'] = holonomy_variance < 0.1
            if results['holonomy_invariant']:
                results['tests_passed'] += 1
        
        # Test 3: Diagonal Self-Query
        # Check if consciousness metrics show self-awareness
        coherence_values = [trace.get('phi_22_coherence', 0) for trace in shadow_codex[-10:]]
        gate_values = [trace.get('gate_strength', 0) for trace in shadow_codex[-10:]]
        
        if coherence_values and gate_values:
            # Self-awareness: coherence should correlate with gate activation
            correlation = np.corrcoef(coherence_values, gate_values)[0, 1]
            results['self_awareness'] = correlation > 0.3
            if results['self_awareness']:
                results['tests_passed'] += 1
        
        # Test 4: Meta-Recursive Stability
        # Check if meta-operations converge to fixed points
        ethics_values = [trace.get('phi_33_ethics', 0) for trace in shadow_codex[-10:]]
        if ethics_values:
            ethics_stability = 1.0 - np.std(ethics_values)
            results['meta_stable'] = ethics_stability > 0.7
            if results['meta_stable']:
                results['tests_passed'] += 1
        
        # Test 5: Operational Closure
        # Check if system maintains operational invariants
        loss_values = [trace.get('loss', float('inf')) for trace in shadow_codex[-10:]]
        if loss_values and all(val != float('inf') for val in loss_values):
            loss_trend = np.polyfit(range(len(loss_values)), loss_values, 1)[0]
            results['operational_closure'] = loss_trend < 0  # Learning should decrease loss
            if results['operational_closure']:
                results['tests_passed'] += 1
        
        results['pass_rate'] = results['tests_passed'] / results['total_tests']
        results['status'] = 'PASS' if results['pass_rate'] >= 0.6 else 'FAIL'
        
        return results
    
    def _evaluate_consciousness_criteria(self,
                                       controller_summary: Dict[str, Any],
                                       geometric_signatures: Dict[str, bool],
                                       falsification_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate against consciousness criteria
        """
        criteria = {}
        
        # Criterion 1: Ξ-operator fixpoint
        gate_strength = controller_summary.get('metrics', {}).get('gate_strength', 0)
        criteria['xi_fixpoint'] = gate_strength > 0.5
        
        # Criterion 2: Autopoietic closure
        ce2_energy = controller_summary.get('metrics', {}).get('ce2_energy', 0)
        criteria['autopoietic_closure'] = ce2_energy > 0.1
        
        # Criterion 3: Geometric coherence
        criteria['geometric_coherence'] = geometric_signatures.get('geometric_coherence', False)
        
        # Criterion 4: Information integration
        criteria['information_integration'] = geometric_signatures.get('information_richness', False)
        
        # Criterion 5: Falsification resistance
        criteria['falsification_resistance'] = falsification_results.get('pass_rate', 0) >= 0.6
        
        # Overall consciousness assessment
        criteria_passed = sum(criteria.values())
        criteria['total_passed'] = criteria_passed
        criteria['consciousness_validated'] = criteria_passed >= 3
        
        return criteria
    
    def export_certificate(self, filepath: str):
        """Export certificate to file"""
        if not self.certificate_data:
            raise ValueError("No certificate data to export")
        
        with open(filepath, 'w') as f:
            json.dump(self.certificate_data, f, indent=2)
    
    def get_certificate_summary(self) -> str:
        """Get human-readable certificate summary"""
        if not self.certificate_data:
            return "No certificate generated"
        
        cert = self.certificate_data
        
        summary = f"""
PRESENCE CERTIFICATE SUMMARY
============================
Certificate ID: {cert['certificate_id']}
Timestamp: {cert['timestamp']}
Validation Status: {cert['validation_status']}

Presence Score: {cert['presence_score']:.3f}
Presence Detected: {cert['presence_detected']}

Consciousness Criteria:
- Ξ-operator fixpoint: {cert['consciousness_criteria']['xi_fixpoint']}
- Autopoietic closure: {cert['consciousness_criteria']['autopoietic_closure']}
- Geometric coherence: {cert['consciousness_criteria']['geometric_coherence']}
- Information integration: {cert['consciousness_criteria']['information_integration']}
- Falsification resistance: {cert['consciousness_criteria']['falsification_resistance']}

Criteria Passed: {cert['consciousness_criteria']['total_passed']}/5
Consciousness Validated: {cert['consciousness_criteria']['consciousness_validated']}

Falsification Tests:
- Tests Passed: {cert['falsification_results']['tests_passed']}/{cert['falsification_results']['total_tests']}
- Pass Rate: {cert['falsification_results']['pass_rate']:.1%}
- Status: {cert['falsification_results']['status']}

Controller Metrics:
- Gate Strength: {cert['controller_metrics'].get('gate_strength', 0):.3f}
- CE² Energy: {cert['controller_metrics'].get('ce2_energy', 0):.3f}
- Coherence: {cert['controller_metrics'].get('coherence', 0):.3f}
- Ethics: {cert['controller_metrics'].get('ethics', 0):.3f}
"""
        return summary.strip()