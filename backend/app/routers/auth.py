"""EX-01 : le rôle est fixé à l'inscription et renvoyé tel quel à la connexion."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas, security
from ..deps import get_db
from ..errors import EmailTakenError, InvalidCredentialsError

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=201)
def register(data: schemas.RegisterRequest, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == data.email).first() is not None:
        raise EmailTakenError()

    user = models.User(
        email=data.email,
        password_hash=security.hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.TokenOut)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if user is None or not security.verify_password(data.password, user.password_hash):
        raise InvalidCredentialsError()

    token = security.create_access_token(user.id, user.role)
    return schemas.TokenOut(access_token=token, role=user.role)
