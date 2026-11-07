from collections import defaultdict
from decimal import Decimal

from django.db import connection, transaction
from django.db.models import Count

from catalog.models import Contact, Product
from trading.models import Document

from .models import Movement, Stock


def _ledger_totals(errors):
    totals = defaultdict(lambda: [0, Decimal(0)])
    by_document = defaultdict(lambda: [0, Decimal(0), 0])
    for item in Movement.objects.order_by("pk").iterator(chunk_size=500):
        balance = totals[item.product_id]
        balance[0] += item.quantity
        balance[1] += item.value
        if balance[0] != item.balance or balance[0] < 0 or balance[1] < 0:
            errors.append(f"Movement {item.pk}: số dư hoặc giá trị lịch sử không khớp.")
        if item.document_id:
            effect = by_document[item.document_id, item.product_id]
            effect[0] += item.quantity
            effect[1] += item.value
            effect[2] += 1
    return totals, by_document


def _check_documents(effects, errors):
    for doc in Document.objects.prefetch_related("lines").iterator(chunk_size=100):
        lines = list(doc.lines.all())
        subtotal = sum(line.subtotal for line in lines)
        if not lines or subtotal - doc.discount != doc.total:
            errors.append(f"Document {doc.pk}: tổng tiền không khớp dòng hàng.")
        if doc.status in ["confirmed", "reversed"]:
            if sum(line.cost for line in lines) != doc.cost or not doc.confirmed_at:
                errors.append(f"Document {doc.pk}: giá vốn hoặc thời điểm xác nhận không hợp lệ.")
        for line in lines:
            sign = 1 if doc.kind == "purchase" else -1
            expected = {
                "draft": [0, Decimal(0), 0],
                "cancelled": [0, Decimal(0), 0],
                "confirmed": [sign * line.quantity, sign * line.cost, 1],
                "reversed": [0, Decimal(0), 2],
            }[doc.status]
            if effects[doc.pk, line.product_id] != expected:
                errors.append(f"Document {doc.pk}, product {line.product_id}: tác động kho sai.")


def check_business_data():
    nested = connection.in_atomic_block
    with transaction.atomic():
        if not nested:
            with connection.cursor() as cursor:
                cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
        return _check_snapshot()


def _check_snapshot():
    errors = []
    totals, effects = _ledger_totals(errors)
    if Product.objects.filter(stock__isnull=True).exists():
        errors.append("Có sản phẩm chưa có bản ghi Stock.")
    for stock in Stock.objects.all().iterator(chunk_size=500):
        if totals[stock.product_id] != [stock.quantity, stock.value]:
            errors.append(f"Product {stock.product_id}: Stock không khớp tổng sổ kho.")
    _check_documents(effects, errors)
    return {
        "products": Product.objects.count(),
        "suppliers": Contact.objects.filter(kind="supplier").count(),
        "customers": Contact.objects.filter(kind="customer").count(),
        "documents": Document.objects.count(),
        "movements": Movement.objects.count(),
        "statuses": dict(Document.objects.values_list("status").annotate(count=Count("pk"))),
        "errors": errors,
        "ok": not errors,
    }
