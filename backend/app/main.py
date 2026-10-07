from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth

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


# Sprint 1: Auth router — register, login, /me, admin user management
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
