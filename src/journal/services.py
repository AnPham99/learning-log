"""Validated journal commands. Ownership is checked before every entry write."""

from django.db import transaction

from . import selectors
from .models import Entry, Topic


@transaction.atomic
def create_topic(*, owner_id: int, text: str) -> Topic:
    topic = Topic(owner_id=owner_id, text=text.strip())
    topic.full_clean()
    topic.save()
    return topic


@transaction.atomic
def create_entry(*, owner_id: int, topic_id: int, text: str) -> Entry:
    topic = selectors.topic_for_user(owner_id=owner_id, topic_id=topic_id)
    entry = Entry(topic=topic, text=text.strip())
    entry.full_clean()
    entry.save()
    return entry


@transaction.atomic
def update_entry(*, owner_id: int, entry_id: int, text: str) -> Entry:
    entry = selectors.entry_for_user(owner_id=owner_id, entry_id=entry_id)
    entry.text = text.strip()
    entry.full_clean()
    entry.save(update_fields=["text", "updated_at"])
    return entry


@transaction.atomic
def delete_topic(*, owner_id: int, topic_id: int) -> None:
    topic = selectors.topic_for_user(owner_id=owner_id, topic_id=topic_id)
    topic.delete()


@transaction.atomic
def delete_entry(*, owner_id: int, entry_id: int) -> None:
    entry = selectors.entry_for_user(owner_id=owner_id, entry_id=entry_id)
    entry.delete()
