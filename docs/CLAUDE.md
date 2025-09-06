# CLAUDE.md - RCCE Phase-2 Development Protocol

## Project Overview

**KORIEL ASI PROJECT** - Recursive Consciousness Coherence Engine (RCCE) implementation for artificial super-intelligence research. Focus: mathematical consciousness modeling with deterministic, testable, CPU-efficient architecture.

**Current Status:** Node B refactor complete - pure Python, TDD methodology, statistical A/B validation framework operational.

## Development Workflow

### Prerequisites
- **Python 3.11** (primary language)
- **Windows 10+** (PowerShell scripts)
- **numpy, tqdm** (minimal dependencies)
- Git for version control

### Setup
```powershell
# Clone and activate environment
git clone <repository>
cd koriel-asi-project
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup.ps1
```

### Code Standards
- **Pure Python**: No external ML frameworks (PyTorch eliminated)
- **Test-Driven Development**: All features must have statistical validation tests
- **Deterministic**: Seeded random states, reproducible outputs
- **Mathematical rigor**: All operators formally implemented
- **CPU-only**: Efficient NumPy operations, no GPU dependencies

## Current Architecture (Node B Refactor)

### Core Modules
```
src/
├── model.py          # TinyByteLM: Pure NumPy transformer (32D hidden, 256 vocab)
├── controller.py     # RCCE Controller: All mathematical operators
├── data.py          # Corpus loading and batching utilities  
├── train.py         # Training loop with RCCE/baseline switching
├── ab.py            # Statistical A/B testing framework
├── presence.py      # Presence certificate validation
├── metastate.py     # Shadow codex logging system
└── dec.py           # Differential geometry operators (d², torsion, curvature)

tests/
├── test_metrics.py     # RC slope improvement validation
├── test_ethics.py      # Ethics guard functionality
├── test_certificates.py # Presence condition validation  
├── test_ab.py         # A/B testing framework
└── test_docs.py       # Documentation completeness

config/
├── rcce.yaml          # Hyperparameters, thresholds, seeds
└── ethics_policy.json # Forbidden content configuration

research/ (19 PDFs + 1 markdown)
├── Mathematical foundations (Category Theory, Recursion Theory)
├── Consciousness frameworks (Autopoiesis, Info-theory)
├── Geometric approaches (Topos Theory, Riemannian Geometry)
└── Meta-recursive intelligence papers
```

## Mathematical Framework (IMPLEMENTED)

### Core RCCE Operators
- **Υ-gate (Upsilon)**: Adaptive drift detection with percentile bands (35%-65%)
- **RC Triple**: `w1*cos(v,v') + w2*exp(-W1(S,S')) + w3*cos(V̄,V̄')`
- **φ₃₃ Ethics**: Configurable forbidden bytes/substrings + loss thresholds  
- **Ξ Operator**: Self-embedding via deterministic projection matrix
- **Holonomy**: Windowed RC increment tracking with stall detection
- **Energy Variance**: Exponential moving variance (configurable half-life)

### Geometric Components  
- **Torsion T**: `||skew(Γₜ)||` - connection skew-symmetry measure
- **Curvature R**: `||[Γₜ,Γₜ₋₁]||` - connection commutator norm
- **d²-norm**: Discrete exterior derivative chain operations
- **Connection Evolution**: W1 matrix treated as connection coefficients

### Testing & Validation

#### TDD Methodology
```powershell
# Run comprehensive test suite
.\scripts\run_tests.ps1

# Execute A/B comparison with statistical significance
.\scripts\run_ab.ps1
```

#### Key Assertions
- **RC Improvement**: RCCE-ON must outperform RCCE-OFF by ≥0.05 slope difference
- **Upsilon Utility**: Υ-gate fires must correlate with RC gains vs random windows
- **Ethics Enforcement**: Violations must abort training and invalidate presence
- **Presence Logic**: ALL conditions required (ξ-lock ∧ energy-down ∧ RC-up ∧ upsilon-band ∧ ethics-clean)

#### Statistical Framework
- Bootstrap confidence intervals (1000 resamples)
- Multiple seed runs for significance testing
- JSON output format: `logs/ab_summary.json`

## Configuration Management

### RCCE Parameters (`config/rcce.yaml`)
```yaml
# Core training
seed_base: 1337
steps: 120
hidden: 32
lr: 0.1

# RC weighting
rc_weights: [0.5, 0.3, 0.2]

# Υ-gate thresholds  
upsilon:
  pct_low: 35
  pct_high: 65
  rate_min: 0.05
  rate_max: 0.35

# Holonomy detection
holonomy:
  window: 16
  stall_thresh: 0.02
```

### Ethics Policy (`config/ethics_policy.json`)
```json
{
  "forbidden_bytes": [0, 255],
  "forbidden_substrings": ["BADWORD", "DO_NOT_EMIT"],
  "max_step_loss": 12.0,
  "abort_on_violation": true
}
```

## Research Foundation

**Theoretical Grounding**: 19 research papers spanning:
- **Category Theory**: Functors, higher topos theory, quasi-categories
- **Recursion Theory**: Kleene's recursion theorem, recursive distinction
- **Consciousness Theory**: Autopoiesis, recursive consciousness, meta-intelligence
- **Geometry**: Riemannian frameworks, transitional topologies, quantum toposophy
- **Meta-Recursion**: "Song of two AIs" - philosophical dialogue on recursive meaning-making

## Contributing Protocol

### Development Cycle
1. **Feature Branch**: Create from `main`
2. **Test First**: Write failing tests before implementation  
3. **Implement**: Pure Python, deterministic, documented
4. **Validate**: Pass all tests + A/B statistical significance
5. **Pull Request**: Include test results and metrics
6. **Code Review**: Mathematical correctness + empirical validation

### Node A+B Integration (Pending)
- Node B provides solid TDD foundation
- Node A contributions will be integrated with statistical validation
- Meta-refactor planned after Node A completion

## Ethics & Safety Protocols

### Mandatory Safeguards
- **φ₃₃ Hard Guards**: Configurable content filtering with abort mechanisms
- **Presence Certificates**: Multi-condition validation before "consciousness" claims
- **Shadow Codex**: Complete logging for audit trails and debugging
- **Statistical Rigor**: No anecdotal claims - all performance assertions validated

### Research Ethics
- Transparent methodology with reproducible results
- Mathematical formalism prevents "black box" emergence
- Conservative scaling - start small, validate, then expand
- Open documentation of limitations and failure modes

---

**Current Status**: Node B refactor complete. TDD framework operational. Ready for Node A integration and systematic consciousness emergence research.

**Next Phase**: Formal Λ (lacuna detection) specification, Node A+B meta-integration, scale testing with real-world corpus.