"""Logique des sessions : création, résolution depuis le cookie, nettoyage."""

from datetime import UTC, datetime, timedelta

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import delete, exists, func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.models import AuthSession, User
from app.security import hash_token, new_token

COOKIE_NAME = "timeo_session"


def _now() -> datetime:
    return datetime.now(UTC)


def _ttl(user: User) -> timedelta:
    settings = get_settings()
    if user.is_guest:
        return timedelta(minutes=settings.guest_idle_minutes)
    return timedelta(hours=settings.session_ttl_hours)


def find_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(func.lower(User.username) == username.lower()))


def ensure_username_free(db: Session, username: str, *, allowed: User | None = None) -> None:
    """Refuse un pseudo déjà pris ; `allowed` peut garder le sien (ex. changer la casse)."""
    owner = find_user_by_username(db, username)
    if owner is not None and owner is not allowed:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ce pseudo est déjà pris")


def create_session(db: Session, user: User) -> str:
    token = new_token()
    db.add(AuthSession(token_hash=hash_token(token), user=user, expires_at=_now() + _ttl(user)))
    db.commit()
    return token


def get_current_session(
    db: Session = Depends(get_db),
    token: str | None = Cookie(default=None, alias=COOKIE_NAME),
) -> AuthSession:
    unauthorized = HTTPException(status.HTTP_401_UNAUTHORIZED, "Non connecté")
    if not token:
        raise unauthorized
    session = db.scalar(select(AuthSession).where(AuthSession.token_hash == hash_token(token)))
    if session is None or _as_utc(session.expires_at) <= _now():
        raise unauthorized
    # Expiration glissante pour les visiteurs : chaque requête prolonge leur session.
    # Sans activité (l'application est fermée), le compte expire puis est supprimé.
    if session.user.is_guest:
        session.expires_at = _now() + _ttl(session.user)
        db.commit()
    return session


def get_current_user(session: AuthSession = Depends(get_current_session)) -> User:
    return session.user


def end_session(db: Session, session: AuthSession) -> None:
    """Déconnexion. Un visiteur qui se déconnecte perd son compte temporaire."""
    user = session.user
    if user.is_guest:
        db.delete(user)
    else:
        db.delete(session)
    db.commit()


def purge_expired(db: Session) -> None:
    """Supprime les sessions expirées et les visiteurs qui n'ont plus de session active."""
    now = _now()
    db.execute(delete(AuthSession).where(AuthSession.expires_at <= now))
    db.execute(
        delete(User).where(
            User.is_guest.is_(True),
            ~exists().where(AuthSession.user_id == User.id),
        )
    )
    db.commit()


def _as_utc(value: datetime) -> datetime:
    # SQLite (tests) renvoie des dates naïves ; PostgreSQL des dates avec fuseau.
    return value if value.tzinfo else value.replace(tzinfo=UTC)
