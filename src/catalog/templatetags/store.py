from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def vnd(value):
    if value is None:
        return "0"
    return f"{Decimal(value):,.0f}".replace(",", ".")


@register.filter
def average(stock):
    return stock.value / stock.quantity if stock.quantity else 0
