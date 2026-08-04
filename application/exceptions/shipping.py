from uuid import UUID


class ShippingEventError(Exception):
    pass


class ShippingEventConflictError(ShippingEventError):
    def __init__(self, order_id: UUID, message: str) -> None:
        self.order_id = order_id

        super().__init__(
            f"Shipping event conflicts with order "
            f"{order_id}: {message}"
        )
