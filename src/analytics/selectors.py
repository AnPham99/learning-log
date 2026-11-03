"""Chỉ đọc: tổng hợp doanh số, hoàn trả, giá vốn và tồn cho dashboard."""

from collections import defaultdict
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import F, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from accounts.permissions import require_role
from catalog.models import Product
from inventory.models import Stock
from trading.models import Document, Line


def date_bounds(start, end):
    zone = timezone.get_current_timezone()
    return (
        timezone.make_aware(datetime.combine(start, time.min), zone),
        timezone.make_aware(datetime.combine(end + timedelta(days=1), time.min), zone),
    )


def dashboard(*, actor, start, end):
    """Kiểm tra quyền, lấy một snapshot nhất quán cho toàn bộ thẻ và biểu đồ."""
    require_role(actor, "manager")
    from django.db import connection

    nested = connection.in_atomic_block
    with transaction.atomic():
        if not nested:
            with connection.cursor() as cursor:
                cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
        return _snapshot(start, end)


def _snapshot(start, end):
    # One consistent snapshot across cards and charts while sales are being confirmed.
    lower, upper = date_bounds(start, end)
    base = Document.objects.filter(kind="sale", status__in=["confirmed", "reversed"])
    sold = base.filter(confirmed_at__gte=lower, confirmed_at__lt=upper)
    returned = base.filter(status="reversed", reversed_at__gte=lower, reversed_at__lt=upper)
    gross = sold.aggregate(amount=Sum("total"), cost=Sum("cost"))
    refunds = returned.aggregate(amount=Sum("total"), cost=Sum("cost"))
    revenue = (gross["amount"] or Decimal(0)) - (refunds["amount"] or Decimal(0))
    cost = (gross["cost"] or Decimal(0)) - (refunds["cost"] or Decimal(0))
    days = defaultdict(lambda: {"sales": 0, "refunds": 0})
    for docs, field, key in [(sold, "confirmed_at", "sales"), (returned, "reversed_at", "refunds")]:
        for row in docs.annotate(day=TruncDate(field)).values("day").annotate(amount=Sum("total")):
            days[row["day"]][key] = int(row["amount"])
    daily = []
    day = start
    while day <= end:
        values = days[day]
        daily.append(
            {
                "date": day.isoformat(),
                "label": day.strftime("%d/%m"),
                "revenue": values["sales"] - values["refunds"],
            }
        )
        day += timedelta(days=1)
    top = defaultdict(int)
    for docs, sign in [(sold, 1), (returned, -1)]:
        for row in (
            Line.objects.filter(document__in=docs)
            .values("product_id")
            .annotate(units=Sum("quantity"))
        ):
            top[row["product_id"]] += sign * row["units"]
    product_names = dict(Product.objects.filter(pk__in=top).values_list("pk", "name"))
    low = (
        Stock.objects.select_related("product")
        .filter(product__active=True, quantity__lte=F("product__reorder_level"))
        .order_by("quantity", "product_id")
    )
    stock_totals = Stock.objects.aggregate(units=Sum("quantity"), value=Sum("value"))
    return {
        "revenue": int(revenue),
        "collected": int(gross["amount"] or 0),
        "refunds": int(refunds["amount"] or 0),
        "profit": float(revenue - cost),
        "orders": sold.count(),
        "returns": returned.count(),
        "daily": daily,
        "stock_units": stock_totals["units"] or 0,
        "stock_value": float(stock_totals["value"] or 0),
        "low_count": low.count(),
        "low_stock": [
            {
                "name": s.product.name,
                "sku": s.product.sku,
                "quantity": s.quantity,
                "threshold": s.product.reorder_level,
            }
            for s in low[:8]
        ],
        "top": [
            {"name": product_names[pid], "units": qty}
            for pid, qty in sorted(top.items(), key=lambda x: (-x[1], x[0]))[:6]
            if qty > 0
        ],
        "recent": [
            {
                "id": d.pk,
                "code": d.code,
                "customer": d.contact_name,
                "total": int(d.total),
                "status": d.get_status_display(),
            }
            for d in sold.select_related("contact").order_by("-confirmed_at", "-pk")[:6]
        ],
        "updated_at": timezone.localtime().strftime("%H:%M:%S"),
        "start": start.isoformat(),
        "end": end.isoformat(),
    }
