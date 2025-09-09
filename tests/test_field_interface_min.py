from koriel.field.field_interface import FieldInterface

class DummyField(FieldInterface[int]):
    def __init__(self, value: int):
        self._value = value

    def apply(self, operator: str, **kwargs):  # type: ignore[override]
        if operator == "inc":
            self._value += 1
        elif operator == "scale":
            factor = int(kwargs.get("factor", 1))
            self._value *= factor
        return self._value


def test_field_interface_basic_mutation():
    f = DummyField(2)
    assert f.apply("inc") == 3
    assert f.apply("scale", factor=2) == 6
