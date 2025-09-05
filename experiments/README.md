# Experiments Directory

This directory contains gated experiments that may:
- Run for extended periods
- Consume significant computational resources
- Modify system behavior
- Generate large output files

## Safety Requirements

**All experiments require explicit opt-in via CLI flags:**
```bash
python koriel-run experiment --name <experiment-name> --allow-experiments
```

**Resource limits are enforced:**
- Memory usage monitoring
- Time limits for execution
- Output size limits
- Safety checkpoints

## Experiment Categories

### legacy_validation/
Original consciousness validation scripts moved from root directory.
- Heavy computational load
- Long execution times (minutes to hours)
- Large memory usage

### qrft_experiments/
Quantum Reality Field Theory experimental validations.
- Complex mathematical operations  
- Stress testing of field equations
- Performance benchmarking

### stress_tests/
System stress testing and attack vectors.
- Intentionally pushes system limits
- Tests failure modes
- Resource exhaustion scenarios

## Running Experiments Safely

1. **Always use dry-run first:**
   ```bash
   python koriel-run experiment --name <name> --dry-run
   ```

2. **Monitor resource usage:**
   ```bash
   # Check memory and CPU before running
   htop
   ```

3. **Use time limits:**
   ```bash
   timeout 300 python koriel-run experiment --name <name> --allow-experiments
   ```

4. **Check experiment config:**
   Each experiment should have a corresponding `.yaml` config file with resource limits.

## Experiment Configuration Format

```yaml
experiment:
  name: "experiment_name"
  category: "stress_tests"  # or legacy_validation, qrft_experiments
  
safety:
  max_execution_time: 300   # seconds
  max_memory_mb: 1024      # megabytes  
  max_output_files: 10     # number of output files
  max_output_size_mb: 100  # total output size
  
resources:
  cpu_intensive: true      # warn user about CPU usage
  memory_intensive: true   # warn user about memory usage
  disk_intensive: false    # warn user about disk usage
  
permissions:
  allow_self_modification: false  # allow system self-modification
  allow_file_creation: true       # allow creating output files
  allow_network_access: false     # allow network requests
```

## Adding New Experiments

1. Create experiment script in appropriate subdirectory
2. Add corresponding config file (same name, .yaml extension)
3. Update this README
4. Test with dry-run mode first
5. Verify resource limits are respected

