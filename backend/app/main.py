"""DoomsDayCalc FastAPI application entry point with PostgreSQL lifespan."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import router as api_v1_router
from app.core.config import API_V1_PREFIX, APP_NAME, APP_VERSION, CORS_ORIGINS
from app.services.seed_db import init_and_seed_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Ensure PostgreSQL tables exist and contain baseline records on startup."""
    init_and_seed_db(force_upsert=False)
    yield


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Enterprise statistical intelligence API backed by Aiven PostgreSQL and Matplotlib.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix=API_V1_PREFIX)


@app.get("/", tags=["System"])
def root() -> dict[str, str]:
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "docs": "/docs",
        "health": f"{API_V1_PREFIX}/health",
    }
