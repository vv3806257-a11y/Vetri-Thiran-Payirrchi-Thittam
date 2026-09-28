from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_generate_demo_mode():
    payload = {
        "document_type": "NDA",
        "parties": "Alice Smith, ABC Ltd",
        "terms": "Confidentiality applies for 2 years; Information must be protected",
        "dates": "September 26, 2026",
    }

    response = client.post("/generate", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["document_type"] == "NDA"
    assert len(body["content"]) > 50
    assert "SIGNATURES" in body["content"]
