from accounts.permissions import has_role


def navigation(request):
    return {
        "can_manage": has_role(request.user, "manager"),
        "can_stock": has_role(request.user, "manager", "warehouse"),
        "can_sell": has_role(request.user, "manager", "sales"),
    }
