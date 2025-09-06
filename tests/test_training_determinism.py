"""
Tests for determinism in training pipeline.

Validates that training produces deterministic results with state hashing.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.train import run


def test_deterministic_training():
    """Test that training produces deterministic results."""
    # Run same seed twice
    m1, rate1 = run(seed=42, rcce_on=True, out_prefix="DET_TEST1")
    m2, rate2 = run(seed=42, rcce_on=True, out_prefix="DET_TEST2")
    
    # Should have identical state hashes
    assert "state_hash" in m1
    assert "state_hash" in m2
    assert m1["state_hash"] == m2["state_hash"]
    
    # Should have same final metrics
    assert abs(rate1 - rate2) < 1e-10


def test_state_hash_in_metrics():
    """Test that state_hash is included in training metrics."""
    m, rate = run(seed=1234, rcce_on=True, out_prefix="STATE_HASH_TEST")
    
    assert "state_hash" in m
    assert isinstance(m["state_hash"], str)
    assert len(m["state_hash"]) == 64  # SHA256 hex


def test_different_seeds_different_hashes():
    """Test that different seeds produce different state hashes."""
    m1, _ = run(seed=111, rcce_on=True, out_prefix="SEED_TEST1")
    m2, _ = run(seed=222, rcce_on=True, out_prefix="SEED_TEST2")
    
    assert m1["state_hash"] != m2["state_hash"]


def test_rcce_on_off_different_hashes():
    """Test that RCCE on/off produces different state hashes."""
    m1, _ = run(seed=333, rcce_on=True, out_prefix="RCCE_ON_TEST")
    m2, _ = run(seed=333, rcce_on=False, out_prefix="RCCE_OFF_TEST")
    
    # Same seed but different RCCE setting should produce different results
    assert m1["state_hash"] != m2["state_hash"]


if __name__ == "__main__":
    pytest.main([__file__])