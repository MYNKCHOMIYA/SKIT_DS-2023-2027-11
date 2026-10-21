"""
test_academic_crud.py — Comprehensive Academic and Research CRUD Tests
Backend Developer: Kunal Gupta

Validates:
- Publication CRUD (add, list, update, delete)
- Project CRUD (add, list, update, delete)
- Patent CRUD (create, list, delete)
- Certification CRUD (create, list, delete)
- Teaching CRUD (create, list, delete)
- Student Guidance CRUD (create, list, delete)
- Workshop & FDP CRUD (create, list, delete)
- Public Portfolio endpoint (/api/v1/portfolio/public/{id})
- Faculty search endpoint (/api/search/)
- Activity logging and Notifications endpoints
"""

import pytest


@pytest.fixture
def user_with_profile(client, auth_headers):
    """Ensure current user has an active faculty profile."""
    client.post(
        "/api/v1/profile/",
        json={
            "first_name": "Kunal",
            "last_name": "Gupta",
            "designation": "Associate Professor",
            "department": "Computer Science & Engineering",
            "skills": "Python, FastAPI, PostgreSQL, Machine Learning",
        },
        headers=auth_headers,
    )
    return auth_headers


def test_publication_crud(client, user_with_profile):
    """Test Publication create, read, update, delete operations."""
    payload = {
        "title": "Scalable Deep Learning Architectures on Distributed Graphs",
        "publication_type": "Journal Paper",
        "publisher": "IEEE",
        "publication_year": 2024,
        "doi": "10.1109/TDSC.2024.123456",
        "citations": 14,
        "authors": "Kunal Gupta, Mayank Kumar, Manan Garg",
        "journal": "IEEE Transactions on Dependable and Secure Computing",
        "issn": "1545-5971",
        "indexed_in": "Scopus, Web of Science",
        "pdf_url": "https://example.com/paper.pdf",
    }
    create_res = client.post(
        "/api/v1/publications/", json=payload, headers=user_with_profile
    )
    assert create_res.status_code == 201
    pub = create_res.json()
    pub_id = pub["id"]
    assert pub["title"] == payload["title"]
    assert pub["citations"] == 14

    list_res = client.get("/api/v1/publications/me", headers=user_with_profile)
    assert list_res.status_code == 200
    assert any(p["id"] == pub_id for p in list_res.json())

    update_res = client.put(
        f"/api/v1/publications/{pub_id}",
        json={
            "title": "Updated: Scalable Deep Learning Architectures",
            "citations": 20,
        },
        headers=user_with_profile,
    )
    assert update_res.status_code == 200
    assert update_res.json()["citations"] == 20

    del_res = client.delete(f"/api/v1/publications/{pub_id}", headers=user_with_profile)
    assert del_res.status_code in (200, 204)


def test_project_crud(client, user_with_profile):
    """Test Project create, read, update, delete operations."""
    payload = {
        "title": "AI-Powered Institutional Faculty Portfolio & Intelligence System",
        "funding_agency": "DST-SERB",
        "budget": 2500000.00,
        "status": "Ongoing",
        "start_date": "2024-01-15",
        "end_date": "2026-12-31",
        "description": "Building next-generation faculty evaluation metrics via ML.",
        "team_members": "Kunal Gupta, Mayank Kumar",
    }
    create_res = client.post(
        "/api/v1/projects/", json=payload, headers=user_with_profile
    )
    assert create_res.status_code == 201
    proj = create_res.json()
    proj_id = proj["id"]
    assert proj["title"] == payload["title"]

    list_res = client.get("/api/v1/projects/me", headers=user_with_profile)
    assert list_res.status_code == 200
    assert any(p["id"] == proj_id for p in list_res.json())

    update_res = client.put(
        f"/api/v1/projects/{proj_id}",
        json={
            "title": "Updated: AI Institutional Portfolio System",
            "budget": 3000000.00,
        },
        headers=user_with_profile,
    )
    assert update_res.status_code == 200

    del_res = client.delete(f"/api/v1/projects/{proj_id}", headers=user_with_profile)
    assert del_res.status_code in (200, 204)


def test_patent_crud(client, user_with_profile):
    """Test Patent create, list, and delete operations."""
    payload = {
        "title": "Automated Profile Scoring Method Using Hybrid TF-IDF Weighting",
        "patent_number": "IN202411089921",
        "filing_date": "2024-04-10",
        "status": "FILED",
        "inventors": "Kunal Gupta, Mayank Kumar, Krishan Kumar Jayaswal",
        "link_url": "https://ipindia.gov.in/patents",
    }
    create_res = client.post("/api/patents/", json=payload, headers=user_with_profile)
    assert create_res.status_code == 201
    patent = create_res.json()
    patent_id = patent["id"]
    assert patent["patent_number"] == payload["patent_number"]

    list_res = client.get("/api/patents/", headers=user_with_profile)
    assert list_res.status_code == 200
    assert any(p["id"] == patent_id for p in list_res.json())

    del_res = client.delete(f"/api/patents/{patent_id}", headers=user_with_profile)
    assert del_res.status_code in (200, 204)


