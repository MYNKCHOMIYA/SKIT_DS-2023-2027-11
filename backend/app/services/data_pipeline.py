"""
data_pipeline.py — Pandas-based ETL Pipeline & Analytics Engine
Sprint 3: Data Pipeline & Portfolio Engine
Author: Mayank Kumar (AI/ML & Data Engineer)

Provides:
  - Robust ETL extraction from PostgreSQL / SQLite models into structured DataFrames.
  - Safe cleaning, null-handling, type-casting, and date-parsing for faculty data.
  - Weighted Profile Completeness scoring algorithm (Form-1 / Form-2 requirement).
  - Time-series aggregation and department publication velocity metrics.
  - Keyword and research focus extraction.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, date
import dateutil.parser
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.models.faculty_profile import FacultyProfile
from app.models.publication import Publication
from app.models.project import Project
from app.models.patent import Patent

logger = logging.getLogger(__name__)


class FacultyETLPipeline:
    """
    Pandas-powered ETL pipeline designed by Mayank Kumar for cleaning,
    normalizing, and transforming incoming academic records for analytics.
    """

    @staticmethod
    def parse_flexible_date(val: Any) -> Optional[date]:
        """
        Safely parse dates from varied formats (strings, ISO, timestamps, year ints).
        Returns None if missing or unparseable without raising exceptions.
        """
        if val is None or pd.isna(val):
            return None
        if isinstance(val, (datetime, pd.Timestamp)):
            return val.date()
        if isinstance(val, date):
            return val
        if isinstance(val, (int, float)):
            try:
                # Handle year-only integers like 2024
                int_yr = int(val)
                if 1950 <= int_yr <= 2100:
                    return date(int_yr, 1, 1)
            except Exception:
                return None
        if isinstance(val, str):
            val_clean = val.strip()
            if not val_clean:
                return None
            if val_clean.isdigit() and len(val_clean) == 4:
                try:
                    int_yr = int(val_clean)
                    if 1950 <= int_yr <= 2100:
                        return date(int_yr, 1, 1)
                except Exception:
                    return None
            try:
                dt = dateutil.parser.parse(val_clean)
                return dt.date()
            except Exception:
                return None
        return None

    @classmethod
    def clean_profile_record(cls, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize raw faculty profile dictionary:
        - Strips whitespace
        - Replaces NaNs with empty strings or sensible defaults
        - Extracts primary domain from text
        """
        cleaned = dict(record)
        for field in [
            "first_name",
            "last_name",
            "designation",
            "department",
            "bio",
            "skills",
            "employee_id",
            "website",
            "linkedin",
            "google_scholar",
            "orcid",
            "office_location",
            "specialization",
            "areas_of_interest",
        ]:
            val = cleaned.get(field)
            if val is None or pd.isna(val):
                cleaned[field] = ""
            else:
                cleaned[field] = str(val).strip()

        # Format full name
        first = cleaned.get("first_name", "")
        last = cleaned.get("last_name", "")
        cleaned["full_name"] = f"{first} {last}".strip()

        return cleaned

    @classmethod
    def calculate_completeness_score(
        cls,
        profile: FacultyProfile,
        pub_count: int = 0,
        proj_count: int = 0,
        pat_count: int = 0,
    ) -> Dict[str, Any]:
        """
        Calculates a weighted completeness score (0-100) based on Form-1/2 metrics:
          - Core Identity & Bio (30%): First, Last, Designation, Department, Bio
          - Academic Credentials & Skills (25%): Skills, Specialization, Areas of Interest
          - Research Productivity (25%): Publications (>=1), Projects (>=1), Patents (>=1)
          - Online & Professional Presence (20%): Image, Google Scholar, ORCID, LinkedIn
        """
        breakdown = {
            "core_identity": 0.0,
            "skills_specialization": 0.0,
            "research_output": 0.0,
            "professional_presence": 0.0,
        }

        # 1. Core Identity (30 points total)
        core_pts = 0.0
        if profile.first_name and profile.first_name.strip():
            core_pts += 6.0
        if profile.last_name and profile.last_name.strip():
            core_pts += 6.0
        if profile.designation and profile.designation.strip():
            core_pts += 6.0
        if profile.department and profile.department.strip():
            core_pts += 6.0
        if profile.bio and len(profile.bio.strip()) >= 20:
            core_pts += 6.0
        breakdown["core_identity"] = min(30.0, core_pts)

        # 2. Skills & Specialization (25 points total)
        skill_pts = 0.0
        if profile.skills and profile.skills.strip():
            skill_pts += 10.0
        if profile.specialization and profile.specialization.strip():
            skill_pts += 8.0
        if profile.areas_of_interest and profile.areas_of_interest.strip():
            skill_pts += 7.0
        breakdown["skills_specialization"] = min(25.0, skill_pts)

        # 3. Research Output (25 points total)
        res_pts = 0.0
        if pub_count > 0:
            res_pts += 12.0
            if pub_count >= 3:
                res_pts += 3.0
        if proj_count > 0:
            res_pts += 5.0
        if pat_count > 0:
            res_pts += 5.0
        breakdown["research_output"] = min(25.0, res_pts)

        # 4. Professional Presence (20 points total)
        pres_pts = 0.0
        if profile.profile_image_url and profile.profile_image_url.strip():
            pres_pts += 5.0
        if profile.google_scholar and profile.google_scholar.strip():
            pres_pts += 5.0
        if profile.orcid and profile.orcid.strip():
            pres_pts += 5.0
        if profile.linkedin and profile.linkedin.strip():
            pres_pts += 5.0
        breakdown["professional_presence"] = min(20.0, pres_pts)

        total_score = round(sum(breakdown.values()), 1)

        recommendations = []
        if breakdown["core_identity"] < 25.0:
            recommendations.append(
                "Add a detailed professional bio (at least 20 words)."
            )
        if breakdown["skills_specialization"] < 20.0:
            recommendations.append(
                "List your primary areas of interest and technical skills."
            )
        if breakdown["research_output"] < 15.0:
            recommendations.append(
                "Add your recent conference/journal publications or research projects."
            )
        if breakdown["professional_presence"] < 15.0:
            recommendations.append(
                "Link your ORCID, Google Scholar ID, or institutional photo."
            )

        return {
            "score": total_score,
            "breakdown": breakdown,
            "is_complete": total_score >= 80.0,
            "recommendations": recommendations,
        }

    @classmethod
    def extract_department_metrics(cls, db: Session) -> pd.DataFrame:
        """
        Extracts all faculty and publication rows into Pandas DataFrames,
        performs outer merges and groupby aggregations, returning cleaned stats.
        """
        profiles = db.query(
            FacultyProfile.id,
            FacultyProfile.department,
            FacultyProfile.designation,
        ).all()

        if not profiles:
            return pd.DataFrame(
                columns=[
                    "department",
                    "faculty_count",
                    "publication_count",
                    "avg_pubs_per_faculty",
                ]
            )

        df_profiles = pd.DataFrame(
            [
                {
                    "profile_id": p[0],
                    "department": p[1] or "General / Unassigned",
                    "designation": p[2],
                }
                for p in profiles
            ]
        )

        pubs = db.query(
            Publication.id,
            Publication.faculty_id,
            Publication.publication_year,
            Publication.citations,
        ).all()

        df_pubs = pd.DataFrame(
            [
                {
                    "pub_id": pub[0],
                    "profile_id": pub[1],
                    "year": pub[2],
                    "citations": pub[3] or 0,
                }
                for pub in pubs
            ]
        )

        if df_pubs.empty:
            dept_grp = (
                df_profiles.groupby("department")["profile_id"].count().reset_index()
            )
            dept_grp.columns = ["department", "faculty_count"]
            dept_grp["publication_count"] = 0
            dept_grp["avg_pubs_per_faculty"] = 0.0
            return dept_grp

        merged = pd.merge(df_profiles, df_pubs, on="profile_id", how="left")

        summary = (
            merged.groupby("department")
            .agg(
                faculty_count=("profile_id", "nunique"),
                publication_count=("pub_id", lambda x: int(x.dropna().count())),
                total_citations=("citations", lambda x: int(x.dropna().sum())),
            )
            .reset_index()
        )

        summary["avg_pubs_per_faculty"] = (
            (summary["publication_count"] / summary["faculty_count"])
            .replace([np.inf, -np.inf], 0.0)
            .fillna(0.0)
            .round(2)
        )

        return summary
