# src/robust_model.py
"""Enhanced model with defensive programming and error recovery"""
import warnings

import numpy as np


def safe_softmax(z, axis=-1, max_clip=50.0):
    """Numerically stable softmax with overflow protection"""
    # Clip extreme values to prevent overflow
    z_clipped = np.clip(z, -max_clip, max_clip)
    z_shifted = z_clipped - np.max(z_clipped, axis=axis, keepdims=True)
    exp_z = np.exp(z_shifted)
    return exp_z / (np.sum(exp_z, axis=axis, keepdims=True) + 1e-12)


def validate_input_shape(x, expected_dims, name="input"):
    """Validate input tensor shapes and fix common issues"""
    if not isinstance(x, np.ndarray):
        try:
            x = np.array(x)
        except Exception as e:
            raise ValueError(f"{name} cannot be converted to numpy array: {e}")

    if len(x.shape) != expected_dims:
        if expected_dims == 2 and len(x.shape) == 1:
            # Auto-expand 1D to 2D
            x = x.reshape(1, -1)
        elif expected_dims == 2 and len(x.shape) > 2:
            # Flatten extra dimensions
            x = x.reshape(x.shape[0], -1)
        else:
            raise ValueError(f"{name} has shape {x.shape}, expected {expected_dims}D")

    return x.astype(np.uint8) if name in ["input", "target"] else x.astype(np.float64)


