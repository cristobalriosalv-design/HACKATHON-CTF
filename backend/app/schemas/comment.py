from datetime import datetime

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    author: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class CommentResponse(BaseModel):
    id: int
    video_id: int
    author: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
