from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth import (
    COOKIE_NAME,
    create_session,
    end_session,
    ensure_username_free,
    find_user_by_username,
    get_current_session,
    get_current_user,
)
from app.config import get_settings
from app.db import get_db
from app.models import AuthSession, User
from app.schemas import Credentials, GuestRequest, LoginRequest, UserOut
from app.security import hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _set_cookie(response: Response, token: str, user: User) -> None:
    settings = get_settings()
    response.set_cookie(
        COOKIE_NAME,
        token,
        # Pas de max_age pour un visiteur : cookie de session, effacé à la fermeture du navigateur.
        max_age=None if user.is_guest else settings.session_ttl_hours * 3600,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        path="/",
    )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(body: Credentials, response: Response, db: Session = Depends(get_db)) -> User:
    ensure_username_free(db, body.username)
    user = User(username=body.username, password_hash=hash_password(body.password))
    db.add(user)
    _set_cookie(response, create_session(db, user), user)
    return user


@router.post("/login", response_model=UserOut)
def login(body: LoginRequest, response: Response, db: Session = Depends(get_db)) -> User:
    user = find_user_by_username(db, body.username.strip())
    if not verify_password(body.password, user.password_hash if user else None):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Pseudo ou mot de passe incorrect")
    _set_cookie(response, create_session(db, user), user)
    return user


@router.post("/guest", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def guest(body: GuestRequest, response: Response, db: Session = Depends(get_db)) -> User:
    ensure_username_free(db, body.username)
    user = User(username=body.username, is_guest=True)
    db.add(user)
    _set_cookie(response, create_session(db, user), user)
    return user


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    session: AuthSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> None:
    end_session(db, session)
    response.delete_cookie(COOKIE_NAME, path="/")
