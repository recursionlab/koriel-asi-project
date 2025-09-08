#!/usr/bin/env python
"""
Train tiny byte-LM with RCCE controller integration.
"""
import argparse
import os
import sys

import torch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from byte_lm.data import get_dataset
from byte_lm.model import TinyByteTransformer, count_parameters
from byte_lm.train import train_one_epoch
from rcc.controller import init_rcce_state


def main():
    parser = argparse.ArgumentParser(description="Train tiny byte-LM with RCCE")
    parser.add_argument("--steps", type=int, default=1000, help="Training steps")
    parser.add_argument("--block-size", type=int, default=128, help="Sequence length")
    parser.add_argument("--batch-size", type=int, default=24, help="Batch size")
    parser.add_argument("--lr", type=float, default=3e-4, help="Learning rate")
    parser.add_argument("--log-every", type=int, default=50, help="Log frequency")

    args = parser.parse_args()

    print("=== Tiny Byte-LM + RCCE Training ===")

    # Data paths
    data_paths = ["conversations-pocket", "data/raw"]

    print("Loading dataset...")
    dataset, meta = get_dataset(data_paths, args.block_size)
    print(f"Dataset: {len(dataset)} sequences, block_size={args.block_size}")
    print(f"Corpus: {meta['corpus_length']} bytes")

    if len(dataset) == 0:
        print(
            "ERROR: No data found! Add .txt/.md files to conversations-pocket/ or data/raw/"
        )
        return

    # Initialize model
    print("Creating model...")
    model = TinyByteTransformer(
        vocab_size=256,
        d_model=128,
        n_head=4,
        n_layer=2,
        seq_len=args.block_size,
        dropout=0.1,
    )

    param_count = count_parameters(model)
    print(f"Model parameters: {param_count:,}")

    # Initialize RCCE state
    state = init_rcce_state()
    print(f"Initial RCCE state: tau={state['tau']}, phase={state['phase']}")

    # Train
    print(f"Training for {args.steps} steps...")
    model, final_state, metrics_log = train_one_epoch(
        model,
        dataset,
        state,
        lr=args.lr,
        steps=args.steps,
        log_every=args.log_every,
        batch_size=args.batch_size,
    )

    # Save checkpoint
    os.makedirs("checkpoints", exist_ok=True)
    checkpoint_path = "checkpoints/tinylm.pt"
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "model_config": {
                "vocab_size": 256,
                "d_model": 128,
                "n_head": 4,
                "n_layer": 2,
                "seq_len": args.block_size,
                "dropout": 0.1,
            },
            "rcce_state": final_state,
            "training_args": vars(args),
        },
        checkpoint_path,
    )

    print(f"Saved checkpoint to {checkpoint_path}")
    print(f"Final RCCE state: {final_state}")

    if metrics_log:
        print(
            f"Logged {len(metrics_log)} RCCE metric entries to rcce_train_metrics.csv"
        )

        # Print final metrics summary
        import pandas as pd

        df = pd.DataFrame(metrics_log)
        final_metrics = df[["D", "H", "C", "RC", "E"]].iloc[-1]
        print("Final metrics:")
        for k, v in final_metrics.items():
            print(f"  {k}: {v:.4f}")


if __name__ == "__main__":
    main()
