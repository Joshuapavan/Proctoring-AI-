from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv
import secrets

load_dotenv()

def generate_secret_key():
    return os.getenv("JWT_SECRET_KEY") or secrets.token_hex(64)

class Settings(BaseSettings):
    # Database settings
    DB_USER: str = os.getenv("MYSQLUSER", "root")
    DB_PASSWORD: str = os.getenv("MYSQL_ROOT_PASSWORD", "")
    DB_HOST: str = os.getenv("MYSQLHOST", "localhost") 
    DB_NAME: str = os.getenv("MYSQL_DATABASE", "defaultdb")
    DB_PORT: int = int(os.getenv("MYSQLPORT", "13926"))

    # JWT settings
    JWT_SECRET_KEY: str = Field(default_factory=generate_secret_key)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Server settings
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = int(os.getenv("PORT", "8080"))

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
