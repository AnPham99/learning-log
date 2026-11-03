"""Danh mục thương mại: Product và Contact (khách hàng/nhà cung cấp)."""

from django.db import models
from django.db.models import Q


class Product(models.Model):
    sku = models.CharField("Mã SKU", max_length=40, unique=True)
    name = models.CharField("Tên sản phẩm", max_length=160)
    category = models.CharField("Danh mục", max_length=80)
    unit = models.CharField("Đơn vị", max_length=30, default="cái")
    selling_price = models.DecimalField("Giá bán (₫)", max_digits=14, decimal_places=0)
    reorder_level = models.PositiveIntegerField("Ngưỡng tồn thấp", default=5)
    active = models.BooleanField("Đang kinh doanh", default=True)

    class Meta:
        ordering = ["name", "pk"]
        constraints = [
            models.CheckConstraint(
                condition=Q(selling_price__gte=0), name="product_price_nonnegative"
            )
        ]

    def __str__(self):
        return f"{self.sku} · {self.name}"


class Contact(models.Model):
    class Kind(models.TextChoices):
        SUPPLIER = "supplier", "Nhà cung cấp"
        CUSTOMER = "customer", "Khách hàng"

    kind = models.CharField(max_length=12, choices=Kind.choices)
    name = models.CharField("Tên", max_length=160)
    phone = models.CharField("Điện thoại", max_length=30, blank=True)
    email = models.EmailField("Email", blank=True)
    address = models.CharField("Địa chỉ", max_length=250, blank=True)
    active = models.BooleanField("Đang hoạt động", default=True)

    class Meta:
        ordering = ["name", "pk"]

    def __str__(self):
        return self.name
