from fastapi.testclient import TestClient

from promptmage.api import PromptMageAPI
from .minimal_example import mage


def test_promptmage_api():
    """Test the PromptMageAPI class."""
    app = PromptMageAPI([mage]).get_app()
    assert app


def test_call_api():
    """Test calling the API."""
    app = PromptMageAPI([mage]).get_app()

    client = TestClient(app)

    response = client.get("/")
    print(response.text)
    assert response.status_code == 200
    assert "PromptMage" in response.text

    response = client.get("/api")
    print(response.text)
    assert response.status_code == 200
    assert "example" in response.text

    # question = "What is your name?"
    # response = client.get(f"/api/example/step1/{question}")
    # print(response.text)
    # assert response.status_code == 200
    # assert question in response.text
