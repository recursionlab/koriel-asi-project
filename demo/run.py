#!/usr/bin/env python
"""
KORIEL ASI Demo Runner
Smoke test demo that generates required artifacts for validation.
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import existing demo functionality
sys.path.append(str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
from scripts.run_rcce_demo import run_demo as run_rcce_demo


def setup_logging(output_dir: Path, level=logging.INFO):
    """Setup logging to both console and file"""
    log_file = output_dir / "logs.txt"
    
    # Create formatters
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    
    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # File handler
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


def run_basic_demo(seed: int, output_dir: Path):
    """Run basic RCCE demo and capture results"""
    logger = logging.getLogger()
    logger.info(f"Starting basic demo with seed {seed}")
    
    # Change to output directory to capture CSV files
    original_dir = os.getcwd()
    os.chdir(output_dir)
    
    try:
        # Run the RCCE demo with specified seed
        logger.info("Running RCCE demo...")
        run_rcce_demo(seed=seed, T=80, N=32, Dval=16, Nt=4)  # Smaller params for smoke test
        
        # Read the generated CSV file
        csv_file = Path("rcce_run_metrics.csv")  # File is created in current directory
        if csv_file.exists():
            df = pd.read_csv(csv_file)
            logger.info(f"Demo generated {len(df)} timesteps of metrics")
            
            # Extract key results
            results = {
                "timesteps": len(df),
                "final_RC": float(df["RC"].iloc[-1]),
                "final_energy": float(df["E"].iloc[-1]),
                "mean_coherence": float(df["RC"].mean()),
                "upsilon_fires": int(df["Y"].sum()),
                "ethics_violations": int((df["ethic"] > 0.2).sum()),
                "drift_stability": float(df["D"].std()),
                "entropy_evolution": {
                    "initial": float(df["H"].iloc[0]),
                    "final": float(df["H"].iloc[-1]),
                    "mean": float(df["H"].mean())
                },
                "consciousness_score": float(df["C"].mean()),
                "metrics_summary": df[["D", "H", "C", "RC", "E", "ZI", "ce2", "ethic", "Y"]].mean().to_dict()
            }
            
            logger.info(f"Final RC: {results['final_RC']:.4f}")
            logger.info(f"Upsilon fires: {results['upsilon_fires']}")
            logger.info(f"Ethics violations: {results['ethics_violations']}")
            
            return results
        else:
            logger.error("RCCE demo did not generate expected CSV file")
            return {"error": "No metrics file generated"}
            
    except Exception as e:
        logger.error(f"Demo execution failed: {e}")
        return {"error": str(e)}
    finally:
        os.chdir(original_dir)


def generate_metadata(task: str, seed: int, output_dir: Path, git_sha: str):
    """Generate metadata.json artifact"""
    # Import determinism utilities
    sys.path.append(str(Path(__file__).parent.parent / "src"))
    from determinism import get_env_fingerprint, compute_state_hash
    
    # Generate environment fingerprint
    env_fingerprint = get_env_fingerprint()
    
    metadata = {
        "experiment_id": f"{task}_{seed}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "task": task,
        "seed": seed,
        "git_sha": git_sha,
        "timestamp": datetime.now().isoformat(),
        "output_directory": str(output_dir),
        "python_version": sys.version,
        "environment": {
            "working_directory": os.getcwd(),
            "user": os.environ.get("USER", "unknown"),
            "system": os.name
        },
        "parameters": {
            "demo_type": "rcce_basic",
            "timesteps": 80,
            "attention_dim": 32,
            "value_dim": 16,
            "topic_bins": 4
        },
        "schema_version": "2.0",
        "env_fingerprint": env_fingerprint
    }
    
    # Compute state hash of the metadata (excluding state_hash itself)
    state_hash = compute_state_hash(metadata)
    metadata["state_hash"] = state_hash
    
    metadata_file = output_dir / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logging.info(f"Generated metadata: {metadata_file}")
    return metadata


def generate_results(demo_results: dict, output_dir: Path):
    """Generate results.json artifact"""
    results = {
        "status": "success" if "error" not in demo_results else "error",
        "demo_results": demo_results,
        "validation": {
            "rc_improvement": demo_results.get("final_RC", 0) > demo_results.get("metrics_summary", {}).get("RC", 0) * 0.8,
            "ethics_clean": demo_results.get("ethics_violations", 1) == 0,
            "stability_check": demo_results.get("drift_stability", 999) < 1.0,
            "upsilon_active": demo_results.get("upsilon_fires", 0) > 0
        },
        "artifacts_generated": [
            "metadata.json",
            "results.json", 
            "logs.txt",
            "rcce_run_metrics.csv"
        ]
    }
    
    results_file = output_dir / "results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logging.info(f"Generated results: {results_file}")
    return results


def main():
    """Main entry point for demo runner"""
    parser = argparse.ArgumentParser(description="KORIEL ASI Demo Runner")
    parser.add_argument("--task", required=True, help="Demo task to run (basic, advanced, etc.)")
    parser.add_argument("--seed", type=int, required=True, help="Random seed for reproducibility")
    parser.add_argument("--out", required=True, help="Output directory for artifacts")
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup logging
    logger = setup_logging(output_dir)
    
    # Get git SHA
    try:
        import subprocess
        git_sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], 
                                        cwd=Path(__file__).parent.parent).decode().strip()
    except:
        git_sha = "unknown"
    
    logger.info(f"Starting demo: task={args.task}, seed={args.seed}, git_sha={git_sha}")
    
    # Generate metadata
    metadata = generate_metadata(args.task, args.seed, output_dir, git_sha)
    
    # Run demo based on task
    if args.task == "basic":
        demo_results = run_basic_demo(args.seed, output_dir)
    else:
        logger.error(f"Unknown task: {args.task}")
        demo_results = {"error": f"Unknown task: {args.task}"}
    
    # Generate results
    results = generate_results(demo_results, output_dir)
    
    # Final status
    if results["status"] == "success":
        logger.info("Demo completed successfully")
        logger.info(f"Artifacts generated in: {output_dir}")
        sys.exit(0)
    else:
        logger.error("Demo failed")
        sys.exit(1)


if __name__ == "__main__":
    main()