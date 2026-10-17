import asyncio
import contextlib
import logging
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.auth import purge_expired
from app.config import get_settings
from app.db import SessionLocal
from app.routers import auth

logger = logging.getLogger(__name__)


def _purge() -> None:
    with SessionLocal() as db:
        purge_expired(db)


async def _cleanup_loop(interval: int) -> None:
    while True:
        try:
            await asyncio.to_thread(_purge)
        except Exception:
            logger.exception("Échec du nettoyage des sessions expirées")
        await asyncio.sleep(interval)


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    task = asyncio.create_task(_cleanup_loop(get_settings().cleanup_interval_seconds))
    yield
    task.cancel()


app = FastAPI(
    title="SiteTimeo", lifespan=lifespan, docs_url="/api/docs", openapi_url="/api/openapi.json"
)
app.include_router(auth.router)


@app.get("/api/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}
