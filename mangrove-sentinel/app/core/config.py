from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Mangrove Sentinel"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for mangrove conservation monitoring"
    
    # Database
    DATABASE_URL: str = "sqlite:///./mangrove_sentinel.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API
    API_V1_STR: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()