# src/data.py
import os, numpy as np, typing as T
from pathlib import Path

def _default_corpus() -> T.List[bytes]:
    s = [
        b"recursive systems grow by invariants\n",
        b"category morphisms preserve structure\n",
        b"autopoiesis maintains organization\n",
        b"language models compose semantics\n",
        b"holonomy tracks coherence increments\n",
        b"ethics guards constrain actions\n",
    ]
    return s

def load_corpus(root: str="conversations-pocket") -> T.List[np.ndarray]:
    root = os.environ.get("KORIEL_CORPUS_DIR", root)
    p = Path(root)
    lines: T.List[bytes] = []
    if p.exists() and p.is_dir():
        for fp in sorted(p.glob("*.txt")):
            try:
                lines.append(fp.read_bytes())
            except Exception:
                pass
    if not lines: lines = _default_corpus()
    return [np.frombuffer(x, dtype=np.uint8) for x in lines]

def make_stream(corpus, ctx: int, steps: int, seed: int):
    rng = np.random.default_rng(seed)
    concat = np.concatenate([np.uint8(10)*np.ones(1,dtype=np.uint8)] + corpus)
    N = len(concat); pos = 0
    for _ in range(steps):
        if pos+ctx+1 >= N: pos = 0
        seq = concat[pos:pos+ctx]; y = concat[pos+1:pos+ctx+1]
        pos += int(rng.integers(1, 5))
        yield seq.copy(), y.copy()

def bigram_features(batch_x: np.ndarray) -> np.ndarray:
    B = 16
    hist = np.zeros(B, dtype=np.float64)
    for row in batch_x:
        for i in range(len(row)-1):
            k = ((int(row[i]) & 15) ^ (int(row[i+1]) & 15)) % B
            hist[k] += 1.0
    s = hist.sum()
    return hist/s if s>0 else hist