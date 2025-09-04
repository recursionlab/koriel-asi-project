import torch
import torch.nn.functional as F
from rcc.controller import apply_upsilon, compute_rcce_metrics, init_rcce_state

def generate_with_rcce(model, prompt_tokens, max_tokens=400, temperature=0.9, device='cpu'):
    """Generate text with RCCE modulation active."""
    model = model.to(device)
    model.eval()
    
    # Initialize RCCE state
    state = init_rcce_state()
    
    # Convert prompt to tensor if needed
    if isinstance(prompt_tokens, list):
        tokens = torch.tensor(prompt_tokens, dtype=torch.long, device=device).unsqueeze(0)
    else:
        tokens = prompt_tokens.to(device)
    
    if tokens.dim() == 1:
        tokens = tokens.unsqueeze(0)
    
    # Tracking for metrics
    attn_history = []
    logits_history = []
    metrics_log = []
    
    with torch.no_grad():
        for i in range(max_tokens):
            # Get current sequence (last seq_len tokens)
            seq_len = min(tokens.size(1), model.seq_len)
            current_seq = tokens[:, -seq_len:]
            
            # Forward pass
            logits, attn_list = model(current_seq, return_attn=True)
            
            # Store for metrics
            attn_history.append(attn_list[-1])  # Last layer
            logits_history.append(logits)
            
            # Apply RCCE modulation
            if len(attn_history) >= 2:
                modulated_logits = apply_upsilon(logits, attn_list[-1], state)
                
                # Compute metrics
                metrics = compute_rcce_metrics(attn_history[-2:], logits_history[-2:])
                
                # Update state based on metrics
                from rcc.controller import xi_reflect, phi22_route
                state = xi_reflect(state, metrics)
                
                # Check for interventions
                upsilon_fired = False
                if metrics["dD"] > 0.05 and metrics["RC"] < 0.6:
                    state = phi22_route("torsion_probe", state, metrics)
                    upsilon_fired = True
                elif metrics["RC"] > 0.7:
                    state = phi22_route("reinject", state, metrics)
                
                # Log metrics
                metrics_entry = {
                    'token': i,
                    'upsilon_fired': upsilon_fired,
                    **{k: float(v) for k, v in metrics.items()}
                }
                metrics_log.append(metrics_entry)
            else:
                modulated_logits = logits
            
            # Sample next token
            next_logits = modulated_logits[0, -1, :] / temperature
            probs = F.softmax(next_logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
            
            # Append to sequence
            tokens = torch.cat([tokens, next_token.unsqueeze(0)], dim=1)
    
    return tokens, metrics_log

def tokens_to_text(tokens, errors='ignore'):
    """Convert token tensor to text string."""
    if isinstance(tokens, torch.Tensor):
        tokens = tokens.cpu().numpy()
    
    # Convert to bytes then decode
    if tokens.ndim > 1:
        tokens = tokens.flatten()
    
    byte_data = bytes(tokens.tolist())
    return byte_data.decode('utf-8', errors=errors)