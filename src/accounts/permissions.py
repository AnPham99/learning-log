"""Quyền theo vai trò. Decorator bảo vệ HTTP; require_role bảo vệ service."""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

ROLES = [("manager", "Quản lý"), ("warehouse", "Nhân viên kho"), ("sales", "Nhân viên bán hàng")]


def has_role(user, *roles):
    return (
        user.is_authenticated
        and user.is_active
        and (user.is_superuser or user.groups.filter(name__in=roles).exists())
    )


def require_role(user, *roles):
    if not has_role(user, *roles):
        raise PermissionDenied("Bạn không có quyền thực hiện thao tác này.")


def roles_required(*roles):
    def decorate(view):
        @login_required
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            require_role(request.user, *roles)
            return view(request, *args, **kwargs)

        return wrapped

    return decorate
