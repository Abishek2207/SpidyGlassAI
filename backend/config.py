import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "VisionVoice AI"
    # In a real environment, you'd load these from a .env file
    sarvam_api_key: str = os.getenv("SARVAM_API_KEY", "MOCK_KEY_FOR_NOW")
    debug_mode: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
