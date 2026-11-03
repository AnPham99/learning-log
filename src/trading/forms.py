"""Kiểm tra phần đầu chứng từ và formset dòng hàng; chưa làm thay đổi tồn."""

import uuid

from django import forms
from django.forms import BaseFormSet, formset_factory

from catalog.models import Contact, Product
from common.forms import StyledFormMixin

from .models import Document


class DocumentForm(StyledFormMixin, forms.Form):
    request_key = forms.UUIDField(widget=forms.HiddenInput, initial=uuid.uuid4)
    contact = forms.ModelChoiceField(
        label="Đối tác", queryset=Contact.objects.none(), required=False, empty_label="Khách lẻ"
    )
    discount = forms.DecimalField(
        label="Giảm giá toàn đơn (₫)", decimal_places=0, max_digits=16, min_value=0, initial=0
    )
    payment_method = forms.ChoiceField(
        label="Phương thức thanh toán", choices=Document.Payment.choices, initial="cash"
    )
    note = forms.CharField(label="Ghi chú", max_length=250, required=False)

    def __init__(self, *args, kind, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contact"].queryset = Contact.objects.filter(
            kind="supplier" if kind == "purchase" else "customer", active=True
        )
        self.fields["contact"].label = "Nhà cung cấp" if kind == "purchase" else "Khách hàng"
        if kind == "purchase":
            self.fields["contact"].required = True
            self.fields["contact"].empty_label = "Chọn nhà cung cấp"
            self.fields["discount"].widget = forms.HiddenInput()
            self.fields["payment_method"].widget = forms.HiddenInput()


class LineForm(StyledFormMixin, forms.Form):
    product = forms.ModelChoiceField(
        label="Sản phẩm", queryset=Product.objects.filter(active=True), empty_label="Chọn sản phẩm"
    )
    quantity = forms.IntegerField(label="Số lượng", min_value=1, max_value=1000000)
    unit_price = forms.DecimalField(
        label="Đơn giá nhập (₫)", decimal_places=0, max_digits=14, min_value=0, required=False
    )


class BaseLineFormSet(BaseFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields["DELETE"].widget = forms.HiddenInput()


LineFormSet = formset_factory(
    LineForm,
    formset=BaseLineFormSet,
    extra=1,
    max_num=100,
    validate_max=True,
    absolute_max=101,
    can_delete=True,
)


class ReversalForm(StyledFormMixin, forms.Form):
    reason = forms.CharField(label="Lý do hủy / hoàn", max_length=250)
