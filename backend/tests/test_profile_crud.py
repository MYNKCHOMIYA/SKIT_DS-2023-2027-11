"""
test_profile_crud.py — Sprint 2 Integration & CRUD Tests.
DevOps / Krishan Kumar Jayaswal.

Tests the full lifecycle of:
  1. Faculty Profile (Create, Read /me, Update /me, Reject duplicates)
  2. Academic Qualifications / Education CRUD
  3. Professional Experience CRUD
  4. Achievements / Honors CRUD
"""

import pytest


def test_profile_unauthorized(client):
    """Accessing profile endpoints without token must return 401."""
    res = client.get("/api/v1/profile/me")
    assert res.status_code == 401


@pytest.mark.smoke
def test_create_and_read_profile(client, auth_headers):
    """Faculty can create their profile and retrieve it via /me."""
    payload = {
        "first_name": "Dr. Sarah",
        "last_name": "Sharma",
        "designation": "Associate Professor",
        "department": "Computer Science & Engineering (Data Science)",
        "bio": "Specializing in Machine Learning and Natural Language Processing.",
        "skills": "Python, PyTorch, Scikit-learn, SQL",
    }
    create_res = client.post("/api/v1/profile/", json=payload, headers=auth_headers)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["first_name"] == "Dr. Sarah"
    assert created_data["designation"] == "Associate Professor"

    # Read profile via /me
    me_res = client.get("/api/v1/profile/me", headers=auth_headers)
    assert me_res.status_code == 200
    assert me_res.json()["first_name"] == "Dr. Sarah"
    assert me_res.json()["id"] == created_data["id"]


def test_duplicate_profile_rejected(client, auth_headers):
    """A user cannot create more than one faculty profile."""
    payload = {
        "first_name": "Sarah",
        "last_name": "Sharma",
        "designation": "Assistant Professor",
    }
    res1 = client.post("/api/v1/profile/", json=payload, headers=auth_headers)
    assert res1.status_code == 201

    # Second creation attempt should fail with 400
    res2 = client.post("/api/v1/profile/", json=payload, headers=auth_headers)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"].lower()


def test_update_profile(client, auth_headers):
    """Faculty can update their profile bio and designation."""
    client.post(
        "/api/v1/profile/",
        json={"first_name": "Sarah", "last_name": "Sharma", "designation": "Lecturer"},
        headers=auth_headers,
    )
    update_res = client.patch(
        "/api/v1/profile/me",
        json={"designation": "Associate Professor", "bio": "Updated faculty bio."},
        headers=auth_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["designation"] == "Associate Professor"
    assert update_res.json()["bio"] == "Updated faculty bio."


@pytest.mark.smoke
def test_education_crud(client, auth_headers):
    """Test full create, read, update, delete cycle for Education records."""
    # Profile is prerequisite for education records
    client.post(
        "/api/v1/profile/",
        json={"first_name": "Sarah", "last_name": "Sharma", "designation": "Professor"},
        headers=auth_headers,
    )

    # 1. Create Education
    edu_payload = {
        "degree": "Ph.D.",
        "institution": "IIT Delhi",
        "field_of_study": "Computer Science",
        "start_date": "2018-08-01",
        "end_date": "2023-05-15",
        "grade": "9.5 CGPA",
    }
    create_res = client.post(
        "/api/v1/education/", json=edu_payload, headers=auth_headers
    )
    assert create_res.status_code == 201
    edu_data = create_res.json()
    edu_id = edu_data["id"]
    assert edu_data["degree"] == "Ph.D."
    assert edu_data["institution"] == "IIT Delhi"

    # 2. List Education
    list_res = client.get("/api/v1/education/", headers=auth_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 3. Update Education
    update_res = client.put(
        f"/api/v1/education/{edu_id}",
        json={
            "degree": "Ph.D.",
            "institution": "IIT Delhi",
            "field_of_study": "Artificial Intelligence",
            "start_date": "2018-08-01",
            "grade": "10.0 CGPA",
        },
        headers=auth_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["field_of_study"] == "Artificial Intelligence"

    # 4. Delete Education
    del_res = client.delete(f"/api/v1/education/{edu_id}", headers=auth_headers)
    assert del_res.status_code == 204

    # Verify deleted
    list_after = client.get("/api/v1/education/", headers=auth_headers)
    assert not any(e["id"] == edu_id for e in list_after.json())


def test_experience_crud(client, auth_headers):
    """Test full create, read, update, delete cycle for Experience records."""
    client.post(
        "/api/v1/profile/",
        json={"first_name": "Sarah", "last_name": "Sharma", "designation": "Professor"},
        headers=auth_headers,
    )

    # 1. Create Experience
    exp_payload = {
        "job_title": "Senior Research Scientist",
        "organization": "Google Research",
        "start_date": "2021-06-01",
        "is_current": True,
        "description": "Leading NLP foundation models research.",
        "employment_type": "Full-time",
    }
    create_res = client.post(
        "/api/v1/experience/", json=exp_payload, headers=auth_headers
    )
    assert create_res.status_code == 201
    exp_data = create_res.json()
    exp_id = exp_data["id"]
    assert exp_data["job_title"] == "Senior Research Scientist"

    # 2. List Experience
    list_res = client.get("/api/v1/experience/", headers=auth_headers)
    assert list_res.status_code == 200
    assert any(x["id"] == exp_id for x in list_res.json())

    # 3. Update Experience
    update_res = client.put(
        f"/api/v1/experience/{exp_id}",
        json={
            "job_title": "Principal Research Scientist",
            "organization": "Google Research",
            "start_date": "2021-06-01",
            "is_current": True,
        },
        headers=auth_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["job_title"] == "Principal Research Scientist"

    # 4. Delete Experience
    del_res = client.delete(f"/api/v1/experience/{exp_id}", headers=auth_headers)
    assert del_res.status_code == 204


def test_achievement_crud(client, auth_headers):
    """Test full create, read, update, delete cycle for Achievement records."""
    client.post(
        "/api/v1/profile/",
        json={"first_name": "Sarah", "last_name": "Sharma", "designation": "Professor"},
        headers=auth_headers,
    )

    # 1. Create Achievement
    ach_payload = {
        "title": "Outstanding Researcher Award",
        "category": "Award",
        "achievement_date": "2025-12-10",
        "description": "Awarded for exceptional contributions to applied AI.",
    }
    create_res = client.post(
        "/api/v1/achievements/", json=ach_payload, headers=auth_headers
    )
    assert create_res.status_code == 201
    ach_data = create_res.json()
    ach_id = ach_data["id"]
    assert ach_data["title"] == "Outstanding Researcher Award"

    # 2. List Achievements
    list_res = client.get("/api/v1/achievements/", headers=auth_headers)
    assert list_res.status_code == 200
    assert any(a["id"] == ach_id for a in list_res.json())

    # 3. Update Achievement
    update_res = client.put(
        f"/api/v1/achievements/{ach_id}",
        json={
            "title": "National AI Excellence Award",
            "category": "Award",
        },
        headers=auth_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "National AI Excellence Award"

    # 4. Delete Achievement
    del_res = client.delete(f"/api/v1/achievements/{ach_id}", headers=auth_headers)
    assert del_res.status_code == 204
