"""EX-12, EX-13, EX-14, EX-20 : construction de la pile d'un intérimaire.

Hypothèse de modélisation (non fixée par le cahier des charges, tranchée avec
le porteur produit) : la fenêtre de dates du filtre est un intervalle de
disponibilité — une annonce est retenue dès que sa période [start_date,
end_date] chevauche, même partiellement, [date_from, date_to] du filtre.
"""

from sqlalchemy.orm import Session

from .. import models
from ..config import ALLOWED_CITIES


def get_stack(db: Session, worker: models.User) -> list[models.Offer]:
    excluded_offer_ids = db.query(models.SwipeAction.offer_id).filter(
        models.SwipeAction.worker_id == worker.id
    )  # EX-14: jamais une annonce déjà swipée, gauche ou droite

    query = db.query(models.Offer).filter(
        models.Offer.status == "open",  # EX-14: jamais une annonce closed
        ~models.Offer.id.in_(excluded_offer_ids),
    )

    active_filter = db.query(models.Filter).filter(models.Filter.worker_id == worker.id).first()
    if active_filter is not None:
        cities = active_filter.cities.split(",")
        query = query.filter(
            models.Offer.city.in_(cities),
            models.Offer.hourly_wage >= active_filter.min_hourly_wage,
            models.Offer.weekly_hours >= active_filter.min_weekly_hours,
            models.Offer.weekly_hours <= active_filter.max_weekly_hours,
            models.Offer.start_date <= active_filter.date_to,
            models.Offer.end_date >= active_filter.date_from,
        )
    else:
        query = query.filter(models.Offer.city.in_(ALLOWED_CITIES))  # EX-12: toutes les annonces open, deux villes

    return query.order_by(models.Offer.created_at.desc()).all()  # EX-12: tri décroissant
