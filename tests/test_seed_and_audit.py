"""Kiểm tra dữ liệu minh họa và bộ đối chiếu độc lập với UI."""

import io

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from inventory.checks import check_business_data
from inventory.models import Stock
from trading.models import Document
from trading.services import confirm_document, reverse_document

from .helpers import receipt, sale

pytestmark = pytest.mark.django_db


def test_seed_covers_modules_and_refuses_duplicate(manager):
    call_command("seed_demo", username=manager.username, stdout=io.StringIO())
    result = check_business_data()
    assert result["ok"]
    assert (result["products"], result["suppliers"], result["customers"]) == (8, 1, 3)
    assert result["documents"] == 29
    assert set(Document.objects.filter(kind="sale").values_list("payment_method", flat=True)) == {
        "cash",
        "bank",
    }
    with pytest.raises(CommandError):
        call_command("seed_demo", username=manager.username, stdout=io.StringIO())
    assert Document.objects.count() == 29


def test_audit_checks_reversed_drafts_and_cancelled(manager, product, supplier):
    incoming = receipt(manager, product, supplier)
    confirm_document(actor=manager, document_id=incoming.pk)
    order = sale(manager, product)
    confirm_document(actor=manager, document_id=order.pk)
    reverse_document(actor=manager, document_id=order.pk, reason="Khách trả")
    sale(manager, product)
    cancelled = sale(manager, product)
    reverse_document(actor=manager, document_id=cancelled.pk, reason="Hủy nháp")
    result = check_business_data()
    assert result["ok"] and set(result["statuses"]) == {
        "confirmed",
        "reversed",
        "draft",
        "cancelled",
    }


def test_audit_detects_broken_stock_and_document(manager, product, supplier):
    incoming = receipt(manager, product, supplier)
    confirm_document(actor=manager, document_id=incoming.pk)
    Stock.objects.filter(product=product).update(quantity=999)
    Document.objects.filter(pk=incoming.pk).update(total=1)
    result = check_business_data()
    assert not result["ok"]
    assert any("Stock" in error for error in result["errors"])
    assert any("tổng tiền" in error for error in result["errors"])
