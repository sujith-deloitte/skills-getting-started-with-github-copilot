from fastapi.testclient import TestClient
import pytest
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Check activity structure
    for activity_name, details in activities.items():
        assert isinstance(activity_name, str)
        assert isinstance(details, dict)
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)

def test_signup_for_activity():
    test_activity = "Chess Club"
    test_email = "test.student@mergington.edu"
    
    # First try signing up
    response = client.post(f"/activities/{test_activity}/signup", params={"email": test_email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {test_email} for {test_activity}"
    
    # Verify the student is in the activity's participant list
    activities = client.get("/activities").json()
    assert test_email in activities[test_activity]["participants"]
    
    # Try signing up again (should fail)
    response = client.post(f"/activities/{test_activity}/signup", params={"email": test_email})
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_unregister_from_activity():
    test_activity = "Chess Club"
    test_email = "test.student@mergington.edu"
    
    # First sign up a student
    client.post(f"/activities/{test_activity}/signup", params={"email": test_email})
    
    # Then unregister them
    response = client.delete(f"/activities/{test_activity}/unregister", params={"email": test_email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {test_email} from {test_activity}"
    
    # Verify the student is no longer in the activity's participant list
    activities = client.get("/activities").json()
    assert test_email not in activities[test_activity]["participants"]
    
    # Try unregistering again (should fail)
    response = client.delete(f"/activities/{test_activity}/unregister", params={"email": test_email})
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()

def test_signup_nonexistent_activity():
    response = client.post("/activities/NonexistentActivity/signup", 
                         params={"email": "test@mergington.edu"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_nonexistent_activity():
    response = client.delete("/activities/NonexistentActivity/unregister", 
                          params={"email": "test@mergington.edu"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()