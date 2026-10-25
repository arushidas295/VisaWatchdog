from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None


if __name__ == "__main__":
    # Quick self-test: python -m app.security
    hashed = hash_password("test-password-123")
    print("hash is not the password:", hashed != "test-password-123")
    print("right password verifies:", verify_password("test-password-123", hashed))
    print("wrong password rejected:", not verify_password("wrong", hashed))

    token = create_access_token(7)
    print("token created, length:", len(token))
    print("token decodes to user id:", decode_access_token(token))
    print("garbage token rejected:", decode_access_token("not-a-token") is None)