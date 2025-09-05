"""IO utilities for save/load and checkpoint management."""

import json
import pickle
import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
import numpy as np

def load_config(config_path: Union[str, Path], 
                apply_env_overrides: bool = True) -> Dict[str, Any]:
    """Load configuration from YAML file with optional environment overrides.
    
    Environment variables can override config values using the pattern:
    KORIEL_{SECTION}_{KEY} = value
    
    Examples:
        KORIEL_ENGINE_DT=0.002 overrides engine.dt
        KORIEL_SAFETY_MAX_ENERGY=15.0 overrides safety.max_energy
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
        
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    if apply_env_overrides:
        config = _apply_environment_overrides(config)
        
    return config

def _apply_environment_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to config."""
    env_prefix = "KORIEL_"
    
    for env_key, env_value in os.environ.items():
        if not env_key.startswith(env_prefix):
            continue
            
        # Parse KORIEL_SECTION_KEY format
        key_parts = env_key[len(env_prefix):].lower().split('_')
        if len(key_parts) < 2:
            continue
            
        section = key_parts[0]
        config_key = '_'.join(key_parts[1:])
        
        if section not in config:
            continue
            
        # Convert string values to appropriate types
        try:
            # Try to parse as number first
            if '.' in env_value:
                parsed_value = float(env_value)
            else:
                parsed_value = int(env_value)
        except ValueError:
            # Keep as string for booleans and other values
            if env_value.lower() in ('true', 'false'):
                parsed_value = env_value.lower() == 'true'
            else:
                parsed_value = env_value
        
        config[section][config_key] = parsed_value
        print(f"Config override from environment: {section}.{config_key} = {parsed_value}")
        
    return config

def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate configuration against bounds and constraints."""
    if 'bounds' not in config:
        return config
        
    validated_config = config.copy()
    bounds = config['bounds']
    
    # Validate engine parameters
    if 'engine' in config:
        engine_config = validated_config['engine']
        
        # Check dt bounds
        if 'dt' in bounds and 'dt' in engine_config:
            dt_min, dt_max = bounds['dt']
            if not (dt_min <= engine_config['dt'] <= dt_max):
                print(f"WARNING: dt={engine_config['dt']} outside bounds [{dt_min}, {dt_max}]")
                engine_config['dt'] = max(dt_min, min(dt_max, engine_config['dt']))
                
        # Check other bounded parameters
        for param in ['c_rate', 'c_thresh', 'field_size', 'evolution_steps']:
            if param in bounds and param in engine_config:
                param_min, param_max = bounds[param]
                if not (param_min <= engine_config[param] <= param_max):
                    print(f"WARNING: {param}={engine_config[param]} outside bounds [{param_min}, {param_max}]")
                    engine_config[param] = max(param_min, min(param_max, engine_config[param]))
    
    return validated_config

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
    return get_project_root() / "configs"

def get_default_config_path() -> Path:
    """Get the default configuration file path."""
    return get_config_dir() / "default.yaml"

def get_checkpoints_dir() -> Path:
    """Get the checkpoints directory."""
    return get_project_root() / "checkpoints"

def get_results_dir() -> Path:
    """Get the results directory."""
    return get_project_root() / "results"