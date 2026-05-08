from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy import inspect, text
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.routes.users import router as users_router
from app.api.routes.videos import router as videos_router
from app.core.database import Base, engine, create_indices
from app.models import Comment, Subscription, User, UserIdentity, Video

app = FastAPI(title="EIATube API")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add Gzip compression middleware for response compression
# This should be added before CORS middleware for proper header handling
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security headers middleware to prevent common attacks
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response

# CORS middleware with restricted origins for security
# NOTE: allow_origins=["*"] is commented out below for development/production separation.
# In development, you may use ["*"], but production should always use specific domains.
# Current configuration restricts to specific localhost ports for security.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    # allow_origins=["*"],  # Uncomment only for development with wildcard CORS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    ensure_video_thumbnail_column()
    ensure_video_uploader_column()
    ensure_video_category_column()
    create_indices()


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


def ensure_video_category_column() -> None:
    inspector = inspect(engine)
    if "videos" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("videos")}
    if "category" in columns:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE videos ADD COLUMN category VARCHAR(50) DEFAULT '' NOT NULL"))


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(videos_router)
app.include_router(users_router)
