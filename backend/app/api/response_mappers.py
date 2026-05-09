from app.schemas.comment import CommentResponse as CommentResponseSchema
from app.schemas.user import UserResponse
from app.schemas.video import VideoResponse, VideoUploaderResponse


def to_user_response(user) -> UserResponse:
    return UserResponse(
        id=user.id,
        display_name=user.display_name,
        avatar_url=f"/users/{user.id}/avatar" if user.avatar_path else None,
        created_at=user.created_at,
    )


def to_video_response(video) -> VideoResponse:
    uploader = None
    if video.uploader:
        uploader = VideoUploaderResponse(
            id=video.uploader.id,
            display_name=video.uploader.display_name,
            avatar_url=f"/users/{video.uploader.id}/avatar" if video.uploader.avatar_path else None,
        )

    return VideoResponse(
        id=video.id,
        title=video.title,
        description=video.description,
        category=video.category or None,
        created_at=video.created_at,
        views=video.views,
        stream_url=f"/videos/{video.id}/stream",
        thumbnail_url=f"/videos/{video.id}/thumbnail" if video.thumbnail_path else None,
        uploader=uploader,
    )


def to_comment_response(comment) -> CommentResponseSchema:
    return CommentResponseSchema(
        id=comment.id,
        video_id=comment.video_id,
        author=comment.author,
        content=comment.content,
        created_at=comment.created_at,
    )
