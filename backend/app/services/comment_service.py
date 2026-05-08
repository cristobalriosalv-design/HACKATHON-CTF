from fastapi import HTTPException

from app.core.cache import cache_manager
from app.repositories.interfaces import CommentRepositoryPort, VideoRepositoryPort


class CommentService:
    def __init__(self, comment_repo: CommentRepositoryPort, video_repo: VideoRepositoryPort):
        self.comment_repo = comment_repo
        self.video_repo = video_repo

    def list_comments(self, video_id: int, limit: int, offset: int):
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Try to get from cache
        cache_key = f"comments:{video_id}:{limit}:{offset}"
        cached_comments = cache_manager.get(cache_key)
        if cached_comments is not None:
            return cached_comments
        
        # Get from repository
        comments = self.comment_repo.get_by_video_id(video_id=video_id, limit=limit, offset=offset)
        
        # Cache with 3 minute TTL
        cache_manager.set(cache_key, comments, ttl=180)
        return comments

    def create_comment(self, video_id: int, author: str, content: str):
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        new_comment = self.comment_repo.create(video_id=video_id, author=author, content=content)
        
        # Invalidate comment list cache for this video
        cache_manager.clear_pattern(f"comments:{video_id}:*")
        
        # Invalidate video recommendations cache since engagement metrics may affect recommendations
        cache_manager.clear_pattern(f"video:recommended:{video_id}")
        
        return new_comment
