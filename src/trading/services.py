"""Nghiệp vụ nhập/bán: lưu nháp, xác nhận, hủy/hoàn có quyền, khóa và transaction."""

from decimal import Decimal

from django.db import connection, transaction
from django.utils import timezone

from accounts.permissions import require_role
from catalog.models import Contact, Product
from common.exceptions import BusinessError
from inventory.models import Movement, Stock
from inventory.services import money, move

from .models import Document, Line


def authorize(actor, kind):
    if kind not in Document.Kind.values:
        raise BusinessError("Loại chứng từ không hợp lệ.")
    require_role(actor, "manager", "warehouse" if kind == "purchase" else "sales")


def validate_lines(kind, items):
    if not items or len(items) > 100:
        raise BusinessError("Mỗi chứng từ cần từ 1 đến 100 sản phẩm.")
    ids = [int(item["product_id"]) for item in items]
    if len(set(ids)) != len(ids):
        raise BusinessError("Mỗi sản phẩm chỉ được xuất hiện một dòng.")
    products = {p.pk: p for p in Product.objects.filter(pk__in=ids, active=True)}
    if len(products) != len(ids):
        raise BusinessError("Sản phẩm không tồn tại hoặc đã ngừng kinh doanh.")
    lines = []
    for item in items:
        product = products[int(item["product_id"])]
        quantity = int(item["quantity"])
        if quantity < 1 or quantity > 1000000:
            raise BusinessError("Số lượng phải từ 1 đến 1.000.000.")
        price = Decimal(item["unit_price"]) if kind == "purchase" else product.selling_price
        line = Line(
            product=product,
            product_name=product.name,
            sku=product.sku,
            quantity=quantity,
            unit_price=price,
        )
        line.clean_fields(exclude=["document"])
        if price < 0:
            raise BusinessError("Đơn giá không được âm.")
        lines.append(line)
    return lines


@transaction.atomic
def save_draft(
    *,
    actor,
    kind,
    items,
    request_key,
    contact_id=None,
    discount=0,
    payment_method="cash",
    note="",
    document_id=None,
):
    """Lưu chứng từ nháp, chụp tên/giá bán; cùng token chỉ tạo một lần."""
    authorize(actor, kind)
    # Serialize retries with the same form token, including requests on separate connections.
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_xact_lock(%s)", [request_key.int & ((1 << 63) - 1)])
    existing = Document.objects.filter(request_key=request_key).first()
    if existing and document_id is None:
        if existing.created_by_id != actor.pk or existing.kind != kind:
            raise BusinessError("Mã yêu cầu không hợp lệ.")
        return existing
    doc = Document(kind=kind, request_key=request_key, created_by=actor)
    if document_id:
        doc = Document.objects.select_for_update().get(pk=document_id, kind=kind)
        if doc.status != "draft":
            raise BusinessError("Chỉ được sửa chứng từ nháp.")
    lines = validate_lines(kind, items)
    contact = None
    if contact_id:
        contact = Contact.objects.filter(
            pk=contact_id, active=True, kind="supplier" if kind == "purchase" else "customer"
        ).first()
        if contact is None:
            raise BusinessError("Đối tác không hợp lệ.")
    if kind == "purchase" and contact is None:
        raise BusinessError("Phiếu nhập cần nhà cung cấp.")
    subtotal = sum(line.subtotal for line in lines)
    discount = Decimal(discount)
    if discount < 0 or discount > subtotal or (kind == "purchase" and discount):
        raise BusinessError("Giảm giá phải từ 0 đến tổng tiền đơn bán.")
    doc.contact = contact
    doc.contact_name = contact.name if contact else "Khách lẻ"
    doc.discount, doc.total = discount, subtotal - discount
    doc.payment_method, doc.note = payment_method, note.strip()
    doc.full_clean()
    doc.save()
    doc.lines.all().delete()
    for line in lines:
        line.document = doc
        line.full_clean()
        line.save()
    return doc


@transaction.atomic
def confirm_document(*, actor, document_id):
    """Khóa chứng từ và tồn; ghi mọi dòng hoặc rollback toàn bộ nếu thiếu hàng."""
    doc = Document.objects.select_for_update().get(pk=document_id)
    authorize(actor, doc.kind)
    if doc.status == "confirmed":
        return doc
    if doc.status != "draft":
        raise BusinessError("Chứng từ đã hủy/hoàn không thể xác nhận.")
    lines = list(doc.lines.select_related("product").order_by("product_id"))
    if not lines:
        raise BusinessError("Chứng từ chưa có sản phẩm.")
    stocks = {
        s.product_id: s
        for s in Stock.objects.select_for_update()
        .filter(product_id__in=[line.product_id for line in lines])
        .order_by("product_id")
    }
    cost = Decimal(0)
    for line in lines:
        if not line.product.active:
            raise BusinessError(f"{line.product_name} đã ngừng kinh doanh.")
        stock = stocks[line.product_id]
        if doc.kind == "purchase":
            value = money(line.subtotal)
            move(
                stock=stock,
                quantity=line.quantity,
                value=value,
                actor=actor,
                reason="Nhập hàng",
                document=doc,
            )
        else:
            if stock.quantity < line.quantity:
                raise BusinessError(
                    f"{line.product_name}: tồn {stock.quantity}, cần {line.quantity}."
                )
            value = (
                stock.value
                if stock.quantity == line.quantity
                else money(stock.value / stock.quantity * line.quantity)
            )
            move(
                stock=stock,
                quantity=-line.quantity,
                value=-value,
                actor=actor,
                reason="Bán hàng",
                document=doc,
            )
        line.cost = value
        line.save(update_fields=["cost"])
        cost += value
    doc.cost, doc.status, doc.confirmed_at = cost, "confirmed", timezone.now()
    doc.confirmed_by = actor
    doc.save(update_fields=["cost", "status", "confirmed_at", "confirmed_by"])
    return doc


@transaction.atomic
def reverse_document(*, actor, document_id, reason):
    """Hủy nháp hoặc hoàn toàn bộ; giữ lịch sử, chỉ đảo tồn một lần."""
    doc = Document.objects.select_for_update().get(pk=document_id)
    authorize(actor, doc.kind)
    if not reason.strip() or len(reason.strip()) > 250:
        raise BusinessError("Cần lý do hủy/hoàn (tối đa 250 ký tự).")
    if doc.status in ["cancelled", "reversed"]:
        return doc
    if doc.status == "draft":
        doc.status = "cancelled"
    else:
        require_role(actor, "manager")
        lines = list(doc.lines.order_by("product_id"))
        stocks = {
            s.product_id: s
            for s in Stock.objects.select_for_update()
            .filter(product_id__in=[line.product_id for line in lines])
            .order_by("product_id")
        }
        for line in lines:
            stock = stocks[line.product_id]
            if doc.kind == "purchase":
                latest = Movement.objects.filter(product_id=line.product_id).first()
                if latest is None or latest.document_id != doc.pk:
                    raise BusinessError(
                        "Không thể hoàn phiếu nhập khi sản phẩm đã có giao dịch tiếp theo."
                    )
                quantity, value = -line.quantity, -line.cost
            else:
                quantity, value = line.quantity, line.cost
            move(
                stock=stock,
                quantity=quantity,
                value=value,
                actor=actor,
                reason=reason.strip(),
                document=doc,
            )
        doc.status = "reversed"
    doc.reversed_at, doc.reversal_reason = timezone.now(), reason.strip()
    doc.reversed_by = actor
    doc.save(update_fields=["status", "reversed_at", "reversal_reason", "reversed_by"])
    return doc
