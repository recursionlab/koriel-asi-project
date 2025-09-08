import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import pandas as pd
from tqdm import tqdm
import os

from rcc.controller import (
    apply_upsilon, compute_rcce_metrics, ethical_guard, 
    xi_reflect, phi22_route
)

def train_one_epoch(model, dataset, state, lr=3e-4, steps=1000, log_every=50, batch_size=24):
    """Train model for one epoch with RCCE controller integration."""
    
    device = 'cpu'
    model = model.to(device)
    model.train()
    
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    optimizer = optim.AdamW(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    
    # Metrics tracking
    metrics_log = []
    attn_history = []
    logits_history = []
    step = 0
    
    pbar = tqdm(dataloader, desc="Training", total=min(steps, len(dataloader)))
    
    for batch_idx, (x, y) in enumerate(pbar):
        if step >= steps:
            break
            
        x, y = x.to(device), y.to(device)
        
        # Forward pass with attention weights
        logits, attn_list = model(x, return_attn=True)
        
        # Store for RCCE metrics
        attn_history.append(attn_list[-1])  # Use last layer attention
        logits_history.append(logits)
        
        # Apply Υ-gate modulation before loss
        if len(attn_history) >= 2:
            modulated_logits = apply_upsilon(logits, attn_list[-1], state)
        else:
            modulated_logits = logits
        
        # Compute loss
        loss = criterion(modulated_logits.view(-1, modulated_logits.size(-1)), y.view(-1))
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        
        # RCCE metrics computation and control
        if len(attn_history) >= 2:
            metrics = compute_rcce_metrics(attn_history[-2:], logits_history[-2:])
            
            # Apply RCCE control updates
            state = xi_reflect(state, metrics)
            
            # φ₂₂ router - check for torsion probe condition
            if metrics["dD"] > 0.05 and metrics["RC"] < 0.6:
                state = phi22_route("torsion_probe", state, metrics)
            elif metrics["RC"] > 0.7:
                state = phi22_route("reinject", state, metrics)
            
            # φ₃₃ ethical guard on generated sample
            if step % (log_every * 2) == 0:  # Check less frequently
                sample_tokens = torch.argmax(logits[0, -10:], dim=-1)  # Last 10 tokens
                ok, reason = ethical_guard(sample_tokens)
                if not ok:
                    # Apply ethical rollback
                    if 'bias' not in state or state['bias'] is None:
                        state['bias'] = torch.zeros(256)
                    state['bias'] *= 0.95
                    state['tau'] = max(0.3, state['tau'] * 0.9)
            
            # Logging
            if step % log_every == 0:
                metrics_entry = {
                    'step': step,
                    'loss': float(loss),
                    'tau': state['tau'],
                    'phase': state['phase'],
                    **{k: float(v) for k, v in metrics.items()}
                }
                metrics_log.append(metrics_entry)
                
                pbar.set_description(
                    f"Step {step}, Loss: {loss:.4f}, D: {metrics['D']:.4f}, "
                    f"H: {metrics['H']:.4f}, C: {metrics['C']:.4f}, RC: {metrics['RC']:.4f}"
                )
        
        step += 1
    
    # Save metrics to CSV
    if metrics_log:
        df = pd.DataFrame(metrics_log)
        csv_path = "rcce_train_metrics.csv"
        if os.path.exists(csv_path):
            df.to_csv(csv_path, mode='a', header=False, index=False)
        else:
            df.to_csv(csv_path, index=False)
        
        print(f"Logged {len(metrics_log)} metric entries to {csv_path}")
    
    return model, state, metrics_log