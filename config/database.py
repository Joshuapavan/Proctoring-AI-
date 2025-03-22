from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.logger import logger
from config.settings import settings
import os

def get_database_url():
    """Get database URL with fallbacks"""
    # First try Railway's URL
    if "MYSQL_URL" in os.environ:
        url = os.environ["MYSQL_URL"]
        # Remove ssl-mode from URL and handle it in create_engine
        if "ssl-mode" in url:
            url = url.split("?")[0]
        return url.replace('mysql://', 'mysql+mysqlconnector://')
    
    # Fallback to constructed URL
    return f"mysql+mysqlconnector://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

# Get Database URL
DATABASE_URL = get_database_url()
logger.info(f"Using database: {DATABASE_URL.split('@')[1]}")  # Log without credentials

# Configure SSL settings
ssl_args = {
    "ssl": {
        "ssl_verify_cert": True,
    }
}

engine = create_engine(
    DATABASE_URL,
    pool_size=5,  # Reduced from 20
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args=ssl_args
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        try:
            db.close()
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")

def init_db():
    import models.users  # Import models to register them
    import models.logs
    
    # Drop and recreate tables with new schema
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Use text() for raw SQL execution
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE users MODIFY COLUMN image LONGBLOB"))
        conn.commit()
