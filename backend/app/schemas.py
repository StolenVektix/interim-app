from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

City = Literal["Bordeaux", "Paris"]
Role = Literal["employeur", "interimaire"]
Direction = Literal["left", "right"]


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: Role


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: Role

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role


class OfferCreate(BaseModel):
    """EX-05: mentions obligatoires d'une annonce, avec leurs bornes."""

    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    hourly_wage: float = Field(gt=0)
    weekly_hours: int = Field(ge=1, le=48)
    start_date: date
    end_date: date
    city: City


class OfferUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    description: str | None = Field(default=None, min_length=1)
    hourly_wage: float | None = Field(default=None, gt=0)
    weekly_hours: int | None = Field(default=None, ge=1, le=48)
    start_date: date | None = None
    end_date: date | None = None
    city: City | None = None


class OfferOut(BaseModel):
    id: int
    employer_id: int
    title: str
    description: str
    hourly_wage: float
    weekly_hours: int
    start_date: date
    end_date: date
    city: City
    status: Literal["open", "closed"]
    created_at: datetime

    model_config = {"from_attributes": True}


class FilterIn(BaseModel):
    """EX-11: composition du filtre unique d'un intérimaire."""

    cities: list[City] = Field(min_length=1)
    min_hourly_wage: float = Field(ge=0)
    min_weekly_hours: int = Field(ge=1, le=48)
    max_weekly_hours: int = Field(ge=1, le=48)
    date_from: date
    date_to: date


class FilterOut(FilterIn):
    id: int
    worker_id: int
    updated_at: datetime


class SwipeRequest(BaseModel):
    direction: Direction


class SwipeResult(BaseModel):
    result: Literal["rejected", "applied"]
    offer: OfferOut | None = None


class ApplicationOut(BaseModel):
    id: int
    offer_id: int
    status: str
    created_at: datetime
    worker: UserOut

    model_config = {"from_attributes": True}
