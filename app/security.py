from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

password_hash = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


# Pre-computed hash of a dummy password. Verifying against it lets the login
# flow spend the same amount of time whether or not a username exists, which
# prevents attackers from enumerating valid usernames via response timing.
_DUMMY_PASSWORD_HASH = password_hash.hash("dummy-password-for-timing")


def dummy_verify_password() -> None:
    """Run a password verification to equalize timing for unknown users."""
    password_hash.verify("dummy-password-for-timing", _DUMMY_PASSWORD_HASH)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        options={"require": ["exp"], "verify_exp": True},
    )
