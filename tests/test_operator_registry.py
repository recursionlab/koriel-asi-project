from koriel.operators.registry import OperatorRegistry, OperatorEntry


def test_registry_register_and_get():
    reg = OperatorRegistry()
    entry = OperatorEntry(name="test.op", category="math", arity=2)
    reg.register(entry)

    got = reg.get("test.op")
    assert got is not None
    assert got.name == "test.op"
    assert got.category == "math"


def test_registry_list_and_duplicate():
    reg = OperatorRegistry()
    a = OperatorEntry(name="a")
    b = OperatorEntry(name="b")
    reg.register(a)
    reg.register(b)
    items = reg.list()
    assert len(items) == 2

    # duplicate registration should raise
    try:
        reg.register(a)
        raised = False
    except KeyError:
        raised = True
    assert raised
