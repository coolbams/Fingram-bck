from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..config import DATA_DIR
from .models import Base

DATABASE_URL = f"sqlite:///{DATA_DIR / 'app.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine) 


def init_db() -> None:
    Base.metadata.create_all(engine)


def get_db():
    """ Dependency to get a database session. """
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()
