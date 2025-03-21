from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:1234567890@localhost/Proctoring_AI"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
