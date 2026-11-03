"""Trang SSR tổng quan và JSON endpoint để dashboard tự lấy dữ liệu mỗi 10 giây."""

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from accounts.permissions import has_role, roles_required

from .forms import date_filter
from .selectors import dashboard


@require_GET
def home(request):
    if not get_user_model().objects.exists():
        return redirect("setup")
    if not request.user.is_authenticated:
        return redirect("login")
    if has_role(request.user, "manager"):
        return dashboard_page(request)
    if has_role(request.user, "warehouse"):
        return redirect("stock")
    if has_role(request.user, "sales"):
        return redirect("documents", kind="sale")
    return render(request, "403.html", status=403)


@roles_required("manager")
@never_cache
@require_GET
def dashboard_page(request):
    form = date_filter(request)
    data = dashboard(actor=request.user, **form.cleaned_data) if form.is_valid() else None
    return render(
        request, "analytics/dashboard.html", {"form": form, "data": data, "nav": "dashboard"}
    )


@roles_required("manager")
@never_cache
@require_GET
def dashboard_data(request):
    form = date_filter(request)
    if not form.is_valid():
        return JsonResponse({"error": "Khoảng ngày không hợp lệ."}, status=400)
    return JsonResponse(dashboard(actor=request.user, **form.cleaned_data))
