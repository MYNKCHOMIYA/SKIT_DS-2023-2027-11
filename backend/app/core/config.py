import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# 1. Dynamically find the absolute path to your 'backend' folder
BACKEND_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
ENV_FILE_PATH = os.path.join(BACKEND_DIR, ".env")

# 2. FIXED: Try to load the .env file if it exists (for local development).
# If it doesn't exist (like on Render), just skip silently!
if os.path.exists(ENV_FILE_PATH):
    load_dotenv(ENV_FILE_PATH)


class Settings(BaseSettings):
    PROJECT_NAME: str = "GFPMS API"
    API_V1_STR: str = "/api/v1"

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_DB: str

    # JWT Auth
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}?sslmode=require"

    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, extra="ignore")


# Tell Pylance to trust us here
settings = Settings()  # type: ignore
