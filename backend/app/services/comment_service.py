from fastapi import HTTPException

from app.repositories.interfaces import CommentRepositoryPort, VideoRepositoryPort


class CommentService:
    def __init__(self, comment_repo: CommentRepositoryPort, video_repo: VideoRepositoryPort):
        self.comment_repo = comment_repo
        self.video_repo = video_repo

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
