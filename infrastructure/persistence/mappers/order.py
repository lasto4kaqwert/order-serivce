from domain.entities import Order
from infrastructure.persistence.models import OrderModel


def to_domain(model: OrderModel) -> Order:
    return Order(
        user_id=model.user_id,
        quantity=model.quantity,
        item_id=model.item_id,
        idempotency_key=model.idempotency_key,
        id=model.id,
        status=model.status,
        created_at=model.created_at,
        update_at=model.update_at,
    )


def to_model(order: Order) -> OrderModel:
    return OrderModel(
        user_id=order.user_id,
        quantity=order.quantity,
        item_id=order.item_id,
        idempotency_key=order.idempotency_key,
        id=order.id,
        status=order.status,
        created_at=order.created_at,
        update_at=order.update_at,
    )
