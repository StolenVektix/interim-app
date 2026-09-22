from fastapi import Depends, Header
from sqlalchemy.orm import Session

from . import security
from .database import SessionLocal
from .errors import AuthRequiredError, ForbiddenError
from .models import User


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    """EX-02: absence/invalidité du token -> 401, avant toute résolution de ressource."""
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthRequiredError()
    token = authorization.removeprefix("Bearer ")
    try:
        payload = security.decode_access_token(token)
    except ValueError:
        raise AuthRequiredError()
    user = db.get(User, int(payload["sub"]))
    if user is None:
        raise AuthRequiredError()
    return user


def require_role(role: str):
    """EX-03: rôle authentifié différent de celui attendu -> 403."""

    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role != role:
            raise ForbiddenError()
        return user

    return dependency
