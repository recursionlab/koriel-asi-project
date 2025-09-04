# src/model.py
import numpy as np

def softmax(z):
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)

class TinyByteLM:
    def __init__(self, ctx=64, d=32, seed=1337):
        rng = np.random.default_rng(seed)
        self.ctx, self.d = ctx, d
        self.E = (rng.standard_normal((256, d))*0.05).astype(np.float64)
        self.W1 = (rng.standard_normal((d, d))*0.05).astype(np.float64)
        self.b1 = np.zeros(d, dtype=np.float64)
        self.W2 = (rng.standard_normal((d, 256))*0.05).astype(np.float64)
        self.b2 = np.zeros(256, dtype=np.float64)
        self.mask = np.zeros(256, dtype=np.float64)
        self.lr = 0.3
        self._x_cache = None
        self._h_cache = None

    def set_lr(self, lr: float): self.lr = float(lr)
    def set_mask(self, m: np.ndarray): self.mask = m.astype(np.float64)

    def forward(self, x_bytes: np.ndarray):
        emb = self.E[x_bytes]        # [B,T,d]
        h = emb.mean(axis=1)         # [B,d]  (hmean)
        h1 = np.tanh(h @ self.W1 + self.b1)
        logits = h1 @ self.W2 + self.b2 - self.mask
        probs = softmax(logits)
        a = probs.mean(axis=0)  # attention/output distribution
        hmean = h.flatten()  # flatten for controller
        vbar = h.flatten()  # same as hmean for this architecture
        return probs, logits, hmean, vbar, a
    
    def loss(self, probs, y):
        B = probs.shape[0]
        y_last = y[:, -1]
        loss = -np.log(np.clip(probs[np.arange(B), y_last], 1e-9, 1.0)).mean()
        return loss

    def cache_io(self, x: np.ndarray, h: np.ndarray):
        self._x_cache = x
        self._h_cache = h

    def step(self, x: np.ndarray, y: np.ndarray, lr=None):
        if lr is None: lr = self.lr
        B, _ = x.shape
        probs, logits, hmean, vbar, a = self.forward(x)
        
        # Get 2D h for gradients
        emb = self.E[x]
        h = emb.mean(axis=1)  # [B,d]
        self.cache_io(x, h)
        
        loss = self.loss(probs, y)
        y_last = y[:, -1]
        dlogits = probs.copy()
        dlogits[np.arange(B), y_last] -= 1.0
        dlogits /= B
        
        h1 = np.tanh(h @ self.W1 + self.b1)  # [B,d]
        dW2 = h1.T @ dlogits  # [d, B] @ [B, 256] = [d, 256]
        db2 = dlogits.sum(axis=0)  # [256]
        dh1 = dlogits @ self.W2.T  # [B, 256] @ [256, d] = [B, d]
        dh = (1.0 - h1*h1) * dh1   # [B, d]
        dW1 = h.T @ dh  # [d, B] @ [B, d] = [d, d]
        db1 = dh.sum(axis=0)  # [d]
        
        dE = np.zeros_like(self.E)
        for b in range(B):
            idxs = self._x_cache[b]
            g = dh[b]/max(1, len(idxs))  # [d]
            dE[idxs] += g
            
        self.W2 -= lr * dW2; self.b2 -= lr * db2
        self.W1 -= lr * dW1; self.b1 -= lr * db1
        self.E  -= lr * dE
        return float(loss), hmean, vbar, a