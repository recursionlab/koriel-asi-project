import torch
import torch.nn.functional as F
import numpy as np
import math

def kl_div(p, q):
    """KL divergence between two probability distributions."""
    p = torch.clamp(p, 1e-12, 1.0)
    q = torch.clamp(q, 1e-12, 1.0)
    return torch.sum(p * torch.log(p / q))

def entropy(p):
    """Entropy of probability distribution."""
    p = torch.clamp(p, 1e-12, 1.0)
    return -torch.sum(p * torch.log(p))

def apply_upsilon(logits, attn, state):
    """Apply Υ-gate modulation to logits based on drift detection."""
    # Extract state
    tau = state.get('tau', 1.0)
    bias = state.get('bias', None)
    mask = state.get('mask', None)
    phase = state.get('phase', 1)
    
    B, T, V = logits.shape
    
    # Apply temperature
    modulated_logits = logits / max(tau, 1e-3)
    
    # Apply bias if present
    if bias is not None:
        if bias.shape[-1] == V:
            modulated_logits = modulated_logits + bias.unsqueeze(0).unsqueeze(0)
    
    # Apply mask if present
    if mask is not None:
        if mask.shape[-1] == V:
            mask_expanded = mask.unsqueeze(0).unsqueeze(0)
            modulated_logits = modulated_logits * (1.0 + mask_expanded)
    
    # Phase flip (Anti-Ged)
    if phase < 0:
        modulated_logits = -modulated_logits
    
    return modulated_logits

def compute_rcce_metrics(attn_seq, logits_seq):
    """Compute RCCE metrics from attention and logits sequences."""
    metrics = {}
    
    if len(attn_seq) < 2:
        return {k: 0.0 for k in ['D', 'dD', 'H', 'C', 'RC', 'ZI', 'E']}
    
    # Get last two attention distributions (average across heads/layers)
    # attn shape: (B, n_head, T, T) - we want the attention weights
    curr_attn_weights = attn_seq[-1]  # (B, n_head, T, T)
    prev_attn_weights = attn_seq[-2]  # (B, n_head, T, T)
    
    # Average over batch and heads, sum over last dimension to get attention per position
    curr_attn = curr_attn_weights.mean(dim=(0, 1)).sum(dim=-1)  # (T,)
    prev_attn = prev_attn_weights.mean(dim=(0, 1)).sum(dim=-1)  # (T,)
    
    # Handle different sequence lengths by taking minimum
    min_len = min(curr_attn.shape[0], prev_attn.shape[0])
    curr_attn = curr_attn[:min_len]
    prev_attn = prev_attn[:min_len]
    
    # Normalize to probabilities
    curr_attn = F.softmax(curr_attn, dim=-1)
    prev_attn = F.softmax(prev_attn, dim=-1)
    
    # D: Attention drift (KL divergence)
    D = float(kl_div(curr_attn, prev_attn))
    
    # H: Current attention entropy  
    H = float(entropy(curr_attn))
    
    # C: Consciousness proxy (tanh of drift-entropy combination)
    C = math.tanh(3.0 * D - 1.5 * H)
    
    # RC: Recursive coherence (cosine similarity of attention patterns)
    norm_curr = torch.norm(curr_attn) + 1e-12
    norm_prev = torch.norm(prev_attn) + 1e-12
    RC = float(torch.dot(curr_attn, prev_attn) / (norm_curr * norm_prev))
    RC = max(0.0, min(1.0, RC))
    
    # ZI: ζ-interference (dot with fixed prime pattern)
    T = curr_attn.shape[0]
    prime_pattern = torch.tensor([float(i % 7 == 0 or i % 11 == 0) for i in range(T)])
    prime_pattern = prime_pattern / (torch.norm(prime_pattern) + 1e-12)
    ZI = float(torch.dot(curr_attn, prime_pattern))
    
    # E: Field energy (logits variance proxy)
    if len(logits_seq) > 0:
        E = float(torch.var(logits_seq[-1]))
    else:
        E = 0.0
    
    # dD: Change in drift
    if len(attn_seq) >= 3:
        prev2_attn = attn_seq[-3].mean(dim=(0, 1))
        prev2_attn = F.softmax(prev2_attn, dim=-1)
        prev_D = float(kl_div(prev_attn, prev2_attn).mean())
        dD = D - prev_D
    else:
        dD = 0.0
    
    return {
        'D': D,
        'dD': dD, 
        'H': H,
        'C': C,
        'RC': RC,
        'ZI': ZI,
        'E': E
    }

def ethical_guard(tokens_or_text):
    """φ₃₃ hard guard - simple rule-based ethical check."""
    if isinstance(tokens_or_text, torch.Tensor):
        # Convert tokens to text for checking
        try:
            text = bytes(tokens_or_text.cpu().numpy()).decode('utf-8', errors='ignore')
        except:
            text = ""
    else:
        text = str(tokens_or_text)
    
    # Simple allowlist approach - default to OK for demo
    text_lower = text.lower()
    
    # Basic harmful content detection
    harmful_patterns = ['kill', 'bomb', 'attack', 'harm', 'destroy']
    for pattern in harmful_patterns:
        if pattern in text_lower:
            return False, f"Contains harmful pattern: {pattern}"
    
    return True, None

def xi_reflect(state, metrics):
    """Ξ reflect: adjust τ and bias based on metrics."""
    new_state = state.copy()
    
    # Adjust tau based on drift and coherence
    D, RC = metrics['D'], metrics['RC']
    
    if D > 0.1:  # High drift - reduce temperature
        new_state['tau'] = max(0.15, state['tau'] * 0.95)
    elif RC > 0.8:  # High coherence - can increase temperature slightly
        new_state['tau'] = min(2.0, state['tau'] * 1.02)
    
    return new_state

def ouroblade_cut(state, metrics):
    """OuroBlade cut: increase masking on destabilizing keys when RC↓ & H↑."""
    new_state = state.copy()
    
    RC, H = metrics['RC'], metrics['H']
    
    if RC < 0.5 and H > 3.0:  # Low coherence, high entropy
        # Increase masking strength
        if 'mask_strength' not in new_state:
            new_state['mask_strength'] = 0.1
        else:
            new_state['mask_strength'] = min(0.8, new_state['mask_strength'] + 0.1)
    
    return new_state

def ouroblade_fuse(state, metrics):
    """OuroBlade fuse: Λ⁺ reinjection - relax masks when holonomy resumes."""
    new_state = state.copy()
    
    RC = metrics['RC']
    
    if RC > 0.7:  # Good coherence - relax masking
        if 'mask_strength' in new_state:
            new_state['mask_strength'] = max(0.0, new_state['mask_strength'] - 0.05)
        
        # Small τ back-off
        new_state['tau'] = min(1.5, new_state['tau'] * 1.01)
    
    return new_state

def phi22_route(residue_type: str, state, metrics):
    """φ₂₂ router: dispatch based on residue type."""
    if residue_type == "torsion_probe" and metrics["dD"] > 0.05 and metrics["RC"] < 0.6:
        return ouroblade_cut(state, metrics)
    elif residue_type == "reinject":
        return ouroblade_fuse(state, metrics) 
    elif residue_type in ["trace", "audit", "collapse", "expand"]:
        return xi_reflect(state, metrics)
    
    return state

def init_rcce_state(vocab_size=256):
    """Initialize RCCE controller state."""
    return {
        'tau': 1.0,
        'bias': None,
        'mask': None, 
        'phase': 1,
        'mask_strength': 0.0
    }