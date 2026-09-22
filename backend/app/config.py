import os

# EX-05: villes autorisées pour une annonce / un filtre
ALLOWED_CITIES = ("Bordeaux", "Paris")

# EX-01: rôles possibles, fixés à l'inscription
ROLES = ("employeur", "interimaire")

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./interim.db")

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24
