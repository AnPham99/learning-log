import uuid

import pytest

from catalog.services import save_product
from inventory.models import Movement
from trading.models import Document
from trading.services import save_draft

pytestmark = pytest.mark.django_db


def second_product(manager):
    return save_product(
        actor=manager,
        data={
            "sku": "ROW-02",
            "name": "Bút thử",
            "category": "Văn phòng phẩm",
            "unit": "cái",
            "selling_price": 20000,
            "reorder_level": 2,
            "active": True,
        },
    )


def payload(kind, supplier, product):
    return {
        "request_key": str(uuid.uuid4()),
        "contact": str(supplier.pk) if kind == "purchase" else "",
        "discount": "0",
        "payment_method": "cash",
        "note": "",
        "lines-TOTAL_FORMS": "2",
        "lines-INITIAL_FORMS": "0",
        "lines-0-DELETE": "on",
        "lines-0-quantity": "-1",
        "lines-1-product": str(product.pk),
        "lines-1-quantity": "3",
        "lines-1-unit_price": "10000" if kind == "purchase" else "",
    }


@pytest.mark.parametrize("kind", ["purchase", "sale"])
def test_create_ignores_deleted_invalid_row(signed_in, manager, product, supplier, kind):
    other = second_product(manager)
    response = signed_in.post(f"/documents/{kind}/new/", payload(kind, supplier, other))
    assert response.status_code == 302
    doc = Document.objects.get()
    assert doc.lines.count() == 1
    assert doc.lines.get().product_id == other.pk
    assert doc.total == (30000 if kind == "purchase" else 60000)
    assert not Movement.objects.exists()


@pytest.mark.parametrize("kind", ["purchase", "sale"])
def test_edit_draft_removes_existing_line(signed_in, manager, product, supplier, kind):
    other = second_product(manager)
    doc = save_draft(
        actor=manager,
        kind=kind,
        request_key=uuid.uuid4(),
        contact_id=supplier.pk if kind == "purchase" else None,
        items=[
            {"product_id": product.pk, "quantity": 1, "unit_price": 10000},
            {"product_id": other.pk, "quantity": 3, "unit_price": 10000},
        ],
    )
    data = payload(kind, supplier, other)
    data["request_key"] = str(doc.request_key)
    data["lines-INITIAL_FORMS"] = "2"
    response = signed_in.post(f"/documents/{kind}/{doc.pk}/edit/", data)
    assert response.status_code == 302
    doc.refresh_from_db()
    assert doc.lines.count() == 1 and doc.lines.get().product_id == other.pk
    assert doc.total == (30000 if kind == "purchase" else 60000)
    assert not Movement.objects.exists()


@pytest.mark.parametrize("kind", ["purchase", "sale"])
def test_delete_all_rows_shows_error_without_creating_document(signed_in, product, supplier, kind):
    data = payload(kind, supplier, product)
    data["lines-1-DELETE"] = "on"
    response = signed_in.post(f"/documents/{kind}/new/", data)
    assert response.status_code == 200
    assert "Mỗi chứng từ cần từ 1 đến 100 sản phẩm." in response.content.decode()
    assert not Document.objects.exists()


@pytest.mark.parametrize("kind", ["purchase", "sale"])
def test_delete_control_is_hidden_and_x_button_is_in_html(signed_in, kind):
    response = signed_in.get(f"/documents/{kind}/new/")
    html = response.content.decode()
    assert response.context["lines"].forms[0].fields["DELETE"].widget.is_hidden
    assert "Bỏ dòng" not in html
    assert 'type="checkbox"' not in html
    assert "data-remove-line" in html and "×" in html
