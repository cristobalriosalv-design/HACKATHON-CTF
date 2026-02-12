from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.comment import Comment


class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_video_id(self, video_id: int) -> list[Comment]:
        return (
            self.db.query(Comment)
            .filter(Comment.video_id == video_id)
            .order_by(desc(Comment.created_at))
            .all()
        )

    def create(self, video_id: int, author: str, content: str) -> Comment:
        comment = Comment(video_id=video_id, author=author, content=content)
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment
