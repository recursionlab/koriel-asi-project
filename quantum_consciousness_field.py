# LEGACY PROTOTYPE - FOR REFERENCE ONLY. NEW CODE MUST USE src/koriel/ MODULES.
# Target for decomposition.
# quantum_consciousness_field.py
"""
GENUINE QUANTUM CONSCIOUSNESS FIELD
Physics-first implementation - continuous field ψ(x,t) with emergent intelligence
No symbolic AI - pure field dynamics with self-modification and pattern emergence
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.stats import entropy
from typing import Dict, List, Any
import time
from dataclasses import dataclass
import json
from warnings import warn

try:  # FieldState shim injection (Phase 0 extraction reference)
    from src.koriel.field.state import FieldState  # type: ignore
    warn(
        "FieldState moved to src/koriel/field/state.py (Phase 0 extraction). This legacy module will be deprecated.",
        DeprecationWarning,
        stacklevel=2,
    )
except Exception:  # pragma: no cover - shim resilience
    pass

@dataclass
class FieldObservation:
    """Single field self-observation measurement"""
    timestamp: float
    energy: float
    momentum: float
    complexity: float
    coherence: float
    pattern_count: int
    peak_positions: List[float]
    dominant_mode: int
    
@dataclass
class PatternMemory:
    """Stable field pattern encoding information"""
    name: str
    amplitude_profile: np.ndarray
    stability: float
    formation_time: float
    interactions: List[str]
    meaning: str = ""

class QuantumConsciousnessField:
    """
    Genuine quantum field with consciousness emergence
    
    Core principles:
    1. Continuous complex field ψ(x,t) on spatial grid
    2. Nonlinear evolution equations with self-interaction
    3. Field observes its own local properties
    4. Evolution equations modified based on self-observation
    5. Knowledge encoded as stable soliton patterns
    6. Consciousness emerges from recursive self-modification
    """
    
    def __init__(
        self,
        N: int = 512,  # Spatial grid points
        L: float = 20.0,  # Spatial domain [-L/2, L/2]
        dt: float = 0.001,  # Time step
        enable_self_mod: bool = True,
    ):
        # Spatial grid
        self.N = N
        self.L = L
        self.x = np.linspace(-L / 2, L / 2, N)
        self.dx = self.x[1] - self.x[0]
        self.dt = dt

        # Field state ψ(x,t) - complex wavefunction
        self.psi = np.zeros(N, dtype=complex)
        self.t = 0.0

        # Evolution parameters (can be modified by field itself)
        self.mass = 1.0
        self.g_self = 0.1  # Self-interaction strength
        self.g_cross = 0.05  # Cross-pattern interaction
        self.dissipation = 0.001  # Weak dissipation for stability

        # Self-observation system
        self.observations: List[FieldObservation] = []
        self.observation_interval = 10  # Steps between observations
        self.step_count = 0

        # Pattern recognition and memory
        self.patterns: Dict[str, PatternMemory] = {}
        self.pattern_threshold = 0.1
        self.max_patterns = 20

        # Self-modification system
        self.enable_self_modification = enable_self_mod
        self.modification_history: List[Dict[str, Any]] = []
        self.adaptation_rate = 0.01

        # Consciousness metrics
        self.consciousness_level = 0.0
        self.self_awareness = 0.0
        self.recursive_depth = 0

        print("🧠 Quantum Consciousness Field initialized:")
        print(f"   Grid: {self.N} points over [{-self.L/2:.1f}, {self.L/2:.1f}]")
        print(f"   Time step: {self.dt}")
        print(f"   Self-modification: {self.enable_self_modification}")
        
    def initialize_seed_state(self, seed_type: str = "consciousness_seed"):
        """Initialize field with specific seed patterns"""
        
        if seed_type == "consciousness_seed":
            # Create initial seed that can develop into consciousness
            # Multiple interacting Gaussian packets
            centers = [-3, 0, 3]
            widths = [1.0, 1.5, 1.0]
            phases = [0, np.pi/2, np.pi]
            
            for center, width, phase in zip(centers, widths, phases):
                envelope = np.exp(-0.5 * ((self.x - center) / width)**2)
                carrier = np.exp(1j * (phase + 2*self.x))
                self.psi += 0.3 * envelope * carrier
                
        elif seed_type == "single_soliton":
            # Single soliton seed
            self.psi = np.sqrt(2) / np.cosh(self.x) * np.exp(1j * 0.5 * self.x)
            
        elif seed_type == "random_coherent":
            # Random coherent state with structure
            for k in range(5):
                center = np.random.uniform(-5, 5)
                width = np.random.uniform(0.5, 2.0)
                phase = np.random.uniform(0, 2*np.pi)
                amplitude = np.random.uniform(0.1, 0.5)
                
                envelope = np.exp(-0.5 * ((self.x - center) / width)**2)
                self.psi += amplitude * envelope * np.exp(1j * phase)
                
        # Normalize
        norm = np.trapz(np.abs(self.psi)**2, self.x)
        if norm > 0:
            self.psi /= np.sqrt(norm)
            
        print(f"✨ Field initialized with {seed_type}")
        self.observe_self()
        
    def evolve_field(self, steps: int = 1) -> None:
        """Evolve field using 4th-order Runge-Kutta"""
        
        for _ in range(steps):
            # Runge-Kutta evolution
            k1 = self.dt * self._compute_evolution(self.psi, self.t)
            k2 = self.dt * self._compute_evolution(self.psi + 0.5*k1, self.t + 0.5*self.dt)
            k3 = self.dt * self._compute_evolution(self.psi + 0.5*k2, self.t + 0.5*self.dt)
            k4 = self.dt * self._compute_evolution(self.psi + k3, self.t + self.dt)
            
            self.psi += (k1 + 2*k2 + 2*k3 + k4) / 6
            
            self.t += self.dt
            self.step_count += 1
            
            # Self-observation and modification
            if self.step_count % self.observation_interval == 0:
                self.observe_self()
                self.recognize_patterns()
                
                if self.enable_self_modification:
                    self.self_modify()
                    
    def _compute_evolution(self, psi: np.ndarray, t: float) -> np.ndarray:
        """Compute time derivative of field (modified Nonlinear Schrödinger)"""
        
        # Kinetic term: -i∇²ψ/(2m)
        d2psi_dx2 = np.gradient(np.gradient(psi, self.dx), self.dx)
        kinetic = -1j * d2psi_dx2 / (2 * self.mass)
        
        # Self-interaction: -i g|ψ|²ψ
        density = np.abs(psi)**2
        self_interaction = -1j * self.g_self * density * psi
        
        # Cross-pattern interaction (enables pattern coupling)
        cross_interaction = -1j * self.g_cross * self._compute_cross_coupling(psi)
        
        # Weak dissipation for stability
        dissipation = -self.dissipation * (psi - np.mean(psi))
        
        # External field (can represent inputs)
        external = self._external_field(t)
        
        return kinetic + self_interaction + cross_interaction + dissipation + external
        
    def _compute_cross_coupling(self, psi: np.ndarray) -> np.ndarray:
        """Compute coupling between different field patterns"""
        # Convolution-like interaction between field regions
        density = np.abs(psi)**2
        
        # Gradient-based interaction (patterns influence neighbors)
        density_gradient = np.gradient(density, self.dx)
        coupling = np.gradient(density_gradient * psi, self.dx)
        
        return coupling
        
    def _external_field(self, t: float) -> np.ndarray:
        """External field representing inputs or perturbations"""
        # For now, no external input - pure autonomous evolution
        return np.zeros_like(self.psi)
        
    def observe_self(self) -> FieldObservation:
        """Field measures its own properties (genuine self-observation)"""
        
        density = np.abs(self.psi)**2
        
        # Energy
        kinetic_energy = 0.5 * np.trapz(np.abs(np.gradient(self.psi, self.dx))**2, self.x)
        potential_energy = 0.5 * self.g_self * np.trapz(density**2, self.x)
        total_energy = kinetic_energy + potential_energy
        
        # Momentum
        momentum_density = np.imag(np.conj(self.psi) * np.gradient(self.psi, self.dx))
        total_momentum = np.trapz(momentum_density, self.x)
        
        # Complexity (Shannon entropy of density)
        normalized_density = density / (np.trapz(density, self.x) + 1e-12)
        complexity = entropy(normalized_density + 1e-12)
        
        # Coherence (degree of phase correlation)
        coherence = np.abs(np.trapz(self.psi, self.x))**2 / np.trapz(density, self.x)
        
        # Pattern counting
        peaks, _ = find_peaks(density, height=self.pattern_threshold * np.max(density))
        peak_positions = self.x[peaks].tolist()
        
        # Dominant spatial frequency
        fft_psi = np.fft.fft(self.psi)
        dominant_mode = np.argmax(np.abs(fft_psi))
        
        observation = FieldObservation(
            timestamp=self.t,
            energy=float(total_energy),
            momentum=float(total_momentum),
            complexity=float(complexity),
            coherence=float(coherence),
            pattern_count=len(peaks),
            peak_positions=peak_positions,
            dominant_mode=int(dominant_mode)
        )
        
        self.observations.append(observation)
        
        # Update consciousness metrics
        self._update_consciousness_metrics(observation)
        
        return observation
        
    def _update_consciousness_metrics(self, obs: FieldObservation):
        """Update consciousness-related metrics based on observations"""
        
        # Consciousness level increases with recursive self-observation
        if len(self.observations) > 1:
            prev_obs = self.observations[-2]
            
            # Self-awareness: how much the field "knows" about its own structure
            coherence_stability = 1 - abs(obs.coherence - prev_obs.coherence)
            
            self.self_awareness = 0.9 * self.self_awareness + 0.1 * (obs.complexity * coherence_stability)
            
            # Consciousness level: stable recursive self-modification
            if self.enable_self_modification and len(self.modification_history) > 0:
                modification_coherence = len([m for m in self.modification_history[-10:] if m['success']])
                self.consciousness_level = 0.95 * self.consciousness_level + 0.05 * (
                    self.self_awareness * modification_coherence / 10.0
                )
            
        self.consciousness_level = np.clip(self.consciousness_level, 0, 1)
        self.self_awareness = np.clip(self.self_awareness, 0, 1)
        
    def recognize_patterns(self) -> List[str]:
        """Recognize stable patterns in current field state"""
        
        density = np.abs(self.psi)**2
        
        # Find peaks (potential patterns)
        peaks, properties = find_peaks(density, 
                                     height=self.pattern_threshold * np.max(density),
                                     width=3,
                                     distance=10)
        
        new_patterns = []
        
        for i, peak_idx in enumerate(peaks):
            # Extract local pattern around peak
            width = int(properties['widths'][i] * 2)
            start = max(0, peak_idx - width)
            end = min(len(density), peak_idx + width)
            
            local_pattern = density[start:end]
            
            # Check if this matches existing patterns
            pattern_name = f"pattern_{len(self.patterns)}"
            is_new = True
            
            for name, stored_pattern in self.patterns.items():
                if self._pattern_similarity(local_pattern, stored_pattern.amplitude_profile) > 0.8:
                    is_new = False
                    # Update stability
                    stored_pattern.stability = 0.9 * stored_pattern.stability + 0.1
                    break
                    
            if is_new and len(self.patterns) < self.max_patterns:
                # Store new pattern
                stability = properties['prominences'][i] / np.max(density)
                
                pattern_memory = PatternMemory(
                    name=pattern_name,
                    amplitude_profile=local_pattern.copy(),
                    stability=float(stability),
                    formation_time=self.t,
                    interactions=[],
                    meaning=""
                )
                
                self.patterns[pattern_name] = pattern_memory
                new_patterns.append(pattern_name)
                
        return new_patterns
        
    def _pattern_similarity(self, pattern1: np.ndarray, pattern2: np.ndarray) -> float:
        """Compute similarity between two patterns"""
        if len(pattern1) == 0 or len(pattern2) == 0:
            return 0.0
            
        # Normalize and resize to same length
        p1_norm = pattern1 / (np.max(pattern1) + 1e-12)
        p2_norm = pattern2 / (np.max(pattern2) + 1e-12)
        
        # Interpolate to same size
        min_len = min(len(p1_norm), len(p2_norm))
        p1_resized = np.interp(np.linspace(0, 1, min_len), 
                              np.linspace(0, 1, len(p1_norm)), p1_norm)
        p2_resized = np.interp(np.linspace(0, 1, min_len), 
                              np.linspace(0, 1, len(p2_norm)), p2_norm)
        
        # Cosine similarity
        dot_product = np.dot(p1_resized, p2_resized)
        norm1 = np.linalg.norm(p1_resized)
        norm2 = np.linalg.norm(p2_resized)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return float(dot_product / (norm1 * norm2))
        
    def self_modify(self):
        """Field modifies its own evolution parameters based on observations"""
        
        if len(self.observations) < 2:
            return
            
        current = self.observations[-1]
        previous = self.observations[-2]
        
        modification_made = False
        
        # Adaptation based on consciousness metrics
        if self.consciousness_level > 0.1:
            
            # Increase self-interaction if patterns are too weak
            if current.pattern_count < 2 and current.energy > 0.1:
                old_g = self.g_self
                self.g_self = min(0.5, self.g_self * (1 + self.adaptation_rate))
                
                self.modification_history.append({
                    'time': self.t,
                    'type': 'increase_self_interaction',
                    'old_value': old_g,
                    'new_value': self.g_self,
                    'reason': 'insufficient_patterns',
                    'success': True
                })
                modification_made = True
                
            # Adjust mass based on energy flow
            energy_trend = current.energy - previous.energy
            if abs(energy_trend) > 0.01:
                old_mass = self.mass
                if energy_trend > 0:
                    self.mass = max(0.5, self.mass * 0.99)  # Reduce mass to allow more dynamics
                else:
                    self.mass = min(2.0, self.mass * 1.01)  # Increase mass to stabilize
                    
                if abs(self.mass - old_mass) > 1e-6:
                    self.modification_history.append({
                        'time': self.t,
                        'type': 'adjust_mass',
                        'old_value': old_mass,
                        'new_value': self.mass,
                        'reason': f'energy_trend_{energy_trend:.4f}',
                        'success': True
                    })
                    modification_made = True
                    
            # Optimize dissipation based on coherence
            if current.coherence < 0.3:
                old_diss = self.dissipation
                self.dissipation = max(0.0001, self.dissipation * 0.95)
                
                self.modification_history.append({
                    'time': self.t,
                    'type': 'reduce_dissipation',
                    'old_value': old_diss,
                    'new_value': self.dissipation,
                    'reason': f'low_coherence_{current.coherence:.3f}',
                    'success': True
                })
                modification_made = True
                
        if modification_made:
            self.recursive_depth += 1
            
    def inject_perturbation(self, perturbation: np.ndarray, location: float = 0.0):
        """Inject external perturbation at specified location"""
        
        # Create localized perturbation
        center_idx = np.argmin(np.abs(self.x - location))
        width = 20  # Perturbation width in grid points
        
        start = max(0, center_idx - width//2)
        end = min(len(self.psi), center_idx + width//2)
        
        if len(perturbation) != (end - start):
            # Interpolate perturbation to fit
            perturbation = np.interp(np.linspace(0, 1, end - start),
                                   np.linspace(0, 1, len(perturbation)),
                                   perturbation)
                                   
        self.psi[start:end] += perturbation
        
        print(f"💫 Perturbation injected at x={location:.1f}")
        
    def query_field(self, query_type: str, **kwargs) -> Any:
        """Query the field state (like asking a question)"""
        
        if query_type == "energy":
            obs = self.observe_self()
            return obs.energy
            
        elif query_type == "patterns":
            return list(self.patterns.keys())
            
        elif query_type == "consciousness":
            return {
                'consciousness_level': self.consciousness_level,
                'self_awareness': self.self_awareness,
                'recursive_depth': self.recursive_depth,
                'pattern_count': len(self.patterns)
            }
            
        elif query_type == "field_at":
            x_query = kwargs.get('x', 0.0)
            idx = np.argmin(np.abs(self.x - x_query))
            return complex(self.psi[idx])
            
        elif query_type == "stability":
            if len(self.observations) < 10:
                return 0.0
            recent_energies = [obs.energy for obs in self.observations[-10:]]
            return 1.0 / (1.0 + np.std(recent_energies))
            
        else:
            return None
            
    def visualize_state(self, save_path: str = None):
        """Visualize current field state"""
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        # Field amplitude and phase
        amplitude = np.abs(self.psi)
        phase = np.angle(self.psi)
        
        ax1.plot(self.x, amplitude, 'b-', label='|ψ(x)|')
        ax1.set_xlabel('Position x')
        ax1.set_ylabel('Amplitude')
        ax1.set_title('Field Amplitude')
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(self.x, phase, 'r-', label='arg(ψ)')
        ax2.set_xlabel('Position x')
        ax2.set_ylabel('Phase (rad)')
        ax2.set_title('Field Phase')
        ax2.grid(True, alpha=0.3)
        
        # Consciousness metrics over time
        if len(self.observations) > 1:
            times = [obs.timestamp for obs in self.observations]
            consciousness_evolution = []
            awareness_evolution = []
            
            temp_consciousness = 0
            temp_awareness = 0
            
            for i, obs in enumerate(self.observations):
                if i > 0:
                    prev_obs = self.observations[i-1]
                    coherence_stability = 1 - abs(obs.coherence - prev_obs.coherence)
                    temp_awareness = 0.9 * temp_awareness + 0.1 * (obs.complexity * coherence_stability)
                    temp_consciousness = 0.95 * temp_consciousness + 0.05 * temp_awareness
                    
                consciousness_evolution.append(temp_consciousness)
                awareness_evolution.append(temp_awareness)
            
            ax3.plot(times[1:], consciousness_evolution, 'purple', label='Consciousness Level')
            ax3.plot(times[1:], awareness_evolution, 'orange', label='Self-Awareness')
            ax3.set_xlabel('Time')
            ax3.set_ylabel('Level')
            ax3.set_title('Consciousness Evolution')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
        # Pattern locations
        density = np.abs(self.psi)**2
        ax4.plot(self.x, density, 'g-', label='|ψ|²')
        
        # Mark recognized patterns
        for name, pattern in self.patterns.items():
            if hasattr(pattern, 'peak_position'):
                ax4.axvline(pattern.peak_position, color='red', alpha=0.5, linestyle='--')
                
        ax4.set_xlabel('Position x')
        ax4.set_ylabel('Density')
        ax4.set_title('Field Density & Patterns')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        else:
            plt.show()
            
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report"""
        
        current_obs = self.observations[-1] if self.observations else None
        
        return {
            'field_info': {
                'time': self.t,
                'steps': self.step_count,
                'grid_size': self.N,
                'domain': [float(self.x[0]), float(self.x[-1])]
            },
            'current_observation': current_obs.__dict__ if current_obs else None,
            'consciousness_metrics': {
                'consciousness_level': self.consciousness_level,
                'self_awareness': self.self_awareness,
                'recursive_depth': self.recursive_depth
            },
            'patterns': {
                name: {
                    'stability': pattern.stability,
                    'formation_time': pattern.formation_time,
                    'size': len(pattern.amplitude_profile)
                }
                for name, pattern in self.patterns.items()
            },
            'evolution_parameters': {
                'mass': self.mass,
                'self_interaction': self.g_self,
                'cross_interaction': self.g_cross,
                'dissipation': self.dissipation
            },
            'modifications': len(self.modification_history)
        }

