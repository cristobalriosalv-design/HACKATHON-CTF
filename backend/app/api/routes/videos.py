from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.video import VideoResponse
from app.services.comment_service import CommentService
from app.services.video_service import VideoService

router = APIRouter(prefix="/videos", tags=["videos"])

UPLOAD_DIR = Path("uploads")


def to_video_response(video) -> VideoResponse:
    return VideoResponse(
        id=video.id,
        title=video.title,
        description=video.description,
        created_at=video.created_at,
        views=video.views,
        stream_url=f"/videos/{video.id}/stream",
    )


@router.get("", response_model=list[VideoResponse])
def get_videos(db: Session = Depends(get_db)):
    videos = VideoService(db).list_videos()
    return [to_video_response(video) for video in videos]


@router.post("/upload", response_model=VideoResponse)
def upload_video(
    title: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    video = VideoService(db).upload_video(title=title, description=description, file=file, upload_dir=UPLOAD_DIR)
    return to_video_response(video)


@router.get("/{video_id}", response_model=VideoResponse)
def get_video(video_id: int, db: Session = Depends(get_db)):
    video = VideoService(db).increment_views(video_id)
    return to_video_response(video)


@router.get("/{video_id}/stream")
def stream_video(video_id: int, db: Session = Depends(get_db)):
    service = VideoService(db)
    video = service.get_video(video_id)
    file_path = service.ensure_video_file_exists(video)
    return FileResponse(file_path, media_type="video/mp4", filename=Path(file_path).name)


@router.get("/{video_id}/comments", response_model=list[CommentResponse])
def get_comments(video_id: int, db: Session = Depends(get_db)):
    return CommentService(db).list_comments(video_id)


@router.post("/{video_id}/comments", response_model=CommentResponse)
def post_comment(video_id: int, payload: CommentCreate, db: Session = Depends(get_db)):
    return CommentService(db).create_comment(video_id=video_id, author=payload.author, content=payload.content)


@router.get("/{video_id}/recommended", response_model=list[VideoResponse])
def get_recommended(video_id: int, db: Session = Depends(get_db)):
    videos = VideoService(db).get_recommended(video_id)
    return [to_video_response(video) for video in videos]
