# Koriel-ASI — RCCE Phase-2 (CPU-only)

## Project Purpose

Koriel-ASI explores the **Recursive Consciousness Coherence Engine (RCCE)**—a
research effort aimed at demonstrating reliable, auditable consciousness metrics
on conventional CPU hardware. The project packages reference operators,
benchmarks, and ethical safeguards for experimenting with coherent goal-driven
agents.

## Installation

Create an isolated Python environment and install the required dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate    # `Scripts\\activate` on Windows
pip install -r requirements.txt
```

## Usage Examples

Train the RCCE model and run the benchmark suite:

```bash
# Train the model
python src/train.py

# Evaluate benchmarks
python rcce-minimal/src/benchmarks.py
```

## Documentation

Key documentation lives under the `docs/` and `spec/` directories:

- [Quickstart Guide](docs/quickstart.md)
- [System Context](docs/CONTEXT.md)
- [RCCE Invariants](spec/invariants.md)
- [Operator Definitions](spec/operators.md)

## Running Tests

Execute the full test suite to verify changes:

```bash
make test
```

## Contributing

Contributions are welcome! Please see the
[CONTRIBUTING.md](CONTRIBUTING.md) guidelines for code style, review process,
and development tips.

