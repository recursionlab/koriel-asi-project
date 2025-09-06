"""
Minimal Byte-Level Language Model
Pure numpy implementation for CPU training
"""

from typing import Dict, Tuple

import numpy as np


class ByteLM:
    def __init__(
        self,
        vocab_size: int = 256,
        d_model: int = 128,
        n_heads: int = 4,
        n_layers: int = 2,
    ):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.n_heads = n_heads
        self.n_layers = n_layers
        self.head_dim = d_model // n_heads

        # Initialize parameters
        self.params = self._init_parameters()

    def _init_parameters(self) -> Dict[str, np.ndarray]:
        """Initialize all model parameters"""
        params = {}

        # Token embeddings
        params["token_embed"] = np.random.normal(
            0, 0.02, (self.vocab_size, self.d_model)
        )

        # Attention layers
        for i in range(self.n_layers):
            # Multi-head attention
            params[f"attn_{i}_qkv"] = np.random.normal(
                0, 0.02, (self.d_model, 3 * self.d_model)
            )
            params[f"attn_{i}_proj"] = np.random.normal(
                0, 0.02, (self.d_model, self.d_model)
            )

            # Feed forward
            params[f"ff_{i}_w1"] = np.random.normal(
                0, 0.02, (self.d_model, 4 * self.d_model)
            )
            params[f"ff_{i}_w2"] = np.random.normal(
                0, 0.02, (4 * self.d_model, self.d_model)
            )

            # Layer norms
            params[f"ln1_{i}_weight"] = np.ones(self.d_model)
            params[f"ln1_{i}_bias"] = np.zeros(self.d_model)
            params[f"ln2_{i}_weight"] = np.ones(self.d_model)
            params[f"ln2_{i}_bias"] = np.zeros(self.d_model)

        # Final layer norm and output projection
        params["ln_f_weight"] = np.ones(self.d_model)
        params["ln_f_bias"] = np.zeros(self.d_model)
        params["lm_head"] = np.random.normal(0, 0.02, (self.d_model, self.vocab_size))

        return params

    def layer_norm(
        self, x: np.ndarray, weight: np.ndarray, bias: np.ndarray, eps: float = 1e-5
    ) -> np.ndarray:
        """Layer normalization"""
        mean = np.mean(x, axis=-1, keepdims=True)
        var = np.var(x, axis=-1, keepdims=True)
        return weight * (x - mean) / np.sqrt(var + eps) + bias

    def softmax(self, x: np.ndarray, axis: int = -1) -> np.ndarray:
        """Softmax activation"""
        exp_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
        return exp_x / np.sum(exp_x, axis=axis, keepdims=True)

    def gelu(self, x: np.ndarray) -> np.ndarray:
        """GELU activation function"""
        return 0.5 * x * (1 + np.tanh(np.sqrt(2 / np.pi) * (x + 0.044715 * x**3)))

    def attention(self, x: np.ndarray, layer_idx: int) -> Tuple[np.ndarray, np.ndarray]:
        """Multi-head self-attention"""
        seq_len, d_model = x.shape

        # QKV projection
        qkv = x @ self.params[f"attn_{layer_idx}_qkv"]
        q, k, v = np.split(qkv, 3, axis=-1)

        # Reshape for multi-head attention
        q = q.reshape(seq_len, self.n_heads, self.head_dim).transpose(1, 0, 2)
        k = k.reshape(seq_len, self.n_heads, self.head_dim).transpose(1, 0, 2)
        v = v.reshape(seq_len, self.n_heads, self.head_dim).transpose(1, 0, 2)

        # Scaled dot-product attention
        scores = np.matmul(q, k.transpose(0, 2, 1)) / np.sqrt(self.head_dim)

        # Causal mask
        mask = np.triu(np.ones((seq_len, seq_len)), k=1) * -1e9
        scores = scores + mask

        # Attention weights
        attn_weights = self.softmax(scores)

        # Apply attention
        out = np.matmul(attn_weights, v)

        # Concatenate heads
        out = out.transpose(1, 0, 2).reshape(seq_len, d_model)

        # Output projection
        out = out @ self.params[f"attn_{layer_idx}_proj"]

        return out, attn_weights

    def feed_forward(self, x: np.ndarray, layer_idx: int) -> np.ndarray:
        """Feed forward network"""
        h = self.gelu(x @ self.params[f"ff_{layer_idx}_w1"])
        return h @ self.params[f"ff_{layer_idx}_w2"]

    def forward(self, tokens: np.ndarray) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """Forward pass through the model"""
        seq_len = len(tokens)

        # Token embeddings
        x = self.params["token_embed"][tokens]

        # Store activations for RCCE analysis
        activations = {"input": x.copy()}
        attention_maps = {}

        # Transformer layers
        for i in range(self.n_layers):
            # Pre-norm attention
            normed = self.layer_norm(
                x, self.params[f"ln1_{i}_weight"], self.params[f"ln1_{i}_bias"]
            )
            attn_out, attn_weights = self.attention(normed, i)
            x = x + attn_out

            # Pre-norm feed forward
            normed = self.layer_norm(
                x, self.params[f"ln2_{i}_weight"], self.params[f"ln2_{i}_bias"]
            )
            ff_out = self.feed_forward(normed, i)
            x = x + ff_out

            activations[f"layer_{i}"] = x.copy()
            attention_maps[f"layer_{i}"] = attn_weights

        # Final layer norm
        x = self.layer_norm(x, self.params["ln_f_weight"], self.params["ln_f_bias"])

        # Language modeling head
        logits = x @ self.params["lm_head"]

        activations["output"] = x.copy()

        return logits, {
            "activations": activations,
            "attention_maps": attention_maps,
            "sequence_length": seq_len,
        }

    def compute_loss(self, logits: np.ndarray, targets: np.ndarray) -> float:
        """Cross-entropy loss computation"""
        # Shift targets for next-token prediction
        logits = logits[:-1]
        targets = targets[1:]

        # Softmax and cross-entropy
        probs = self.softmax(logits)
        log_probs = np.log(probs + 1e-8)

        # Gather target probabilities
        target_log_probs = log_probs[np.arange(len(targets)), targets]

        return -np.mean(target_log_probs)

    def get_geometric_state(
        self, activations: Dict[str, np.ndarray]
    ) -> Dict[str, float]:
        """Extract geometric properties from model state"""
        metrics = {}

        # Compute entropy across layers
        for layer_name, acts in activations.items():
            if acts.ndim == 2:  # sequence x features
                # Information entropy
                probs = self.softmax(acts, axis=-1)
                entropy = -np.sum(probs * np.log(probs + 1e-8), axis=-1)
                metrics[f"{layer_name}_entropy"] = np.mean(entropy)

                # Activation magnitude
                metrics[f"{layer_name}_magnitude"] = np.linalg.norm(acts)

                # Spectral radius (largest eigenvalue)
                if acts.shape[0] > 1:
                    cov = np.cov(acts.T)
                    eigenvals = np.linalg.eigvals(cov)
                    metrics[f"{layer_name}_spectral_radius"] = np.max(
                        np.real(eigenvals)
                    )

        return metrics
