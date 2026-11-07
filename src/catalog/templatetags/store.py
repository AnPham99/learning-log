from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def staff_role(user):
    if user.is_superuser:
        return "Quản lý"
    labels = {"manager": "Quản lý", "warehouse": "Nhân viên kho", "sales": "Bán hàng"}
    return (
        " / ".join(labels[group.name] for group in user.groups.all() if group.name in labels)
        or "Nhân viên"
    )


@register.filter
def vnd(value):
    if value is None:
        return "0"
    return f"{Decimal(value):,.0f}".replace(",", ".")


@register.filter
def average(stock):
    return stock.value / stock.quantity if stock.quantity else 0
