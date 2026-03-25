import mimetypes
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse

from app.api.response_mappers import to_user_response, to_video_response
from app.dependencies import get_subscription_service, get_user_service
from app.schemas.subscription import SubscriptionListResponse, SubscriptionResponse
from app.schemas.user import ProviderListResponse, UserResponse
from app.schemas.video import VideoResponse
from app.services.interfaces import SubscriptionServicePort, UserServicePort

router = APIRouter(prefix="/users", tags=["users"])

UPLOAD_DIR = Path("uploads")


@router.get("", response_model=list[UserResponse])
def list_users(user_service: UserServicePort = Depends(get_user_service)):
    users = user_service.list_users()
    return [to_user_response(user) for user in users]


@router.post("", response_model=UserResponse)
def create_user(
    provider: str = Form("local"),
    display_name: str = Form(...),
    provider_subject: str = Form(""),
    email: str | None = Form(None),
    avatar: UploadFile | None = File(None),
    user_service: UserServicePort = Depends(get_user_service),
):
    user = user_service.create_user(
        provider_name=provider,
        display_name=display_name,
        provider_subject=provider_subject,
        email=email,
        avatar=avatar,
        upload_dir=UPLOAD_DIR,
    )
    return to_user_response(user)


@router.get("/providers", response_model=ProviderListResponse)
def list_providers(user_service: UserServicePort = Depends(get_user_service)):
    providers = user_service.list_providers()
    return ProviderListResponse(providers=providers)


@router.get("/{user_id}/avatar")
def stream_avatar(user_id: int, user_service: UserServicePort = Depends(get_user_service)):
    user = user_service.get_user(user_id)
    file_path = user_service.ensure_avatar_file_exists(user)
    media_type = mimetypes.guess_type(file_path)[0] or "image/jpeg"
    return FileResponse(file_path, media_type=media_type, filename=Path(file_path).name)


@router.post("/{user_id}/subscriptions/{creator_id}", response_model=SubscriptionResponse)
def subscribe(
    user_id: int,
    creator_id: int,
    subscription_service: SubscriptionServicePort = Depends(get_subscription_service),
):
    return subscription_service.subscribe(follower_id=user_id, creator_id=creator_id)


@router.delete("/{user_id}/subscriptions/{creator_id}")
def unsubscribe(
    user_id: int,
    creator_id: int,
    subscription_service: SubscriptionServicePort = Depends(get_subscription_service),
):
    subscription_service.unsubscribe(follower_id=user_id, creator_id=creator_id)
    return {"status": "ok"}


@router.get("/{user_id}/subscriptions", response_model=SubscriptionListResponse)
def get_subscriptions(
    user_id: int,
    subscription_service: SubscriptionServicePort = Depends(get_subscription_service),
):
    creator_ids = subscription_service.list_subscription_creator_ids(follower_id=user_id)
    return SubscriptionListResponse(creator_ids=creator_ids)


@router.get("/{user_id}/feed", response_model=list[VideoResponse])
def get_subscription_feed(
    user_id: int,
    subscription_service: SubscriptionServicePort = Depends(get_subscription_service),
):
    videos = subscription_service.get_subscription_feed(follower_id=user_id)
    return [to_video_response(video) for video in videos]
