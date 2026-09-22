# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

"Intérim MVP" — a Tinder-style temp-job matching app. Two roles fixed at registration:
- **employeur** (employer): posts/manages job offers ("annonces"), views applications.
- **interimaire** (worker): swipes right/left through a stack of offers; a right swipe creates an application.

FastAPI backend (`backend/`) + React/Vite frontend (`frontend/`), talking over a JSON REST API under `/api`.

## Commands

Run everything (installs deps on first run, backend on :8000, frontend on :5173):
```
./start.sh
./stop.sh
```

Backend (from `backend/`, using the venv at `backend/.venv`):
```
.venv/bin/pytest                    # all tests
.venv/bin/pytest tests/test_swipes.py            # one file
.venv/bin/pytest tests/test_swipes.py::test_name # one test
.venv/bin/uvicorn app.main:app --reload --port 8000
```

Frontend (from `frontend/`):
```
npm run dev       # Vite dev server
npm run build
npm run lint       # oxlint
```

There is no backend lint/format command configured (no ruff/black/flake8 in `requirements.txt`).

## Architecture

**Backend** is layered `router -> service -> models`, one router+service pair per resource:
- `app/routers/{auth,offers,filters,stack,swipes}.py` — thin, just request/response wiring and role enforcement via `Depends(require_role(...))`.
- `app/services/*_service.py` — all business logic and DB writes live here, not in routers.
- `app/models.py` — SQLAlchemy models: `User`, `Offer`, `Filter` (one active filter per worker, unique on `worker_id`), `SwipeAction` (idempotency log, unique on `worker_id`+`offer_id`), `Application` (unique on `worker_id`+`offer_id`).
- `app/schemas.py` — Pydantic request/response models; `City` and `Role` are `Literal` types tied to `config.ALLOWED_CITIES` / `config.ROLES`.
- `app/errors.py` — every error is an `ApiError` subclass mapped to a fixed JSON shape `{code, message, fields}`; add new failure modes as new `ApiError` subclasses here rather than raising raw `HTTPException`.
- `app/deps.py` — `get_current_user` (401 if missing/invalid bearer token) and `require_role(role)` (403 if mismatched) are the two auth gates; every protected route depends on one of these.
- SQLite by default (`backend/interim.db`, gitignored); swap via `DATABASE_URL` env var.

Key domain rules encoded in the service layer (worth checking before changing swipe/offer/filter logic):
- Swipes are idempotent: replaying the same `(worker, offer)` swipe returns the original outcome instead of erroring or duplicating (`swipes_service.apply_swipe`), including a race handled via `IntegrityError` rollback-and-recheck.
- A right swipe on a closed offer is rejected with 409 (`OfferClosedError`); a stack never includes swiped or closed offers (`stack_service.get_stack`).
- Closing an offer (`offers_service.close_offer`) never deletes existing applications.
- A worker's filter window is treated as an *overlap* with the offer's `[start_date, end_date]`, not containment — this was an explicit product decision, not a spec requirement (see comment in `stack_service.py`).

**Traceability comments**: most backend modules carry `EX-NN` comments (e.g. `EX-05`, `EX-18`) referencing requirement IDs from an external spec/cahier des charges that is not checked into this repo. When touching business logic, preserve/update these references rather than deleting them — they're the link back to the requirement being satisfied.

**Frontend** is plain React (no state library) with `react-router-dom`:
- `src/api/client.js` — single fetch wrapper; reads the JWT from `localStorage`, throws `ApiError` (status/code/fields) on non-2xx responses matching the backend's error shape.
- `src/auth/AuthContext.jsx` — auth state/session.
- `src/worker/*` — swipe stack (`StackPage.jsx`, `SwipeCard.jsx`) and filter form (`FilterPage.jsx`) for the `interimaire` role.
- `src/employer/*` — offer CRUD (`EmployerOffersPage.jsx`, `OfferForm.jsx`) and applications view (`OfferApplicationsPage.jsx`) for the `employeur` role.
- `App.jsx`'s `RequireRole` does client-side redirect-by-role for UX only; the real 401/403 enforcement is server-side in `deps.py`.

## Testing conventions

`backend/tests/conftest.py` provides `client` (isolated SQLite per test via `tmp_path`) and helpers `register_and_login(client, email, password, role)` and `create_offer(client, headers, **overrides)`. Test files are split by resource (`test_auth.py`, `test_offers.py`, `test_filters.py`, `test_stack.py`, `test_swipes.py`) — follow that split for new tests.
