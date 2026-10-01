# Analytics Architecture — Sprint 1 Planning
**Author:** Mayank Kumar (AI/ML Engineer)
**Sprint:** 1 — Foundation & Access Management
**Date:** Sep 15, 2026 – Oct 15, 2026

---

## Objective
Define the core analytics pipeline architecture that will underpin all ML and
statistical work in Sprints 3–6. This document records the research outcomes
and metric decisions made during Sprint 1.

---

## Key Metrics Selected for Evaluation

| Metric | Source Field | Planned Use |
|--------|-------------|-------------|
| **Publication Count** | `publications` table | Time-series paper output per year |
| **Profile Completeness Score** | `faculty_profiles` fields | Weighted scoring (30 completeness + 30 keyword + 20 verb + 20 impact) |
| **Domain Keywords** | `bio`, `skills`, `areas_of_interest` | TF-IDF clustering into research domains |
| **H-Index Simulation** | `publications.citations` | Approximate h-index from citation counts |
| **Project Activity** | `projects.status = 'active'` | Research engagement indicator |

---

## Proposed ML Pipeline (Sprint 3+)

```
PostgreSQL DB
    │
    ▼
[ETL — Pandas/SQLAlchemy]
    │  • Extract faculty records
    │  • Handle nulls, date parsing
    │  • Normalize text fields
    ▼
[Feature Engineering]
    │  • TF-IDF on bio/skills → domain clusters
    │  • Count-based features (pub count, h-index)
    │  • Completeness vector (0-1 per field)
    ▼
[Scikit-Learn Models]
    │  • Completeness scoring (weighted algorithm)
    │  • Research trend time-series aggregation
    │  • Cosine similarity for domain classification
    ▼
[FastAPI Endpoints — /api/analytics]
    │  • Serve insights to frontend dashboard
    ▼
[Recharts Frontend Dashboard]
```

---

## Research Outcomes (Sprint 1)

- **Approach chosen:** Statistical aggregation + NLP (NLTK/spaCy) over full ML model training.
  Justification: Faculty dataset is small (~100 records); heavy model training is overkill.
- **Library stack confirmed:** `pandas`, `numpy`, `scikit-learn`, `spacy`, `sentence-transformers`
- **Profile completeness scoring:** Weighted rubric approach (modelled after ATS systems)
- **Domain classification:** Zero-shot semantic similarity via SentenceTransformer embeddings

---

## Dependencies to Add (Sprint 3+)

```
pandas>=2.1.0
numpy>=1.26.0
scikit-learn>=1.4.0
spacy>=3.7.0
sentence-transformers>=2.2.0
nltk>=3.8.0
```
