"""Kiểm tra thông tin tài khoản, mật khẩu và vai trò trước khi gọi service."""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from common.forms import StyledFormMixin

from .permissions import ROLES


class LoginForm(StyledFormMixin, AuthenticationForm):
    pass


class SetupForm(StyledFormMixin, UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "first_name"]
        labels = {"first_name": "Tên hiển thị"}


class StaffForm(SetupForm):
    role = forms.ChoiceField(label="Vai trò", choices=ROLES)
