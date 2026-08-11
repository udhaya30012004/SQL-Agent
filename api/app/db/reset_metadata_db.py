"""Drop all public tables and recreate backend metadata tables."""

from sqlalchemy import inspect, text

from api.app.core.config import settings
from api.app.db.session import Base, engine

# Import models so SQLAlchemy registers every table on Base.metadata.
from api.app.models.user import User  # noqa: F401
from api.app.models.chat import ChatMessage, ChatSession  # noqa: F401


def reset_metadata_db() -> None:
    if not settings.DATABASE_URL.startswith("postgresql"):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        return

    inspector = inspect(engine)
    table_names = inspector.get_table_names(schema="public")
    preparer = engine.dialect.identifier_preparer

    with engine.begin() as connection:
        for table_name in table_names:
            qualified_name = (
                f"{preparer.quote_schema('public')}.{preparer.quote(table_name)}"
            )
            connection.execute(text(f"DROP TABLE IF EXISTS {qualified_name} CASCADE"))

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    reset_metadata_db()
    print("Backend metadata tables reset successfully.")
