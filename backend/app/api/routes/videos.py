from pathlib import Path
import mimetypes

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import FileResponse

from app.api.response_mappers import to_video_response
from app.dependencies import get_comment_service, get_video_service
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.video import VideoResponse
from app.services.interfaces import CommentServicePort, VideoServicePort

router = APIRouter(prefix="/videos", tags=["videos"])

UPLOAD_DIR = Path("uploads")


@router.get("", response_model=list[VideoResponse])
def get_videos(video_service: VideoServicePort = Depends(get_video_service)):
    videos = video_service.list_videos()
    return [to_video_response(video) for video in videos]


@router.post("/upload", response_model=VideoResponse)
def upload_video(
    title: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    thumbnail: UploadFile | None = File(None),
    uploader_id: int | None = Form(None),
    video_service: VideoServicePort = Depends(get_video_service),
):
    video = video_service.upload_video(
        title=title,
        description=description,
        file=file,
        upload_dir=UPLOAD_DIR,
        thumbnail=thumbnail,
        uploader_id=uploader_id,
    )
    return to_video_response(video)


@router.get("/{video_id}", response_model=VideoResponse)
def get_video(video_id: int, video_service: VideoServicePort = Depends(get_video_service)):
    video = video_service.increment_views(video_id)
    return to_video_response(video)


@router.delete("/{video_id}")
def delete_video(
    video_id: int,
    requester_user_id: int = Query(...),
    video_service: VideoServicePort = Depends(get_video_service),
):
    video_service.delete_video(video_id=video_id, requester_user_id=requester_user_id)
    return {"status": "ok"}


@router.get("/{video_id}/stream")
def stream_video(video_id: int, video_service: VideoServicePort = Depends(get_video_service)):
    video = video_service.get_video(video_id)
    file_path = video_service.ensure_video_file_exists(video)
    return FileResponse(file_path, media_type="video/mp4", filename=Path(file_path).name)


@router.get("/{video_id}/thumbnail")
def stream_thumbnail(video_id: int, video_service: VideoServicePort = Depends(get_video_service)):
    video = video_service.get_video(video_id)
    file_path = video_service.ensure_thumbnail_file_exists(video)
    media_type = mimetypes.guess_type(file_path)[0] or "image/jpeg"
    return FileResponse(file_path, media_type=media_type, filename=Path(file_path).name)


@router.get("/{video_id}/comments", response_model=list[CommentResponse])
def get_comments(video_id: int, comment_service: CommentServicePort = Depends(get_comment_service)):
    return comment_service.list_comments(video_id)


@router.post("/{video_id}/comments", response_model=CommentResponse)
def post_comment(
    video_id: int,
    payload: CommentCreate,
    comment_service: CommentServicePort = Depends(get_comment_service),
):
    return comment_service.create_comment(video_id=video_id, author=payload.author, content=payload.content)


@router.get("/{video_id}/recommended", response_model=list[VideoResponse])
def get_recommended(video_id: int, video_service: VideoServicePort = Depends(get_video_service)):
    videos = video_service.get_recommended(video_id)
    return [to_video_response(video) for video in videos]
