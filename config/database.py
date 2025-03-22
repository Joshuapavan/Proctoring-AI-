from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.logger import logger

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:1234567890@localhost/Proctoring_AI"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
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
