import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.video import Video
from app.repositories.video_repository import VideoRepository


class VideoService:
    def __init__(self, db: Session):
        self.repo = VideoRepository(db)

    def list_videos(self) -> list[Video]:
        return self.repo.get_all()

    def get_video(self, video_id: int) -> Video:
        video = self.repo.get_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        return video

    def upload_video(self, title: str, description: str, file: UploadFile, upload_dir: Path) -> Video:
        suffix = Path(file.filename or "video.mp4").suffix or ".mp4"
        filename = f"{uuid.uuid4()}{suffix}"
        upload_dir.mkdir(parents=True, exist_ok=True)
        destination = upload_dir / filename

        with destination.open("wb") as buffer:
            buffer.write(file.file.read())

        return self.repo.create(title=title, description=description, file_path=str(destination))

    def get_recommended(self, video_id: int, limit: int = 8) -> list[Video]:
        current = self.get_video(video_id)
        all_videos = self.repo.get_all()

        current_terms = set(current.title.lower().split())

        def score(video: Video) -> tuple[int, int]:
            if video.id == current.id:
                return (-1, -1)
            terms = set(video.title.lower().split())
            overlap = len(current_terms.intersection(terms))
            return (overlap, video.views)

        ranked = sorted(all_videos, key=score, reverse=True)
        return [video for video in ranked if video.id != current.id][:limit]

    def increment_views(self, video_id: int) -> Video:
        video = self.get_video(video_id)
        return self.repo.increment_views(video)

    def ensure_video_file_exists(self, video: Video) -> str:
        if not os.path.exists(video.file_path):
            raise HTTPException(status_code=404, detail="Video file not found")
        return video.file_path
