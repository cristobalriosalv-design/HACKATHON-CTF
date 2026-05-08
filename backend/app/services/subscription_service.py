from fastapi import HTTPException

from app.core.cache import cache_manager
from app.models.subscription import Subscription
from app.models.video import Video
from app.repositories.interfaces import SubscriptionRepositoryPort, UserRepositoryPort, VideoRepositoryPort


class SubscriptionService:
    def __init__(
        self,
        user_repo: UserRepositoryPort,
        subscription_repo: SubscriptionRepositoryPort,
        video_repo: VideoRepositoryPort,
    ):
        self.user_repo = user_repo
        self.subscription_repo = subscription_repo
        self.video_repo = video_repo

    def subscribe(self, follower_id: int, creator_id: int) -> Subscription:
        self._ensure_user_exists(follower_id)
        self._ensure_user_exists(creator_id)

        if follower_id == creator_id:
            raise HTTPException(status_code=400, detail="Cannot subscribe to yourself")

        existing = self.subscription_repo.get_by_pair(follower_id=follower_id, creator_id=creator_id)
        if existing:
            return existing

        result = self.subscription_repo.create(follower_id=follower_id, creator_id=creator_id)
        
        # Invalidate subscription and feed caches after subscribing
        cache_manager.clear_pattern(f"subscriptions:{follower_id}:*")
        cache_manager.clear_pattern(f"feed:{follower_id}:*")
        
        return result

    def unsubscribe(self, follower_id: int, creator_id: int) -> None:
        self._ensure_user_exists(follower_id)
        self._ensure_user_exists(creator_id)

        existing = self.subscription_repo.get_by_pair(follower_id=follower_id, creator_id=creator_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Subscription not found")

        self.subscription_repo.delete(existing)
        
        # Invalidate subscription and feed caches after unsubscribing
        cache_manager.clear_pattern(f"subscriptions:{follower_id}:*")
        cache_manager.clear_pattern(f"feed:{follower_id}:*")

    def list_subscription_creator_ids(self, follower_id: int, limit: int, offset: int) -> list[int]:
        self._ensure_user_exists(follower_id)
        
        # Try to get from cache
        cache_key = f"subscriptions:{follower_id}:{limit}:{offset}"
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Cache miss, fetch from repository
        result = self.subscription_repo.list_creator_ids(follower_id=follower_id, limit=limit, offset=offset)
        
        # Cache for 5 minutes
        cache_manager.set(cache_key, result, ttl=300)
        
        return result

    def get_subscription_feed(self, follower_id: int, limit: int, offset: int) -> list[Video]:
        # Try to get from cache (expensive operation with multiple table joins)
        cache_key = f"feed:{follower_id}:{limit}:{offset}"
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            # Deserialize Video objects if cached
            return [Video(**video_dict) if isinstance(video_dict, dict) else video_dict for video_dict in cached_result]
        
        # Cache miss, fetch from repositories
        creator_ids = self.list_subscription_creator_ids(follower_id=follower_id, limit=limit, offset=0)
        result = self.video_repo.get_by_uploader_ids(creator_ids, limit=limit, offset=offset)
        
        # Cache for 10 minutes (feed changes less frequently)
        # Convert Video objects to dict for JSON serialization
        cache_manager.set(cache_key, [video.model_dump() if hasattr(video, 'model_dump') else vars(video) for video in result], ttl=600)
        
        return result

    def is_subscribed(self, follower_id: int, creator_id: int) -> bool:
        if follower_id == creator_id:
            return False
        existing = self.subscription_repo.get_by_pair(follower_id=follower_id, creator_id=creator_id)
        return existing is not None

    def _ensure_user_exists(self, user_id: int) -> None:
        if not self.user_repo.get_by_id(user_id):
            raise HTTPException(status_code=404, detail="User not found")
