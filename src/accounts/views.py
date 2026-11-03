"""HTTP cho thiết lập, đăng nhập và nhân viên; gọi service để tạo tài khoản."""

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from common.exceptions import BusinessError

from .forms import LoginForm, SetupForm, StaffForm
from .permissions import roles_required
from .services import create_owner, create_staff


class SignInView(LoginView):
    template_name = "registration/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if not get_user_model().objects.exists():
            return redirect("setup")
        return super().dispatch(request, *args, **kwargs)


@require_http_methods(["GET", "POST"])
def setup(request):
    if get_user_model().objects.exists():
        return redirect("login")
    form = SetupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            user = create_owner(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
                first_name=form.cleaned_data["first_name"],
            )
        except BusinessError as error:
            form.add_error(None, str(error))
        else:
            login(request, user)
            return redirect("home")
    return render(request, "registration/setup.html", {"form": form})


@roles_required("manager")
@require_http_methods(["GET", "POST"])
def staff(request):
    form = StaffForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        create_staff(
            actor=request.user,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password1"],
            first_name=form.cleaned_data["first_name"],
            role=form.cleaned_data["role"],
        )
        messages.success(request, "Đã tạo tài khoản nhân viên.")
        return redirect("staff")
    users = get_user_model().objects.prefetch_related("groups").order_by("username")
    return render(request, "accounts/staff.html", {"form": form, "staff": users})
