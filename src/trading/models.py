import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q


class Document(models.Model):
    class Kind(models.TextChoices):
        PURCHASE = "purchase", "Phiếu nhập"
        SALE = "sale", "Đơn bán"

    class Status(models.TextChoices):
        DRAFT = "draft", "Nháp"
        CONFIRMED = "confirmed", "Đã xác nhận"
        CANCELLED = "cancelled", "Đã hủy"
        REVERSED = "reversed", "Đã hoàn"

    class Payment(models.TextChoices):
        CASH = "cash", "Tiền mặt"
        BANK = "bank", "Chuyển khoản"

    kind = models.CharField(max_length=12, choices=Kind.choices)
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.DRAFT, db_index=True
    )
    request_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    contact = models.ForeignKey("catalog.Contact", null=True, blank=True, on_delete=models.PROTECT)
    contact_name = models.CharField(max_length=160, blank=True)
    discount = models.DecimalField(max_digits=16, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=18, decimal_places=0, default=0)
    cost = models.DecimalField(max_digits=22, decimal_places=4, default=0)
    payment_method = models.CharField(max_length=8, choices=Payment.choices, default=Payment.CASH)
    note = models.CharField(max_length=250, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="confirmed_documents",
    )
    reversed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="reversed_documents",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    reversed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    reversal_reason = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ["-pk"]
        constraints = [
            models.CheckConstraint(
                condition=Q(total__gte=0, discount__gte=0), name="document_amount_nonnegative"
            )
        ]

    @property
    def code(self):
        return f"{'PN' if self.kind == 'purchase' else 'BH'}-{self.pk:05d}"


class Line(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey("catalog.Product", on_delete=models.PROTECT)
    product_name = models.CharField(max_length=160)
    sku = models.CharField(max_length=40)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=14, decimal_places=0)
    cost = models.DecimalField(max_digits=22, decimal_places=4, default=0)

    class Meta:
        ordering = ["pk"]
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0, unit_price__gte=0), name="line_valid_amounts"
            ),
            models.UniqueConstraint(fields=["document", "product"], name="line_unique_product"),
        ]

    @property
    def subtotal(self):
        return self.unit_price * self.quantity
