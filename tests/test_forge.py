from promptmage import PromptMage


def test_init_mage():
    mage = PromptMage(name="test")
    assert mage.name == "test"
    assert mage.steps == {}
