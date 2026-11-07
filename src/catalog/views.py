from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from accounts.permissions import require_role, roles_required
from common.pagination import paginate, search_term

from .forms import ContactForm, ProductForm
from .models import Contact, Product
from .services import save_contact, save_product


@roles_required("manager", "warehouse", "sales")
@require_GET
def products(request):
    query = search_term(request)
    rows = Product.objects.select_related("stock")
    if query:
        rows = rows.filter(
            Q(sku__icontains=query) | Q(name__icontains=query) | Q(category__icontains=query)
        )
    return render(
        request,
        "catalog/products.html",
        {"page": paginate(request, rows), "query": query, "nav": "products"},
    )


@roles_required("manager")
@require_http_methods(["GET", "POST"])
def product_edit(request, pk=None):
    instance = get_object_or_404(Product, pk=pk) if pk else None
    form = ProductForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        save_product(actor=request.user, data=form.cleaned_data, instance=instance)
        messages.success(request, "Đã lưu sản phẩm.")
        return redirect("products")
    return render(
        request,
        "generic_form.html",
        {
            "form": form,
            "title": "Sửa sản phẩm" if pk else "Thêm sản phẩm",
            "back": "products",
            "nav": "products",
        },
    )


def contact_kind(request, kind):
    if kind not in Contact.Kind.values:
        raise Http404
    require_role(request.user, "manager", "warehouse" if kind == "supplier" else "sales")
    return "Nhà cung cấp" if kind == "supplier" else "Khách hàng"


@login_required
@require_GET
def contacts(request, kind):
    title = contact_kind(request, kind)
    query = search_term(request)
    rows = Contact.objects.filter(kind=kind)
    if query:
        rows = rows.filter(Q(name__icontains=query) | Q(phone__icontains=query))
    return render(
        request,
        "catalog/contacts.html",
        {
            "page": paginate(request, rows),
            "query": query,
            "kind": kind,
            "title": title,
            "nav": kind,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def contact_edit(request, kind, pk=None):
    title = contact_kind(request, kind)
    instance = get_object_or_404(Contact, pk=pk, kind=kind) if pk else None
    form = ContactForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        save_contact(actor=request.user, kind=kind, data=form.cleaned_data, instance=instance)
        messages.success(request, "Đã lưu thông tin đối tác.")
        return redirect("contacts", kind=kind)
    return render(
        request,
        "catalog/contact_form.html",
        {"form": form, "kind": kind, "title": title, "nav": kind},
    )
