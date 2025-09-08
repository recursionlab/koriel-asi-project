"""Test safety and experiment gating functionality."""

import os
import sys

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from koriel.safety import (
    ExperimentSafetyGate,
    ResourceLimits,
    ResourceMonitor,
    check_system_resources,
)


class TestSafety:
    """Test safety and resource monitoring."""

    def test_resource_limits_creation(self):
        """Test ResourceLimits dataclass creation."""
        limits = ResourceLimits(
            max_execution_time=300,
            max_memory_mb=1024,
            max_output_files=10,
            max_output_size_mb=100,
        )

        assert limits.max_execution_time == 300
        assert limits.max_memory_mb == 1024
        assert limits.max_output_files == 10
        assert limits.max_output_size_mb == 100

    def test_resource_monitor_initialization(self):
        """Test ResourceMonitor can be initialized."""
        limits = ResourceLimits(max_execution_time=60, max_memory_mb=512)
        monitor = ResourceMonitor(limits)

        assert monitor.limits == limits
        assert monitor.start_time is None
        assert monitor.initial_memory is None

    def test_resource_monitor_start_stop(self):
        """Test resource monitoring start and stats collection."""
        limits = ResourceLimits(max_execution_time=60, max_memory_mb=512)
        monitor = ResourceMonitor(limits)

        # Before starting
        stats = monitor.get_stats()
        assert stats["status"] == "not_started"

        # After starting
        monitor.start_monitoring()
        assert monitor.start_time is not None
        assert monitor.initial_memory is not None

        stats = monitor.get_stats()
        assert "elapsed_time" in stats
        assert "memory_mb" in stats
        assert "cpu_percent" in stats

    def test_experiment_safety_gate(self):
        """Test ExperimentSafetyGate functionality."""
        safety_gate = ExperimentSafetyGate()

        # Test safety check without allow flag
        mock_config = {"safety": {"max_execution_time": 300}}
        result = safety_gate.check_safety_requirements(
            mock_config, allow_experiments=False
        )

        assert not result["allowed"]
        assert "require explicit" in result["reason"]

        # Test safety check with allow flag
        result = safety_gate.check_safety_requirements(
            mock_config, allow_experiments=True
        )
        assert result["allowed"]

    def test_system_resource_check(self):
        """Test system resource checking."""
        resources = check_system_resources()

        required_keys = [
            "memory_total_gb",
            "memory_available_gb",
            "memory_percent_used",
            "disk_total_gb",
            "disk_free_gb",
            "disk_percent_used",
            "cpu_count",
        ]

        for key in required_keys:
            assert key in resources
            assert isinstance(resources[key], (int, float))
            assert resources[key] >= 0

    def test_high_risk_experiment_detection(self):
        """Test detection of high-risk experiments."""
        safety_gate = ExperimentSafetyGate()

        # Low risk config
        low_risk_config = {
            "safety": {"max_execution_time": 60, "max_memory_mb": 512},
            "resources": {"cpu_intensive": False, "memory_intensive": False},
        }

        result = safety_gate.check_safety_requirements(
            low_risk_config, allow_experiments=True
        )
        assert result["risk_level"] == "medium"

        # High risk config
        high_risk_config = {
            "safety": {"max_execution_time": 1800, "max_memory_mb": 4096},
            "resources": {"cpu_intensive": True, "memory_intensive": True},
        }

        result = safety_gate.check_safety_requirements(
            high_risk_config, allow_experiments=True
        )
        assert result["risk_level"] == "high"
