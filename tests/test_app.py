import copy

from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


def setup_function():
    # Ensure each test starts with a fresh copy of the in-memory activities
    app_module._ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)


def teardown_function():
    # Restore original activities state after each test
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(app_module._ORIGINAL_ACTIVITIES))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect some known activity keys from the seeded data
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_and_unregister_flow():
    activity = "Soccer Team"
    email = "tester@example.com"

    # Ensure there's no participant initially
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert email not in data[activity]["participants"]

    # Sign up
    signup_resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup_resp.status_code == 200
    assert "Signed up" in signup_resp.json().get("message", "")

    # Check participant added in activities
    resp_after = client.get("/activities")
    assert resp_after.status_code == 200
    data_after = resp_after.json()
    assert email in data_after[activity]["participants"]

    # Unregister
    unregister_resp = client.post(f"/activities/{activity}/unregister?email={email}")
    assert unregister_resp.status_code == 200
    assert "Unregistered" in unregister_resp.json().get("message", "")

    # Ensure participant removed
    final = client.get("/activities").json()
    assert email not in final[activity]["participants"]