class RobustTinyByteLM:
    """Enhanced TinyByteLM with error recovery and numerical stability"""

    def __init__(self, ctx=64, d=32, seed=1337, stability_checks=True):
        rng = np.random.default_rng(seed)
        self.ctx, self.d = ctx, d
        self.stability_checks = stability_checks

        # Initialize with better numerical properties
        std = 0.02 / np.sqrt(d)  # Xavier-like initialization
        self.E = (rng.standard_normal((256, d)) * std).astype(np.float64)
        self.W1 = (rng.standard_normal((d, d)) * std).astype(np.float64)
        self.b1 = np.zeros(d, dtype=np.float64)
        self.W2 = (rng.standard_normal((d, 256)) * std).astype(np.float64)
        self.b2 = np.zeros(256, dtype=np.float64)
        self.mask = np.zeros(256, dtype=np.float64)
        self.lr = 0.3

        # Error tracking
        self.error_count = 0
        self.last_stable_state = None
        self._x_cache = None
        self._h_cache = None

    def save_stable_state(self):
        """Save current parameters as stable checkpoint"""
        self.last_stable_state = {
            "E": self.E.copy(),
            "W1": self.W1.copy(),
            "b1": self.b1.copy(),
            "W2": self.W2.copy(),
            "b2": self.b2.copy(),
        }

    def restore_stable_state(self):
        """Restore parameters from last stable checkpoint"""
        if self.last_stable_state is not None:
            self.E = self.last_stable_state["E"].copy()
            self.W1 = self.last_stable_state["W1"].copy()
            self.b1 = self.last_stable_state["b1"].copy()
            self.W2 = self.last_stable_state["W2"].copy()
            self.b2 = self.last_stable_state["b2"].copy()
            warnings.warn("Restored from stable state due to numerical instability")

    def check_parameter_health(self):
        """Monitor parameter health and detect instability"""
        params = [self.E, self.W1, self.b1, self.W2, self.b2]

        for name, param in zip(["E", "W1", "b1", "W2", "b2"], params):
            if not np.isfinite(param).all():
                warnings.warn(f"Non-finite values in parameter {name}")
                return False

            param_norm = np.linalg.norm(param)
            if param_norm > 100.0:  # Parameter explosion
                warnings.warn(f"Parameter explosion in {name}: norm={param_norm}")
                return False

        return True

    def set_lr(self, lr: float):
        self.lr = max(1e-6, min(float(lr), 10.0))  # Clamp learning rate

    def set_mask(self, m: np.ndarray):
        m = np.nan_to_num(m.astype(np.float64), nan=0.0)
        self.mask = np.clip(m, -100.0, 100.0)  # Prevent extreme mask values

    def forward(self, x_bytes: np.ndarray):
        """Forward pass with input validation and error recovery"""
        try:
            # Input validation and sanitization
            x_bytes = validate_input_shape(x_bytes, 2, "input")

            # Clip to valid byte range
            x_bytes = np.clip(x_bytes, 0, 255).astype(np.uint8)

            emb = self.E[x_bytes]  # [B,T,d]
            h = emb.mean(axis=1)  # [B,d]

            # Numerically stable forward pass
            z1 = h @ self.W1 + self.b1
            z1_clipped = np.clip(z1, -10.0, 10.0)  # Prevent tanh saturation
            h1 = np.tanh(z1_clipped)

            logits = h1 @ self.W2 + self.b2 - self.mask

            # Numerical stability check
            if self.stability_checks and not np.isfinite(logits).all():
                warnings.warn("Non-finite logits detected, applying correction")
                logits = np.nan_to_num(logits, nan=0.0, posinf=10.0, neginf=-10.0)

            return logits, h1, h

        except Exception as e:
            self.error_count += 1
            warnings.warn(f"Forward pass error #{self.error_count}: {e}")

            # Return safe fallback values
            B = x_bytes.shape[0] if hasattr(x_bytes, "shape") else 1
            return (np.zeros((B, 256)), np.zeros((B, self.d)), np.zeros((B, self.d)))

    def step(self, x: np.ndarray, y: np.ndarray, lr=None):
        """Training step with error recovery and gradient clipping"""
        if lr is None:
            lr = self.lr
        lr = max(1e-6, min(float(lr), 1.0))  # Clamp learning rate

        try:
            # Save state before risky operation
            if self.stability_checks:
                self.save_stable_state()

            # Input validation
            x = validate_input_shape(x, 2, "input")
            y = validate_input_shape(y, 2, "target")

            B, T = x.shape
            if B != y.shape[0] or T != y.shape[1]:
                raise ValueError(f"Shape mismatch: x={x.shape}, y={y.shape}")

            # Forward pass
            logits, h1, h = self.forward(x)
            self.cache_io(x, h)

            # Stable softmax and loss computation
            probs = safe_softmax(logits)
            y_last = y[:, -1]

            # Ensure valid indices
            y_last = np.clip(y_last, 0, 255).astype(np.int64)

            # Cross-entropy loss with numerical stability
            selected_probs = probs[np.arange(B), y_last]
            selected_probs = np.clip(selected_probs, 1e-9, 1.0)
            loss = -np.log(selected_probs).mean()

            if not np.isfinite(loss):
                warnings.warn("Non-finite loss, skipping update")
                return float(loss), probs, h1

            # Backward pass with gradient clipping
            dlogits = probs.copy()
            dlogits[np.arange(B), y_last] -= 1.0
            dlogits /= B

            # Gradient clipping
            grad_norm = np.linalg.norm(dlogits)
            if grad_norm > 5.0:  # Gradient clipping threshold
                dlogits = dlogits * (5.0 / grad_norm)

            # Parameter updates with clipping
            dW2 = h1.T @ dlogits
            db2 = dlogits.sum(axis=0)
            dh1 = dlogits @ self.W2.T
            dh = (1.0 - h1 * h1) * dh1
            dW1 = h.T @ dh
            db1 = dh.sum(axis=0)

            # Embedding gradients
            dE = np.zeros_like(self.E)
            for b in range(B):
                if hasattr(self, "_x_cache") and self._x_cache is not None:
                    idxs = self._x_cache[b]
                    if len(idxs) > 0:
                        g = (dh[b] @ self.W1.T) / len(idxs)
                        dE[idxs] += g

            # Clip gradients to prevent explosion
            for grad in [dW2, db2, dW1, db1, dE]:
                np.clip(grad, -1.0, 1.0, out=grad)

            # Apply updates
            self.W2 -= lr * dW2
            self.b2 -= lr * db2
            self.W1 -= lr * dW1
            self.b1 -= lr * db1
            self.E -= lr * dE

            # Health check after update
            if self.stability_checks and not self.check_parameter_health():
                self.restore_stable_state()
                self.error_count += 1

            return float(loss), probs, h1

        except Exception as e:
            self.error_count += 1
            warnings.warn(f"Training step error #{self.error_count}: {e}")

            if self.stability_checks and self.last_stable_state is not None:
                self.restore_stable_state()

            # Return safe fallback
            B = 1
            try:
                B = x.shape[0]
            except Exception:
                pass
            return 10.0, np.ones((B, 256)) / 256.0, np.zeros((B, self.d))

    def cache_io(self, x: np.ndarray, h: np.ndarray):
        """Cache inputs/outputs for gradient computation"""
        try:
            self._x_cache = x
            self._h_cache = h
        except Exception as e:
            warnings.warn(f"Caching error: {e}")


# Export as drop-in replacement
TinyByteLM = RobustTinyByteLM
