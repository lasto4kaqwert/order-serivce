

class DomainError(Exception):
    pass


class InvalidOrderQuantityError(DomainError):
    def __init__(
        self,
        quantity: int,
    ) -> None:
        self.quantity = quantity

        super().__init__(
            f"Order quantity must be positive, got {quantity}"
        )
