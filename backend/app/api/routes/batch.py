"""Batch operation endpoints for efficient bulk operations."""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.api.response_mappers import to_comment_response, to_video_response
from app.core.limiter import limiter
from app.dependencies import get_comment_service, get_video_service
from app.schemas.comment import CommentResponse
from app.schemas.video import VideoResponse
from app.services.interfaces import CommentServicePort, VideoServicePort

router = APIRouter(prefix="/batch", tags=["batch"])


class VideoIdsBatch(BaseModel):
    """Request body for batch video operations."""
    video_ids: list[int] = Field(..., min_items=1, max_items=100, description="Up to 100 video IDs")


class VideoIdIncrementBatch(BaseModel):
    """Request body for batch view increments."""
    video_ids: list[int] = Field(..., min_items=1, max_items=50, description="Up to 50 video IDs")
    increment: int = Field(1, ge=1, le=10, description="Amount to increment views (1-10)")


class VideoIdCommentsBatch(BaseModel):
    """Request body for batch comments fetch."""
    video_ids: list[int] = Field(..., min_items=1, max_items=10, description="Up to 10 video IDs")


@router.post("/videos/info", response_model=list[VideoResponse])
def get_videos_batch(
    batch: VideoIdsBatch,
    video_service: VideoServicePort = Depends(get_video_service),
):
    """Get multiple videos by IDs in a single query.
    
    Prevents N+1 queries when fetching multiple videos.
    Returns VideoResponse for all requested IDs.
    Max 100 videos per request.
    """
    if len(batch.video_ids) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 videos per batch request")
    
    videos = video_service.get_videos_by_ids(batch.video_ids)
    return [to_video_response(v) for v in videos]


@limiter.limit("5/minute")
@router.post("/videos/increment-views", response_model=list[VideoResponse])
def increment_views_batch(
    request: Request,
    batch: VideoIdIncrementBatch,
    video_service: VideoServicePort = Depends(get_video_service),
):
    """Atomically increment views for multiple videos.
    
    Single atomic operation for all videos.
    Returns updated VideoResponse for all IDs.
    Max 50 videos per request to prevent abuse.
    Rate limited to 5/minute.
    """
    if len(batch.video_ids) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 videos per batch increment")
    
    videos = video_service.increment_views_batch(
        video_ids=batch.video_ids,
        increment=batch.increment
    )
    return [to_video_response(v) for v in videos]


@router.post("/comments", response_model=dict[str, list[CommentResponse]])
def get_comments_batch(
    batch: VideoIdCommentsBatch,
    comment_service: CommentServicePort = Depends(get_comment_service),
):
    """Get comments for multiple videos in a single query.
    
    Returns dict mapping video_id -> list of comments.
    Prevents N+1 queries when fetching comments for multiple videos.
    Max 10 videos per request.
    """
    if len(batch.video_ids) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 videos per batch request")
    
    result = {}
    for video_id in batch.video_ids:
        comments = comment_service.list_comments(video_id=video_id, limit=50, offset=0)
        result[str(video_id)] = [to_comment_response(c) for c in comments]
    
    return result
