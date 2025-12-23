import uuid
import urllib.parse
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    email = f"test-{uuid.uuid4().hex}@example.com"
    activity = "Chess Club"

    # Ensure email isn't already present
    r = client.get("/activities")
    assert r.status_code == 200
    assert email not in r.json()[activity]["participants"]

    # Sign up
    r = client.post(f"/activities/{urllib.parse.quote(activity)}/signup?email={urllib.parse.quote(email)}")
    assert r.status_code == 200
    assert "Signed up" in r.json()["message"]

    # Verify presence
    r = client.get("/activities")
    assert email in r.json()[activity]["participants"]

    # Duplicate signup should fail
    r = client.post(f"/activities/{urllib.parse.quote(activity)}/signup?email={urllib.parse.quote(email)}")
    assert r.status_code == 400

    # Unregister
    r = client.delete(f"/activities/{urllib.parse.quote(activity)}/participants?email={urllib.parse.quote(email)}")
    assert r.status_code == 200
    assert "Unregistered" in r.json()["message"]

    # Verify removed
    r = client.get("/activities")
    assert email not in r.json()[activity]["participants"]

    # Unregistering again should return 404
    r = client.delete(f"/activities/{urllib.parse.quote(activity)}/participants?email={urllib.parse.quote(email)}")
    assert r.status_code == 404


def test_activity_not_found():
    fake_activity = "Nonexistent Activity"
    email = "noone@example.com"

    r = client.post(f"/activities/{urllib.parse.quote(fake_activity)}/signup?email={urllib.parse.quote(email)}")
    assert r.status_code == 404

    r = client.delete(f"/activities/{urllib.parse.quote(fake_activity)}/participants?email={urllib.parse.quote(email)}")
    assert r.status_code == 404
