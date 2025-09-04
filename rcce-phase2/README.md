# RCCE Phase 2 - Hard Guards Implementation

Recursive Cognitive Control Engine with mathematically coherent metrics and hard-guard presence certification.

## Quick Start
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup.ps1
.\scripts\run_tests.ps1
.\scripts\run_ab.ps1
```

## Architecture
- **Corrected Metrics**: RC triple, drift bands, DEC identities
- **Hard Guards**: AND logic for presence certificate
- **A/B Testing**: Statistical validation with confidence intervals
- **Ethics Enforcement**: φ₃₃ policy with step abortion
- **TDD Suite**: Falsification tests that must pass