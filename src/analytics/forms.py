"""Khoảng ngày cho dashboard: giờ Việt Nam, đúng thứ tự và tối đa 366 ngày."""

from datetime import timedelta

from django import forms
from django.utils import timezone

from common.forms import StyledFormMixin


class DateFilter(StyledFormMixin, forms.Form):
    start = forms.DateField(label="Từ ngày", widget=forms.DateInput(attrs={"type": "date"}))
    end = forms.DateField(label="Đến ngày", widget=forms.DateInput(attrs={"type": "date"}))

    def clean(self):
        data = super().clean()
        if data.get("start") and data.get("end"):
            if data["end"] < data["start"] or (data["end"] - data["start"]).days > 365:
                raise forms.ValidationError("Khoảng ngày phải đúng thứ tự và tối đa 366 ngày.")
        return data


def date_filter(request):
    today = timezone.localdate()
    defaults = {"start": (today - timedelta(days=13)).isoformat(), "end": today.isoformat()}
    return DateFilter(request.GET if ("start" in request.GET or "end" in request.GET) else defaults)
