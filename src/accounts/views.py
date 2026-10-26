from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from . import services
from .forms import LoginForm, RegistrationForm


class SignInView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm


@require_http_methods(["GET", "POST"])
def register(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("journal:topic_list")
    form = RegistrationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            user = services.register_user(
                username=form.cleaned_data["username"], password=form.cleaned_data["password1"]
            )
        except ValidationError as error:
            form.add_error(None, error)
        else:
            login(request, user)
            messages.success(request, "Chào mừng bạn! Hãy bắt đầu với chủ đề đầu tiên.")
            return redirect("journal:topic_list")
    return render(request, "accounts/register.html", {"form": form})
