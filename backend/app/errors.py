"""Exceptions métier et handlers produisant le corps d'erreur uniforme requis :
{ "code": "...", "message": "...", "fields": [...] } (contrainte transverse du cahier des charges).
"""

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ApiError(Exception):
    status_code = 400
    code = "ERROR"

    def __init__(self, message: str, fields: list[str] | None = None):
        self.message = message
        self.fields = fields or []
        super().__init__(message)


class AuthRequiredError(ApiError):
    """EX-02: route protégée sans authentification -> 401, sans divulguer l'existence de la ressource."""

    status_code = 401
    code = "AUTH_REQUIRED"

    def __init__(self, message: str = "Authentification requise."):
        super().__init__(message)


class ForbiddenError(ApiError):
    """EX-03, EX-10: rôle ou propriétaire incorrect -> 403."""

    status_code = 403
    code = "FORBIDDEN"

    def __init__(self, message: str = "Accès refusé."):
        super().__init__(message)


class NotFoundError(ApiError):
    status_code = 404
    code = "NOT_FOUND"

    def __init__(self, message: str = "Ressource introuvable."):
        super().__init__(message)


class ValidationFailedError(ApiError):
    """EX-07: champ obligatoire absent ou hors bornes -> 422 avec la liste des champs fautifs."""

    status_code = 422
    code = "VALIDATION_ERROR"

    def __init__(self, message: str = "Champs invalides.", fields: list[str] | None = None):
        super().__init__(message, fields)


class InvalidPeriodError(ApiError):
    """EX-08: date de fin antérieure à la date de début -> 422 INVALID_PERIOD."""

    status_code = 422
    code = "INVALID_PERIOD"

    def __init__(self, message: str = "La date de fin doit être postérieure ou égale à la date de début."):
        super().__init__(message, fields=["end_date"])


class InvalidCredentialsError(ApiError):
    status_code = 401
    code = "INVALID_CREDENTIALS"

    def __init__(self, message: str = "Identifiants invalides."):
        super().__init__(message)


class EmailTakenError(ApiError):
    status_code = 409
    code = "EMAIL_TAKEN"

    def __init__(self, message: str = "Cet email est déjà utilisé."):
        super().__init__(message, fields=["email"])


class OfferClosedError(ApiError):
    """EX-18: annonce clôturée entre affichage et swipe à droite -> 409 OFFER_CLOSED."""

    status_code = 409
    code = "OFFER_CLOSED"

    def __init__(self, message: str = "Cette annonce vient d'être clôturée."):
        super().__init__(message)


def register_error_handlers(app) -> None:
    @app.exception_handler(ApiError)
    async def handle_api_error(request: Request, exc: ApiError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message, "fields": exc.fields},
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        fields: list[str] = []
        for err in exc.errors():
            loc = err.get("loc", ())
            name = str(loc[-1]) if loc else "body"
            if name not in fields:
                fields.append(name)
        return JSONResponse(
            status_code=422,
            content={"code": "VALIDATION_ERROR", "message": "Champs invalides.", "fields": fields},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"code": "INTERNAL_ERROR", "message": "Une erreur inattendue est survenue.", "fields": []},
        )
