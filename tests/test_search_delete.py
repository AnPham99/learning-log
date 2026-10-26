import pytest
from django.test import Client
from django.urls import reverse

from journal import selectors, services
from journal.exceptions import JournalNotFound
from journal.models import Entry, Topic

pytestmark = pytest.mark.django_db


def test_search_by_title_or_entry_preserves_counts_and_privacy(user, other_user, signed_in):
    topic = services.create_topic(owner_id=user.pk, text="Python")
    services.create_entry(owner_id=user.pk, topic_id=topic.pk, text="Django forms")
    services.create_entry(owner_id=user.pk, topic_id=topic.pk, text="Django views")
    services.create_entry(owner_id=user.pk, topic_id=topic.pk, text="Unrelated")
    hidden = services.create_topic(owner_id=other_user.pk, text="Django private")
    for query in [" django ", "Python"]:
        response = signed_in.get(reverse("journal:topic_list"), {"q": query})
        assert response.status_code == 200
        results = list(response.context["topics"])
        assert [item.pk for item in results] == [topic.pk]
        assert results[0].entry_count == 3
        assert hidden.text not in response.content.decode()
    response = signed_in.get(reverse("journal:topic_list"), {"q": "absent"})
    assert "Không tìm thấy" in response.content.decode()


def test_search_entries_within_topic(user, signed_in):
    topic = services.create_topic(owner_id=user.pk, text="Python")
    match = services.create_entry(owner_id=user.pk, topic_id=topic.pk, text="Django forms")
    services.create_entry(owner_id=user.pk, topic_id=topic.pk, text="Other")
    url = reverse("journal:topic_detail", args=[topic.pk])
    response = signed_in.get(url, {"q": " forms "})
    assert list(response.context["entries"]) == [match]
    assert signed_in.get(url, {"q": "missing"}).status_code == 200
    assert len(signed_in.get(url).context["entries"]) == 2


@pytest.mark.parametrize("kind", ["topic", "entry"])
def test_delete_confirmation_then_post(user, signed_in, kind):
    topic = services.create_topic(owner_id=user.pk, text="Python")
    entry = services.create_entry(owner_id=user.pk, topic_id=topic.pk, text="Note")
    obj = topic if kind == "topic" else entry
    url = reverse(f"journal:{kind}_delete", args=[obj.pk])
    assert signed_in.get(url).status_code == 200
    assert Entry.objects.filter(pk=entry.pk).exists()
    assert signed_in.post(url).status_code == 302
    assert not Entry.objects.filter(pk=entry.pk).exists()
    assert Topic.objects.filter(pk=topic.pk).exists() == (kind == "entry")
    assert signed_in.post(url).status_code == 404


@pytest.mark.parametrize("kind", ["topic", "entry"])
def test_delete_authorization_csrf_and_methods(user, other_user, signed_in, kind):
    topic = services.create_topic(owner_id=other_user.pk, text="Private")
    entry = services.create_entry(owner_id=other_user.pk, topic_id=topic.pk, text="Private")
    obj = topic if kind == "topic" else entry
    url = reverse(f"journal:{kind}_delete", args=[obj.pk])
    assert signed_in.get(url).status_code == 404
    assert signed_in.post(url).status_code == 404
    with pytest.raises(JournalNotFound):
        getattr(services, f"delete_{kind}")(**{"owner_id": user.pk, f"{kind}_id": obj.pk})
    assert Client().post(url).status_code == 302
    secure = Client(enforce_csrf_checks=True)
    secure.force_login(other_user)
    assert secure.post(url).status_code == 403
    assert secure.put(url).status_code == 403
    signed_in.force_login(other_user)
    assert signed_in.put(url).status_code == 405
    assert Entry.objects.filter(pk=entry.pk).exists()
    assert list(selectors.topics_for_user(owner_id=user.pk, query="Private")) == []
