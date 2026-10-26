from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from journal import selectors, services
from journal.forms import EntryForm

from .errors import resource_errors


@login_required
@require_http_methods(["GET", "POST"])
@resource_errors
def entry_create(request: HttpRequest, topic_id: int) -> HttpResponse:
    topic = selectors.topic_for_user(owner_id=request.user.pk, topic_id=topic_id)
    form = EntryForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        services.create_entry(
            owner_id=request.user.pk, topic_id=topic_id, text=form.cleaned_data["text"]
        )
        messages.success(request, "Đã lưu ghi chép mới.")
        return redirect("journal:topic_detail", topic_id=topic_id)
    return render(request, "journal/entry_form.html", {"form": form, "topic": topic})


@login_required
@require_http_methods(["GET", "POST"])
@resource_errors
def entry_edit(request: HttpRequest, entry_id: int) -> HttpResponse:
    entry = selectors.entry_for_user(owner_id=request.user.pk, entry_id=entry_id)
    form = EntryForm(
        request.POST if request.method == "POST" else None, initial={"text": entry.text}
    )
    if request.method == "POST" and form.is_valid():
        services.update_entry(
            owner_id=request.user.pk, entry_id=entry_id, text=form.cleaned_data["text"]
        )
        messages.success(request, "Đã cập nhật ghi chép.")
        return redirect("journal:topic_detail", topic_id=entry.topic_id)
    return render(
        request,
        "journal/entry_form.html",
        {
            "form": form,
            "topic": entry.topic,
            "entry": entry,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
@resource_errors
def entry_delete(request: HttpRequest, entry_id: int) -> HttpResponse:
    entry = selectors.entry_for_user(owner_id=request.user.pk, entry_id=entry_id)
    if request.method == "POST":
        services.delete_entry(owner_id=request.user.pk, entry_id=entry_id)
        messages.success(request, "Đã xóa ghi chép.")
        return redirect("journal:topic_detail", topic_id=entry.topic_id)
    return render(request, "journal/delete_confirm.html", {"topic": entry.topic, "entry": entry})
