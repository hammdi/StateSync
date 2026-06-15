from datetime import datetime, timedelta

from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from .config import settings

security = HTTPBearer(auto_error=False)


def create_access_token(
    data: dict, expires_delta: timedelta = timedelta(hours=1)
) -> str:
    """Create a signed JWT token."""
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + expires_delta
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """Verify and decode a JWT token from the Authorization header."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
