from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

Username = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=3, max_length=32, pattern=r"^[\w.-]+$"),
]
Password = Annotated[str, StringConstraints(min_length=8, max_length=128)]


class Credentials(BaseModel):
    username: Username
    password: Password


class LoginRequest(BaseModel):
    # Pas de contraintes de format à la connexion : on se contente de vérifier.
    username: str
    password: str


class GuestRequest(BaseModel):
    username: Username


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    is_guest: bool
    created_at: datetime
    avatar_url: str | None


class UsernameUpdate(BaseModel):
    username: Username


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: Password
