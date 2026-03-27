from fastapi.testclient import TestClient

from app.main import create_app
from app.store import InMemoryEntryStore


def test_entries_flow() -> None:
    app = create_app(store_factory=InMemoryEntryStore)
    client = TestClient(app)

    assert client.get("/healthz").status_code == 200
    assert client.get("/entries").json() == {"entries": []}

    created = client.post("/entries", json={"value": "ALPHA"})
    assert created.status_code == 200
    assert created.json()["value"] == "ALPHA"

    listed = client.get("/entries")
    assert listed.status_code == 200
    assert listed.json()["entries"][0]["value"] == "ALPHA"
