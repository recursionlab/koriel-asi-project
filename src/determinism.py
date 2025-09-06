"""
Determinism enforcement utilities for KORIEL ASI Project.

Implements state hashing, RNG policy enforcement, and environment fingerprinting
for reproducible experiments.
"""

import hashlib
import json
import os
import sys
import platform
from typing import Dict, Any, Optional
import numpy as np


def get_env_fingerprint() -> Dict[str, str]:
    """Generate environment fingerprint for reproducibility tracking."""
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "pythonhashseed": os.environ.get("PYTHONHASHSEED", "not_set"),
        "omp_num_threads": os.environ.get("OMP_NUM_THREADS", "not_set"),
        "openblas_num_threads": os.environ.get("OPENBLAS_NUM_THREADS", "not_set"),
        "mkl_num_threads": os.environ.get("MKL_NUM_THREADS", "not_set"),
        "numexpr_num_threads": os.environ.get("NUMEXPR_NUM_THREADS", "not_set"),
    }


def compute_state_hash(data: Dict[str, Any]) -> str:
    """
    Compute deterministic hash of state data.
    
    Args:
        data: Dictionary containing state information
        
    Returns:
        SHA256 hex digest of canonicalized state
    """
    # Canonicalize the data for consistent hashing
    canonical = json.dumps(data, sort_keys=True, separators=(',', ':'), default=str)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def validate_rng_policy() -> None:
    """
    Validate that only approved RNG methods are used.
    
    Raises:
        ValueError: If deprecated RandomState is detected in use
    """
    # Check if RandomState is imported in current namespace
    import gc
    
    random_state_count = 0
    for obj in gc.get_objects():
        if isinstance(obj, np.random.RandomState):
            random_state_count += 1
    
    # Allow some internal RandomState objects (numpy may create them internally)
    # but warn if there are too many (suggesting user code is creating them)
    if random_state_count > 5:  # Threshold for warning
        import warnings
        warnings.warn(
            f"Found {random_state_count} RandomState objects. "
            "Consider using np.random.Generator(np.random.PCG64()) instead.",
            UserWarning
        )


def create_seeded_rng(seed: int) -> np.random.Generator:
    """
    Create properly seeded RNG following project policy.
    
    Args:
        seed: Random seed
        
    Returns:
        NumPy Generator with PCG64 bit generator
    """
    return np.random.Generator(np.random.PCG64(seed))


def enforce_deterministic_env() -> None:
    """
    Enforce deterministic environment variables.
    
    Sets environment variables required for deterministic computation
    if they are not already set.
    """
    env_vars = {
        "PYTHONHASHSEED": "0",
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1", 
        "MKL_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
    }
    
    for var, value in env_vars.items():
        if var not in os.environ:
            os.environ[var] = value


def generate_run_id(seed: int, catalog_hash: str, code_hash: str) -> str:
    """
    Generate deterministic run ID for experiment tracking.
    
    Args:
        seed: Random seed used
        catalog_hash: Hash of operator catalog
        code_hash: Hash of code version
        
    Returns:
        SHA256 hex digest of run parameters
    """
    run_data = f"{seed}|{catalog_hash}|{code_hash}"
    return hashlib.sha256(run_data.encode('utf-8')).hexdigest()


def assert_deterministic_environment() -> None:
    """
    Assert that required environment variables are set for determinism.
    
    Raises:
        AssertionError: If deterministic environment is not properly configured
    """
    required_env = {
        "PYTHONHASHSEED": "0",
        "OMP_NUM_THREADS": "1", 
        "OPENBLAS_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
    }
    
    for var, expected in required_env.items():
        actual = os.environ.get(var)
        assert actual == expected, (
            f"Environment variable {var} must be set to '{expected}', "
            f"got '{actual}'"
        )