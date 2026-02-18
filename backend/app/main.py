from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.api.routes.videos import router as videos_router
from app.core.database import Base, engine
from app.models import Comment, Video

app = FastAPI(title="YouTube Clone API")

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


def ensure_video_thumbnail_column() -> None:
    inspector = inspect(engine)
    if "videos" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("videos")}
    if "thumbnail_path" in columns:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE videos ADD COLUMN thumbnail_path VARCHAR(500)"))


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(videos_router)
