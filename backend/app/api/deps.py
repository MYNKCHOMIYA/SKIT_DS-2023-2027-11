"""
Sprint 1: FastAPI dependency injection utilities.
Provides database session and current-user resolution from the JWT token.
"""
from typing import Annotated, Generator
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_db() -> Generator:
    """Yield a DB session and guarantee it is closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: SessionDep, token: str = Depends(oauth2_scheme)
) -> User:
    """Decode JWT and return the corresponding User record."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Raise 400 if the user account is disabled."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Raise 403 if the user is not an admin."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return current_user
