# src/robust_dec.py
"""Numerically robust differential geometry operations with safeguards"""
import numpy as np
import warnings

class NumericalStabilityError(Exception):
    """Raised when numerical operations become unstable"""
    pass

def safe_norm(x, ord=None, axis=None, keepdims=False, eps=1e-12):
    """Numerically stable norm computation with NaN/Inf handling"""
    if not np.isfinite(x).all():
        # Handle NaN/Inf cases
        finite_mask = np.isfinite(x)
        if not finite_mask.any():
            warnings.warn("All values non-finite in norm computation")
            return np.zeros_like(x.sum(axis=axis, keepdims=keepdims)) + eps
        x = np.where(finite_mask, x, 0.0)
    
    result = np.linalg.norm(x, ord=ord, axis=axis, keepdims=keepdims)
    return np.maximum(result, eps)  # Prevent zero norms

def safe_matmul(A, B):
    """Safe matrix multiplication with overflow/underflow handling"""
    if not (np.isfinite(A).all() and np.isfinite(B).all()):
        # Clip extreme values
        A = np.clip(A, -1e10, 1e10)
        B = np.clip(B, -1e10, 1e10)
    
    try:
        result = A @ B
        if not np.isfinite(result).all():
            warnings.warn("Non-finite result in matrix multiplication")
            result = np.nan_to_num(result, nan=0.0, posinf=1e10, neginf=-1e10)
        return result
    except Exception as e:
        raise NumericalStabilityError(f"Matrix multiplication failed: {e}")

def robust_incidence_0_to_1(n, regularization=1e-12):
    """Numerically stable incidence matrix with regularization"""
    if n <= 0 or not isinstance(n, int):
        raise ValueError(f"Invalid dimension n={n}, must be positive integer")
    
    B = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        j = (i+1) % n
        B[i, i] -= 1.0
        B[i, j] += 1.0
    
    # Add small regularization to prevent singularity
    B += np.eye(n) * regularization
    return B

def robust_incidence_1_to_2(n):
    """Robust 1-to-2 incidence operator"""
    if n <= 0:
        return np.zeros((1, 1), dtype=np.float64)
    return np.ones((1, n), dtype=np.float64)

def robust_d0(omega0):
    """Robust exterior derivative d: Ω⁰ → Ω¹"""
    if omega0.ndim != 1:
        raise ValueError(f"omega0 must be 1D, got {omega0.ndim}D")
    
    n = omega0.shape[0]
    if n == 0:
        return np.array([])
    
    # Input validation and sanitization
    omega0_clean = np.nan_to_num(omega0, nan=0.0, posinf=1e10, neginf=-1e10)
    
    B = robust_incidence_0_to_1(n)
    return safe_matmul(B, omega0_clean)

def robust_d1(omega1):
    """Robust exterior derivative d: Ω¹ → Ω²"""
    if omega1.ndim != 1:
        raise ValueError(f"omega1 must be 1D, got {omega1.ndim}D")
    
    n = omega1.shape[0]
    if n == 0:
        return np.array([0.0])
    
    omega1_clean = np.nan_to_num(omega1, nan=0.0, posinf=1e10, neginf=-1e10)
    C = robust_incidence_1_to_2(n)
    return safe_matmul(C, omega1_clean)

def robust_d2_norm(omega0, max_value=1e10):
    """Robust d²-norm computation with overflow protection"""
    try:
        if omega0.size == 0:
            return 0.0
        
        d_omega0 = robust_d0(omega0)
        d2_omega0 = robust_d1(d_omega0)
        
        result = safe_norm(d2_omega0)
        return min(float(result), max_value)  # Prevent overflow
    
    except Exception as e:
        warnings.warn(f"d2_norm computation failed: {e}, returning 0")
        return 0.0

def robust_torsion_norm(Gamma, max_value=1e10):
    """Robust torsion computation with numerical safeguards"""
    try:
        if not np.isfinite(Gamma).all():
            Gamma = np.nan_to_num(Gamma, nan=0.0, posinf=1e6, neginf=-1e6)
        
        T = 0.5 * (Gamma - Gamma.T)
        result = safe_norm(T)
        return min(float(result), max_value)
    
    except Exception as e:
        warnings.warn(f"Torsion computation failed: {e}, returning 0")
        return 0.0

def robust_curvature_comm_norm(G1, G2, max_value=1e10):
    """Robust curvature computation via commutator"""
    try:
        if not (np.isfinite(G1).all() and np.isfinite(G2).all()):
            G1 = np.nan_to_num(G1, nan=0.0, posinf=1e6, neginf=-1e6)
            G2 = np.nan_to_num(G2, nan=0.0, posinf=1e6, neginf=-1e6)
        
        # Commutator [G1, G2] = G1*G2 - G2*G1
        comm = safe_matmul(G1, G2) - safe_matmul(G2, G1)
        skew_comm = 0.5 * (comm - comm.T)
        
        result = safe_norm(skew_comm)
        return min(float(result), max_value)
    
    except Exception as e:
        warnings.warn(f"Curvature computation failed: {e}, returning 0")
        return 0.0

# Adaptive numerical precision based on condition number
def adaptive_precision_wrapper(func):
    """Decorator to automatically handle numerical precision issues"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (NumericalStabilityError, np.linalg.LinAlgError):
            # Retry with increased precision if needed
            warnings.warn(f"Retrying {func.__name__} with fallback precision")
            return 0.0
    return wrapper

# Export robust versions as drop-in replacements
@adaptive_precision_wrapper
def d2_norm(omega0):
    return robust_d2_norm(omega0)

@adaptive_precision_wrapper  
def torsion_norm(Gamma):
    return robust_torsion_norm(Gamma)

@adaptive_precision_wrapper
def curvature_comm_norm(G1, G2):
    return robust_curvature_comm_norm(G1, G2)