from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./erp.db"  # Pas eventueel aan naar jouw pad

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency die je in klanten.py gebruikt
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()