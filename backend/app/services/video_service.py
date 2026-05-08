import os
import re
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.cache import cache_manager
from app.core.uploads import validate_video_size, validate_thumbnail_size
from app.models.video import Video
from app.repositories.interfaces import UserRepositoryPort, VideoRepositoryPort


class VideoService:
    UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1 MiB
    ALLOWED_CATEGORIES = {"music", "gaming", "news"}

    def __init__(self, repo: VideoRepositoryPort, user_repo: UserRepositoryPort):
        self.repo = repo
        self.user_repo = user_repo

    def list_videos(self, limit: int, offset: int) -> list[Video]:
        cache_key = f"videos:list:{limit}:{offset}"
        
        # Check cache first
        cached_videos = cache_manager.get(cache_key)
        if cached_videos is not None:
            return cached_videos
        
        # Query DB if not cached
        videos = self.repo.get_all(limit=limit, offset=offset)
        
        # Cache result for 5 minutes
        cache_manager.set(cache_key, videos, ttl=300)
        
        return videos

    def get_video(self, video_id: int) -> Video:
        cache_key = f"video:{video_id}"
        
        # Check cache first
        cached_video = cache_manager.get(cache_key)
        if cached_video is not None:
            return cached_video
        
        # Query DB if not cached
        video = self.repo.get_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Cache result for 10 minutes
        cache_manager.set(cache_key, video, ttl=600)
        
        return video

    def upload_video(
        self,
        title: str,
        description: str,
        category: str | None,
        file: UploadFile,
        upload_dir: Path,
        thumbnail: UploadFile | None = None,
        uploader_id: int | None = None,
    ) -> Video:
        normalized_category: str | None = None
        if category and category.strip():
            normalized_category = category.strip().lower()
            if normalized_category not in self.ALLOWED_CATEGORIES:
                allowed = ", ".join(sorted(self.ALLOWED_CATEGORIES))
                raise HTTPException(status_code=400, detail=f"Invalid category. Allowed values: {allowed}")

        if uploader_id is not None and self.user_repo.get_by_id(uploader_id) is None:
            raise HTTPException(status_code=404, detail="Uploader not found")

        # Validate video file size before processing
        import asyncio
        asyncio.run(validate_video_size(file))

        upload_dir.mkdir(parents=True, exist_ok=True)

        video_path = self._save_upload_file(file=file, directory=upload_dir, default_name="video.mp4")

        thumbnail_path: str | None = None
        if thumbnail:
            if thumbnail.content_type and not thumbnail.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="Thumbnail must be an image")
            # Validate thumbnail size before processing
            asyncio.run(validate_thumbnail_size(thumbnail))
            thumbnail_dir = upload_dir / "thumbnails"
            thumbnail_dir.mkdir(parents=True, exist_ok=True)
            thumbnail_path = self._save_upload_file(file=thumbnail, directory=thumbnail_dir, default_name="thumb.jpg")

        video = self.repo.create(
            title=title,
            description=description,
            category=normalized_category,
            file_path=video_path,
            thumbnail_path=thumbnail_path,
            uploader_id=uploader_id,
        )
        
        # Invalidate list caches when new video is uploaded
        cache_manager.clear_pattern("videos:list:*")
        
        return video

    def get_recommended(self, video_id: int, limit: int = 8) -> list[Video]:
        cache_key = f"video:recommended:{video_id}"
        
        # Check cache first
        cached_recommendations = cache_manager.get(cache_key)
        if cached_recommendations is not None:
            return cached_recommendations
        
        # Query DB if not cached
        current = self.get_video(video_id)
        terms = self._extract_title_terms(current.title)
        recommendations = self.repo.get_recommended_by_title_terms(
            excluded_video_id=current.id,
            terms=terms,
            limit=limit,
        )
        
        # Cache result for 30 minutes (recommendations change less frequently)
        cache_manager.set(cache_key, recommendations, ttl=1800)
        
        return recommendations

    def increment_views(self, video_id: int) -> Video:
        video = self.get_video(video_id)
        updated_video = self.repo.increment_views(video)
        
        # Invalidate video cache since views changed
        cache_manager.delete(f"video:{video_id}")
        # Invalidate recommendations cache since view counts may affect sorting
        cache_manager.delete(f"video:recommended:{video_id}")
        
        return updated_video


    def get_videos_by_ids(self, video_ids: list[int]) -> list[Video]:
        """Get multiple videos by IDs in a single query (prevents N+1 queries)."""
        if not video_ids:
            return []
        
        cache_key = f"videos:batch:{','.join(map(str, sorted(video_ids)))}"
        
        # Check cache first
        cached_videos = cache_manager.get(cache_key)
        if cached_videos is not None:
            return cached_videos
        
        # Query DB if not cached
        videos = self.repo.get_by_ids(video_ids)
        
        # Cache result for 10 minutes
        cache_manager.set(cache_key, videos, ttl=600)
        
        return videos

    def increment_views_batch(self, video_ids: list[int], increment: int = 1) -> list[Video]:
        """Atomically increment views for multiple videos in a single operation."""
        if not video_ids:
            return []
        
        # Atomic database update
        videos = self.repo.increment_views_batch(video_ids, increment)
        
        # Invalidate caches for all affected videos
        for video_id in video_ids:
            cache_manager.delete(f"video:{video_id}")
            cache_manager.delete(f"video:recommended:{video_id}")
        
        return videos

    def delete_video(self, video_id: int, requester_user_id: int) -> None:
        if self.user_repo.get_by_id(requester_user_id) is None:
            raise HTTPException(status_code=404, detail="User not found")

        video = self.get_video(video_id)
        if video.uploader_id is None or video.uploader_id != requester_user_id:
            raise HTTPException(status_code=403, detail="Only the video owner can delete this video")

        file_paths = [video.file_path]
        if video.thumbnail_path:
            file_paths.append(video.thumbnail_path)

        self.repo.delete(video)
        
        # Invalidate all related caches when video is deleted
        cache_manager.delete(f"video:{video_id}")
        cache_manager.delete(f"video:recommended:{video_id}")
        cache_manager.clear_pattern("videos:list:*")

        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)

    def ensure_video_file_exists(self, video: Video) -> str:
        if not os.path.exists(video.file_path):
            raise HTTPException(status_code=404, detail="Video file not found")
        return video.file_path

    def ensure_thumbnail_file_exists(self, video: Video) -> str:
        if not video.thumbnail_path or not os.path.exists(video.thumbnail_path):
            raise HTTPException(status_code=404, detail="Thumbnail not found")
        return video.thumbnail_path

    def _save_upload_file(self, file: UploadFile, directory: Path, default_name: str) -> str:
        suffix = Path(file.filename or default_name).suffix or Path(default_name).suffix
        filename = f"{uuid.uuid4()}{suffix}"
        destination = directory / filename

        with destination.open("wb") as buffer:
            while True:
                chunk = file.file.read(self.UPLOAD_CHUNK_SIZE)
                if not chunk:
                    break
                buffer.write(chunk)

        return str(destination)

    def _extract_title_terms(self, title: str) -> list[str]:
        terms: list[str] = []
        for term in re.findall(r"\w+", title.lower()):
            if len(term) < 3 or term in terms:
                continue
            terms.append(term)
            if len(terms) >= 12:
                break
        return terms
