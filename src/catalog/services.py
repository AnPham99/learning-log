from django.db import transaction

from accounts.permissions import require_role
from common.exceptions import BusinessError
from inventory.models import Stock

from .models import Contact, Product


@transaction.atomic
def save_product(*, actor, data, instance=None):
    require_role(actor, "manager")
    product = instance or Product()
    for field in ["sku", "name", "category", "unit", "selling_price", "reorder_level", "active"]:
        setattr(product, field, data[field])
    product.full_clean()
    product.save()
    Stock.objects.get_or_create(product=product)
    return product


@transaction.atomic
def save_contact(*, actor, kind, data, instance=None):
    if kind not in Contact.Kind.values or (instance is not None and instance.kind != kind):
        raise BusinessError("Loại đối tác không hợp lệ.")
    require_role(actor, "manager", "warehouse" if kind == "supplier" else "sales")
    contact = instance or Contact(kind=kind)
    for field in ["name", "phone", "email", "address", "active"]:
        setattr(contact, field, data[field])
    contact.full_clean()
    contact.save()
    return contact
