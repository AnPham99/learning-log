"""Bản đồ URL của StoreDesk: nối màn hình với view của từng nghiệp vụ."""

from django.contrib.auth.views import LogoutView
from django.urls import path

from accounts import views as accounts
from analytics import views as analytics
from catalog import views as catalog
from inventory import views as inventory
from trading import views as trading

urlpatterns = [
    path("", analytics.home, name="home"),
    path("setup/", accounts.setup, name="setup"),
    path("login/", accounts.SignInView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("staff/", accounts.staff, name="staff"),
    path("dashboard/data/", analytics.dashboard_data, name="dashboard_data"),
    path("products/", catalog.products, name="products"),
    path("products/new/", catalog.product_edit, name="product_new"),
    path("products/<int:pk>/edit/", catalog.product_edit, name="product_edit"),
    path("contacts/<str:kind>/", catalog.contacts, name="contacts"),
    path("contacts/<str:kind>/new/", catalog.contact_edit, name="contact_new"),
    path("contacts/<str:kind>/<int:pk>/edit/", catalog.contact_edit, name="contact_edit"),
    path("stock/", inventory.stock_list, name="stock"),
    path("stock/adjust/", inventory.adjustment, name="adjustment"),
    path("stock/ledger/", inventory.ledger, name="ledger"),
    path("documents/<str:kind>/", trading.document_list, name="documents"),
    path("documents/<str:kind>/new/", trading.document_edit, name="document_new"),
    path("documents/<str:kind>/<int:pk>/edit/", trading.document_edit, name="document_edit"),
    path("document/<int:pk>/", trading.document_detail, name="document"),
]
