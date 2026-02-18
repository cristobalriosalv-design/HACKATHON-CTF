from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    identities = relationship("UserIdentity", back_populates="user", cascade="all, delete-orphan")
    uploaded_videos = relationship("Video", back_populates="uploader")
    followers = relationship(
        "Subscription",
        foreign_keys="Subscription.creator_id",
        back_populates="creator",
        cascade="all, delete-orphan",
    )
    subscriptions = relationship(
        "Subscription",
        foreign_keys="Subscription.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
    )
