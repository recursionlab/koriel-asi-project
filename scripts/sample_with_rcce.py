#!/usr/bin/env python
"""
Sample from trained byte-LM with RCCE modulation active.
"""
import argparse
import os
import torch
import pandas as pd
from rich.console import Console
from rich.table import Table

from src.byte_lm.model import TinyByteTransformer
from src.byte_lm.generate import generate_with_rcce, tokens_to_text

def main():
    parser = argparse.ArgumentParser(description='Sample from tiny byte-LM with RCCE')
    parser.add_argument('--tokens', type=int, default=400, help='Number of tokens to generate')
    parser.add_argument('--temperature', type=float, default=0.9, help='Sampling temperature')
    parser.add_argument('--prompt', type=str, default="The recursive", help='Text prompt')
    parser.add_argument('--checkpoint', type=str, default='checkpoints/tinylm.pt', help='Model checkpoint')
    
    args = parser.parse_args()
    console = Console()
    
    print("=== Tiny Byte-LM + RCCE Sampling ===")
    
    # Load checkpoint
    if not os.path.exists(args.checkpoint):
        print(f"ERROR: Checkpoint {args.checkpoint} not found!")
        print("Run train_tiny_lm.py first.")
        return
    
    checkpoint = torch.load(args.checkpoint, map_location='cpu')
    model_config = checkpoint['model_config']
    
    # Initialize model
    model = TinyByteTransformer(**model_config)
    model.load_state_dict(checkpoint['model_state_dict'])
    print(f"Loaded model from {args.checkpoint}")
    
    # Convert prompt to bytes/tokens
    prompt_bytes = args.prompt.encode('utf-8', errors='ignore')
    prompt_tokens = list(prompt_bytes)
    
    print(f"Prompt: '{args.prompt}' ({len(prompt_tokens)} bytes)")
    
    # Generate
    print(f"Generating {args.tokens} tokens with RCCE...")
    output_tokens, metrics_log = generate_with_rcce(
        model, prompt_tokens, 
        max_tokens=args.tokens,
        temperature=args.temperature
    )
    
    # Decode output
    generated_text = tokens_to_text(output_tokens[0])  # Remove batch dim
    
    print("\n" + "="*60)
    print("GENERATED TEXT:")
    print("="*60)
    print(generated_text)
    print("="*60)
    
    # Show metrics table
    if metrics_log:
        console.print("\n[bold]RCCE Metrics During Generation[/bold]")
        
        table = Table()
        table.add_column("Token")
        table.add_column("D")
        table.add_column("H") 
        table.add_column("C")
        table.add_column("RC")
        table.add_column("Y Fired")
        
        # Show every 10th entry to keep table manageable
        step = max(1, len(metrics_log) // 20)
        for i in range(0, len(metrics_log), step):
            entry = metrics_log[i]
            table.add_row(
                str(entry['token']),
                f"{entry['D']:.3f}",
                f"{entry['H']:.3f}", 
                f"{entry['C']:.3f}",
                f"{entry['RC']:.3f}",
                "Y" if entry['upsilon_fired'] else "-"
            )
        
        console.print(table)
        
        # Summary stats
        df = pd.DataFrame(metrics_log)
        upsilon_fires = sum(df['upsilon_fired'])
        print(f"\nY-gate fired {upsilon_fires}/{len(metrics_log)} times")
        print(f"Mean RC: {df['RC'].mean():.3f}")
        print(f"Mean D: {df['D'].mean():.3f}")

if __name__ == "__main__":
    main()