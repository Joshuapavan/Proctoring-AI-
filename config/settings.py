from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database settings
    DB_USER: str = os.getenv("MYSQLUSER", "root")
    DB_PASSWORD: str = os.getenv("MYSQL_ROOT_PASSWORD", "")
    DB_HOST: str = os.getenv("MYSQLHOST", "localhost") 
    DB_NAME: str = os.getenv("MYSQL_DATABASE", "Proctoring_AI")
    DB_PORT: int = int(os.getenv("MYSQLPORT", "3306"))

    # JWT settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Server settings
    SERVER_HOST: str = os.getenv("SERVER_HOST", "localhost")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8080"))

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
