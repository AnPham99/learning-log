import uuid
from decimal import Decimal

import pytest
from django.core.exceptions import PermissionDenied, ValidationError

from catalog.services import save_product
from common.exceptions import BusinessError
from inventory.models import Movement, Stock
from inventory.services import adjust_stock
from trading.models import Document
from trading.services import confirm_document, reverse_document, save_draft

from .helpers import receipt, sale

pytestmark = pytest.mark.django_db


def test_receipt_sale_and_repeat_confirm(manager, product, supplier):
    incoming = receipt(manager, product, supplier)
    assert Stock.objects.get(product=product).quantity == 0
    confirm_document(actor=manager, document_id=incoming.pk)
    confirm_document(actor=manager, document_id=incoming.pk)
    stock = Stock.objects.get(product=product)
    assert (stock.quantity, stock.value) == (10, 200000)
    order = sale(manager, product, quantity=3, discount=10000)
    assert order.total == 140000
    confirm_document(actor=manager, document_id=order.pk)
    confirm_document(actor=manager, document_id=order.pk)
    order.refresh_from_db()
    stock.refresh_from_db()
    assert (stock.quantity, stock.value, order.cost) == (7, 140000, 60000)
    assert Movement.objects.count() == 2


def test_insufficient_stock_rolls_back_entire_document(manager, product, supplier):
    other = save_product(
        actor=manager,
        data={
            "sku": "SKU-002",
            "name": "Bút",
            "category": "Văn phòng phẩm",
            "unit": "cái",
            "selling_price": 10000,
            "reorder_level": 5,
            "active": True,
        },
    )
    incoming = receipt(manager, product, supplier)
    confirm_document(actor=manager, document_id=incoming.pk)
    order = save_draft(
        actor=manager,
        kind="sale",
        request_key=uuid.uuid4(),
        items=[{"product_id": product.pk, "quantity": 2}, {"product_id": other.pk, "quantity": 1}],
    )
    with pytest.raises(BusinessError):
        confirm_document(actor=manager, document_id=order.pk)
    assert Stock.objects.get(product=product).quantity == 10
    assert Movement.objects.count() == 1
    order.refresh_from_db()
    assert order.status == "draft" and order.cost == 0


def test_weighted_cost_and_full_return_preserve_value(manager, product, supplier):
    for qty, price in [(10, 10000), (10, 30000)]:
        doc = receipt(manager, product, supplier, qty, price)
        confirm_document(actor=manager, document_id=doc.pk)
    order = sale(manager, product, 5)
    confirm_document(actor=manager, document_id=order.pk)
    order.refresh_from_db()
    assert order.cost == 100000
    reverse_document(actor=manager, document_id=order.pk, reason="Khách trả toàn bộ hàng")
    reverse_document(actor=manager, document_id=order.pk, reason="Lặp request")
    stock = Stock.objects.get(product=product)
    assert (stock.quantity, stock.value) == (20, 400000)
    assert Movement.objects.filter(document=order).count() == 2
    with pytest.raises(BusinessError):
        confirm_document(actor=manager, document_id=order.pk)


def test_receipt_reversal_and_block_later_movement(manager, product, supplier):
    first = receipt(manager, product, supplier)
    confirm_document(actor=manager, document_id=first.pk)
    reverse_document(actor=manager, document_id=first.pk, reason="Nhập nhầm")
    assert Stock.objects.get(product=product).quantity == 0
    second = receipt(manager, product, supplier)
    confirm_document(actor=manager, document_id=second.pk)
    adjust_stock(
        actor=manager, product_id=product.pk, quantity=1, unit_cost=20000, reason="Kiểm kê"
    )
    with pytest.raises(BusinessError):
        reverse_document(actor=manager, document_id=second.pk, reason="Hoàn phiếu")
    assert Stock.objects.get(product=product).quantity == 11


def test_price_snapshot_and_draft_idempotency(manager, product):
    key = uuid.uuid4()
    items = [{"product_id": product.pk, "quantity": 2, "unit_price": 1}]
    order = save_draft(actor=manager, kind="sale", request_key=key, items=items)
    repeat = save_draft(actor=manager, kind="sale", request_key=key, items=items)
    assert order.pk == repeat.pk
    product.selling_price = 90000
    product.name = "Tên mới"
    product.save()
    assert order.lines.get().unit_price == 50000
    assert order.lines.get().product_name == "Sổ tay"
    assert Document.objects.count() == 1


@pytest.mark.parametrize(
    "items,discount",
    [
        ([], 0),
        ([{"quantity": 0}], 0),
        ([{"quantity": 1}, {"quantity": 1}], 0),
        ([{"quantity": 1}], -1),
        ([{"quantity": 1}], 100000),
    ],
)
def test_reject_invalid_drafts(manager, product, items, discount):
    for item in items:
        item["product_id"] = product.pk
    with pytest.raises((BusinessError, ValidationError)):
        save_draft(
            actor=manager, kind="sale", request_key=uuid.uuid4(), items=items, discount=discount
        )
    assert not Document.objects.exists()


def test_roles_enforced_in_services(manager, seller, warehouse, product, supplier):
    with pytest.raises(PermissionDenied):
        receipt(seller, product, supplier)
    with pytest.raises(PermissionDenied):
        sale(warehouse, product)
    with pytest.raises(PermissionDenied):
        adjust_stock(actor=seller, product_id=product.pk, quantity=1, unit_cost=1, reason="x")
    incoming = receipt(warehouse, product, supplier)
    confirm_document(actor=warehouse, document_id=incoming.pk)
    order = sale(seller, product)
    confirm_document(actor=seller, document_id=order.pk)
    with pytest.raises(PermissionDenied):
        reverse_document(actor=seller, document_id=order.pk, reason="x")
    reverse_document(actor=manager, document_id=order.pk, reason="Khách trả")


def test_adjustment_validation_and_cost(manager, product):
    for quantity, reason in [(0, "Kiểm kê"), (1, ""), (-1, "Kiểm kê")]:
        with pytest.raises(BusinessError):
            adjust_stock(
                actor=manager, product_id=product.pk, quantity=quantity, unit_cost=1, reason=reason
            )
    adjust_stock(
        actor=manager, product_id=product.pk, quantity=3, unit_cost=10000, reason="Tồn đầu"
    )
    adjust_stock(actor=manager, product_id=product.pk, quantity=-3, reason="Hỏng")
    stock = Stock.objects.get(product=product)
    assert stock.quantity == 0 and stock.value == Decimal(0)


def test_draft_cancel_and_immutability(manager, product, supplier):
    order = sale(manager, product)
    reverse_document(actor=manager, document_id=order.pk, reason="Không mua")
    order.refresh_from_db()
    assert order.reversed_by_id == manager.pk
    assert not Movement.objects.exists()
    with pytest.raises(BusinessError):
        confirm_document(actor=manager, document_id=order.pk)
    doc = receipt(manager, product, supplier)
    confirm_document(actor=manager, document_id=doc.pk)
    with pytest.raises(BusinessError):
        save_draft(
            actor=manager,
            kind="purchase",
            request_key=doc.request_key,
            document_id=doc.pk,
            contact_id=supplier.pk,
            items=[{"product_id": product.pk, "quantity": 1, "unit_price": 1}],
        )


def test_contact_kind_cannot_bypass_role(warehouse, supplier):
    from catalog.services import save_contact

    with pytest.raises(BusinessError):
        save_contact(actor=warehouse, kind="customer", data={}, instance=supplier)
