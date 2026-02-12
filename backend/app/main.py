from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(videos_router)