def test_certification_crud(client, user_with_profile):
    """Test Certification create, list, and delete operations."""
    payload = {
        "name": "AWS Certified Solutions Architect - Associate",
        "organization": "Amazon Web Services",
        "issue_date": "2023-08-15",
        "expiry_date": "2026-08-15",
        "certificate_url": "https://aws.amazon.com/verify/12345",
    }
    create_res = client.post(
        "/api/certifications/", json=payload, headers=user_with_profile
    )
    assert create_res.status_code == 201
    cert = create_res.json()
    cert_id = cert["id"]
    assert cert["organization"] == "Amazon Web Services"

    list_res = client.get("/api/certifications/", headers=user_with_profile)
    assert list_res.status_code == 200
    assert any(c["id"] == cert_id for c in list_res.json())

    del_res = client.delete(f"/api/certifications/{cert_id}", headers=user_with_profile)
    assert del_res.status_code in (200, 204)


def test_teaching_crud(client, user_with_profile):
    """Test Teaching record create, list, and delete operations."""
    payload = {
        "course_name": "Advanced Operating Systems",
        "subject_code": "CS-401",
        "semester": "Odd",
        "academic_year": "2025-2026",
        "credits": 4,
    }
    create_res = client.post("/api/teaching/", json=payload, headers=user_with_profile)
    assert create_res.status_code == 201
    teaching = create_res.json()
    teaching_id = teaching["id"]
    assert teaching["subject_code"] == "CS-401"

    list_res = client.get("/api/teaching/", headers=user_with_profile)
    assert list_res.status_code == 200
    assert any(t["id"] == teaching_id for t in list_res.json())

    del_res = client.delete(f"/api/teaching/{teaching_id}", headers=user_with_profile)
    assert del_res.status_code in (200, 204)


def test_student_guidance_crud(client, user_with_profile):
    """Test Student Guidance create, list, and delete operations."""
    payload = {
        "student_name": "Aarav Mehta",
        "project_title": "Blockchain-Enabled Academic Credential Verification",
        "degree": "B.Tech",
        "year": 2025,
        "status": "ONGOING",
    }
    create_res = client.post(
        "/api/student-guidance/", json=payload, headers=user_with_profile
    )
    assert create_res.status_code == 201
    sg = create_res.json()
    sg_id = sg["id"]
    assert sg["student_name"] == "Aarav Mehta"

    list_res = client.get("/api/student-guidance/", headers=user_with_profile)
    assert list_res.status_code == 200
    assert any(s["id"] == sg_id for s in list_res.json())

    del_res = client.delete(f"/api/student-guidance/{sg_id}", headers=user_with_profile)
    assert del_res.status_code in (200, 204)


def test_workshop_crud(client, user_with_profile):
    """Test Workshop and FDP create, list, and delete operations."""
    payload = {
        "event_name": "Faculty Development Program on Cloud Computing & Microservices",
        "organizer": "IIT Roorkee",
        "event_date": "2024-07-20",
        "certificate_url": "https://example.com/fdp_cert.pdf",
    }
    create_res = client.post("/api/workshops/", json=payload, headers=user_with_profile)
    assert create_res.status_code == 201
    ws = create_res.json()
    ws_id = ws["id"]
    assert ws["organizer"] == "IIT Roorkee"

    list_res = client.get("/api/workshops/", headers=user_with_profile)
    assert list_res.status_code == 200
    assert any(w["id"] == ws_id for w in list_res.json())

    del_res = client.delete(f"/api/workshops/{ws_id}", headers=user_with_profile)
    assert del_res.status_code in (200, 204)


def test_public_portfolio_endpoint(client, user_with_profile):
    """Test that public portfolio returns full nested profile data without authentication."""
    me_res = client.get("/api/v1/profile/me", headers=user_with_profile)
    assert me_res.status_code == 200
    profile_id = me_res.json()["id"]

    # Public endpoint requires NO auth headers
    pub_res = client.get(f"/api/v1/portfolio/public/{profile_id}")
    assert pub_res.status_code == 200
    data = pub_res.json()
    assert data["id"] == profile_id
    assert "publications" in data
    assert "education" in data
    assert "experience" in data
    assert "projects" in data


def test_search_endpoint(client, user_with_profile):
    """Test search endpoint filters faculty by department and designation."""
    res = client.get("/api/search/?department=Computer", headers=user_with_profile)
    assert res.status_code == 200
    results = res.json()
    assert isinstance(results, list)
    assert any("Computer" in (r.get("department") or "") for r in results)


def test_activity_and_notifications(client, user_with_profile):
    """Test user notifications and activity logs."""
    notif_res = client.get("/api/notifications/", headers=user_with_profile)
    assert notif_res.status_code == 200

    mark_res = client.post(
        "/api/notifications/mark-all-read", headers=user_with_profile
    )
    assert mark_res.status_code == 200

    act_res = client.get("/api/activity/", headers=user_with_profile)
    assert act_res.status_code == 200
