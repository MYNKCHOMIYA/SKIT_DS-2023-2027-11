# SKIT_DS-2023-2027-11 — Generalised Faculty Portfolio System

A full-stack web application for faculty profile management, research analytics, and publication tracking at SKIT Jaipur.

---

## Project Overview

| Detail | Info |
|--------|------|
| **Batch** | 2023–2027 |
| **Group** | DS-11 |
| **Tech Stack** | FastAPI · PostgreSQL · Next.js · SQLAlchemy · AI/ML (Scikit-Learn, spaCy) |

---

## Team Roles

| Member | Role |
|--------|------|
| **Kunal** | Backend Engineer — FastAPI, PostgreSQL, Auth, APIs |
| **Mayank** | AI/ML Engineer — Analytics, Data Modelling, ML Pipeline |
| **Manan** | Frontend Engineer — Next.js, UI/UX, Dashboard |

---

## Sprint Progress

### ✅ Sprint 1 (15 Sep – 15 Oct 2026) — Foundation & Access Management

**Kunal (Backend):**
- FastAPI project scaffolded with PostgreSQL/Render DB connection
- SQLAlchemy base models (`base.py`, `faculty_profile.py`)
- Initial DB migration setup

**Mayank (AI/ML):**
- Analytics architecture designed & documented (`backend/docs/analytics_architecture.md`)
- Key metrics defined: publication count, profile completeness score, domain keywords, h-index simulation
- AI/ML dependency stack researched & documented (`backend/docs/requirements_ai.txt`)
- Enhanced `FacultyProfile` schema with NLP-ready text fields (`bio`, `skills`) and analytical annotations

---

## Project Structure

```
SKIT_DS-2023-2027-11/
├── backend/
│   ├── app/
│   │   └── models/
│   │       ├── base.py              # SQLAlchemy declarative base
│   │       └── faculty_profile.py   # Core faculty schema (AI/ML annotated)
│   └── docs/
│       ├── analytics_architecture.md  # ML pipeline design (Mayank - Sprint 1)
│       └── requirements_ai.txt        # AI/ML dependencies (Mayank - Sprint 1)
└── README.md
```

---

## Getting Started

```bash
# Backend (FastAPI)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```