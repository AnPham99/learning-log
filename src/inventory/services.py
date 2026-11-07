from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction

from accounts.permissions import require_role
from common.exceptions import BusinessError

from .models import Movement, Stock

PRECISION = Decimal("0.0001")


def money(value):
    return Decimal(value).quantize(PRECISION, rounding=ROUND_HALF_UP)


def move(*, stock, quantity, value, actor, reason, document=None):
    if stock.quantity + quantity < 0 or stock.value + value < 0:
        raise BusinessError("Không đủ tồn kho để thực hiện giao dịch.")
    stock.quantity += quantity
    stock.value += value
    stock.save(update_fields=["quantity", "value"])
    return Movement.objects.create(
        product_id=stock.product_id,
        document=document,
        quantity=quantity,
        value=value,
        balance=stock.quantity,
        reason=reason,
        actor=actor,
    )


@transaction.atomic
def adjust_stock(*, actor, product_id, quantity, reason, unit_cost=0):
    reason = reason.strip()
    require_role(actor, "manager")
    if not reason or len(reason) > 250 or not quantity:
        raise BusinessError("Nhập chênh lệch khác 0 và lý do điều chỉnh (tối đa 250 ký tự).")
    stock = Stock.objects.select_for_update().get(product_id=product_id)
    if quantity > 0:
        if Decimal(unit_cost) < 0:
            raise BusinessError("Giá vốn không được âm.")
        value = money(Decimal(unit_cost) * quantity)
    else:
        if stock.quantity < -quantity:
            raise BusinessError("Điều chỉnh sẽ làm tồn kho âm.")
        value = (
            -stock.value
            if stock.quantity == -quantity
            else money(stock.value / stock.quantity * quantity)
        )
    return move(stock=stock, quantity=quantity, value=value, actor=actor, reason=reason)
