import time
from sqlite3 import Connection as SQLite3Connection

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import QueuePool

DATABASE_URL = "sqlite:///./eiatube.db"


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30,
    },
    poolclass=QueuePool,
    pool_size=20,  # Number of connections to maintain in the pool
    max_overflow=40,  # Additional connections allowed when the pool is exhausted
    pool_recycle=3600,  # Recycle connections after 1 hour to prevent stale connections
    pool_pre_ping=True,  # Test connection before using it to ensure it's still valid
    # Connection pooling is crucial for handling concurrent users:
    # - pool_size ensures a baseline of ready connections, reducing connection setup overhead
    # - max_overflow allows the pool to scale under load without rejecting requests
    # - pool_recycle prevents SQLite stale connection issues in long-running processes
    # - pool_pre_ping detects disconnected connections and reconnects automatically,
    #   improving reliability under high concurrency and stress tests
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


def create_indices() -> None:
    """Create database indices for query optimization."""
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_video_uploader_id ON videos(uploader_id)",
        "CREATE INDEX IF NOT EXISTS idx_video_created_at ON videos(created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_video_category ON videos(category)",
        "CREATE INDEX IF NOT EXISTS idx_comment_video_id ON comments(video_id)",
        "CREATE INDEX IF NOT EXISTS idx_comment_created_at ON comments(created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_subscription_follower_id ON subscriptions(follower_id)",
        "CREATE INDEX IF NOT EXISTS idx_subscription_creator_id ON subscriptions(creator_id)",
    ]
    
    with engine.begin() as connection:
        for index_sql in indices:
            connection.execute(text(index_sql))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
