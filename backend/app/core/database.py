import time
from sqlite3 import Connection as SQLite3Connection

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./eiatube.db"


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30,
    },
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@event.listens_for(Engine, "connect")
def configure_sqlite_connection(dbapi_connection, _):
    if not isinstance(dbapi_connection, SQLite3Connection):
        return

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.execute("PRAGMA busy_timeout=30000;")
    cursor.close()


def commit_with_retry(db, max_retries: int = 5, base_delay_seconds: float = 0.05) -> None:
    for attempt in range(max_retries + 1):
        try:
            db.commit()
            return
        except OperationalError as exc:
            error_message = str(exc).lower()
            is_locked_error = "database is locked" in error_message or "database table is locked" in error_message
            if not is_locked_error or attempt >= max_retries:
                db.rollback()
                raise

            db.rollback()
            time.sleep(base_delay_seconds * (2**attempt))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
