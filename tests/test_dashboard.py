from datetime import timedelta

import pytest
from django.utils import timezone

from analytics.selectors import dashboard
from trading.models import Document
from trading.services import confirm_document, reverse_document

from .helpers import receipt, sale

pytestmark = pytest.mark.django_db


def test_dashboard_sales_and_return_dates(manager, product, supplier):
    incoming = receipt(manager, product, supplier)
    confirm_document(actor=manager, document_id=incoming.pk)
    order = sale(manager, product, 2, discount=10000)
    confirm_document(actor=manager, document_id=order.pk)
    today = timezone.localdate()
    now = timezone.now()
    Document.objects.filter(pk=order.pk).update(confirmed_at=now - timedelta(days=1))
    before = dashboard(actor=manager, start=today - timedelta(days=1), end=today)
    assert before["revenue"] == 90000 and before["profit"] == 50000
    reverse_document(actor=manager, document_id=order.pk, reason="Trả hàng")
    yesterday = dashboard(
        actor=manager, start=today - timedelta(days=1), end=today - timedelta(days=1)
    )
    assert yesterday["revenue"] == 90000 and yesterday["refunds"] == 0
    current = dashboard(actor=manager, start=today, end=today)
    assert current["revenue"] == -90000 and current["refunds"] == 90000
    combined = dashboard(actor=manager, start=today - timedelta(days=1), end=today)
    assert combined["revenue"] == 0 and combined["profit"] == 0
    assert combined["stock_units"] == 10 and combined["top"] == []
    assert sum(row["revenue"] for row in combined["daily"]) == combined["revenue"]


def test_dashboard_ignores_drafts(manager, product):
    sale(manager, product)
    today = timezone.localdate()
    data = dashboard(actor=manager, start=today, end=today)
    assert data["revenue"] == 0 and data["orders"] == 0
    assert data["low_count"] == 1


@pytest.mark.parametrize(
    "query", ["?start=bad", "?start=2026-01-01&end=2025-12-31", "?start=2020-01-01&end=2026-01-01"]
)
def test_dashboard_invalid_dates(signed_in, query):
    assert signed_in.get("/dashboard/data/" + query).status_code == 400
    assert signed_in.get("/" + query).status_code == 200
