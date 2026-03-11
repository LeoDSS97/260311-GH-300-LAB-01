from urllib.parse import quote


def activity_path(activity_name: str) -> str:
    return f"/activities/{quote(activity_name, safe='')}"


def test_get_activities_returns_payload(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Math Club" in payload
    assert "participants" in payload["Math Club"]
    assert isinstance(payload["Math Club"]["participants"], list)


def test_signup_registers_new_participant(client):
    email = "new.student@mergington.edu"

    response = client.post(f"{activity_path('Math Club')}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Math Club"

    activities_response = client.get("/activities")
    participants = activities_response.json()["Math Club"]["participants"]
    assert email in participants


def test_signup_rejects_unknown_activity(client):
    response = client.post(f"{activity_path('Unknown Club')}/signup", params={"email": "any@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        f"{activity_path('Math Club')}/signup",
        params={"email": "alex@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_participant_success(client):
    response = client.delete(
        f"{activity_path('Math Club')}/participants",
        params={"email": "alex@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Unregistered alex@mergington.edu from Math Club"

    activities_response = client.get("/activities")
    participants = activities_response.json()["Math Club"]["participants"]
    assert "alex@mergington.edu" not in participants


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        f"{activity_path('Unknown Club')}/participants",
        params={"email": "any@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_non_registered_email(client):
    response = client.delete(
        f"{activity_path('Math Club')}/participants",
        params={"email": "nobody@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not registered in this activity"
