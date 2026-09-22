"""EX-05 à EX-10, EX-22 : cycle de vie d'une annonce côté employeur."""

from sqlalchemy.orm import Session

from .. import models
from ..errors import ForbiddenError, InvalidPeriodError, NotFoundError
from ..schemas import OfferCreate, OfferUpdate
from ..timeutils import utc_now


def create_offer(db: Session, employer: models.User, data: OfferCreate) -> models.Offer:
    if data.end_date < data.start_date:
        raise InvalidPeriodError()  # EX-08

    offer = models.Offer(
        employer_id=employer.id,
        title=data.title,
        description=data.description,
        hourly_wage=data.hourly_wage,
        weekly_hours=data.weekly_hours,
        start_date=data.start_date,
        end_date=data.end_date,
        city=data.city,
        status="open",
        created_at=utc_now(),
    )
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer  # EX-06


def get_owned_offer(db: Session, employer: models.User, offer_id: int) -> models.Offer:
    """EX-10: seul le propriétaire agit sur son annonce."""
    offer = db.get(models.Offer, offer_id)
    if offer is None:
        raise NotFoundError("Annonce introuvable.")
    if offer.employer_id != employer.id:
        raise ForbiddenError()
    return offer


def update_offer(db: Session, employer: models.User, offer_id: int, data: OfferUpdate) -> models.Offer:
    offer = get_owned_offer(db, employer, offer_id)
    updates = data.model_dump(exclude_unset=True)

    new_start = updates.get("start_date", offer.start_date)
    new_end = updates.get("end_date", offer.end_date)
    if new_end < new_start:
        raise InvalidPeriodError()

    for field, value in updates.items():
        setattr(offer, field, value)

    db.commit()
    db.refresh(offer)
    return offer


def close_offer(db: Session, employer: models.User, offer_id: int) -> models.Offer:
    """EX-09: clôture -> statut closed, retrait immédiat des piles (via le filtre status=open),
    les candidatures déjà reçues sont conservées (aucune suppression)."""
    offer = get_owned_offer(db, employer, offer_id)
    offer.status = "closed"
    db.commit()
    db.refresh(offer)
    return offer


def list_own_offers(db: Session, employer: models.User) -> list[models.Offer]:
    return (
        db.query(models.Offer)
        .filter(models.Offer.employer_id == employer.id)
        .order_by(models.Offer.created_at.desc())
        .all()
    )


def list_applications_for_offer(db: Session, employer: models.User, offer_id: int) -> list[models.Application]:
    """EX-22: candidatures visibles côté employeur propriétaire, avec le profil de l'intérimaire."""
    get_owned_offer(db, employer, offer_id)  # lève 403/404 si non-propriétaire
    return (
        db.query(models.Application)
        .filter(models.Application.offer_id == offer_id)
        .order_by(models.Application.created_at.desc())
        .all()
    )
