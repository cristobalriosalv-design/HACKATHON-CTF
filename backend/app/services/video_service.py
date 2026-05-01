import os
import re
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.models.video import Video
from app.repositories.interfaces import UserRepositoryPort, VideoRepositoryPort


class VideoService:
    UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1 MiB
    ALLOWED_CATEGORIES = {"music", "gaming", "news"}

    def __init__(self, repo: VideoRepositoryPort, user_repo: UserRepositoryPort):
        self.repo = repo
        self.user_repo = user_repo

    def list_videos(self, limit: int, offset: int) -> list[Video]:
        return self.repo.get_all(limit=limit, offset=offset)

    def get_video(self, video_id: int) -> Video:
        video = self.repo.get_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
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

        upload_dir.mkdir(parents=True, exist_ok=True)

        video_path = self._save_upload_file(file=file, directory=upload_dir, default_name="video.mp4")

        thumbnail_path: str | None = None
        if thumbnail:
            if thumbnail.content_type and not thumbnail.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="Thumbnail must be an image")
            thumbnail_dir = upload_dir / "thumbnails"
            thumbnail_dir.mkdir(parents=True, exist_ok=True)
            thumbnail_path = self._save_upload_file(file=thumbnail, directory=thumbnail_dir, default_name="thumb.jpg")

        return self.repo.create(
            title=title,
            description=description,
            category=normalized_category,
            file_path=video_path,
            thumbnail_path=thumbnail_path,
            uploader_id=uploader_id,
        )

    def get_recommended(self, video_id: int, limit: int = 8) -> list[Video]:
        current = self.get_video(video_id)
        # Keep recommendation query bounded and computed in SQL.
        terms = self._extract_title_terms(current.title)
        return self.repo.get_recommended_by_title_terms(
            excluded_video_id=current.id,
            terms=terms,
            limit=limit,
        )

    def increment_views(self, video_id: int) -> Video:
        video = self.get_video(video_id)
        return self.repo.increment_views(video)

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
