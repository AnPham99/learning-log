"""Adapter HTTP: đọc form, gọi trading service, hiển thị kết quả và chuyển trang."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from common.exceptions import BusinessError
from common.pagination import paginate, search_term

from .forms import DocumentForm, LineFormSet, ReversalForm
from .models import Document
from .services import authorize, confirm_document, reverse_document, save_draft


@login_required
@require_GET
def document_list(request, kind):
    if kind not in Document.Kind.values:
        raise Http404
    authorize(request.user, kind)
    query = search_term(request)
    rows = Document.objects.filter(kind=kind).select_related("contact", "created_by")
    if query:
        condition = Q(contact_name__icontains=query) | Q(note__icontains=query)
        numeric = query.removeprefix("PN-").removeprefix("BH-")
        if numeric.isdigit():
            condition |= Q(pk=int(numeric))
        rows = rows.filter(condition)
    if request.GET.get("status") in Document.Status.values:
        rows = rows.filter(status=request.GET["status"])
    return render(
        request,
        "trading/list.html",
        {
            "page": paginate(request, rows),
            "kind": kind,
            "title": "Phiếu nhập kho" if kind == "purchase" else "Đơn bán hàng",
            "query": query,
            "nav": kind,
            "statuses": Document.Status.choices,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def document_edit(request, kind, pk=None):
    if kind not in Document.Kind.values:
        raise Http404
    authorize(request.user, kind)
    doc = get_object_or_404(Document, pk=pk, kind=kind) if pk else None
    if doc and doc.status != "draft":
        messages.error(request, "Chỉ được sửa chứng từ nháp.")
        return redirect("document", pk=pk)
    initial = (
        {
            "request_key": doc.request_key,
            "contact": doc.contact_id,
            "discount": doc.discount,
            "payment_method": doc.payment_method,
            "note": doc.note,
        }
        if doc
        else {}
    )
    form = DocumentForm(
        request.POST if request.method == "POST" else None, kind=kind, initial=initial
    )
    initial_lines = (
        [
            {"product": line.product_id, "quantity": line.quantity, "unit_price": line.unit_price}
            for line in doc.lines.all()
        ]
        if doc
        else []
    )
    lines = LineFormSet(
        request.POST if request.method == "POST" else None, prefix="lines", initial=initial_lines
    )
    if request.method == "POST":
        valid = form.is_valid() & lines.is_valid()
        if valid:
            items = []
            for row in lines.cleaned_data:
                if row and not row.get("DELETE"):
                    if kind == "purchase" and row.get("unit_price") is None:
                        form.add_error(None, "Nhập đơn giá cho mọi dòng sản phẩm.")
                        valid = False
                        break
                    items.append(
                        {
                            "product_id": row["product"].pk,
                            "quantity": row["quantity"],
                            "unit_price": row.get("unit_price"),
                        }
                    )
            if valid:
                try:
                    contact = form.cleaned_data["contact"]
                    doc = save_draft(
                        actor=request.user,
                        kind=kind,
                        items=items,
                        request_key=form.cleaned_data["request_key"],
                        contact_id=contact.pk if contact else None,
                        discount=form.cleaned_data["discount"],
                        payment_method=form.cleaned_data["payment_method"],
                        note=form.cleaned_data["note"],
                        document_id=pk,
                    )
                except (BusinessError, ValidationError) as error:
                    form.add_error(
                        None,
                        "; ".join(error.messages)
                        if isinstance(error, ValidationError)
                        else str(error),
                    )
                else:
                    messages.success(
                        request, "Đã lưu nháp. Kiểm tra rồi xác nhận để cập nhật tồn kho."
                    )
                    return redirect("document", pk=doc.pk)
    return render(
        request,
        "trading/form.html",
        {
            "form": form,
            "lines": lines,
            "kind": kind,
            "doc": doc,
            "title": "Phiếu nhập" if kind == "purchase" else "Đơn bán",
            "nav": kind,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def document_detail(request, pk):
    doc = get_object_or_404(
        Document.objects.select_related("contact", "created_by").prefetch_related("lines"), pk=pk
    )
    authorize(request.user, doc.kind)
    form = ReversalForm(request.POST if request.method == "POST" else None)
    if request.method == "POST":
        try:
            if request.POST.get("action") == "confirm":
                confirm_document(actor=request.user, document_id=pk)
                messages.success(request, "Đã xác nhận và cập nhật tồn kho.")
            elif request.POST.get("action") == "reverse" and form.is_valid():
                reverse_document(
                    actor=request.user, document_id=pk, reason=form.cleaned_data["reason"]
                )
                messages.success(request, "Đã hủy / hoàn chứng từ.")
            else:
                raise BusinessError("Chọn thao tác hợp lệ và nhập lý do.")
        except BusinessError as error:
            messages.error(request, str(error))
        return redirect("document", pk=pk)
    return render(request, "trading/detail.html", {"doc": doc, "form": form, "nav": doc.kind})
