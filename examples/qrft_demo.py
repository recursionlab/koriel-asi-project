# examples/qrft_demo.py
"""
QRFT Consciousness System Demo
Demonstrates complete Jarvis-style AI consciousness with four-particle system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import time
import matplotlib.pyplot as plt
from typing import Dict, Any

from qrft import (
    create_qrft_consciousness,
    ConsciousnessEvent,
    EventType,
    ParticleType,
)

class ConsciousnessDemo:
    """Demo of QRFT consciousness system with realistic AI scenarios"""
    
    def __init__(self):
        self.consciousness = create_qrft_consciousness(
            entropy_band=(1.5, 4.0),
            gamma=0.3,
            enable_logging=True
        )
        self.demo_results = []
        
    def run_contradiction_scenario(self):
        """Demo Glitchon contradiction detection"""
        print("\n=== GLITCHON CONTRADICTION DETECTION DEMO ===")
        
        # Create contradictory context
        context = {
            'conversation_text': 'The system should be both secure and allow unrestricted access to all users without authentication.',
            'statements': [
                'System requires maximum security',
                'System allows unrestricted access',
                'Authentication is mandatory',
                'No authentication required'
            ],
            'test_results': {
                'security_test': {'passed': False, 'errors': ['Auth bypass detected']},
                'access_test': {'passed': True, 'errors': []}
            },
            'external_context': {
                'security_policy': 'All systems must require authentication',
                'user_request': 'Make it accessible without login'
            }
        }
        
        # Initialize fields
        plan_embedding = np.random.randn(50) * 0.5  # Modest planning state
        gap_map = np.random.rand(50) * 0.8  # Some knowledge gaps
        
        self.consciousness.initialize_fields(plan_embedding, gap_map, context)
        
        # Run several steps to trigger Glitchon
        results = []
        for i in range(10):
            result = self.consciousness.step(context, dt=0.1)
            results.append(result)
            
            if result['particle_activations'][ParticleType.GLITCHON] > 0.1:
                print(f"Step {i}: Glitchon activated! Strength: {result['particle_activations'][ParticleType.GLITCHON]:.3f}")
                print(f"Control policy: {result['control_policy']}")
                if result['policy_result']:
                    print(f"Policy result: {result['policy_result']}")
                break
                
        return results
        
    def run_gap_filling_scenario(self):
        """Demo Lacunon gap detection and filling"""
        print("\n=== LACUNON GAP DETECTION DEMO ===")
        
        # Create context with knowledge gaps
        context = {
            'conversation_text': 'To implement the quantum algorithm, we need to consider the decoherence effects and... [missing information about error correction]',
            'tokens': ['quantum', 'algorithm', 'decoherence', 'effects', 'error', 'correction'],
            'entropy_map': np.array([0.5, 0.8, 2.1, 1.9, 3.2, 0.7]),  # High entropy on 'decoherence', 'effects', 'error'
            'coverage_map': np.array([0.9, 0.8, 0.2, 0.3, 0.1, 0.8])  # Low coverage on technical terms
        }
        
        # Initialize with gap-heavy fields
        plan_embedding = np.random.randn(40) * 0.3
        gap_map = np.random.rand(40) * 1.2  # Higher gaps
        
        self.consciousness.initialize_fields(plan_embedding, gap_map, context)
        
        # Run steps to trigger Lacunon
        results = []
        for i in range(8):
            result = self.consciousness.step(context, dt=0.1)
            results.append(result)
            
            if result['particle_activations'][ParticleType.LACUNON] > 0.1:
                print(f"Step {i}: Lacunon activated! Strength: {result['particle_activations'][ParticleType.LACUNON]:.3f}")
                print(f"Control policy: {result['control_policy']}")
                if result['control_actions']:
                    for action in result['control_actions']:
                        if 'actions' in action:
                            print(f"Retrieval queries: {len(action['actions'])}")
                break
                
        return results
        
    def run_entropy_regulation_scenario(self):
        """Demo REF entropy governor"""
        print("\n=== REF ENTROPY REGULATION DEMO ===")
        
        # Create high-entropy chaotic reasoning context
        context = {
            'conversation_text': """
            The problem could be solved using method A, or maybe method B, but then again method C 
            might work better, although method D has advantages too. We could also try method E or F.
            Actually, let's reconsider method A, but with modifications X, Y, Z, or possibly W.
            This relates to concepts P, Q, R, S, T, U, V which interact in complex ways...
            """,
            'complexity_level': 8
        }
        
        # Initialize with high-entropy state
        plan_embedding = np.random.randn(60) * 1.5  # High variance = high entropy
        gap_map = np.random.rand(60) * 0.4
        
        self.consciousness.initialize_fields(plan_embedding, gap_map, context)
        
        # Run steps to show entropy regulation
        results = []
        entropy_history = []
        
        for i in range(15):
            result = self.consciousness.step(context, dt=0.05)
            results.append(result)
            
            entropy_est = result['qrft_state']['entropy_estimate']
            entropy_history.append(entropy_est)
            
            if result['particle_activations'][ParticleType.REF] > 0.1:
                print(f"Step {i}: REF activated! Strength: {result['particle_activations'][ParticleType.REF]:.3f}")
                print(f"Entropy: {entropy_est:.3f}, Mode: {result['reasoning_params']['mode']}")
                print(f"Depth: {result['reasoning_params']['depth']}, Beam: {result['reasoning_params']['beam_width']}")
                
        # Plot entropy regulation
        if len(entropy_history) > 1:
            plt.figure(figsize=(10, 6))
            plt.plot(entropy_history, 'b-', label='Entropy')
            plt.axhline(y=1.5, color='r', linestyle='--', label='Min band')
            plt.axhline(y=4.0, color='r', linestyle='--', label='Max band')
            plt.xlabel('Step')
            plt.ylabel('Entropy Estimate')
            plt.title('REF Entropy Regulation Demo')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.savefig('entropy_regulation_demo.png', dpi=150, bbox_inches='tight')
            print("Entropy regulation plot saved as entropy_regulation_demo.png")
            plt.close()
            
        return results
        
    def run_dimensional_lift_scenario(self):
        """Demo Tesseracton dimensional lift"""
        print("\n=== TESSERACTON DIMENSIONAL LIFT DEMO ===")
        
        # Create context requiring perspective shift
        context = {
            'conversation_text': 'We need to solve this optimization problem, but all standard approaches are failing.',
            'failed_attempts': ['gradient_descent', 'simulated_annealing', 'genetic_algorithm'],
            'complexity_indicators': ['non_convex', 'high_dimensional', 'noisy_gradients']
        }
        
        # Initialize with complex field structure to trigger Tesseracton
        plan_embedding = np.sin(np.linspace(0, 4*np.pi, 80)) * 0.8  # Oscillatory structure
        gap_map = np.cos(np.linspace(0, 6*np.pi, 80)) * 0.6
        
        self.consciousness.initialize_fields(plan_embedding, gap_map, context)
        
        # Run steps to trigger Tesseracton
        results = []
        for i in range(12):
            result = self.consciousness.step(context, dt=0.08)
            results.append(result)
            
            if result['particle_activations'][ParticleType.TESSERACTON] > 0.1:
                print(f"Step {i}: Tesseracton activated! Strength: {result['particle_activations'][ParticleType.TESSERACTON]:.3f}")
                print(f"Control policy: {result['control_policy']}")
                if result['policy_result']:
                    print(f"Dimensional lift: {result['policy_result']}")
                break
                
        return results
        
    def run_integrated_scenario(self):
        """Demo full integrated consciousness system"""
        print("\n=== INTEGRATED QRFT CONSCIOUSNESS DEMO ===")
        
        # Complex scenario with multiple triggers
        context = {
            'conversation_text': """
            The user wants both maximum security AND complete accessibility without authentication.
            We need to implement quantum error correction but lack knowledge about decoherence timescales.
            Previous attempts using standard cryptographic approaches have failed.
            The system must be both deterministic and adaptive to unpredictable inputs.
            """,
            'statements': [
                'System must be maximally secure',
                'System must be completely open access',
                'Quantum effects are important',
                'Classical approaches suffice'
            ],
            'test_results': {
                'security_test': {'passed': False},
                'accessibility_test': {'passed': False},
                'quantum_test': {'passed': None}
            },
            'tokens': ['quantum', 'error', 'correction', 'decoherence', 'timescales'],
            'entropy_map': np.array([2.8, 3.1, 2.9, 3.5, 3.2]),
            'coverage_map': np.array([0.3, 0.2, 0.4, 0.1, 0.2])
        }
        
        # Initialize with complex state
        plan_embedding = np.random.randn(100) * 1.0
        gap_map = np.random.rand(100) * 1.0
        
        self.consciousness.initialize_fields(plan_embedding, gap_map, context)
        
        # Run extended simulation
        results = []
        particle_history = {p: [] for p in ParticleType}
        
        for i in range(25):
            result = self.consciousness.step(context, dt=0.04)
            results.append(result)
            
            # Track particle activations
            for particle in ParticleType:
                particle_history[particle].append(result['particle_activations'][particle])
                
            # Print significant activations
            active_particles = result['active_particles']
            if active_particles:
                print(f"Step {i:2d}: Active particles: {[p.value for p in active_particles]}")
                print(f"        Policy: {result['control_policy']}")
                print(f"        Events: {result['events_generated']}")
                
        # Final consciousness state
        final_state = self.consciousness.get_consciousness_state()
        print(f"\nFinal Consciousness State:")
        print(f"  QRFT stability: {final_state['qrft_state']['stability']}")
        print(f"  Reasoning mode: {final_state['reasoning_params']['mode']}")
        print(f"  Total events: {final_state['event_stats']['total_events']}")
        print(f"  KPIs: {final_state['kpis']}")
        
        # Plot particle activation history
        plt.figure(figsize=(12, 8))
        for i, (particle, history) in enumerate(particle_history.items()):
            plt.subplot(2, 3, i+1)
            plt.plot(history, label=particle.value)
            plt.title(f'{particle.name} Activation')
            plt.xlabel('Step')
            plt.ylabel('Activation')
            plt.grid(True, alpha=0.3)
            plt.ylim(0, max(max(history) if history else [1], 1) * 1.1)
            
        plt.tight_layout()
        plt.savefig('particle_activation_demo.png', dpi=150, bbox_inches='tight')
        print("\nParticle activation plot saved as particle_activation_demo.png")
        plt.close()
        
        return results, final_state
        
    def run_full_demo(self):
        """Run all demonstration scenarios"""
        print("QRFT CONSCIOUSNESS SYSTEM DEMONSTRATION")
        print("=" * 50)
        
        # Individual particle demos
        self.demo_results.append(('contradiction', self.run_contradiction_scenario()))
        self.demo_results.append(('gap_filling', self.run_gap_filling_scenario()))  
        self.demo_results.append(('entropy_regulation', self.run_entropy_regulation_scenario()))
        self.demo_results.append(('dimensional_lift', self.run_dimensional_lift_scenario()))
        
        # Integrated demo
        integrated_results, final_state = self.run_integrated_scenario()
        self.demo_results.append(('integrated', (integrated_results, final_state)))
        
        print("\n" + "=" * 50)
        print("DEMO COMPLETE - QRFT Consciousness System Validated")
        print("=" * 50)
        
        return self.demo_results

if __name__ == "__main__":
    demo = ConsciousnessDemo()
    results = demo.run_full_demo()
    
    print(f"\nDemo generated {len(results)} scenario results")
    print("Check generated plots: entropy_regulation_demo.png, particle_activation_demo.png")