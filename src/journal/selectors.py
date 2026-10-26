"""Read queries. Every public query is scoped to the current owner."""

from django.db.models import Count, Max, Q, QuerySet

from .exceptions import JournalNotFound
from .models import Entry, Topic


def topic_for_user(*, owner_id: int, topic_id: int) -> Topic:
    try:
        return Topic.objects.get(pk=topic_id, owner_id=owner_id)
    except Topic.DoesNotExist as error:
        raise JournalNotFound from error


def entry_for_user(*, owner_id: int, entry_id: int) -> Entry:
    try:
        return Entry.objects.select_related("topic").get(pk=entry_id, topic__owner_id=owner_id)
    except Entry.DoesNotExist as error:
        raise JournalNotFound from error


def topics_for_user(*, owner_id: int, query: str = "") -> QuerySet[Topic]:
    topics = Topic.objects.filter(owner_id=owner_id)
    if query := query.strip():
        matching_entries = Entry.objects.filter(
            topic__owner_id=owner_id, text__icontains=query
        ).values("topic_id")
        topics = topics.filter(Q(text__icontains=query) | Q(pk__in=matching_entries))
    return topics.annotate(
        entry_count=Count("entries"), last_entry_at=Max("entries__date_added")
    ).order_by("-date_added", "-pk")


def entries_for_topic(*, owner_id: int, topic_id: int, query: str = "") -> QuerySet[Entry]:
    entries = Entry.objects.filter(topic_id=topic_id, topic__owner_id=owner_id)
    if query := query.strip():
        entries = entries.filter(text__icontains=query)
    return entries


def summary_for_user(*, owner_id: int) -> dict:
    summary = Entry.objects.filter(topic__owner_id=owner_id).aggregate(
        entry_count=Count("id"), last_entry_at=Max("date_added")
    )
    summary["topic_count"] = Topic.objects.filter(owner_id=owner_id).count()
    return summary
