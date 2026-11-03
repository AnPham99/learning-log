import uuid

from trading.services import save_draft


def receipt(actor, product, supplier, quantity=10, price=20000):
    return save_draft(
        actor=actor,
        kind="purchase",
        request_key=uuid.uuid4(),
        contact_id=supplier.pk,
        items=[{"product_id": product.pk, "quantity": quantity, "unit_price": price}],
    )


def sale(actor, product, quantity=2, discount=0):
    return save_draft(
        actor=actor,
        kind="sale",
        request_key=uuid.uuid4(),
        discount=discount,
        items=[{"product_id": product.pk, "quantity": quantity}],
    )
