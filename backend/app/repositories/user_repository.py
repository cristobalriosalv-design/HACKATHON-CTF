from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.database import commit_with_retry
from app.models.user import User
from app.models.user_identity import UserIdentity


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_users(self, limit: int, offset: int) -> list[User]:
        return self.db.query(User).order_by(desc(User.created_at)).offset(offset).limit(limit).all()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_provider_subject(self, provider: str, provider_subject: str) -> User | None:
        identity = (
            self.db.query(UserIdentity)
            .filter(UserIdentity.provider == provider, UserIdentity.provider_subject == provider_subject)
            .first()
        )
        return identity.user if identity else None

    def create_user(self, display_name: str, avatar_path: str | None = None) -> User:
        user = User(display_name=display_name, avatar_path=avatar_path)
        self.db.add(user)
        self.db.flush()
        return user

    def create_identity(
        self,
        user_id: int,
        provider: str,
        provider_subject: str,
        email: str | None = None,
    ) -> UserIdentity:
        identity = UserIdentity(
            user_id=user_id,
            provider=provider,
            provider_subject=provider_subject,
            email=email,
        )
        self.db.add(identity)
        return identity

    def commit(self) -> None:
        commit_with_retry(self.db)

    def refresh_user(self, user: User) -> None:
        self.db.refresh(user)
