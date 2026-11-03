import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from django.contrib.auth import get_user_model
from django.db import connections

from common.exceptions import BusinessError
from inventory.models import Movement, Stock
from trading.models import Document
from trading.services import confirm_document, save_draft

from .helpers import receipt, sale

pytestmark = pytest.mark.django_db(transaction=True)


def run_concurrently(actor_id, actions):
    barrier = Barrier(2)

    def worker(action):
        connections.close_all()
        try:
            actor = get_user_model().objects.get(pk=actor_id)
            with connections["default"].cursor() as cursor:
                cursor.execute("SET statement_timeout = '8s'")
            barrier.wait(timeout=5)
            try:
                return action(actor)
            except BusinessError:
                return "rejected"
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(worker, action) for action in actions]
        return [f.result(timeout=12) for f in futures]


def test_concurrent_sales_cannot_oversell(manager, product, supplier):
    incoming = receipt(manager, product, supplier, 5)
    confirm_document(actor=manager, document_id=incoming.pk)
    orders = [sale(manager, product, 4), sale(manager, product, 4)]
    actions = [
        lambda actor, pk=order.pk: confirm_document(actor=actor, document_id=pk).status
        for order in orders
    ]
    result = run_concurrently(manager.pk, actions)
    assert sorted(result) == ["confirmed", "rejected"]
    assert Stock.objects.get(product=product).quantity == 1
    assert Document.objects.filter(kind="sale", status="confirmed").count() == 1


def test_concurrent_confirm_only_once(manager, product, supplier):
    incoming = receipt(manager, product, supplier)

    def action(actor):
        return confirm_document(actor=actor, document_id=incoming.pk).status

    assert run_concurrently(manager.pk, [action, action]) == ["confirmed", "confirmed"]
    assert Stock.objects.get(product=product).quantity == 10
    assert Movement.objects.count() == 1


def test_concurrent_draft_request_only_once(manager, product):
    key = uuid.uuid4()

    def action(actor):
        return save_draft(
            actor=actor,
            kind="sale",
            request_key=key,
            items=[{"product_id": product.pk, "quantity": 1}],
        ).pk

    result = run_concurrently(manager.pk, [action, action])
    assert result[0] == result[1]
    assert Document.objects.count() == 1
