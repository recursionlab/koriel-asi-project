"""IO utilities for save/load and checkpoint management."""

import json
import pickle
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
import numpy as np

def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
        
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def save_config(config: Dict[str, Any], config_path: Union[str, Path]):
    """Save configuration to YAML file."""
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

def save_checkpoint(obj: Any, checkpoint_path: Union[str, Path]):
    """Save object checkpoint using pickle."""
    checkpoint_path = Path(checkpoint_path)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(checkpoint_path, 'wb') as f:
        pickle.dump(obj, f)

def load_checkpoint(checkpoint_path: Union[str, Path]) -> Any:
    """Load object checkpoint using pickle."""
    checkpoint_path = Path(checkpoint_path)
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
        
    with open(checkpoint_path, 'rb') as f:
        return pickle.load(f)

def save_results(results: Dict[str, Any], results_path: Union[str, Path]):
    """Save results to JSON file."""
    results_path = Path(results_path)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert numpy arrays to lists for JSON serialization
    def convert_numpy(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: convert_numpy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy(item) for item in obj]
        else:
            return obj
    
    serializable_results = convert_numpy(results)
    
    with open(results_path, 'w') as f:
        json.dump(serializable_results, f, indent=2)

def load_results(results_path: Union[str, Path]) -> Dict[str, Any]:
    """Load results from JSON file."""
    results_path = Path(results_path)
    if not results_path.exists():
        raise FileNotFoundError(f"Results file not found: {results_path}")
        
    with open(results_path, 'r') as f:
        return json.load(f)

def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if needed."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent

def get_config_dir() -> Path:
    """Get the configuration directory."""
    return get_project_root() / "config"

def get_checkpoints_dir() -> Path:
    """Get the checkpoints directory."""
    return get_project_root() / "checkpoints"

def get_results_dir() -> Path:
    """Get the results directory."""
    return get_project_root() / "results"