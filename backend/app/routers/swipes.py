"""EX-15 à EX-19, EX-21 : action de swipe de l'espace intérimaire."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..deps import get_db, require_role
from ..services import swipes_service

router = APIRouter(prefix="/api/offers", tags=["swipes"])


@router.post("/{offer_id}/swipe", response_model=schemas.SwipeResult)
def swipe(
    offer_id: int,
    data: schemas.SwipeRequest,
    db: Session = Depends(get_db),
    worker=Depends(require_role("interimaire")),
):
    result, offer = swipes_service.apply_swipe(db, worker, offer_id, data.direction)
    return schemas.SwipeResult(result=result, offer=offer)
