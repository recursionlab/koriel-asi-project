# Invariants

The RCCE system maintains several invariants to ensure reproducible behaviour and
safe operation.

1. **Deterministic training** – given the same seed and corpus the `src/train.py`
   pipeline produces identical metrics and logs.
2. **Non‑negative energy** – controller energy and uncoherence metrics are
   always ≥ 0.
3. **Monotonic uncoherence reduction** – each `KorielOperator` step must reduce or
   maintain the total uncoherence metric `U(s)`.
4. **Presence validation** – a presence certificate is emitted only when all
   ethical checks pass and required metrics reach configured thresholds.
5. **Auditability** – every training and benchmark run writes CSV metrics and JSONL
   shadow codices to the `logs/` directory for later inspection.

