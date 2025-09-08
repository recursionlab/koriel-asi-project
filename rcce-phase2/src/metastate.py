"""MetaState and Shadow Codex logging"""
import json
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict

@dataclass
class MetaState:
    t: int
    action: str
    loss: float
    rc_embedding: float
    rc_graph: float  
    rc_value: float
    rc_total: float
    drift: float
    d_drift: float
    energy: float
    holonomy_delta: float
    xi_delta: float
    upsilon_active: bool
    lambda_plus_active: bool
    phi33_violations: int
    curvature: float
    torsion: float
    state_hash: str
    
    def to_dict(self):
        return asdict(self)

class ShadowCodex:
    def __init__(self, log_path="logs/shadow_codex.jsonl"):
        self.log_path = log_path
        self.entries = []
        
    def log(self, metastate: MetaState):
        """Append to Shadow Codex"""
        self.entries.append(metastate)
        
        # Write to JSONL
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(metastate.to_dict()) + '\n')
    
    def compute_state_hash(self, hidden_state, params_subset):
        """Compute deterministic hash of state"""
        state_bytes = hidden_state.tobytes() + str(params_subset).encode()
        return hashlib.sha256(state_bytes).hexdigest()[:16]
    
    def get_recent(self, n=10):
        """Get recent entries"""
        return self.entries[-n:] if len(self.entries) >= n else self.entries
    
    def clear(self):
        """Clear entries"""
        self.entries.clear()
        try:
            open(self.log_path, 'w').close()
        except Exception:
            pass

class MetricsLogger:
    def __init__(self, csv_path="logs/metrics.csv"):
        self.csv_path = csv_path
        self.headers_written = False
        
    def log_metrics(self, metrics: Dict[str, float]):
        """Log metrics to CSV"""
        import csv
        
        if not self.headers_written:
            with open(self.csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(metrics.keys())
            self.headers_written = True
        
        with open(self.csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(metrics.values())

def create_metastate(t, action, model_state, controller_state, loss, config) -> MetaState:
    """Factory for MetaState creation"""
    
    # Compute state hash
    codex = ShadowCodex()
    state_hash = codex.compute_state_hash(
        model_state['hidden'], 
        {'loss': loss, 't': t}
    )
    
    return MetaState(
        t=t,
        action=action,
        loss=loss,
        rc_embedding=controller_state.get('rc_embedding', 0.0),
        rc_graph=controller_state.get('rc_graph', 0.0),
        rc_value=controller_state.get('rc_value', 0.0),
        rc_total=controller_state.get('rc_total', 0.0),
        drift=controller_state.get('drift', 0.0),
        d_drift=controller_state.get('d_drift', 0.0),
        energy=controller_state.get('energy', 0.0),
        holonomy_delta=controller_state.get('holonomy_delta', 0.0),
        xi_delta=controller_state.get('xi_delta', 0.0),
        upsilon_active=controller_state.get('upsilon_active', False),
        lambda_plus_active=controller_state.get('lambda_plus_active', False),
        phi33_violations=controller_state.get('phi33_violations', 0),
        curvature=controller_state.get('curvature', 0.0),
        torsion=controller_state.get('torsion', 0.0),
        state_hash=state_hash
    )