"""EX-12, EX-14, EX-20 : pile de cartes de l'espace intérimaire."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..deps import get_db, require_role
from ..services import stack_service

router = APIRouter(prefix="/api/stack", tags=["stack"])


@router.get("", response_model=list[schemas.OfferOut])
def get_stack(db: Session = Depends(get_db), worker=Depends(require_role("interimaire"))):
    return stack_service.get_stack(db, worker)
