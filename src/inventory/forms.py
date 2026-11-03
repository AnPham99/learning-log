from django import forms

from catalog.models import Product
from common.forms import StyledFormMixin


class AdjustmentForm(StyledFormMixin, forms.Form):
    product = forms.ModelChoiceField(label="Sản phẩm", queryset=Product.objects.all())
    quantity = forms.IntegerField(
        label="Chênh lệch số lượng (+ nhập thêm / − xuất bớt)",
        min_value=-1000000,
        max_value=1000000,
    )
    unit_cost = forms.DecimalField(
        label="Đơn giá vốn khi tăng tồn (₫)",
        decimal_places=0,
        max_digits=14,
        min_value=0,
        initial=0,
    )
    reason = forms.CharField(label="Lý do điều chỉnh", max_length=250)
