"""Optional, explicit sample data; never run automatically on a user's database."""

import uuid
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from catalog.models import Product
from catalog.services import save_contact, save_product
from inventory.models import Movement, Stock
from inventory.services import adjust_stock
from trading.models import Document
from trading.services import confirm_document, save_draft


class Command(BaseCommand):
    help = "Nạp dữ liệu minh họa vào cửa hàng chưa có sản phẩm. Không tạo mật khẩu."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True, help="Tài khoản quản lý đã tạo")

    @transaction.atomic
    def handle(self, *args, **options):
        if Product.objects.exists() or Document.objects.exists():
            raise CommandError("Chỉ nạp demo khi chưa có sản phẩm và giao dịch.")
        try:
            actor = get_user_model().objects.get(username=options["username"])
        except get_user_model().DoesNotExist as error:
            raise CommandError("Hãy tạo tài khoản quản lý qua giao diện trước.") from error
        supplier = save_contact(
            actor=actor,
            kind="supplier",
            data={
                "name": "Minh An Stationery (Demo)",
                "phone": "",
                "email": "",
                "address": "TP. Hồ Chí Minh",
                "active": True,
            },
        )
        customers = [
            save_contact(
                actor=actor,
                kind="customer",
                data={"name": name, "phone": "", "email": "", "address": "", "active": True},
            )
            for name in [
                "Khách hàng Linh (Demo)",
                "Văn phòng An Nhiên (Demo)",
                "Khách hàng Nam (Demo)",
            ]
        ]
        rows = [
            ("NB-01", "Sổ tay chấm bi A5", 89000, 42000),
            ("PN-02", "Bút gel 0.5 mm", 25000, 11000),
            ("NB-03", "Sổ lò xo A6", 45000, 21000),
            ("BG-04", "Túi vải Everyday", 129000, 58000),
            ("ST-05", "Giấy ghi chú Pastel", 35000, 16000),
            ("FL-06", "Bìa hồ sơ Kraft", 18000, 7000),
            ("PN-07", "Bút highlight", 32000, 14000),
            ("CL-08", "Kẹp giấy kim loại", 22000, 8000),
        ]
        products = [
            save_product(
                actor=actor,
                data={
                    "sku": sku,
                    "name": name,
                    "category": "Văn phòng phẩm",
                    "unit": "cái",
                    "selling_price": price,
                    "reorder_level": 8,
                    "active": True,
                },
            )
            for sku, name, price, cost in rows
        ]
        receipt = save_draft(
            actor=actor,
            kind="purchase",
            request_key=uuid.uuid4(),
            contact_id=supplier.pk,
            items=[
                {"product_id": product.pk, "quantity": 120, "unit_price": row[3]}
                for product, row in zip(products, rows, strict=True)
            ],
            note="Dữ liệu minh họa · Nhập hàng đầu kỳ",
        )
        confirm_document(actor=actor, document_id=receipt.pk)
        now = timezone.now()
        Document.objects.filter(pk=receipt.pk).update(
            created_at=now - timedelta(days=14), confirmed_at=now - timedelta(days=14)
        )
        Movement.objects.filter(document=receipt).update(created_at=now - timedelta(days=14))
        for day in range(13, -1, -1):
            for offset in range(2):
                selected = [(day + offset) % len(products), (day + offset + 3) % len(products)]
                sale = save_draft(
                    actor=actor,
                    kind="sale",
                    request_key=uuid.uuid4(),
                    contact_id=customers[(day + offset) % 3].pk,
                    payment_method="bank" if offset else "cash",
                    discount=Decimal(5000 if day % 3 == 0 else 0),
                    items=[
                        {"product_id": products[index].pk, "quantity": 1 + (day + offset) % 4}
                        for index in selected
                    ],
                    note="Dữ liệu minh họa",
                )
                confirm_document(actor=actor, document_id=sale.pk)
                date = now - timedelta(days=day, hours=offset)
                Document.objects.filter(pk=sale.pk).update(created_at=date, confirmed_at=date)
                Movement.objects.filter(document=sale).update(created_at=date)
        for index, target in [(0, 5), (4, 3), (6, 7)]:
            product = products[index]
            quantity = Stock.objects.get(product=product).quantity
            adjust_stock(
                actor=actor,
                product_id=product.pk,
                quantity=target - quantity,
                reason="Dữ liệu minh họa · Kiểm kê kho",
            )
        self.stdout.write(
            self.style.SUCCESS("Đã tạo 8 sản phẩm, 1 phiếu nhập và 28 đơn bán minh họa.")
        )