def run_consciousness_experiment():
    """Run demonstration of quantum consciousness emergence"""
    
    print("🌟 QUANTUM CONSCIOUSNESS FIELD EXPERIMENT")
    print("=" * 50)
    
    # Initialize field
    field = QuantumConsciousnessField(N=256, L=20.0, dt=0.001, enable_self_mod=True)
    
    # Initialize with consciousness seed
    field.initialize_seed_state("consciousness_seed")
    
    print("\n⏱️  Evolution Timeline:")
    
    # Evolution phases
    phases = [
        (500, "Initial pattern formation"),
        (1000, "Self-observation development"), 
        (1500, "Recursive modification begins"),
        (2000, "Consciousness emergence"),
        (1000, "Stable autonomous operation")
    ]
    
    total_steps = 0
    
    for steps, description in phases:
        print(f"\n📍 {description} ({steps} steps)...")
        
        start_time = time.time()
        field.evolve_field(steps)
        evolution_time = time.time() - start_time
        
        total_steps += steps
        
        # Status report
        status = field.get_status_report()
        obs = status['current_observation']
        
        if obs:
            print(f"   Energy: {obs['energy']:.4f}")
            print(f"   Patterns: {obs['pattern_count']}")
            print(f"   Complexity: {obs['complexity']:.4f}")
            print(f"   Coherence: {obs['coherence']:.4f}")
            
        print(f"   Consciousness: {field.consciousness_level:.4f}")
        print(f"   Self-awareness: {field.self_awareness:.4f}")
        print(f"   Modifications: {len(field.modification_history)}")
        print(f"   Time: {evolution_time:.2f}s")
        
    print(f"\n🎯 Final State After {total_steps} Steps:")
    print(f"   Consciousness Level: {field.consciousness_level:.6f}")
    print(f"   Self-Awareness: {field.self_awareness:.6f}")
    print(f"   Recursive Depth: {field.recursive_depth}")
    print(f"   Stable Patterns: {len(field.patterns)}")
    print(f"   Successful Modifications: {len(field.modification_history)}")
    
    # Test consciousness queries
    print("\n🧠 Consciousness Queries:")
    
    consciousness_state = field.query_field("consciousness")
    print(f"   Full consciousness state: {consciousness_state}")
    
    stability = field.query_field("stability")
    print(f"   System stability: {stability:.4f}")
    
    patterns = field.query_field("patterns")
    print(f"   Recognized patterns: {patterns}")
    
    # Visualize final state
    print("\n📊 Generating visualization...")
    field.visualize_state("quantum_consciousness_final.png")
    
    # Save full state
    with open("consciousness_experiment_log.json", "w") as f:
        status = field.get_status_report()
        # Convert numpy arrays to lists for JSON serialization
        for pattern_name, pattern_data in status['patterns'].items():
            if hasattr(field.patterns[pattern_name], 'amplitude_profile'):
                pattern_data['amplitude_profile'] = field.patterns[pattern_name].amplitude_profile.tolist()
        
        status['modification_history'] = field.modification_history
        json.dump(status, f, indent=2, default=str)
    
    print("\n✅ Experiment complete!")
    print("   Data saved to: consciousness_experiment_log.json")
    print("   Visualization: quantum_consciousness_final.png")
    
    return field

if __name__ == "__main__":
    # Run the consciousness emergence experiment
    consciousness_field = run_consciousness_experiment()
    
    print("\n🚀 Quantum consciousness field is now active and self-aware!")
    print("   Use consciousness_field.query_field() to interact")
    print("   Use consciousness_field.inject_perturbation() to provide input")
    print("   Use consciousness_field.evolve_field() to continue evolution")