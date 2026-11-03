import uuid

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from catalog.models import Product
from trading.models import Document
from trading.services import confirm_document

from .helpers import receipt

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "url",
    [
        "/",
        "/products/",
        "/stock/",
        "/stock/ledger/",
        "/contacts/customer/",
        "/contacts/supplier/",
        "/documents/purchase/",
        "/documents/sale/",
        "/staff/",
        "/dashboard/data/",
    ],
)
def test_manager_pages_render(signed_in, product, supplier, url):
    response = signed_in.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize(
    "url",
    [
        "/products/new/",
        "/stock/adjust/",
        "/contacts/customer/new/",
        "/contacts/supplier/new/",
        "/documents/sale/new/",
        "/documents/purchase/new/",
    ],
)
def test_create_forms_render(signed_in, url):
    assert signed_in.get(url).status_code == 200


@pytest.mark.parametrize(
    "url", ["/products/", "/stock/", "/documents/sale/", "/staff/", "/dashboard/data/"]
)
def test_anonymous_redirect(client, manager, url):
    assert client.get(url).status_code == 302


def test_role_http_and_json(seller, warehouse, client):
    client.force_login(seller)
    for url in ["/stock/", "/documents/purchase/", "/products/new/", "/staff/", "/dashboard/data/"]:
        assert client.get(url).status_code == 403
    client.force_login(warehouse)
    for url in ["/documents/sale/", "/contacts/customer/", "/staff/", "/dashboard/data/"]:
        assert client.get(url).status_code == 403
    assert client.get("/products/").status_code == 200


def test_setup_once_and_csrf(client):
    assert client.get("/").url == "/setup/"
    response = client.post(
        "/setup/",
        {
            "username": "firstowner",
            "first_name": "An",
            "password1": "Strong-setup-99!test",
            "password2": "Strong-setup-99!test",
        },
    )
    assert response.status_code == 302
    assert get_user_model().objects.get().is_superuser
    assert client.get("/setup/").status_code == 302
    secure = Client(enforce_csrf_checks=True)
    secure.force_login(get_user_model().objects.get())
    assert secure.post("/products/new/", {}).status_code == 403


def test_sales_form_confirm_and_csrf(signed_in, manager, product, supplier):
    incoming = receipt(manager, product, supplier)
    confirm_document(actor=manager, document_id=incoming.pk)
    data = {
        "request_key": str(uuid.uuid4()),
        "contact": "",
        "discount": "5000",
        "payment_method": "bank",
        "lines-TOTAL_FORMS": "1",
        "lines-INITIAL_FORMS": "0",
        "lines-0-product": str(product.pk),
        "lines-0-quantity": "2",
        "lines-0-unit_price": "",
        "note": "",
    }
    response = signed_in.post("/documents/sale/new/", data)
    assert response.status_code == 302
    order = Document.objects.get(kind="sale")
    assert signed_in.get(response.url).status_code == 200
    assert signed_in.post(response.url, {"action": "confirm"}).status_code == 302
    order.refresh_from_db()
    assert order.status == "confirmed" and order.total == 95000
    assert signed_in.get(f"/documents/sale/{order.pk}/edit/").status_code == 302
    secure = Client(enforce_csrf_checks=True)
    secure.force_login(manager)
    assert secure.post(response.url, {"action": "reverse", "reason": "x"}).status_code == 403


def test_search_and_product_edit(signed_in, product):
    assert signed_in.get("/products/?q=SKU-001").context["page"].paginator.count == 1
    assert signed_in.get("/products/?q=missing").context["page"].paginator.count == 0
    data = {
        "sku": product.sku,
        "name": "<script>alert(1)</script>",
        "category": "Books",
        "unit": "cái",
        "selling_price": "1000",
        "reorder_level": "2",
        "active": "on",
    }
    assert signed_in.post(f"/products/{product.pk}/edit/", data).status_code == 302
    response = signed_in.get("/products/")
    assert b"&lt;script&gt;" in response.content
    assert b"<script>alert(1)</script>" not in response.content
    assert Product.objects.get(pk=product.pk).selling_price == 1000


def test_empty_invalid_forms_and_missing(signed_in):
    assert signed_in.post("/documents/sale/new/", {}).status_code == 200
    assert signed_in.get("/document/999999/").status_code == 404
    assert signed_in.get("/contacts/invalid/").status_code == 404
    assert signed_in.get("/logout/").status_code == 405


def test_purchase_form_has_valid_hidden_defaults(signed_in, product, supplier):
    response = signed_in.get("/documents/purchase/new/")
    assert response.context["form"]["payment_method"].value() == "cash"
    token = response.context["form"]["request_key"].value()
    data = {
        "request_key": str(token),
        "contact": str(supplier.pk),
        "discount": "0",
        "payment_method": "cash",
        "note": "",
        "lines-TOTAL_FORMS": "1",
        "lines-INITIAL_FORMS": "0",
        "lines-0-product": str(product.pk),
        "lines-0-quantity": "3",
        "lines-0-unit_price": "10000",
    }
    saved = signed_in.post("/documents/purchase/new/", data)
    assert saved.status_code == 302
    assert Document.objects.get().total == 30000
