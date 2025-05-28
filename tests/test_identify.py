import pytest
from fastapi.testclient import TestClient
from app import app, SessionLocal, Base, engine
from models import Contact

client = TestClient(app)

# Setup & teardown the DB for each test
@pytest.fixture(autouse=True)
def clear_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

def test_create_new_contact():
    response = client.post("/identify", json={
        "email": "a@test.com",
        "phoneNumber": "111111"
    })
    assert response.status_code == 200
    data = response.json()["contact"]
    assert data["primaryContactId"] == 1
    assert data["emails"] == ["a@test.com"]
    assert data["phoneNumbers"] == ["111111"]
    assert data["secondaryContactIds"] == []

def test_duplicate_contact_returns_same_primary():
    client.post("/identify", json={"email": "a@test.com", "phoneNumber": "111111"})
    response = client.post("/identify", json={"email": "a@test.com"})
    data = response.json()["contact"]
    assert data["primaryContactId"] == 1
    assert "a@test.com" in data["emails"]
    assert 2 in data["secondaryContactIds"]

def test_merge_on_phone_overlap():
    client.post("/identify", json={"email": "a@test.com", "phoneNumber": "111111"})
    response = client.post("/identify", json={"email": "b@test.com", "phoneNumber": "111111"})
    data = response.json()["contact"]
    assert data["primaryContactId"] == 1
    assert set(data["emails"]) == {"a@test.com", "b@test.com"}
    assert 2 in data["secondaryContactIds"]

def test_only_email():
    response = client.post("/identify", json={"email": "c@test.com"})
    assert response.status_code == 200
    data = response.json()["contact"]
    assert data["emails"] == ["c@test.com"]
    assert data["phoneNumbers"] == []

def test_only_phone():
    response = client.post("/identify", json={"phoneNumber": "222222"})
    assert response.status_code == 200
    data = response.json()["contact"]
    assert data["phoneNumbers"] == ["222222"]
    assert data["emails"] == []

def test_empty_payload():
    response = client.post("/identify", json={})
    assert response.status_code == 422
