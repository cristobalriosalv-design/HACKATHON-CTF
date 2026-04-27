import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.auth.providers import ProviderUserCreateInput, UserProviderRegistryPort
from app.models.user import User
from app.repositories.interfaces import UserRepositoryPort


class UserService:
    UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1 MiB

    def __init__(self, repo: UserRepositoryPort, provider_registry: UserProviderRegistryPort):
        self.repo = repo
        self.provider_registry = provider_registry

    def list_users(self, limit: int, offset: int) -> list[User]:
        return self.repo.list_users(limit=limit, offset=offset)

    def get_user(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def create_user(
        self,
        provider_name: str,
        display_name: str,
        provider_subject: str,
        email: str | None,
        avatar: UploadFile | None,
        upload_dir: Path,
    ) -> User:
        provider = self.provider_registry.get(provider_name)
        avatar_path = self._save_avatar(avatar=avatar, upload_dir=upload_dir)

        payload = ProviderUserCreateInput(
            display_name=display_name.strip(),
            provider_subject=provider_subject,
            email=email,
            avatar_path=avatar_path,
        )
        if not payload.display_name:
            raise HTTPException(status_code=400, detail="display_name is required")

        normalized_subject = provider.normalize_subject(payload)

        existing = self.repo.get_by_provider_subject(provider_name, normalized_subject)
        if existing:
            raise HTTPException(status_code=409, detail="A user for this provider subject already exists")

        user = self.repo.create_user(display_name=payload.display_name, avatar_path=payload.avatar_path)
        self.repo.create_identity(
            user_id=user.id,
            provider=provider_name,
            provider_subject=normalized_subject,
            email=payload.email.strip() if payload.email else None,
        )
        self.repo.commit()
        self.repo.refresh_user(user)
        return user

    def ensure_avatar_file_exists(self, user: User) -> str:
        if not user.avatar_path or not os.path.exists(user.avatar_path):
            raise HTTPException(status_code=404, detail="Avatar not found")
        return user.avatar_path

    def list_providers(self) -> list[str]:
        return self.provider_registry.list_provider_names()

    def _save_avatar(self, avatar: UploadFile | None, upload_dir: Path) -> str | None:
        if avatar is None:
            return None
        if avatar.content_type and not avatar.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Avatar must be an image")

        avatar_dir = upload_dir / "avatars"
        avatar_dir.mkdir(parents=True, exist_ok=True)

        suffix = Path(avatar.filename or "avatar.jpg").suffix or ".jpg"
        destination = avatar_dir / f"{uuid.uuid4()}{suffix}"

        with destination.open("wb") as buffer:
            while True:
                chunk = avatar.file.read(self.UPLOAD_CHUNK_SIZE)
                if not chunk:
                    break
                buffer.write(chunk)

        return str(destination)
