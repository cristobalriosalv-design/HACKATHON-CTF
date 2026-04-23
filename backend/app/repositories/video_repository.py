from sqlalchemy import case, desc, func
from sqlalchemy.orm import Session

from app.core.database import commit_with_retry
from app.models.video import Video


class VideoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Video]:
        return self.db.query(Video).order_by(desc(Video.created_at)).all()

    def get_by_id(self, video_id: int) -> Video | None:
        return self.db.query(Video).filter(Video.id == video_id).first()

    def get_by_uploader_ids(self, uploader_ids: list[int]) -> list[Video]:
        if not uploader_ids:
            return []
        return (
            self.db.query(Video)
            .filter(Video.uploader_id.in_(uploader_ids))
            .order_by(desc(Video.created_at))
            .all()
        )

    def get_recommended_by_title_terms(self, excluded_video_id: int, terms: list[str], limit: int) -> list[Video]:
        query = self.db.query(Video).filter(Video.id != excluded_video_id)

        if terms:
            overlap_score = sum(
                case(
                    (func.lower(Video.title).like(f"%{term.lower()}%"), 1),
                    else_=0,
                )
                for term in terms
            ).label("overlap_score")
            query = query.order_by(desc(overlap_score), desc(Video.views), desc(Video.created_at))
        else:
            query = query.order_by(desc(Video.views), desc(Video.created_at))

        return query.limit(limit).all()

    def create(
        self,
        title: str,
        description: str,
        file_path: str,
        thumbnail_path: str | None = None,
        uploader_id: int | None = None,
    ) -> Video:
        video = Video(
            title=title,
            description=description,
            file_path=file_path,
            thumbnail_path=thumbnail_path,
            uploader_id=uploader_id,
        )
        self.db.add(video)
        commit_with_retry(self.db)
        self.db.refresh(video)
        return video

    def increment_views(self, video: Video) -> Video:
        video.views += 1
        commit_with_retry(self.db)
        self.db.refresh(video)
        return video

    def delete(self, video: Video) -> None:
        self.db.delete(video)
        commit_with_retry(self.db)
