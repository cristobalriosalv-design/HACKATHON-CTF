from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.comment_repository import CommentRepository
from app.repositories.video_repository import VideoRepository


class CommentService:
    def __init__(self, db: Session):
        self.comment_repo = CommentRepository(db)
        self.video_repo = VideoRepository(db)

    def list_comments(self, video_id: int):
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        return self.comment_repo.get_by_video_id(video_id)

    def create_comment(self, video_id: int, author: str, content: str):
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        return self.comment_repo.create(video_id=video_id, author=author, content=content)
