from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from journal import selectors, services
from journal.forms import TopicForm

from .errors import resource_errors


@login_required
@require_GET
def topic_list(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "").strip()
    context = {
        "query": query,
        "topics": selectors.topics_for_user(owner_id=request.user.pk, query=query),
        "summary": selectors.summary_for_user(owner_id=request.user.pk),
        "active_nav": "topics",
    }
    return render(request, "journal/topic_list.html", context)


@login_required
@require_GET
@resource_errors
def topic_detail(request: HttpRequest, topic_id: int) -> HttpResponse:
    topic = selectors.topic_for_user(owner_id=request.user.pk, topic_id=topic_id)
    query = request.GET.get("q", "").strip()
    entries = selectors.entries_for_topic(owner_id=request.user.pk, topic_id=topic_id, query=query)
    return render(
        request,
        "journal/topic_detail.html",
        {
            "topic": topic,
            "entries": entries,
            "query": query,
            "active_nav": "topics",
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def topic_create(request: HttpRequest) -> HttpResponse:
    form = TopicForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        topic = services.create_topic(owner_id=request.user.pk, text=form.cleaned_data["text"])
        messages.success(request, "Đã tạo chủ đề. Bạn có thể thêm ghi chép đầu tiên.")
        return redirect("journal:topic_detail", topic_id=topic.pk)
    return render(request, "journal/topic_form.html", {"form": form, "active_nav": "new"})


@login_required
@require_http_methods(["GET", "POST"])
@resource_errors
def topic_delete(request: HttpRequest, topic_id: int) -> HttpResponse:
    topic = selectors.topic_for_user(owner_id=request.user.pk, topic_id=topic_id)
    if request.method == "POST":
        services.delete_topic(owner_id=request.user.pk, topic_id=topic_id)
        messages.success(request, "Đã xóa chủ đề và các ghi chép bên trong.")
        return redirect("journal:topic_list")
    entries = selectors.entries_for_topic(owner_id=request.user.pk, topic_id=topic_id)
    return render(
        request,
        "journal/delete_confirm.html",
        {
            "topic": topic,
            "entry_count": entries.count(),
        },
    )
