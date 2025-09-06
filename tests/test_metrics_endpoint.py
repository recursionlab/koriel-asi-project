"""
Tests for metrics endpoint and observability.

Validates that /metrics endpoint provides required metrics and handles errors correctly.
"""

import json
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from metrics_server import MetricsHandler, validate_required_metrics


class MockRequest:
    """Mock HTTP request for testing."""
    def __init__(self, path="/metrics"):
        self.path = path


def test_metrics_handler_basic():
    """Test basic metrics handler functionality."""
    handler = MetricsHandler()
    handler.get_timestamp = MagicMock(return_value="2024-01-01T12:00:00")
    
    metrics = handler.get_metrics()
    
    # Check required fields are present
    required_keys = {"math_available", "sympy_version", "x_g", "state_hash"}
    assert all(key in metrics for key in required_keys)
    
    # Check types
    assert isinstance(metrics["math_available"], bool)
    assert isinstance(metrics["sympy_version"], str)
    assert isinstance(metrics["x_g"], (int, float))
    assert isinstance(metrics["state_hash"], str)
    assert len(metrics["state_hash"]) == 64  # SHA256 hex


def test_validate_required_metrics_success():
    """Test metrics validation with complete metrics."""
    complete_metrics = {
        "math_available": True,
        "sympy_version": "1.12",
        "x_g": 0.5,
        "state_hash": "a" * 64,
        "extra_field": "allowed"
    }
    
    # Should not raise
    validate_required_metrics(complete_metrics)


def test_validate_required_metrics_failure():
    """Test metrics validation with missing required fields."""
    incomplete_metrics = {
        "math_available": True,
        "sympy_version": "1.12",
        # Missing x_g and state_hash
    }
    
    with pytest.raises(AssertionError, match="Missing required metrics"):
        validate_required_metrics(incomplete_metrics)


def test_extended_metrics_present():
    """Test that extended metrics are included."""
    handler = MetricsHandler()
    handler.get_timestamp = MagicMock(return_value="2024-01-01T12:00:00")
    
    metrics = handler.get_metrics()
    
    extended_keys = {
        "witness_count", "glue_success_rate", "glue_frontier_size",
        "operator_hit_counts", "theorem_tests_passed", "seed",
        "env_fingerprint", "timestamp"
    }
    
    assert all(key in metrics for key in extended_keys)
    
    # Check types for extended metrics
    assert isinstance(metrics["witness_count"], int)
    assert isinstance(metrics["glue_success_rate"], (int, float))
    assert isinstance(metrics["glue_frontier_size"], int)
    assert isinstance(metrics["operator_hit_counts"], dict)
    assert isinstance(metrics["theorem_tests_passed"], int)
    assert isinstance(metrics["seed"], int)
    assert isinstance(metrics["env_fingerprint"], dict)


def test_metrics_deterministic():
    """Test that metrics are deterministic for same inputs."""
    handler1 = MetricsHandler()
    handler2 = MetricsHandler()
    
    # Mock timestamp to be consistent
    timestamp = "2024-01-01T12:00:00"
    handler1.get_timestamp = MagicMock(return_value=timestamp)
    handler2.get_timestamp = MagicMock(return_value=timestamp)
    
    with patch('metrics_server.get_current_state', return_value={"test": "value"}):
        metrics1 = handler1.get_metrics()
        metrics2 = handler2.get_metrics()
    
    # State hash should be identical for same state and timestamp
    assert metrics1["state_hash"] == metrics2["state_hash"]


def test_error_handling():
    """Test error handling in metrics generation."""
    handler = MetricsHandler()
    
    # Mock an exception in state retrieval
    with patch('metrics_server.get_current_state', side_effect=Exception("Test error")):
        metrics = handler.get_metrics()
        
        # Should still return basic metrics
        assert "math_available" in metrics
        assert "state_hash" in metrics
        

def test_sympy_availability():
    """Test sympy availability detection."""
    handler = MetricsHandler()
    metrics = handler.get_metrics()
    
    # Should report sympy version (either real version or "not_installed")
    assert "sympy_version" in metrics
    assert isinstance(metrics["sympy_version"], str)


@patch('builtins.open', side_effect=FileNotFoundError)
def test_uptime_fallback(mock_open):
    """Test uptime calculation fallback when /proc/uptime is not available."""
    handler = MetricsHandler()
    uptime = handler.get_uptime()
    
    # Should fallback to 0.0 when /proc/uptime is not readable
    assert uptime == 0.0


def test_json_response_serializable():
    """Test that metrics can be serialized to JSON."""
    handler = MetricsHandler()
    handler.get_timestamp = MagicMock(return_value="2024-01-01T12:00:00")
    
    metrics = handler.get_metrics()
    
    # Should not raise JSON serialization error
    json_str = json.dumps(metrics)
    
    # Should be able to deserialize back
    parsed = json.loads(json_str)
    assert parsed["math_available"] == metrics["math_available"]


if __name__ == "__main__":
    pytest.main([__file__])