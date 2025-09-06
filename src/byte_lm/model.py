import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, n_head, dropout=0.1):
        super().__init__()
        assert d_model % n_head == 0
        self.d_model = d_model
        self.n_head = n_head
        self.d_k = d_model // n_head

        self.w_q = nn.Linear(d_model, d_model, bias=False)
        self.w_k = nn.Linear(d_model, d_model, bias=False)
        self.w_v = nn.Linear(d_model, d_model, bias=False)
        self.w_o = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mask=None, return_attn=True):
        B, T, C = x.shape

        # Linear projections in batch from d_model => h x d_k
        q = (
            self.w_q(x).view(B, T, self.n_head, self.d_k).transpose(1, 2)
        )  # (B, nh, T, dk)
        k = (
            self.w_k(x).view(B, T, self.n_head, self.d_k).transpose(1, 2)
        )  # (B, nh, T, dk)
        v = (
            self.w_v(x).view(B, T, self.n_head, self.d_k).transpose(1, 2)
        )  # (B, nh, T, dk)

        # Attention
        att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(self.d_k))

        # Causal mask
        if mask is None:
            mask = torch.tril(torch.ones(T, T, device=x.device)).view(1, 1, T, T)
        att = att.masked_fill(mask == 0, float("-inf"))

        att_weights = F.softmax(att, dim=-1)
        att_weights = self.dropout(att_weights)

        y = att_weights @ v  # (B, nh, T, dk)
        y = (
            y.transpose(1, 2).contiguous().view(B, T, C)
        )  # re-assemble all head outputs side by side

        y = self.w_o(y)

        if return_attn:
            return y, att_weights
        return y


class FeedForward(nn.Module):
    def __init__(self, d_model, dropout=0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_model, 4 * d_model),
            nn.GELU(),
            nn.Linear(4 * d_model, d_model),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.net(x)


class TransformerBlock(nn.Module):
    def __init__(self, d_model, n_head, dropout=0.1):
        super().__init__()
        self.ln1 = nn.LayerNorm(d_model)
        self.attn = MultiHeadAttention(d_model, n_head, dropout)
        self.ln2 = nn.LayerNorm(d_model)
        self.ffn = FeedForward(d_model, dropout)

    def forward(self, x, return_attn=True):
        # Self-attention with residual connection
        if return_attn:
            attn_out, attn_weights = self.attn(self.ln1(x), return_attn=True)
            x = x + attn_out

            # Feed forward with residual connection
            x = x + self.ffn(self.ln2(x))
            return x, attn_weights
        else:
            x = x + self.attn(self.ln1(x), return_attn=False)
            x = x + self.ffn(self.ln2(x))
            return x


class TinyByteTransformer(nn.Module):
    def __init__(
        self, vocab_size=256, d_model=128, n_head=4, n_layer=2, seq_len=128, dropout=0.1
    ):
        super().__init__()
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.seq_len = seq_len

        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.position_embedding = nn.Embedding(seq_len, d_model)
        self.dropout = nn.Dropout(dropout)

        self.blocks = nn.ModuleList(
            [TransformerBlock(d_model, n_head, dropout) for _ in range(n_layer)]
        )

        self.ln_f = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size, bias=False)

        # Initialize weights
        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, x, return_attn=True):
        B, T = x.shape
        assert (
            T <= self.seq_len
        ), f"Cannot forward sequence of length {T}, max is {self.seq_len}"

        # Token + position embeddings
        pos = torch.arange(0, T, dtype=torch.long, device=x.device).unsqueeze(
            0
        )  # (1, T)
        tok_emb = self.token_embedding(x)  # (B, T, d_model)
        pos_emb = self.position_embedding(pos)  # (1, T, d_model)
        x = self.dropout(tok_emb + pos_emb)

        attn_list = []
        for block in self.blocks:
            if return_attn:
                x, attn_weights = block(x, return_attn=True)
                attn_list.append(attn_weights)
            else:
                x = block(x, return_attn=False)

        x = self.ln_f(x)
        logits = self.head(x)  # (B, T, vocab_size)

        if return_attn:
            return logits, attn_list
        return logits


def count_parameters(model) -> int:
    """Count total trainable parameters in model."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
