import pytest
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db


def test_home_introduces_app(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Learning Log" in response.content.decode()


@pytest.mark.parametrize("path", ["/accounts/login/", "/accounts/register/"])
def test_account_forms_are_available(client, path):
    assert client.get(path).status_code == 200


def test_registration_creates_user_and_signs_in(client):
    response = client.post(
        "/accounts/register/",
        {
            "username": "newlearner",
            "password1": "A-strong-test-pass-42!",
            "password2": "A-strong-test-pass-42!",
        },
    )
    assert response.status_code == 302
    assert response.url == "/topics/"
    new_user = get_user_model().objects.get(username="newlearner")
    assert new_user.check_password("A-strong-test-pass-42!")
    assert str(new_user.pk) == client.session["_auth_user_id"]


@pytest.mark.parametrize("password2", ["different-pass", "123"])
def test_invalid_registration_does_not_create_user(client, password2):
    response = client.post(
        "/accounts/register/",
        {
            "username": "invaliduser",
            "password1": "123",
            "password2": password2,
        },
    )
    assert response.status_code == 200
    assert response.context["form"].errors
    assert not get_user_model().objects.filter(username="invaliduser").exists()


def test_duplicate_username_is_rejected(client, user):
    response = client.post(
        "/accounts/register/",
        {
            "username": user.username,
            "password1": "A-strong-test-pass-42!",
            "password2": "A-strong-test-pass-42!",
        },
    )
    assert response.status_code == 200
    assert "username" in response.context["form"].errors


def test_login_and_logout(client, user):
    response = client.post(
        "/accounts/login/",
        {
            "username": user.username,
            "password": "A-strong-test-pass-42!",
        },
    )
    assert response.status_code == 302
    assert client.session["_auth_user_id"] == str(user.pk)
    response = client.post("/accounts/logout/")
    assert response.status_code == 302
    assert "_auth_user_id" not in client.session


def test_invalid_login_displays_error(client, user):
    response = client.post("/accounts/login/", {"username": user.username, "password": "wrong"})
    assert response.status_code == 200
    assert response.context["form"].non_field_errors()


def test_login_does_not_redirect_outside_app(client, user):
    response = client.post(
        "/accounts/login/?next=https://evil.example/",
        {
            "username": user.username,
            "password": "A-strong-test-pass-42!",
        },
    )
    assert response.url == "/topics/"


def test_signed_in_home_and_registration_redirect(signed_in):
    assert signed_in.get("/").url == "/topics/"
    assert signed_in.get("/accounts/register/").url == "/topics/"


def test_logout_requires_post(signed_in):
    assert signed_in.get("/accounts/logout/").status_code == 405


def test_unknown_route_returns_friendly_404(client):
    response = client.get("/missing-page/")
    assert response.status_code == 404
    assert "Không tìm thấy" in response.content.decode()
