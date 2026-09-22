"""EX-15 à EX-19, EX-21 : traitement transactionnel d'un swipe."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models
from ..errors import NotFoundError, OfferClosedError
from ..timeutils import utc_now


def _existing_action(db: Session, worker_id: int, offer_id: int) -> models.SwipeAction | None:
    return (
        db.query(models.SwipeAction)
        .filter(models.SwipeAction.worker_id == worker_id, models.SwipeAction.offer_id == offer_id)
        .first()
    )


def apply_swipe(
    db: Session, worker: models.User, offer_id: int, direction: str
) -> tuple[str, models.Offer | None]:
    offer = db.get(models.Offer, offer_id)
    if offer is None:
        raise NotFoundError("Annonce introuvable.")

    existing = _existing_action(db, worker.id, offer_id)
    if existing is not None:
        # EX-19: rejeu (double-tap, rejeu réseau, retour arrière) -> idempotent, aucun doublon.
        if existing.direction == "right":
            return "applied", offer
        return "rejected", None

    if direction == "right" and offer.status != "open":
        # EX-18: clôturée par l'employeur entre l'affichage et le swipe -> 409, rien n'est créé.
        raise OfferClosedError()

    db.add(
        models.SwipeAction(
            worker_id=worker.id,
            offer_id=offer_id,
            direction=direction,
            created_at=utc_now(),
        )
    )
    if direction == "right":
        db.add(
            models.Application(
                worker_id=worker.id,
                offer_id=offer_id,
                status="pending",
                created_at=utc_now(),
            )
        )  # EX-17, EX-21 (contrainte unique en base garantit l'unicité)

    try:
        db.commit()
    except IntegrityError:
        # Course concurrente : un autre appel a inséré l'état entre-temps -> même règle d'idempotence.
        db.rollback()
        existing = _existing_action(db, worker.id, offer_id)
        if existing is not None and existing.direction == "right":
            return "applied", offer
        return "rejected", None

    if direction == "right":
        db.refresh(offer)
        return "applied", offer
    return "rejected", None  # EX-15
