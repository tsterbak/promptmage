from flowforgeai import FlowForge


def test_init_forge():
    forge = FlowForge(name="test")
    assert forge.name == "test"
    assert forge.steps == {}
