from pydantic import BaseModel
import os

class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://interview:interview_pw@db:5432/interview_prep")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000")

settings = Settings()
