"""Regression tests to ensure legacy symbols remain importable during Phase 0.

These tests assert the compatibility shim exports the expected names.
"""
def test_legacy_field_imports():
    from koriel.field import SimpleQuantumField, FieldObservation, PatternMemory

    # Basic smoke assertions
    assert SimpleQuantumField is not None
    assert FieldObservation is not None
    assert PatternMemory is not None
