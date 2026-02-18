import mimetypes
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.subscription import SubscriptionListResponse, SubscriptionResponse
from app.schemas.user import ProviderListResponse, UserResponse
from app.schemas.video import VideoResponse
from app.services.subscription_service import SubscriptionService
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

UPLOAD_DIR = Path("uploads")


def to_user_response(user) -> UserResponse:
    return UserResponse(
        id=user.id,
        display_name=user.display_name,
        avatar_url=f"/users/{user.id}/avatar" if user.avatar_path else None,
        created_at=user.created_at,
    )


def to_video_response(video) -> VideoResponse:
    uploader = None
    if video.uploader:
        uploader = {
            "id": video.uploader.id,
            "display_name": video.uploader.display_name,
            "avatar_url": f"/users/{video.uploader.id}/avatar" if video.uploader.avatar_path else None,
        }

    return VideoResponse(
        id=video.id,
        title=video.title,
        description=video.description,
        created_at=video.created_at,
        views=video.views,
        stream_url=f"/videos/{video.id}/stream",
        thumbnail_url=f"/videos/{video.id}/thumbnail" if video.thumbnail_path else None,
        uploader=uploader,
    )


@router.get("", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    users = UserService(db).list_users()
    return [to_user_response(user) for user in users]


@router.post("", response_model=UserResponse)
def create_user(
    provider: str = Form("local"),
    display_name: str = Form(...),
    provider_subject: str = Form(""),
    email: str | None = Form(None),
    avatar: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    user = UserService(db).create_user(
        provider_name=provider,
        display_name=display_name,
        provider_subject=provider_subject,
        email=email,
        avatar=avatar,
        upload_dir=UPLOAD_DIR,
    )
    return to_user_response(user)


@router.get("/providers", response_model=ProviderListResponse)
def list_providers(db: Session = Depends(get_db)):
    providers = UserService(db).list_providers()
    return ProviderListResponse(providers=providers)


@router.get("/{user_id}/avatar")
def stream_avatar(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.get_user(user_id)
    file_path = service.ensure_avatar_file_exists(user)
    media_type = mimetypes.guess_type(file_path)[0] or "image/jpeg"
    return FileResponse(file_path, media_type=media_type, filename=Path(file_path).name)


@router.post("/{user_id}/subscriptions/{creator_id}", response_model=SubscriptionResponse)
def subscribe(user_id: int, creator_id: int, db: Session = Depends(get_db)):
    return SubscriptionService(db).subscribe(follower_id=user_id, creator_id=creator_id)


@router.delete("/{user_id}/subscriptions/{creator_id}")
def unsubscribe(user_id: int, creator_id: int, db: Session = Depends(get_db)):
    SubscriptionService(db).unsubscribe(follower_id=user_id, creator_id=creator_id)
    return {"status": "ok"}


@router.get("/{user_id}/subscriptions", response_model=SubscriptionListResponse)
def get_subscriptions(user_id: int, db: Session = Depends(get_db)):
    creator_ids = SubscriptionService(db).list_subscription_creator_ids(follower_id=user_id)
    return SubscriptionListResponse(creator_ids=creator_ids)


@router.get("/{user_id}/feed", response_model=list[VideoResponse])
def get_subscription_feed(user_id: int, db: Session = Depends(get_db)):
    videos = SubscriptionService(db).get_subscription_feed(follower_id=user_id)
    return [to_video_response(video) for video in videos]
