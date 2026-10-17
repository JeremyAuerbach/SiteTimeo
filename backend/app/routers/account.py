from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session, undefer

from app.auth import ensure_username_free, get_current_session, get_current_user
from app.db import get_db
from app.models import AuthSession, User, UserAvatar, utcnow
from app.schemas import PasswordUpdate, UsernameUpdate, UserOut
from app.security import hash_password, verify_password

router = APIRouter(prefix="/api", tags=["account"])

MAX_AVATAR_BYTES = 2 * 1024 * 1024
# Signature des premiers octets de chaque format accepté : on ne se fie pas à l'en-tête
# Content-Type envoyé par le client.
_IMAGE_SIGNATURES = {
    "image/png": (b"\x89PNG\r\n\x1a\n",),
    "image/jpeg": (b"\xff\xd8\xff",),
    "image/gif": (b"GIF87a", b"GIF89a"),
}


def _image_type(data: bytes) -> str | None:
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    for content_type, signatures in _IMAGE_SIGNATURES.items():
        if data.startswith(signatures):
            return content_type
    return None


@router.patch("/account", response_model=UserOut)
def update_username(
    body: UsernameUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> User:
    ensure_username_free(db, body.username, allowed=user)
    user.username = body.username
    db.commit()
    return user


@router.put("/account/password", status_code=status.HTTP_204_NO_CONTENT)
def update_password(
    body: PasswordUpdate,
    session: AuthSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> None:
    user = session.user
    if user.is_guest:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Un compte visiteur n'a pas de mot de passe")
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Mot de passe actuel incorrect")
    user.password_hash = hash_password(body.new_password)
    # Les autres appareils connectés sont déconnectés ; celui-ci reste connecté.
    db.execute(
        delete(AuthSession).where(AuthSession.user_id == user.id, AuthSession.id != session.id)
    )
    db.commit()


@router.put("/account/avatar", response_model=UserOut)
async def update_avatar(
    request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> User:
    # Corps brut de la requête (image seule) : pas besoin de formulaire multipart.
    data = await request.body()
    if len(data) > MAX_AVATAR_BYTES:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "L'image ne doit pas dépasser 2 Mo"
        )
    content_type = _image_type(data)
    if content_type is None:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Formats acceptés : PNG, JPEG, WebP ou GIF"
        )
    if user.avatar is None:
        user.avatar = UserAvatar(content_type=content_type, data=data)
    else:
        user.avatar.content_type = content_type
        user.avatar.data = data
        user.avatar.updated_at = utcnow()
    db.commit()
    return user


@router.delete("/account/avatar", response_model=UserOut)
def delete_avatar(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    user.avatar = None
    db.commit()
    return user


@router.get("/users/{user_id}/avatar")
def get_avatar(
    user_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Response:
    avatar = db.scalar(
        select(UserAvatar).where(UserAvatar.user_id == user_id).options(undefer(UserAvatar.data))
    )
    if avatar is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pas de photo de profil")
    # L'URL change à chaque nouvelle photo, on peut donc la garder longtemps en cache.
    return Response(
        avatar.data,
        media_type=avatar.content_type,
        headers={"Cache-Control": "private, max-age=31536000, immutable"},
    )
