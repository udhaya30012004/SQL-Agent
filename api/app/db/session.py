from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from api.app.core.config import settings

# SQLite support is kept for tests/local overrides. The default metadata
# database is PostgreSQL.
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

# Create Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all ORM models
Base = declarative_base()

def get_db():
    """
    Dependency generator yielding a database session.
    Automatically closes the session after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
