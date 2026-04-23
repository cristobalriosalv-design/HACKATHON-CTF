from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.api.routes.users import router as users_router
from app.api.routes.videos import router as videos_router
from app.core.database import Base, engine
from app.models import Comment, Subscription, User, UserIdentity, Video

app = FastAPI(title="EIATube API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    ensure_video_thumbnail_column()
    ensure_video_uploader_column()


def ensure_video_thumbnail_column() -> None:
    inspector = inspect(engine)
    if "videos" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("videos")}
    if "thumbnail_path" in columns:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE videos ADD COLUMN thumbnail_path VARCHAR(500)"))


def ensure_video_uploader_column() -> None:
    inspector = inspect(engine)
    if "videos" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("videos")}
    if "uploader_id" in columns:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE videos ADD COLUMN uploader_id INTEGER"))


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(videos_router)
app.include_router(users_router)
