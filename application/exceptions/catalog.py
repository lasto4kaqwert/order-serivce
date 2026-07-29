class CatalogClientError(Exception):
    pass


class CatalogItemNotFoundError(CatalogClientError):
    pass


class CatalogUnavailableError(CatalogClientError):
    pass


class InvalidCatalogResponseError(CatalogClientError):
    pass
