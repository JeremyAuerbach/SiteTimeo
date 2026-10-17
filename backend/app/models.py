from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, LargeBinary, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(32))
    # Nul pour un visiteur : il n'a pas de mot de passe.
    password_hash: Mapped[str | None] = mapped_column(String(255))
    is_guest: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    sessions: Mapped[list["AuthSession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    avatar: Mapped["UserAvatar | None"] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )

    @property
    def avatar_url(self) -> str | None:
        if self.avatar is None:
            return None
        # Le paramètre change à chaque nouvelle photo : le navigateur ne garde pas l'ancienne.
        return f"/api/users/{self.id}/avatar?v={int(self.avatar.updated_at.timestamp())}"


# Pseudos uniques sans tenir compte de la casse : « Timeo » et « timeo » sont le même pseudo.
Index("uq_users_username_lower", func.lower(User.username), unique=True)


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Empreinte SHA-256 du jeton : le jeton en clair n'est jamais stocké.
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    user: Mapped[User] = relationship(back_populates="sessions")


class UserAvatar(Base):
    __tablename__ = "user_avatars"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    content_type: Mapped[str] = mapped_column(String(32))
    # Chargé seulement à la demande : lire un utilisateur ne doit pas lire son image.
    data: Mapped[bytes] = mapped_column(LargeBinary, deferred=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped[User] = relationship(back_populates="avatar")
