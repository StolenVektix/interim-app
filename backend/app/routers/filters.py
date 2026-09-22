"""EX-11, EX-13 : filtre unique de l'espace intérimaire."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db, require_role
from ..errors import InvalidPeriodError, ValidationFailedError

router = APIRouter(prefix="/api/filter", tags=["filters"])


def _to_out(f: models.Filter) -> schemas.FilterOut:
    return schemas.FilterOut(
        id=f.id,
        worker_id=f.worker_id,
        cities=f.cities.split(","),
        min_hourly_wage=f.min_hourly_wage,
        min_weekly_hours=f.min_weekly_hours,
        max_weekly_hours=f.max_weekly_hours,
        date_from=f.date_from,
        date_to=f.date_to,
        updated_at=f.updated_at,
    )


@router.get("", response_model=schemas.FilterOut | None)
def get_filter(db: Session = Depends(get_db), worker=Depends(require_role("interimaire"))):
    active_filter = db.query(models.Filter).filter(models.Filter.worker_id == worker.id).first()
    return _to_out(active_filter) if active_filter is not None else None


@router.put("", response_model=schemas.FilterOut)
def put_filter(
    data: schemas.FilterIn,
    db: Session = Depends(get_db),
    worker=Depends(require_role("interimaire")),
):
    if data.min_weekly_hours > data.max_weekly_hours:
        raise ValidationFailedError(
            "La borne minimale d'heures doit être inférieure ou égale à la borne maximale.",
            fields=["min_weekly_hours", "max_weekly_hours"],
        )
    if data.date_to < data.date_from:
        raise InvalidPeriodError()

    active_filter = db.query(models.Filter).filter(models.Filter.worker_id == worker.id).first()
    if active_filter is None:
        active_filter = models.Filter(worker_id=worker.id)
        db.add(active_filter)

    active_filter.cities = ",".join(data.cities)
    active_filter.min_hourly_wage = data.min_hourly_wage
    active_filter.min_weekly_hours = data.min_weekly_hours
    active_filter.max_weekly_hours = data.max_weekly_hours
    active_filter.date_from = data.date_from
    active_filter.date_to = data.date_to

    db.commit()
    db.refresh(active_filter)
    return _to_out(active_filter)  # EX-13: recalcul immédiat, sans jamais toucher aux swipe_actions existants
