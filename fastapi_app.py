from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from infrastructure.persistence.database import engine
from presentation.api.exception_handlers import (
    register_exception_handlers,
)
from presentation.api.routes.health import (
    router as health_router,
)
from presentation.api.routes.order import (
    router as order_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(5.0),
    ) as client:
        app.state.http_client = client
        yield

    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(order_router, prefix="/api")

    return app
