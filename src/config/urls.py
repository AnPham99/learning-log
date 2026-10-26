from django.contrib import admin
from django.urls import include, path

from common import views

urlpatterns = [
    path("", views.home, name="home"),
    path("", include("journal.urls")),
    path("accounts/", include("accounts.urls")),
    path("admin/", admin.site.urls),
]
handler404 = "common.views.not_found"
handler500 = "common.views.server_error"
