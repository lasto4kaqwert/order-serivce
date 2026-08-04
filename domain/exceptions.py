

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


class InvalidOrderStatusTransitionError(DomainError):
    def __init__(
        self,
        current_status: str,
        target_status: str,
    ) -> None:
        self.current_status = current_status
        self.target_status = target_status

        super().__init__(
            f"Cannot change order status from "
            f"{current_status} to {target_status}"
        )
