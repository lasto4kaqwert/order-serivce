import uuid


class OrderApplicationError(Exception):
    pass


class OrderNotFoundError(OrderApplicationError):
    def __init__(self, order_id: uuid.UUID) -> None:
        self.order_id = order_id

        super().__init__(
            f"Order {order_id} not found"
        )


class InsufficientStockError(OrderApplicationError):
    def __init__(
        self,
        item_id: uuid.UUID,
        requested: int,
        available: int,
    ) -> None:
        self.item_id = item_id
        self.requested = requested
        self.available = available

        super().__init__(
            f"Requested {requested} items, but only {available} are available"
        )


class DuplicateIdempotencyKeyError(OrderApplicationError):
    def __init__(self, idempotency_key: str) -> None:
        self.idempotency_key = idempotency_key

        super().__init__(
            f"Order with idempotency_key {idempotency_key!r} already exists"
        )
