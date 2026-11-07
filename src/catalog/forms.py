from django import forms

from common.forms import StyledFormMixin

from .models import Contact, Product


class ProductForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = ["sku", "name", "category", "unit", "selling_price", "reorder_level", "active"]


class ContactForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["name", "phone", "email", "address", "active"]
