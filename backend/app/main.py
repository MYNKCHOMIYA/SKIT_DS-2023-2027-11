from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Force SQLAlchemy to load all models from __init__.py at startup
import app.models as _models  # noqa: F401

from app.api import auth, faculty_profile, education, experience, achievement

from sqlalchemy import text
from contextlib import asynccontextmanager
from app.db.session import engine
from app.models.base import Base


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
    title="Generalized Faculty Portfolio System API",
    description="Backend API for managing faculty profiles, achievements, and statistics",
    version="1.0.0",
    lifespan=lifespan,
)


# CORS Configuration for Frontend (Next.js)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
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
