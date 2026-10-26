import pytest
from django.core.exceptions import ValidationError

from journal import selectors, services
from journal.exceptions import JournalNotFound
from journal.models import Entry, Topic

pytestmark = pytest.mark.django_db


def test_commands_validate_even_without_a_web_form(user):
    with pytest.raises(ValidationError):
        services.create_topic(owner_id=user.pk, text=" ")
    topic = services.create_topic(owner_id=user.pk, text=" Python ")
    with pytest.raises(ValidationError):
        services.create_entry(owner_id=user.pk, topic_id=topic.pk, text=" ")
    entry = services.create_entry(owner_id=user.pk, topic_id=topic.pk, text=" Original ")
    with pytest.raises(ValidationError):
        services.update_entry(owner_id=user.pk, entry_id=entry.pk, text=" ")
    entry.refresh_from_db()
    assert entry.text == "Original"


def test_write_service_cannot_bypass_ownership(user, other_user):
    topic = Topic.objects.create(owner=other_user, text="Private")
    entry = Entry.objects.create(topic=topic, text="Secret")
    with pytest.raises(JournalNotFound):
        services.create_entry(owner_id=user.pk, topic_id=topic.pk, text="Wrong owner")
    with pytest.raises(JournalNotFound):
        services.update_entry(owner_id=user.pk, entry_id=entry.pk, text="Wrong owner")
    entry.refresh_from_db()
    assert entry.text == "Secret"


def test_summary_excludes_other_accounts(user, other_user):
    topic = Topic.objects.create(owner=user, text="Mine")
    Entry.objects.create(topic=topic, text="One")
    other = Topic.objects.create(owner=other_user, text="Other")
    Entry.objects.create(topic=other, text="Hidden")
    summary = selectors.summary_for_user(owner_id=user.pk)
    assert summary["topic_count"] == 1
    assert summary["entry_count"] == 1
    assert summary["last_entry_at"] is not None


def test_topic_and_entry_strings_are_readable(user):
    topic = Topic(owner=user, text="Python")
    entry = Entry(topic=topic, text="A" * 120)
    assert str(topic) == "Python"
    assert str(entry) == "A" * 80


def test_dashboard_topics_are_newest_first_after_annotation(user):
    old = Topic.objects.create(owner=user, text="First")
    new = Topic.objects.create(owner=user, text="Newest")
    topics = list(selectors.topics_for_user(owner_id=user.pk))
    assert topics == [new, old]


def test_account_service_enforces_password_and_unique_username(user):
    from accounts.services import register_user

    with pytest.raises(ValidationError):
        register_user(username="new", password="123")
    with pytest.raises(ValidationError):
        register_user(username=user.username, password="Different-strong-pass-49!")
