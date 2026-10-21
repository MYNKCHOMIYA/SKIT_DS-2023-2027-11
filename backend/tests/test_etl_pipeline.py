"""
test_etl_pipeline.py — Unit & Integration tests for Mayank Kumar's Pandas ETL Pipeline
Author: Mayank Kumar (AI/ML & Data Engineer)
Sprint 3: Data Pipeline & Analytics
"""

import pytest
from datetime import date
from app.services.data_pipeline import FacultyETLPipeline
from app.models.faculty_profile import FacultyProfile


def test_parse_flexible_date_handles_mixed_formats():
    """Validates date normalization across strings, ints, datetimes, and nulls."""
    assert FacultyETLPipeline.parse_flexible_date("2024-05-15") == date(2024, 5, 15)
    assert FacultyETLPipeline.parse_flexible_date("2024") == date(2024, 1, 1)
    assert FacultyETLPipeline.parse_flexible_date(2023) == date(2023, 1, 1)
    assert FacultyETLPipeline.parse_flexible_date(None) is None
    assert FacultyETLPipeline.parse_flexible_date("invalid_date_string") is None
    assert FacultyETLPipeline.parse_flexible_date("") is None


def test_clean_profile_record_null_and_whitespace_handling():
    """Validates cleaning of messy user input and NaN values."""
    raw = {
        "first_name": "  Mayank  ",
        "last_name": "Kumar",
        "designation": "Assistant Professor",
        "department": None,
        "bio": float("nan"),  # Pandas NaN
        "skills": "Python, Machine Learning",
    }
    cleaned = FacultyETLPipeline.clean_profile_record(raw)
    assert cleaned["first_name"] == "Mayank"
    assert cleaned["last_name"] == "Kumar"
    assert cleaned["full_name"] == "Mayank Kumar"
    assert cleaned["department"] == ""
    assert cleaned["bio"] == ""
    assert cleaned["skills"] == "Python, Machine Learning"


def test_completeness_scoring_algorithm():
    """Tests weighted completeness score for partial vs populated profiles."""
    profile = FacultyProfile(
        first_name="Mayank",
        last_name="Kumar",
        designation="Assistant Professor",
        department="Computer Science & Engineering",
        bio="Passionate researcher focusing on distributed ETL and machine learning workflows.",
        skills="Python, Pandas, FastAPI, SQL",
        specialization="Data Engineering",
        areas_of_interest="Distributed Systems, NLP",
        google_scholar="https://scholar.google.com/citations?user=test",
        orcid="0000-0002-1825-0097",
    )

    # 1. Evaluate with publications and projects
    result = FacultyETLPipeline.calculate_completeness_score(
        profile, pub_count=4, proj_count=2, pat_count=1
    )
    assert result["score"] >= 80.0
    assert result["is_complete"] is True
    assert "breakdown" in result
    assert result["breakdown"]["core_identity"] == 30.0

    # 2. Evaluate minimal profile
    minimal_profile = FacultyProfile(
        first_name="New",
        last_name="Faculty",
        designation="Lecturer",
    )
    min_result = FacultyETLPipeline.calculate_completeness_score(minimal_profile)
    assert min_result["score"] < 50.0
    assert min_result["is_complete"] is False
    assert len(min_result["recommendations"]) > 0


def test_department_metrics_extraction(db_session):
    """Tests Pandas groupby and aggregation over database records."""
    metrics_df = FacultyETLPipeline.extract_department_metrics(db_session)
    assert hasattr(metrics_df, "columns")
    assert "department" in metrics_df.columns
    assert "faculty_count" in metrics_df.columns
    assert "publication_count" in metrics_df.columns


def test_completeness_and_summary_api_endpoints(client, auth_headers):
    """Integration test verifying GET /api/v1/analytics/completeness/me and ETL summary."""
    # Create profile
    client.post(
        "/api/v1/profile/",
        json={
            "first_name": "ETL",
            "last_name": "Tester",
            "designation": "Associate Professor",
            "department": "Data Science",
            "bio": "Expert in big data systems and scalable ETL data architecture.",
        },
        headers=auth_headers,
    )

    # Completeness check
    comp_resp = client.get("/api/v1/analytics/completeness/me", headers=auth_headers)
    assert comp_resp.status_code == 200
    comp_data = comp_resp.json()
    assert "score" in comp_data
    assert "breakdown" in comp_data

    # ETL Department summary check
    summary_resp = client.get(
        "/api/v1/analytics/etl/department-summary", headers=auth_headers
    )
    assert summary_resp.status_code == 200
    assert isinstance(summary_resp.json(), list)
