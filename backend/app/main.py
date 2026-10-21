from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text
import cloudinary

# Force SQLAlchemy to load all models from __init__.py at startup
import app.models as _models  # noqa: F401

from app.core.config import settings
from app.db.session import engine
from app.models.base import Base

from app.api import (
    auth,
    faculty_profile,
    education,
    experience,
    achievement,
    publication,
    project,
    patent,
    certification,
    teaching,
    student_guidance,
    workshop,
    upload,
    search,
    analytics,
    notifications,
    activity,
    public_portfolio,
)


def startup_db_init():
    """Ensure database tables exist and SQLite columns are up to date for local development."""
    Base.metadata.create_all(bind=engine)
    if "sqlite" in str(engine.url):
        with engine.connect() as conn:
            try:
                columns = [
                    col[1]
                    for col in conn.execute(text("PRAGMA table_info(users)")).fetchall()
                ]
                if columns:
                    if "auth_provider" not in columns:
                        conn.execute(
                            text(
                                "ALTER TABLE users ADD COLUMN auth_provider VARCHAR DEFAULT 'local'"
                            )
                        )
                    if "google_id" not in columns:
                        conn.execute(
                            text("ALTER TABLE users ADD COLUMN google_id VARCHAR")
                        )
                    conn.commit()
            except Exception:
                pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    startup_db_init()
    yield


# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for managing faculty profiles, achievements, and statistics",
    version="1.0.0",
    lifespan=lifespan,
)

# Cloudinary configuration
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Generalized Faculty Portfolio System API"}


# ── Routers ────────────────────────────────────────────────────────────────────
# Sprint 1: Auth router
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])

# Sprint 2: Core Faculty Profile, Education, Experience, Achievement
app.include_router(
    faculty_profile.router, prefix="/api/v1/profile", tags=["Faculty Profile"]
)
app.include_router(education.router, prefix="/api/v1/education", tags=["Education"])
app.include_router(experience.router, prefix="/api/v1/experience", tags=["Experience"])
app.include_router(
    achievement.router, prefix="/api/v1/achievements", tags=["Achievements"]
)

# Sprint 2 & 3: Academic & Research Modules (Kunal)
app.include_router(
    publication.router, prefix="/api/v1/publications", tags=["Publications"]
)
app.include_router(project.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(patent.router, prefix="/api/patents", tags=["Patents"])
app.include_router(
    patent.router,
    prefix="/api/v1/patents",
    tags=["Patents (v1)"],
    include_in_schema=False,
)
app.include_router(
    certification.router, prefix="/api/certifications", tags=["Certifications"]
)
app.include_router(
    certification.router,
    prefix="/api/v1/certifications",
    tags=["Certifications (v1)"],
    include_in_schema=False,
)
app.include_router(teaching.router, prefix="/api/teaching", tags=["Teaching"])
app.include_router(
    teaching.router,
    prefix="/api/v1/teaching",
    tags=["Teaching (v1)"],
    include_in_schema=False,
)
app.include_router(
    student_guidance.router, prefix="/api/student-guidance", tags=["Student Guidance"]
)
app.include_router(
    student_guidance.router,
    prefix="/api/v1/student-guidance",
    tags=["Student Guidance (v1)"],
    include_in_schema=False,
)
app.include_router(workshop.router, prefix="/api/workshops", tags=["Workshops & FDP"])
app.include_router(
    workshop.router,
    prefix="/api/v1/workshops",
    tags=["Workshops & FDP (v1)"],
    include_in_schema=False,
)
app.include_router(upload.router, prefix="/api/upload", tags=["File Uploads"])
app.include_router(
    upload.router,
    prefix="/api/v1/upload",
    tags=["File Uploads (v1)"],
    include_in_schema=False,
)
app.include_router(search.router, prefix="/api/search", tags=["Search & Filter"])
app.include_router(
    search.router,
    prefix="/api/v1/search",
    tags=["Search & Filter (v1)"],
    include_in_schema=False,
)
app.include_router(analytics.router, prefix="/api/analytics", tags=["Data & Analytics"])
app.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["Data & Analytics (v1)"],
    include_in_schema=False,
)
app.include_router(notifications.router, prefix="/api")
app.include_router(activity.router, prefix="/api")
app.include_router(
    public_portfolio.router,
    prefix="/api/v1/portfolio/public",
    tags=["Public Portfolio"],
)
