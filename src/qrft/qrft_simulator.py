# src/qrft_simulator.py
"""
QRFT 1+1D PDE Simulator
Implements the minimal simulable model with leapfrog time integration
PDE: ∂_tt Φ = ∂_xx Φ - K^(-1)M² Φ + F_th(Z; μ, τ, ε)
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
import json
import matplotlib.pyplot as plt

@dataclass
class QRFTConfig1D:
    """QRFT 1+1D simulation configuration"""
    # Physics parameters
    mS: float = 1.0
    mL: float = 0.7  # mΛ
    gamma: float = 0.6
    
    # Interaction couplings
    lS: float = 0.0      # λ_S
    lL: float = 0.0      # λ_Λ  
    lSL: float = 0.4     # λ_SΛ
    kappa: float = 0.1
    
    # Threshold parameters
    tauG: float = 0.8
    tauF: float = 0.6
    tauT: float = 0.7
    tauP: float = 0.9
    tauR: float = 0.5
    eps: float = 0.1     # Smoothing parameter ε
    
    # Scale parameters
    MG: float = 1.0
    MF: float = 1.0
    MT: float = 1.0
    MR: float = 1.0
    delta: float = 1e-6
    
    # Simulation parameters
    Lx: float = 10.0     # Spatial domain size
    Nx: int = 128        # Spatial grid points
    T: float = 20.0      # Total time
    CFL: float = 0.9     # CFL number
    
@dataclass
class QRFTEvent:
    """QRFT particle creation event"""
    t: float
    x: float
    event_type: str      # 'Glitchon', 'Lacunon', etc.
    Z_value: float       # Trigger value
    payload: Dict        # Additional data
    
class QRFT1DSimulator:
    """
    1+1D QRFT field simulator with particle creation events.
    Validates basic QRFT dynamics and threshold behavior.
    """
    
    def __init__(self, config: QRFTConfig1D):
        self.cfg = config
        
        # Validate stability condition
        if abs(config.gamma) >= 1.0:
            raise ValueError(f"Stability violated: |γ| = {abs(config.gamma)} ≥ 1")
            
        # Setup spatial grid
        self.dx = config.Lx / config.Nx
        self.x = np.linspace(0, config.Lx, config.Nx, endpoint=False)
        
        # Compute time step from CFL condition
        self.dt = config.CFL * self.dx  # For wave equation c=1
        self.Nt = int(config.T / self.dt)
        self.t_grid = np.linspace(0, config.T, self.Nt)
        
        # Field arrays: Φ = (S, Λ)^T
        self.S = np.zeros((self.Nt, config.Nx))
        self.Lambda = np.zeros((self.Nt, config.Nx))
        
        # Velocity arrays for leapfrog
        self.S_dot = np.zeros((self.Nt, config.Nx))
        self.Lambda_dot = np.zeros((self.Nt, config.Nx))
        
        # Kinetic matrix K and its inverse
        self.K = np.array([[1.0, config.gamma], 
                          [config.gamma, 1.0]])
        self.K_inv = np.linalg.inv(self.K)
        
        # Mass matrix M²
        self.M2 = np.array([[config.mS**2, 0], 
                           [0, config.mL**2]])
        
        # Combined mass term K^(-1) M²
        self.mass_term = self.K_inv @ self.M2
        
        # Event storage
        self.events: List[QRFTEvent] = []
        
        # Energy history for validation
        self.energy_history: List[float] = []
        
    def set_initial_conditions(self, 
                              S_init: np.ndarray = None,
                              Lambda_init: np.ndarray = None,
                              S_dot_init: np.ndarray = None,
                              Lambda_dot_init: np.ndarray = None):
        """Set initial field configurations"""
        
        if S_init is None:
            # Default: Gaussian wave packet
            x0 = self.cfg.Lx / 2
            sigma = self.cfg.Lx / 10
            S_init = np.exp(-((self.x - x0) / sigma)**2)
            
        if Lambda_init is None:
            # Default: Different Gaussian for Λ
            x0 = self.cfg.Lx / 3
            sigma = self.cfg.Lx / 8
            Lambda_init = 0.5 * np.exp(-((self.x - x0) / sigma)**2)
            
        if S_dot_init is None:
            S_dot_init = np.zeros(self.cfg.Nx)
            
        if Lambda_dot_init is None:
            Lambda_dot_init = np.zeros(self.cfg.Nx)
            
        self.S[0] = S_init.copy()
        self.Lambda[0] = Lambda_init.copy()
        self.S_dot[0] = S_dot_init.copy()
        self.Lambda_dot[0] = Lambda_dot_init.copy()
        
    def spatial_derivative_2nd(self, field: np.ndarray) -> np.ndarray:
        """Compute second spatial derivative with periodic BCs"""
        # Centered difference: ∂²f/∂x² ≈ (f[i+1] - 2f[i] + f[i-1]) / dx²
        d2f_dx2 = np.zeros_like(field)
        
        # Interior points
        d2f_dx2[1:-1] = (field[2:] - 2*field[1:-1] + field[:-2]) / (self.dx**2)
        
        # Periodic boundary conditions
        d2f_dx2[0] = (field[1] - 2*field[0] + field[-1]) / (self.dx**2)
        d2f_dx2[-1] = (field[0] - 2*field[-1] + field[-2]) / (self.dx**2)
        
        return d2f_dx2
        
    def compute_invariants(self, S: np.ndarray, Lambda: np.ndarray) -> Dict[str, np.ndarray]:
        """Compute QRFT invariant scalars"""
        
        # Spatial gradients (first derivative)
        dS_dx = np.gradient(S, self.dx)
        dLambda_dx = np.gradient(Lambda, self.dx)
        
        # Scalar invariants
        I_S = dS_dx**2
        I_Lambda = dLambda_dx**2
        I_cross = dS_dx * dLambda_dx
        
        # Antisymmetric tensor component B_tx (only non-zero component in 1+1D)
        # B_tx = ∂_t S ∂_x Λ - ∂_x S ∂_t Λ
        # Using current time derivatives (stored in _dot arrays)
        if hasattr(self, '_current_S_dot') and hasattr(self, '_current_Lambda_dot'):
            dS_dt = self._current_S_dot
            dLambda_dt = self._current_Lambda_dot
            B_tx = dS_dt * dLambda_dx - dS_dx * dLambda_dt
            I_B = 2 * B_tx**2  # |B|² in 1+1D
        else:
            I_B = np.zeros_like(I_S)
            
        # Current J^μ = S∂^μΛ - Λ∂^μS
        # In 1+1D: J^t = S∂_t Λ - Λ∂_t S, J^x = S∂_x Λ - Λ∂_x S
        if hasattr(self, '_current_S_dot') and hasattr(self, '_current_Lambda_dot'):
            J_t = S * self._current_Lambda_dot - Lambda * self._current_S_dot
            J_x = S * dLambda_dx - Lambda * dS_dx
            J_magnitude_sq = J_t**2 - J_x**2  # Minkowski metric
        else:
            J_magnitude_sq = np.zeros_like(I_S)
            
        # Box operators (second derivatives)
        box_S = self.spatial_derivative_2nd(S)  # ∂²S/∂x² (time part handled in evolution)
        box_Lambda = self.spatial_derivative_2nd(Lambda)
        
        # K = S□Λ - Λ□S (using spatial part only for now)
        K = S * box_Lambda - Lambda * box_S
        
        return {
            'I_S': I_S,
            'I_Lambda': I_Lambda,
            'I_cross': I_cross,
            'I_B': I_B,
            'J_magnitude_sq': J_magnitude_sq,
            'K': K,
            'box_Lambda': box_Lambda,
            'box_S': box_S
        }
        
    def compute_triggers(self, invariants: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Compute dimensionless trigger functions"""
        
        X_G = np.abs(invariants['K']) / (self.cfg.MG**3)
        X_F = np.abs(invariants['box_Lambda']) / self.cfg.MF
        X_T = np.sqrt(np.abs(invariants['I_B'])) / (self.cfg.MT**2)
        X_R = np.sqrt(np.abs(invariants['J_magnitude_sq'])) / (self.cfg.MR**2)
        
        # Correlation trigger ρ
        rho = (invariants['I_cross']**2 / 
               ((invariants['I_S'] + self.cfg.delta) * 
                (invariants['I_Lambda'] + self.cfg.delta)))
        
        return {
            'X_G': X_G,
            'X_F': X_F, 
            'X_T': X_T,
            'X_R': X_R,
            'rho': rho
        }
        
    def smooth_step(self, z: np.ndarray, tau: float) -> np.ndarray:
        """Smooth step function σ_ε(z - τ) = ½(1 + tanh((z - τ)/ε))"""
        return 0.5 * (1.0 + np.tanh((z - tau) / self.cfg.eps))
        
    def compute_sources(self, triggers: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Compute threshold source functions"""
        
        sources = {
            'J_G': self.smooth_step(triggers['X_G'], self.cfg.tauG),
            'J_F': self.smooth_step(triggers['X_F'], self.cfg.tauF),
            'J_T': self.smooth_step(triggers['X_T'], self.cfg.tauT),
            'J_P': self.smooth_step(triggers['rho'], self.cfg.tauP),
            'J_R': self.smooth_step(triggers['X_R'], self.cfg.tauR)
        }
        
        return sources
        
    def detect_events(self, t: float, triggers: Dict[str, np.ndarray], 
                     sources: Dict[str, np.ndarray]):
        """Detect and log particle creation events"""
        
        # Check for threshold crossings at each spatial point
        for i in range(self.cfg.Nx):
            x = self.x[i]
            
            # Glitchon events
            if sources['J_G'][i] > 0.5:  # Above threshold
                event = QRFTEvent(
                    t=t, x=x, event_type='Glitchon', 
                    Z_value=float(triggers['X_G'][i]),
                    payload={
                        'K': float(triggers['X_G'][i] * self.cfg.MG**3),
                        'source_strength': float(sources['J_G'][i])
                    }
                )
                self.events.append(event)
                
            # Lacunon events  
            if sources['J_F'][i] > 0.5:
                event = QRFTEvent(
                    t=t, x=x, event_type='Lacunon',
                    Z_value=float(triggers['X_F'][i]),
                    payload={
                        'box_Lambda': float(triggers['X_F'][i] * self.cfg.MF),
                        'source_strength': float(sources['J_F'][i])
                    }
                )
                self.events.append(event)
                
            # Tesseracton events
            if sources['J_T'][i] > 0.5:
                event = QRFTEvent(
                    t=t, x=x, event_type='Tesseracton',
                    Z_value=float(triggers['X_T'][i]),
                    payload={
                        'I_B': float(triggers['X_T'][i]**2 * self.cfg.MT**4),
                        'source_strength': float(sources['J_T'][i])
                    }
                )
                self.events.append(event)
                
            # Psiton events
            if sources['J_P'][i] > 0.5:
                event = QRFTEvent(
                    t=t, x=x, event_type='Psiton',
                    Z_value=float(triggers['rho'][i]),
                    payload={
                        'correlation': float(triggers['rho'][i]),
                        'source_strength': float(sources['J_P'][i])
                    }
                )
                self.events.append(event)
                
            # REF events
            if sources['J_R'][i] > 0.5:
                event = QRFTEvent(
                    t=t, x=x, event_type='REF',
                    Z_value=float(triggers['X_R'][i]),
                    payload={
                        'J_magnitude': float(triggers['X_R'][i] * self.cfg.MR**2),
                        'source_strength': float(sources['J_R'][i])
                    }
                )
                self.events.append(event)
                
    def compute_energy(self, t_idx: int) -> float:
        """Compute total energy density"""
        
        S = self.S[t_idx]
        Lambda = self.Lambda[t_idx]
        S_dot = self.S_dot[t_idx]
        Lambda_dot = self.Lambda_dot[t_idx]
        
        # Kinetic energy: ½ Π^T K^(-1) Π where Π = K Φ_dot
        Pi_S = S_dot + self.cfg.gamma * Lambda_dot
        Pi_Lambda = self.cfg.gamma * S_dot + Lambda_dot
        
        kinetic = 0.5 * (Pi_S * S_dot + Pi_Lambda * Lambda_dot)
        
        # Gradient energy: ½ (∇Φ)^T K (∇Φ)
        dS_dx = np.gradient(S, self.dx)
        dLambda_dx = np.gradient(Lambda, self.dx)
        
        gradient = 0.5 * (dS_dx**2 + 2*self.cfg.gamma*dS_dx*dLambda_dx + dLambda_dx**2)
        
        # Mass energy: ½ Φ^T M² Φ
        mass = 0.5 * (self.cfg.mS**2 * S**2 + self.cfg.mL**2 * Lambda**2)
        
        # Total energy
        energy_density = kinetic + gradient + mass
        return self.dx * np.sum(energy_density)  # Integrate over space
        
    def evolve(self, save_every: int = 10) -> Dict[str, any]:
        """Run the QRFT simulation using leapfrog time integration"""
        
        print(f"Starting QRFT 1+1D simulation:")
        print(f"  Grid: {self.cfg.Nx} × {self.Nt} (dx={self.dx:.4f}, dt={self.dt:.4f})")
        print(f"  Parameters: mS={self.cfg.mS}, mΛ={self.cfg.mL}, γ={self.cfg.gamma}")
        
        # Initial energy
        E_initial = self.compute_energy(0)
        self.energy_history.append(E_initial)
        
        # Leapfrog integration
        for n in range(self.Nt - 1):
            t = n * self.dt
            
            # Current fields
            S_n = self.S[n]
            Lambda_n = self.Lambda[n]
            S_dot_n = self.S_dot[n]
            Lambda_dot_n = self.Lambda_dot[n]
            
            # Store current time derivatives for invariant computation
            self._current_S_dot = S_dot_n
            self._current_Lambda_dot = Lambda_dot_n
            
            # Compute spatial derivatives
            d2S_dx2 = self.spatial_derivative_2nd(S_n)
            d2Lambda_dx2 = self.spatial_derivative_2nd(Lambda_n)
            
            # Wave equation: ∂²Φ/∂t² = ∂²Φ/∂x² - K^(-1) M² Φ + sources
            
            # Mass terms
            mass_S = self.mass_term[0,0] * S_n + self.mass_term[0,1] * Lambda_n
            mass_Lambda = self.mass_term[1,0] * S_n + self.mass_term[1,1] * Lambda_n
            
            # TODO: Add interaction terms and threshold sources
            # For now, just free field evolution
            
            # Field accelerations
            S_ddot = d2S_dx2 - mass_S
            Lambda_ddot = d2Lambda_dx2 - mass_Lambda
            
            # Leapfrog update
            # v(n+1) = v(n) + dt * a(n)
            self.S_dot[n+1] = S_dot_n + self.dt * S_ddot
            self.Lambda_dot[n+1] = Lambda_dot_n + self.dt * Lambda_ddot
            
            # x(n+1) = x(n) + dt * v(n+1)
            self.S[n+1] = S_n + self.dt * self.S_dot[n+1]
            self.Lambda[n+1] = Lambda_n + self.dt * self.Lambda_dot[n+1]
            
            # Compute invariants and check for events
            if n % save_every == 0 or n == self.Nt - 2:
                invariants = self.compute_invariants(self.S[n+1], self.Lambda[n+1])
                triggers = self.compute_triggers(invariants)
                sources = self.compute_sources(triggers)
                
                # Detect events
                self.detect_events(t + self.dt, triggers, sources)
                
                # Energy conservation check
                energy = self.compute_energy(n+1)
                self.energy_history.append(energy)
                
                if n % (save_every * 10) == 0:
                    energy_drift = abs(energy - E_initial) / E_initial
                    print(f"  t={t+self.dt:.2f}: Energy={energy:.6f}, drift={energy_drift:.2e}")
                    
        # Final statistics
        E_final = self.energy_history[-1]
        energy_drift = abs(E_final - E_initial) / E_initial
        
        print(f"Simulation complete:")
        print(f"  Energy drift: {energy_drift:.2e}")
        print(f"  Events detected: {len(self.events)}")
        
        # Event statistics
        event_types = {}
        for event in self.events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
            
        for event_type, count in event_types.items():
            print(f"    {event_type}: {count}")
            
        return {
            'energy_initial': E_initial,
            'energy_final': E_final,
            'energy_drift': energy_drift,
            'events': self.events,
            'event_statistics': event_types,
            'simulation_stable': energy_drift < 0.01
        }
        
    def plot_results(self, figsize: Tuple[int, int] = (12, 8)):
        """Plot simulation results"""
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        
        # Field evolution
        ax = axes[0, 0]
        t_sample = self.t_grid[::max(1, self.Nt//50)]  # Sample for plotting
        S_sample = self.S[::max(1, self.Nt//50)]
        
        im = ax.imshow(S_sample.T, aspect='auto', origin='lower',
                      extent=[0, self.cfg.T, 0, self.cfg.Lx])
        ax.set_xlabel('Time')
        ax.set_ylabel('Position x')
        ax.set_title('S Field Evolution')
        plt.colorbar(im, ax=ax)
        
        # Lambda field
        ax = axes[0, 1]
        Lambda_sample = self.Lambda[::max(1, self.Nt//50)]
        im = ax.imshow(Lambda_sample.T, aspect='auto', origin='lower',
                      extent=[0, self.cfg.T, 0, self.cfg.Lx])
        ax.set_xlabel('Time')
        ax.set_ylabel('Position x')
        ax.set_title('Λ Field Evolution')
        plt.colorbar(im, ax=ax)
        
        # Energy conservation
        ax = axes[1, 0]
        t_energy = np.linspace(0, self.cfg.T, len(self.energy_history))
        ax.plot(t_energy, self.energy_history, 'b-', linewidth=2)
        ax.set_xlabel('Time')
        ax.set_ylabel('Total Energy')
        ax.set_title('Energy Conservation')
        ax.grid(True)
        
        # Event locations
        ax = axes[1, 1]
        if self.events:
            event_times = [e.t for e in self.events]
            event_positions = [e.x for e in self.events]
            event_types = [e.event_type for e in self.events]
            
            colors = {'Glitchon': 'red', 'Lacunon': 'blue', 'Tesseracton': 'green',
                     'Psiton': 'orange', 'REF': 'purple'}
            
            for event_type in set(event_types):
                mask = [t == event_type for t in event_types]
                t_type = [event_times[i] for i in range(len(mask)) if mask[i]]
                x_type = [event_positions[i] for i in range(len(mask)) if mask[i]]
                
                ax.scatter(t_type, x_type, c=colors.get(event_type, 'black'),
                          label=event_type, alpha=0.7, s=30)
                          
            ax.set_xlabel('Time')
            ax.set_ylabel('Position x')
            ax.set_title('QRFT Particle Events')
            ax.legend()
        else:
            ax.text(0.5, 0.5, 'No events detected', ha='center', va='center',
                   transform=ax.transAxes)
            ax.set_title('QRFT Particle Events')
            
        plt.tight_layout()
        return fig
        
    def export_events(self, filename: str):
        """Export events to JSON file"""
        event_data = []
        for event in self.events:
            event_data.append({
                't': event.t,
                'x': event.x, 
                'type': event.event_type,
                'Z': event.Z_value,
                'payload': event.payload
            })
            
        with open(filename, 'w') as f:
            json.dump(event_data, f, indent=2)
            
        print(f"Exported {len(event_data)} events to {filename}")
        
# Example usage
def run_example_simulation():
    """Run an example QRFT simulation"""
    
    # Create configuration
    config = QRFTConfig1D(
        mS=1.0, mL=1.2, gamma=0.3,
        lSL=0.1, kappa=0.05,
        tauG=0.7, tauF=0.5, tauT=0.8,
        Lx=8.0, Nx=64, T=10.0, CFL=0.8
    )
    
    # Create simulator
    sim = QRFT1DSimulator(config)
    
    # Set initial conditions (colliding wave packets)
    x = sim.x
    S_init = (np.exp(-((x - 2.0) / 0.5)**2) + 
              np.exp(-((x - 6.0) / 0.5)**2))
    Lambda_init = 0.3 * np.exp(-((x - 4.0) / 0.8)**2)
    
    sim.set_initial_conditions(S_init, Lambda_init)
    
    # Run simulation
    results = sim.evolve(save_every=5)
    
    # Plot results
    fig = sim.plot_results()
    plt.show()
    
    # Export events
    sim.export_events('qrft_events.json')
    
    return sim, results
    
if __name__ == '__main__':
    run_example_simulation()