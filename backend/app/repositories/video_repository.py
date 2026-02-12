from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.video import Video


class VideoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Video]:
        return self.db.query(Video).order_by(desc(Video.created_at)).all()

    def get_by_id(self, video_id: int) -> Video | None:
        return self.db.query(Video).filter(Video.id == video_id).first()

    def create(self, title: str, description: str, file_path: str) -> Video:
        video = Video(title=title, description=description, file_path=file_path)
        self.db.add(video)
        self.db.commit()
        self.db.refresh(video)
        return video

    def increment_views(self, video: Video) -> Video:
        video.views += 1
        self.db.commit()
        self.db.refresh(video)
        return video
