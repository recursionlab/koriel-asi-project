# Collaborator Questions (RCCE alignment)

## 1) Mathematical substrate
- Primary structures we will **actually implement first** (choose one to start):
  - ☐ Byte-level transformer (PyTorch CPU)
  - ☐ NumPy RCCE simulation only (Υ/CE²/φ₂₂/φ₃₃ metrics)
  - ☐ JAX-in-WSL2, math-first kernels

- Mandatory definitions you will supply:
  - Ξ operator spec at toy scale (inputs/outputs & stop rule)
  - Λ detection signal (how we flag lacunae in text/graphs)
  - φ₃₃ ethical rules (what to block/penalize)

## 2) Data
- Source texts you can legally use (list paths/URLs).
- Target “unit tests” of behavior (e.g., resolve paradox class X, or reframe Y).

## 3) Control & metrics
- Acceptable drift band (ℓ,u) for Υ.
- Which RC components to weight (embedding vs value-readout vs topic-graph).

## 4) Deliverable cadence
- First demo goal (1–2 days of work): RCCE demo reproduces key curves.
- Next goal (end of week): minimal byte-level LM w/ observer hooks.
