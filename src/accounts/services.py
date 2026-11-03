"""Tạo quản lý đầu tiên và nhân viên qua Django Auth; không xử lý HTTP."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import connection, transaction

from common.exceptions import BusinessError

from .permissions import require_role


@transaction.atomic
def create_owner(*, username, password, first_name=""):
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_xact_lock(734008119)")
    if get_user_model().objects.exists():
        raise BusinessError("Cửa hàng đã được thiết lập. Hãy đăng nhập.")
    return get_user_model().objects.create_superuser(
        username=username, password=password, first_name=first_name
    )


@transaction.atomic
def create_staff(*, actor, username, password, first_name, role):
    require_role(actor, "manager")
    if role not in ["manager", "warehouse", "sales"]:
        raise BusinessError("Vai trò không hợp lệ.")
    user = get_user_model().objects.create_user(
        username=username, password=password, first_name=first_name
    )
    group, _ = Group.objects.get_or_create(name=role)
    user.groups.add(group)
    return user
