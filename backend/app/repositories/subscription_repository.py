from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.database import commit_with_retry
from app.models.subscription import Subscription


class SubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_pair(self, follower_id: int, creator_id: int) -> Subscription | None:
        return (
            self.db.query(Subscription)
            .filter(
                Subscription.follower_id == follower_id,
                Subscription.creator_id == creator_id,
            )
            .first()
        )

    def list_creator_ids(self, follower_id: int, limit: int, offset: int) -> list[int]:
        subscriptions = (
            self.db.query(Subscription)
            .filter(Subscription.follower_id == follower_id)
            .order_by(desc(Subscription.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [item.creator_id for item in subscriptions]

    def create(self, follower_id: int, creator_id: int) -> Subscription:
        subscription = Subscription(follower_id=follower_id, creator_id=creator_id)
        self.db.add(subscription)
        commit_with_retry(self.db)
        self.db.refresh(subscription)
        return subscription

    def delete(self, subscription: Subscription) -> None:
        self.db.delete(subscription)
        commit_with_retry(self.db)
