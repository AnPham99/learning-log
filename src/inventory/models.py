"""Stock lưu số dư hiện tại; Movement lưu từng lần thay đổi và người thực hiện."""

from django.conf import settings
from django.db import models
from django.db.models import Q


class Stock(models.Model):
    product = models.OneToOneField(
        "catalog.Product", on_delete=models.PROTECT, related_name="stock"
    )
    quantity = models.PositiveIntegerField(default=0)
    value = models.DecimalField(max_digits=22, decimal_places=4, default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(value__gte=0), name="stock_value_nonnegative")
        ]


class Movement(models.Model):
    product = models.ForeignKey("catalog.Product", on_delete=models.PROTECT)
    document = models.ForeignKey(
        "trading.Document",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="movements",
    )
    quantity = models.IntegerField()
    value = models.DecimalField(max_digits=22, decimal_places=4)
    balance = models.PositiveIntegerField()
    reason = models.CharField(max_length=250)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-pk"]
