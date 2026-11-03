"""Phân trang và chuẩn hóa từ khóa dùng chung cho các danh sách."""

from django.core.paginator import Paginator


def paginate(request, queryset):
    return Paginator(queryset, 20).get_page(request.GET.get("page"))


def search_term(request):
    return request.GET.get("q", "").strip()[:200]
