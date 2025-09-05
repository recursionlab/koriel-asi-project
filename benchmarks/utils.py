import numpy as np

def logprob(model, prompt: str, continuation: str) -> float:
    """Compute log-prob of ``continuation`` given ``prompt`` using TinyByteLM.

    ``model`` is assumed to behave like :class:`TinyByteLM`.
    """
    buf = np.zeros(model.ctx, dtype=np.uint8)
    p_bytes = prompt.encode("utf-8")
    if len(p_bytes) >= model.ctx:
        buf[:] = np.frombuffer(p_bytes[-model.ctx:], dtype=np.uint8)
    else:
        buf[-len(p_bytes):] = np.frombuffer(p_bytes, dtype=np.uint8)
    logp = 0.0
    for b in continuation.encode("utf-8"):
        probs, *_ = model.forward(buf[None, :])
        logp += float(np.log(np.clip(probs[0, b], 1e-9, 1.0)))
        buf = np.roll(buf, -1)
        buf[-1] = b
    return logp
