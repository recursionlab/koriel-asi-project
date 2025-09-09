import pytest
from koriel.operators.operator_spec import OperatorSpec

def test_operator_spec_valid():
    spec = OperatorSpec(name="normalize", category="transform")
    assert spec.name == "normalize"
    assert spec.category == "transform"

@pytest.mark.parametrize("bad_args", [
    {"name": "", "category": "transform"},
    {"name": "x" * 256, "category": "transform"},
    {"name": "norm", "category": ""},
    {"name": "n", "category": "transform", "arity": -1},
])
def test_operator_spec_invalid(bad_args):
    with pytest.raises(ValueError):
        OperatorSpec(**bad_args)
