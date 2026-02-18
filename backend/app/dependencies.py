from fastapi import Depends
from sqlalchemy.orm import Session

from app.auth.providers import UserProviderRegistry, UserProviderRegistryPort
from app.core.database import get_db
from app.repositories.comment_repository import CommentRepository
from app.repositories.interfaces import (
    CommentRepositoryPort,
    SubscriptionRepositoryPort,
    UserRepositoryPort,
    VideoRepositoryPort,
)
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.user_repository import UserRepository
from app.repositories.video_repository import VideoRepository
from app.services.comment_service import CommentService
from app.services.interfaces import CommentServicePort, SubscriptionServicePort, UserServicePort, VideoServicePort
from app.services.subscription_service import SubscriptionService
from app.services.user_service import UserService
from app.services.video_service import VideoService


def get_video_repository(db: Session = Depends(get_db)) -> VideoRepositoryPort:
    return VideoRepository(db)


def get_comment_repository(db: Session = Depends(get_db)) -> CommentRepositoryPort:
    return CommentRepository(db)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepositoryPort:
    return UserRepository(db)


def get_subscription_repository(db: Session = Depends(get_db)) -> SubscriptionRepositoryPort:
    return SubscriptionRepository(db)


def get_user_provider_registry() -> UserProviderRegistryPort:
    return UserProviderRegistry()


def get_video_service(
    video_repo: VideoRepositoryPort = Depends(get_video_repository),
    user_repo: UserRepositoryPort = Depends(get_user_repository),
) -> VideoServicePort:
    return VideoService(repo=video_repo, user_repo=user_repo)


def get_comment_service(
    comment_repo: CommentRepositoryPort = Depends(get_comment_repository),
    video_repo: VideoRepositoryPort = Depends(get_video_repository),
) -> CommentServicePort:
    return CommentService(comment_repo=comment_repo, video_repo=video_repo)


def get_user_service(
    user_repo: UserRepositoryPort = Depends(get_user_repository),
    provider_registry: UserProviderRegistryPort = Depends(get_user_provider_registry),
) -> UserServicePort:
    return UserService(repo=user_repo, provider_registry=provider_registry)


def get_subscription_service(
    user_repo: UserRepositoryPort = Depends(get_user_repository),
    subscription_repo: SubscriptionRepositoryPort = Depends(get_subscription_repository),
    video_repo: VideoRepositoryPort = Depends(get_video_repository),
) -> SubscriptionServicePort:
    return SubscriptionService(
        user_repo=user_repo,
        subscription_repo=subscription_repo,
        video_repo=video_repo,
    )
