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
- FastAPI app scaffolded with CORS middleware for Next.js (`backend/app/main.py`)
- PostgreSQL connection via SQLAlchemy + env-based URL, SQLite fallback for local dev (`backend/app/db/session.py`)
- JWT authentication — bcrypt password hashing + PyJWT token creation (`backend/app/core/security.py`)
- Pydantic settings with `.env` + Render env var support (`backend/app/core/config.py`)
- Auth API — `/register`, `/login`, `/me`, admin user management endpoints (`backend/app/api/auth.py`)
- FastAPI dependency injection — JWT decode, session provider, role guards (`backend/app/api/deps.py`)
- DB models — `User` (UUID PK, RBAC roles), `Department`, `FacultyProfile` (`backend/app/models/`)
- Pydantic schemas — `UserCreate`, `UserResponse`, `UserAdminResponse`, `Token` (`backend/app/schemas/`)
- Alembic migration setup wired to PostgreSQL via env (`backend/alembic/env.py`, `alembic.ini`)

**Mayank (AI/ML):**
- Analytics architecture designed & documented (`backend/docs/analytics_architecture.md`)
- Key metrics defined: publication count, profile completeness score, domain keywords, h-index simulation
- AI/ML dependency stack researched & documented (`backend/docs/requirements_ai.txt`)
- Enhanced `FacultyProfile` schema with NLP-ready text fields (`bio`, `skills`) and analytical annotations

**Manan (Frontend):**
- Next.js project scaffolded with TypeScript, Tailwind CSS, Shadcn UI
- Global design system & CSS tokens (`frontend/app/globals.css`)
- Root layout with Inter font, metadata, and Sprint 2 provider hooks (`frontend/app/layout.tsx`)
- Login page — React Hook Form + Zod validation + Framer Motion animations (`frontend/app/(auth)/login/page.tsx`)
- Register page — `@skit.ac.in` email enforcement, faculty-role info banner (`frontend/app/(auth)/register/page.tsx`)
- Axios API client with JWT interceptor & 401 auto-redirect (`frontend/lib/api.ts`)
- React Query (`TanStack Query`) provider with 5-min stale time config (`frontend/lib/providers.tsx`)

---

## Project Structure

```
SKIT_DS-2023-2027-11/
├── backend/
│   ├── app/
│   │   └── models/
│   │       ├── base.py                    # SQLAlchemy declarative base
│   │       └── faculty_profile.py         # Core faculty schema (AI/ML annotated)
│   └── docs/
│       ├── analytics_architecture.md      # ML pipeline design (Mayank - Sprint 1)
│       └── requirements_ai.txt            # AI/ML dependencies (Mayank - Sprint 1)
├── frontend/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx             # Login UI — RHF + Zod + Framer Motion
│   │   │   └── register/page.tsx          # Register UI — @skit.ac.in validation
│   │   ├── globals.css                    # Tailwind CSS tokens & design system
│   │   └── layout.tsx                     # Root layout with metadata
│   └── lib/
│       ├── api.ts                         # Axios client + JWT interceptor
│       └── providers.tsx                  # React Query provider
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