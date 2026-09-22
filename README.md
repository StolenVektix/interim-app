# Intérim MVP

A Tinder-style temp-job matching app. Two account roles, fixed at registration:

- **employeur** (employer): posts and manages job offers ("annonces"), reviews applications.
- **interimaire** (worker): swipes right/left through a stack of offers; a right swipe creates an application.

FastAPI backend + React/Vite frontend, talking over a JSON REST API under `/api`.

## Quick start

```bash
./start.sh   # installs deps on first run, starts backend on :8000 and frontend on :5173
./stop.sh    # stops both
```

Then open http://localhost:5173. Interactive API docs are served at http://localhost:8000/docs.

## Manual setup

**Backend** (from `backend/`):

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000
```

**Frontend** (from `frontend/`):

```bash
npm install
npm run dev
```

## Testing

```bash
cd backend
.venv/bin/pytest
```

## Configuration

Environment variables (all optional, sensible defaults for local dev):

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./interim.db` | SQLAlchemy database URL |
| `JWT_SECRET` | `dev-secret-change-me` | Secret used to sign access tokens — set a real value outside local dev |
| `BACKEND_PORT` | `8000` | Port used by `start.sh`/`stop.sh` |
| `FRONTEND_PORT` | `5173` | Port used by `start.sh`/`stop.sh` |

## Tech stack

- Backend: FastAPI, SQLAlchemy, Pydantic, python-jose (JWT), passlib/bcrypt, pytest
- Frontend: React 19, react-router-dom, Vite, oxlint

## Project layout

```
backend/
  app/
    routers/     # HTTP endpoints per resource (auth, offers, filters, stack, swipes)
    services/     # business logic, called by routers
    models.py     # SQLAlchemy models
    schemas.py    # Pydantic request/response models
    errors.py     # uniform API error handling
  tests/          # pytest suite, one file per resource
frontend/
  src/
    api/          # fetch client
    auth/         # login/register, auth context
    worker/       # interimaire pages (swipe stack, filter)
    employer/     # employeur pages (offers, applications)
```

See `CLAUDE.md` for more detail on architecture and business rules.
