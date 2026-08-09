from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    app_name: str = "VITALS.IO API"
    version: str = "1.0.0"
    
    # Security / Database
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    next_public_supabase_url: Optional[str] = None # Fallback
    
    # Third-party APIs
    mistral_api_key: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env.local", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
