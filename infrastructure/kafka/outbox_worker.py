import asyncio
import logging

from application.ports.usecases.publish_outbox import (
    ABCPublishOutboxUseCase,
)

logger = logging.getLogger(__name__)


class OutboxWorker:
    def __init__(
        self,
        usecase: ABCPublishOutboxUseCase,
    ) -> None:
        self._usecase = usecase

    async def run(self) -> None:
        while True:
            try:
                published = await self._usecase.execute()
            except asyncio.CancelledError:
                raise
            except Exception:
                logging.exception(
                    "Outbox publishing iteration failed"
                )
                await asyncio.sleep(5)
            else:
                if published:
                    await asyncio.sleep(0.1)
                else:
                    await asyncio.sleep(1)
