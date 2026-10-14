from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Force SQLAlchemy to load all models from __init__.py at startup
import app.models as _models  # noqa: F401

from app.api import auth, faculty_profile, education, experience, achievement

# Initialize FastAPI App
app = FastAPI(
    title="Generalized Faculty Portfolio System API",
    description="Backend API for managing faculty profiles, achievements, and statistics",
    version="1.0.0",
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
