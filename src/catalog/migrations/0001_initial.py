from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Contact",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "kind",
                    models.CharField(
                        choices=[("supplier", "Nhà cung cấp"), ("customer", "Khách hàng")],
                        max_length=12,
                    ),
                ),
                ("name", models.CharField(max_length=160, verbose_name="Tên")),
                ("phone", models.CharField(blank=True, max_length=30, verbose_name="Điện thoại")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="Email")),
                ("address", models.CharField(blank=True, max_length=250, verbose_name="Địa chỉ")),
                ("active", models.BooleanField(default=True, verbose_name="Đang hoạt động")),
            ],
            options={
                "ordering": ["name", "pk"],
            },
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("sku", models.CharField(max_length=40, unique=True, verbose_name="Mã SKU")),
                ("name", models.CharField(max_length=160, verbose_name="Tên sản phẩm")),
                ("category", models.CharField(max_length=80, verbose_name="Danh mục")),
                ("unit", models.CharField(default="cái", max_length=30, verbose_name="Đơn vị")),
                (
                    "selling_price",
                    models.DecimalField(
                        decimal_places=0, max_digits=14, verbose_name="Giá bán (₫)"
                    ),
                ),
                (
                    "reorder_level",
                    models.PositiveIntegerField(default=5, verbose_name="Ngưỡng tồn thấp"),
                ),
                ("active", models.BooleanField(default=True, verbose_name="Đang kinh doanh")),
            ],
            options={
                "ordering": ["name", "pk"],
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("selling_price__gte", 0)),
                        name="product_price_nonnegative",
                    )
                ],
            },
        ),
    ]
