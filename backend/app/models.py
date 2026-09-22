from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base
from .timeutils import utc_now


class User(Base):
    """EX-01: un compte porte exactement un rôle, fixé à l'inscription."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "employeur" | "interimaire"
    created_at = Column(DateTime, default=utc_now, nullable=False)

    offers = relationship("Offer", back_populates="employer")
    filter = relationship("Filter", back_populates="worker", uselist=False)


class Offer(Base):
    """EX-05, EX-06, EX-09: annonce d'une mission côté employeur."""

    __tablename__ = "offers"

    id = Column(Integer, primary_key=True)
    employer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    hourly_wage = Column(Float, nullable=False)
    weekly_hours = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    city = Column(String, nullable=False)
    status = Column(String, nullable=False, default="open")  # "open" | "closed"
    created_at = Column(DateTime, default=utc_now, nullable=False)

    employer = relationship("User", back_populates="offers")


class Filter(Base):
    """EX-11: au plus un filtre actif par intérimaire (unique sur worker_id)."""

    __tablename__ = "filters"

    id = Column(Integer, primary_key=True)
    worker_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    cities = Column(String, nullable=False)  # sous-ensemble de ALLOWED_CITIES, séparé par virgules
    min_hourly_wage = Column(Float, nullable=False)
    min_weekly_hours = Column(Integer, nullable=False)
    max_weekly_hours = Column(Integer, nullable=False)
    date_from = Column(Date, nullable=False)
    date_to = Column(Date, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    worker = relationship("User", back_populates="filter")


class SwipeAction(Base):
    """Journal d'idempotence des swipes (EX-14, EX-19), gauche et droite confondus."""

    __tablename__ = "swipe_actions"
    __table_args__ = (UniqueConstraint("worker_id", "offer_id", name="uq_swipe_worker_offer"),)

    id = Column(Integer, primary_key=True)
    worker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)
    direction = Column(String, nullable=False)  # "left" | "right"
    created_at = Column(DateTime, default=utc_now, nullable=False)


class Application(Base):
    """EX-17, EX-21, EX-22: candidature créée par un swipe à droite accepté."""

    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("worker_id", "offer_id", name="uq_application_worker_offer"),)

    id = Column(Integer, primary_key=True)
    worker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=utc_now, nullable=False)

    worker = relationship("User")
