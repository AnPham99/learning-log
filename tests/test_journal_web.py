import pytest

pytestmark = pytest.mark.django_db


def journal_models():
    from journal.models import Entry, Topic

    return Topic, Entry


@pytest.mark.parametrize(
    "path",
    [
        "/topics/",
        "/topics/new/",
        "/topics/1/",
        "/topics/1/entries/new/",
        "/entries/1/edit/",
    ],
)
def test_anonymous_user_must_sign_in(client, path):
    response = client.get(path)
    assert response.status_code == 302
    assert response.url.startswith("/accounts/login/?next=")


def test_empty_dashboard_has_action(signed_in):
    response = signed_in.get("/topics/")
    assert response.status_code == 200
    assert "Tạo chủ đề đầu tiên" in response.content.decode()


def test_create_topic_sets_owner(signed_in, user):
    response = signed_in.post("/topics/new/", {"text": "  Python căn bản  "})
    assert response.status_code == 302
    Topic, _ = journal_models()
    topic = Topic.objects.get()
    assert topic.text == "Python căn bản"
    assert topic.owner == user
    assert response.url == f"/topics/{topic.pk}/"


@pytest.mark.parametrize("text", ["", "   ", "x" * 201])
def test_invalid_topic_is_not_saved(signed_in, text):
    response = signed_in.post("/topics/new/", {"text": text})
    assert response.status_code == 200
    assert response.context["form"].errors
    Topic, _ = journal_models()
    assert not Topic.objects.exists()


def test_dashboard_only_shows_own_topics(signed_in, user, other_user):
    Topic, _ = journal_models()
    Topic.objects.create(owner=user, text="My Python")
    Topic.objects.create(owner=other_user, text="Other secret topic")
    response = signed_in.get("/topics/")
    assert "My Python" in response.content.decode()
    assert "Other secret topic" not in response.content.decode()


def test_create_and_edit_entry(signed_in, user):
    Topic, Entry = journal_models()
    topic = Topic.objects.create(owner=user, text="Python")
    response = signed_in.post(f"/topics/{topic.pk}/entries/new/", {"text": "  Learned lists  "})
    assert response.url == f"/topics/{topic.pk}/"
    entry = Entry.objects.get()
    assert entry.topic == topic
    assert entry.text == "Learned lists"
    response = signed_in.get(f"/entries/{entry.pk}/edit/")
    assert response.context["form"].initial["text"] == "Learned lists"
    response = signed_in.post(f"/entries/{entry.pk}/edit/", {"text": "Updated learning"})
    assert response.url == f"/topics/{topic.pk}/"
    entry.refresh_from_db()
    assert entry.text == "Updated learning"


@pytest.mark.parametrize("method", ["get", "post"])
@pytest.mark.parametrize("route", ["topic", "create_entry", "edit_entry"])
def test_other_users_data_is_inaccessible(signed_in, other_user, method, route):
    Topic, Entry = journal_models()
    topic = Topic.objects.create(owner=other_user, text="Private topic")
    entry = Entry.objects.create(topic=topic, text="Private entry")
    paths = {
        "topic": f"/topics/{topic.pk}/",
        "create_entry": f"/topics/{topic.pk}/entries/new/",
        "edit_entry": f"/entries/{entry.pk}/edit/",
    }
    response = getattr(signed_in, method)(paths[route], {"text": "Attacker input"})
    # The read-only detail endpoint rejects POST before resolving any resource.
    expected_status = 405 if route == "topic" and method == "post" else 404
    assert response.status_code == expected_status
    entry.refresh_from_db()
    assert entry.text == "Private entry"
    assert Entry.objects.count() == 1


@pytest.mark.parametrize("path", ["/topics/999/", "/topics/999/entries/new/", "/entries/999/edit/"])
def test_nonexistent_resources_are_404(signed_in, path):
    assert signed_in.get(path).status_code == 404


def test_invalid_entry_keeps_existing_content(signed_in, user):
    Topic, Entry = journal_models()
    topic = Topic.objects.create(owner=user, text="Python")
    entry = Entry.objects.create(topic=topic, text="Original")
    assert signed_in.post(f"/topics/{topic.pk}/entries/new/", {"text": "  "}).status_code == 200
    response = signed_in.post(f"/entries/{entry.pk}/edit/", {"text": ""})
    assert response.status_code == 200
    entry.refresh_from_db()
    assert entry.text == "Original"
    assert Entry.objects.count() == 1


def test_entry_text_is_escaped_and_newest_comes_first(signed_in, user):
    Topic, Entry = journal_models()
    topic = Topic.objects.create(owner=user, text="Python")
    old = Entry.objects.create(topic=topic, text="First lesson")
    new = Entry.objects.create(topic=topic, text="<script>alert('x')</script>")
    response = signed_in.get(f"/topics/{topic.pk}/")
    html = response.content.decode()
    assert "<script>alert('x')</script>" not in html
    assert "&lt;script&gt;" in html
    assert list(response.context["entries"]) == [new, old]


def test_csrf_rejects_unprotected_write(user):
    from django.test import Client

    client = Client(enforce_csrf_checks=True)
    client.force_login(user)
    assert client.post("/topics/new/", {"text": "Unsafe"}).status_code == 403
