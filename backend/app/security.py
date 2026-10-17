import hashlib
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError

_hasher = PasswordHasher()
# Empreinte factice : permet de faire le même travail quand le pseudo n'existe pas,
# pour ne pas révéler par le temps de réponse quels pseudos sont pris.
_DUMMY_HASH = _hasher.hash("pas-un-vrai-mot-de-passe")


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    try:
        _hasher.verify(password_hash or _DUMMY_HASH, password)
    except VerificationError:
        return False
    return password_hash is not None


def new_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
