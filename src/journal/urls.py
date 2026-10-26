from django.urls import path

from .web import entries, topics

app_name = "journal"
urlpatterns = [
    path("topics/", topics.topic_list, name="topic_list"),
    path("topics/new/", topics.topic_create, name="topic_create"),
    path("topics/<int:topic_id>/", topics.topic_detail, name="topic_detail"),
    path("topics/<int:topic_id>/entries/new/", entries.entry_create, name="entry_create"),
    path("entries/<int:entry_id>/edit/", entries.entry_edit, name="entry_edit"),
    path("topics/<int:topic_id>/delete/", topics.topic_delete, name="topic_delete"),
    path("entries/<int:entry_id>/delete/", entries.entry_delete, name="entry_delete"),
]
