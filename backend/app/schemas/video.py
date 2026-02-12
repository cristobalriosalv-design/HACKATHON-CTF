from datetime import datetime

from pydantic import BaseModel


class VideoBase(BaseModel):
    title: str
    description: str


class VideoResponse(VideoBase):
    id: int
    created_at: datetime
    views: int
    stream_url: str

    model_config = {"from_attributes": True}
