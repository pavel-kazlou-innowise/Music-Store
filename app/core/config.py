from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./data/records_store.db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-keep-it-secret"  # В реальном проекте должен быть в .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Records Store API"
    
    class Config:
        case_sensitive = True

settings = Settings()
