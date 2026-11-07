from django.contrib import messages
from django.db.models import F, Q
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from accounts.permissions import roles_required
from common.exceptions import BusinessError
from common.pagination import paginate, search_term

from .forms import AdjustmentForm
from .models import Movement, Stock
from .services import adjust_stock


@roles_required("manager", "warehouse")
@require_GET
def stock_list(request):
    query = search_term(request)
    rows = Stock.objects.select_related("product").order_by("product__name", "product_id")
    if query:
        rows = rows.filter(Q(product__name__icontains=query) | Q(product__sku__icontains=query))
    if request.GET.get("low") == "1":
        rows = rows.filter(quantity__lte=F("product__reorder_level"), product__active=True)
    return render(
        request,
        "inventory/stock.html",
        {"page": paginate(request, rows), "query": query, "nav": "stock"},
    )


@roles_required("manager", "warehouse")
@require_GET
def ledger(request):
    query = search_term(request)
    rows = Movement.objects.select_related("product", "actor", "document")
    if query:
        rows = rows.filter(
            Q(product__sku__icontains=query)
            | Q(product__name__icontains=query)
            | Q(reason__icontains=query)
        )
    return render(
        request,
        "inventory/ledger.html",
        {"page": paginate(request, rows), "query": query, "nav": "ledger"},
    )


@roles_required("manager")
@require_http_methods(["GET", "POST"])
def adjustment(request):
    form = AdjustmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            adjust_stock(
                actor=request.user,
                product_id=form.cleaned_data["product"].pk,
                quantity=form.cleaned_data["quantity"],
                reason=form.cleaned_data["reason"],
                unit_cost=form.cleaned_data["unit_cost"],
            )
        except BusinessError as error:
            form.add_error(None, str(error))
        else:
            messages.success(request, "Đã điều chỉnh tồn kho và ghi sổ kho.")
            return redirect("stock")
    return render(
        request,
        "generic_form.html",
        {"form": form, "title": "Điều chỉnh tồn kho", "back": "stock", "nav": "stock"},
    )
