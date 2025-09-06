"""
Tests for artifact validation and schema compliance.

Validates that artifacts meet schema requirements and contain required fields.
"""

import json
import pytest
from pathlib import Path
import sys
import tempfile
import os

# Add tools and src to path
sys.path.append(str(Path(__file__).parent.parent / "tools"))
sys.path.append(str(Path(__file__).parent.parent / "src"))

from validate_artifact import validate_metadata, basic_validate_metadata
from determinism import get_env_fingerprint, compute_state_hash


def test_schema_validation_required_fields():
    """Test that schema validation catches missing required fields."""
    schema_file = Path(__file__).parent.parent / "tools" / "metadata_schema.json"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        # Missing required fields
        incomplete_metadata = {
            "experiment_id": "test_123",
            "task": "basic",
            "seed": 1337,
            "schema_version": "2.0"
            # Missing state_hash, env_fingerprint, etc.
        }
        json.dump(incomplete_metadata, f)
        temp_file = Path(f.name)
    
    try:
        result = validate_metadata(temp_file, schema_file)
        assert not result["valid"]
        assert any("state_hash" in error for error in result["errors"])
        assert any("env_fingerprint" in error for error in result["errors"])
    finally:
        temp_file.unlink()


def test_schema_validation_complete_metadata():
    """Test that complete metadata passes validation."""
    schema_file = Path(__file__).parent.parent / "tools" / "metadata_schema.json"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        # Complete metadata
        env_fingerprint = get_env_fingerprint()
        complete_metadata = {
            "experiment_id": "test_123_20240101_120000",
            "task": "basic",
            "seed": 1337,
            "git_sha": "abcd1234",
            "timestamp": "2024-01-01T12:00:00",
            "output_directory": "/tmp/test",
            "python_version": "3.12.0",
            "environment": {
                "working_directory": "/tmp",
                "user": "test",
                "system": "posix"
            },
            "parameters": {
                "demo_type": "rcce_basic",
                "timesteps": 80,
                "attention_dim": 32,
                "value_dim": 16,
                "topic_bins": 4
            },
            "schema_version": "2.0",
            "env_fingerprint": env_fingerprint,
        }
        complete_metadata["state_hash"] = compute_state_hash(complete_metadata)
        json.dump(complete_metadata, f)
        temp_file = Path(f.name)
    
    try:
        result = validate_metadata(temp_file, schema_file)
        if not result["valid"]:
            print("Validation errors:", result["errors"])
        assert result["valid"]
    finally:
        temp_file.unlink()


def test_basic_validation_fallback():
    """Test basic validation when jsonschema is not available."""
    schema = {
        "required": ["experiment_id", "seed", "schema_version"],
        "properties": {
            "experiment_id": {"type": "string"},
            "seed": {"type": "integer"},
            "schema_version": {"type": "string"}
        }
    }
    
    # Valid metadata
    valid_metadata = {
        "experiment_id": "test_123",
        "seed": 1337,
        "schema_version": "2.0"
    }
    
    errors = basic_validate_metadata(valid_metadata, schema)
    assert len(errors) == 0
    
    # Missing required field
    invalid_metadata = {
        "experiment_id": "test_123",
        "schema_version": "2.0"
        # Missing seed
    }
    
    errors = basic_validate_metadata(invalid_metadata, schema)
    assert len(errors) > 0
    assert any("seed" in error for error in errors)
    
    # Wrong type
    wrong_type_metadata = {
        "experiment_id": "test_123",
        "seed": "not_an_integer",  # Should be integer
        "schema_version": "2.0"
    }
    
    errors = basic_validate_metadata(wrong_type_metadata, schema)
    assert len(errors) > 0
    assert any("seed" in error and "integer" in error for error in errors)


def test_state_hash_validation():
    """Test that state hash validation works correctly."""
    # Valid state hash (64 hex characters)
    valid_hash = "a" * 64
    assert len(valid_hash) == 64
    
    # Invalid state hash (wrong length)
    invalid_hash = "a" * 32
    assert len(invalid_hash) != 64
    
    # Test with schema pattern
    import re
    pattern = r"^[a-fA-F0-9]{64}$"
    
    assert re.match(pattern, valid_hash)
    assert not re.match(pattern, invalid_hash)
    assert not re.match(pattern, "invalid_characters_123")


def test_env_fingerprint_schema():
    """Test that environment fingerprint matches schema requirements."""
    env_fingerprint = get_env_fingerprint()
    
    # Check required fields
    required_fields = ["python_version", "platform", "numpy_version"]
    for field in required_fields:
        assert field in env_fingerprint
        assert isinstance(env_fingerprint[field], str)
    
    # Check optional fields
    optional_fields = [
        "pythonhashseed", "omp_num_threads", "openblas_num_threads",
        "mkl_num_threads", "numexpr_num_threads"
    ]
    for field in optional_fields:
        assert field in env_fingerprint
        assert isinstance(env_fingerprint[field], str)


if __name__ == "__main__":
    pytest.main([__file__])