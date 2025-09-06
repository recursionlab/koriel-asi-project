"""Minimal byte language model - numpy only"""

import numpy as np


class ByteLM:
    def __init__(self, vocab_size=256, d_model=32, seed=1337):
        np.random.seed(seed)
        self.vocab_size = vocab_size
        self.d_model = d_model

        # Single-head self-attention + MLP
        self.embed = np.random.normal(0, 0.02, (vocab_size, d_model))
        self.W_q = np.random.normal(0, 0.02, (d_model, d_model))
        self.W_k = np.random.normal(0, 0.02, (d_model, d_model))
        self.W_v = np.random.normal(0, 0.02, (d_model, d_model))
        self.W_o = np.random.normal(0, 0.02, (d_model, d_model))
        self.W1 = np.random.normal(0, 0.02, (d_model, d_model * 2))
        self.W2 = np.random.normal(0, 0.02, (d_model * 2, d_model))
        self.W_out = np.random.normal(0, 0.02, (d_model, vocab_size))

    def attention(self, x):
        """Single-head self-attention"""
        seq_len = x.shape[0]

        Q = x @ self.W_q
        K = x @ self.W_k
        V = x @ self.W_v

        # Attention scores
        scores = Q @ K.T / np.sqrt(self.d_model)

        # Causal mask
        mask = np.triu(np.ones((seq_len, seq_len)), k=1) * -1e9
        scores = scores + mask

        # Softmax
        exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
        attn_weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)

        # Apply attention
        out = attn_weights @ V
        return out @ self.W_o, attn_weights

    def mlp(self, x):
        """2-layer MLP with GELU"""
        h = x @ self.W1
        h = 0.5 * h * (1 + np.tanh(np.sqrt(2 / np.pi) * (h + 0.044715 * h**3)))  # GELU
        return h @ self.W2

    def forward(self, tokens):
        """Forward pass"""
        x = self.embed[tokens]  # (seq_len, d_model)

        # Self-attention
        attn_out, attn_weights = self.attention(x)
        x = x + attn_out

        # MLP
        mlp_out = self.mlp(x)
        x = x + mlp_out

        # Output projection
        logits = x @ self.W_out

        return logits, {
            "embeddings": self.embed[tokens],
            "hidden": x,
            "attention": attn_weights,
            "pre_mlp": x - mlp_out,
            "post_mlp": x,
        }

    def loss(self, logits, tokens):
        """Cross-entropy loss for next-token prediction"""
        if logits.shape[0] <= 1:
            return float("inf")

        pred_logits = logits[:-1]
        targets = tokens[1:]

        # Softmax
        exp_logits = np.exp(pred_logits - np.max(pred_logits, axis=-1, keepdims=True))
        probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)

        # Cross-entropy
        target_probs = probs[np.arange(len(targets)), targets]
        return -np.mean(np.log(target_probs + 1e-8))

    def update(self, gradients, lr=0.01):
        """Apply gradients"""
        for param_name in ["embed", "W_q", "W_k", "W_v", "W_o", "W1", "W2", "W_out"]:
            if param_name in gradients:
                setattr(
                    self,
                    param_name,
                    getattr(self, param_name) - lr * gradients[param_name],
                )

    def compute_gradients(self, logits, tokens, states):
        """Simplified gradient computation"""
        if logits.shape[0] <= 1:
            return {}

        pred_logits = logits[:-1]
        targets = tokens[1:]
        hidden = states["hidden"][:-1]

        # Output gradients
        exp_logits = np.exp(pred_logits - np.max(pred_logits, axis=-1, keepdims=True))
        probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)

        grad_logits = probs.copy()
        grad_logits[np.arange(len(targets)), targets] -= 1
        grad_logits /= len(targets)

        # Backprop (simplified)
        gradients = {}
        gradients["W_out"] = hidden.T @ grad_logits

        grad_hidden = grad_logits @ self.W_out.T
        gradients["W2"] = states["pre_mlp"][:-1].T @ grad_hidden
        gradients["W1"] = states["embeddings"][:-1].T @ grad_hidden

        # Token embedding gradients
        grad_embed = np.zeros_like(self.embed)
        for i, token in enumerate(targets):
            if i < grad_hidden.shape[0]:
                grad_embed[token] += grad_hidden[i]
        gradients["embed"] = grad_embed

        return gradients
