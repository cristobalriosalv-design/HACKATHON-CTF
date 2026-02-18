from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from app.models.video import Video
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.user_repository import UserRepository
from app.repositories.video_repository import VideoRepository


class SubscriptionService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.subscription_repo = SubscriptionRepository(db)
        self.video_repo = VideoRepository(db)

    def subscribe(self, follower_id: int, creator_id: int) -> Subscription:
        self._ensure_user_exists(follower_id)
        self._ensure_user_exists(creator_id)

        if follower_id == creator_id:
            raise HTTPException(status_code=400, detail="Cannot subscribe to yourself")

        existing = self.subscription_repo.get_by_pair(follower_id=follower_id, creator_id=creator_id)
        if existing:
            return existing

        return self.subscription_repo.create(follower_id=follower_id, creator_id=creator_id)

    def unsubscribe(self, follower_id: int, creator_id: int) -> None:
        self._ensure_user_exists(follower_id)
        self._ensure_user_exists(creator_id)

        existing = self.subscription_repo.get_by_pair(follower_id=follower_id, creator_id=creator_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Subscription not found")

        self.subscription_repo.delete(existing)

    def list_subscription_creator_ids(self, follower_id: int) -> list[int]:
        self._ensure_user_exists(follower_id)
        return self.subscription_repo.list_creator_ids(follower_id=follower_id)

    def get_subscription_feed(self, follower_id: int) -> list[Video]:
        creator_ids = self.list_subscription_creator_ids(follower_id=follower_id)
        return self.video_repo.get_by_uploader_ids(creator_ids)

    def is_subscribed(self, follower_id: int, creator_id: int) -> bool:
        if follower_id == creator_id:
            return False
        existing = self.subscription_repo.get_by_pair(follower_id=follower_id, creator_id=creator_id)
        return existing is not None

    def _ensure_user_exists(self, user_id: int) -> None:
        if not self.user_repo.get_by_id(user_id):
            raise HTTPException(status_code=404, detail="User not found")
