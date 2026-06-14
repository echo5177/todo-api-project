import os
import secrets
import warnings


def parse_allowed_origins(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _load_secret_key() -> str:
    """Load the JWT signing key from the environment.

    Shipping a hardcoded fallback key would let anyone who can read the
    source code forge valid tokens for any user. When no key is provided we
    generate a strong random one for this process only and warn loudly, so a
    real deployment is forced to set SECRET_KEY explicitly.
    """
    secret = os.getenv("SECRET_KEY")
    if secret:
        return secret

    warnings.warn(
        "SECRET_KEY is not set. Generating a temporary, in-memory key for "
        "this process. Tokens will be invalidated on restart and the app is "
        "NOT safe for production. Set the SECRET_KEY environment variable.",
        RuntimeWarning,
        stacklevel=2,
    )
    return secrets.token_urlsafe(64)


SECRET_KEY = _load_secret_key()
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
ALLOWED_ORIGINS = parse_allowed_origins(
    os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
)
