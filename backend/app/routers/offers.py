"""EX-05 à EX-10, EX-22 : endpoints de l'espace employeur pour les annonces."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..deps import get_db, require_role
from ..services import offers_service

router = APIRouter(prefix="/api/offers", tags=["offers"])


@router.post("", response_model=schemas.OfferOut, status_code=201)
def create_offer(
    data: schemas.OfferCreate,
    db: Session = Depends(get_db),
    employer=Depends(require_role("employeur")),
):
    return offers_service.create_offer(db, employer, data)


@router.get("/mine", response_model=list[schemas.OfferOut])
def list_mine(db: Session = Depends(get_db), employer=Depends(require_role("employeur"))):
    return offers_service.list_own_offers(db, employer)


@router.patch("/{offer_id}", response_model=schemas.OfferOut)
def update_offer(
    offer_id: int,
    data: schemas.OfferUpdate,
    db: Session = Depends(get_db),
    employer=Depends(require_role("employeur")),
):
    return offers_service.update_offer(db, employer, offer_id, data)


@router.post("/{offer_id}/close", response_model=schemas.OfferOut)
def close_offer(
    offer_id: int,
    db: Session = Depends(get_db),
    employer=Depends(require_role("employeur")),
):
    return offers_service.close_offer(db, employer, offer_id)


@router.get("/{offer_id}/applications", response_model=list[schemas.ApplicationOut])
def list_applications(
    offer_id: int,
    db: Session = Depends(get_db),
    employer=Depends(require_role("employeur")),
):
    return offers_service.list_applications_for_offer(db, employer, offer_id)
