import uuid
from abc import ABC, abstractmethod

from application.dto.catalog import CatalogItem


class ABCCatalogClient(ABC):
    @abstractmethod
    async def get_item(self, item_id: uuid.UUID) -> CatalogItem:
        raise NotImplementedError
