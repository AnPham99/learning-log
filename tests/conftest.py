import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from catalog.services import save_contact, save_product


@pytest.fixture
def manager(db):
    return get_user_model().objects.create_superuser(
        username="owner", password="Test-only-38!secure"
    )


@pytest.fixture
def warehouse(db):
    user = get_user_model().objects.create_user(
        username="warehouse", password="Test-only-38!secure"
    )
    group, _ = Group.objects.get_or_create(name="warehouse")
    user.groups.add(group)
    return user


@pytest.fixture
def seller(db):
    user = get_user_model().objects.create_user(username="seller", password="Test-only-38!secure")
    group, _ = Group.objects.get_or_create(name="sales")
    user.groups.add(group)
    return user


@pytest.fixture
def product(manager):
    return save_product(
        actor=manager,
        data={
            "sku": "SKU-001",
            "name": "Sổ tay",
            "category": "Văn phòng phẩm",
            "unit": "quyển",
            "selling_price": 50000,
            "reorder_level": 5,
            "active": True,
        },
    )


@pytest.fixture
def supplier(manager):
    return save_contact(
        actor=manager,
        kind="supplier",
        data={
            "name": "Nhà cung cấp A",
            "phone": "0900000000",
            "email": "",
            "address": "",
            "active": True,
        },
    )


@pytest.fixture
def signed_in(client, manager):
    client.force_login(manager)
    return client
