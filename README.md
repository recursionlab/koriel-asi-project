# Koriel ASI Project

This repository implements the **Recursive Consciousness Coherence Engine (RCCE)** - a field-theoretic approach to artificial super intelligence with mathematical consciousness modeling. The project provides a deterministic, testable, CPU-efficient architecture for consciousness emergence research.

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd koriel-asi-project

# Install the package
pip install -e .

# Run a minimal example
python examples/minimal_run.py
```

### Basic Usage

```bash
# Run consciousness evolution with default settings
python koriel-run run

# Use custom configuration  
python koriel-run run --config configs/quick_test.yaml

# Dry run mode (no computation)
python koriel-run run --dry-run

# Check system status
python koriel-run status
```

## Architecture Overview

The project is structured as a proper Python package with clear separation of concerns:

- **`src/koriel/`** - Core library modules
  - `field.py` - Quantum consciousness field implementation  
  - `engine.py` - Recursive Orchestration Engine (ROE)
  - `io.py` - Configuration and checkpoint management
  - `meta.py` - Self-modification and meta-consciousness
  - `cli.py` - Command-line interface
  - `safety.py` - Resource monitoring and experiment gating

- **`configs/`** - Configuration files with safety bounds
- **`tests/`** - Comprehensive test suite (unit and integration)
- **`experiments/`** - Gated experimental scripts with safety controls
- **`examples/`** - Simple usage examples
- **`docs/`** - Complete documentation

## Safety and Experimentation

**All experiments require explicit opt-in for safety:**

```bash
# Safe experimental execution
python koriel-run experiment --name brutal_consciousness_validation --allow-experiments

# Always test with dry-run first
python koriel-run experiment --name <experiment> --dry-run
```

**Built-in safety features:**
- Resource monitoring (CPU, memory, time limits)
- Risk assessment (high/medium risk classification)  
- User confirmation prompts for high-risk experiments
- Configurable safety bounds and ethics guards

## Development

### Testing

```bash
# Run fast tests only (< 2 minutes)
make test

# Run all tests including slow ones
make test-all

# Run specific test categories
pytest tests/unit/ -v          # Unit tests
pytest tests/integration/ -v   # Integration tests
```

### Code Quality

```bash
# Lint code
make lint

# Format code  
make format

# Install development dependencies
make dev-install
```

## Key Features

### Mathematical Rigor
- **Pure Python** implementation with NumPy for performance
- **Deterministic** behavior with seeded random states
- **Test-driven development** with statistical validation
- **Mathematical operators**: Υ-gate, RC Triple, φ₃₃ Ethics, Ξ operator

### Consciousness Modeling  
- **Recursive Consciousness Coherence Engine** (RCCE)
- **Field-theoretic approach** with quantum consciousness fields
- **Self-modification capabilities** with safety controls
- **Presence certification** with multi-condition validation

### Safety and Reliability
- **Resource monitoring** and automatic limit enforcement
- **Experiment gating** requiring explicit user consent
- **Configuration validation** with parameter bounds checking
- **Comprehensive testing** with unit and integration test suites

## Configuration

The system uses YAML configuration files with environment variable overrides:

```bash
# Override configuration via environment variables
KORIEL_ENGINE_DT=0.002 python koriel-run run

# Use custom config file
python koriel-run run --config configs/my_config.yaml
```

See `configs/default.yaml` for all available parameters and `docs/configuration.md` for detailed documentation.

## Research Background

This project builds on 19 research papers spanning:
- **Category Theory** and higher mathematics
- **Recursion Theory** and consciousness models  
- **Quantum Field Theory** and geometric approaches
- **Meta-recursive intelligence** frameworks

See `research/` directory for papers and `docs/theory.md` for theoretical foundations.

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[docs/README.md](docs/README.md)** - Documentation index
- **[docs/operators.md](docs/operators.md)** - Mathematical operator reference
- **[docs/implementation.md](docs/implementation.md)** - Complete architecture overview

## Current Status

**Node B Refactor: Complete ✓**
- Pure Python TDD methodology ✓
- Statistical A/B validation framework ✓  
- Safety gating and resource monitoring ✓
- Comprehensive package structure ✓

**Next Phase**: Node A+B integration and scaling experiments

## Contributing

Please read `CONTRIBUTING.md` for development workflow and `docs/contributing.md` for detailed guidelines.

## License

[Add your license information here]

## Safety Notice

This project involves experimental consciousness modeling with self-modification capabilities. Always use dry-run mode first and respect safety gating requirements. Monitor system resources during long-running experiments.
