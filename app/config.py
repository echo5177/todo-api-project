import os


def parse_allowed_origins(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "change-this-before-real-deployment-please-1234567890",
)

ALGORITHM = os.getenv("ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

ALLOWED_ORIGINS = parse_allowed_origins(
    os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
)
