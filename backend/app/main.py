from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .errors import register_error_handlers
from .routers import auth, filters, offers, stack, swipes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Intérim MVP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(auth.router)
app.include_router(offers.router)
app.include_router(filters.router)
app.include_router(stack.router)
app.include_router(swipes.router)
