import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user("learner", password="A-strong-test-pass-42!")


@pytest.fixture
def other_user(db):
    return get_user_model().objects.create_user("another", password="Another-test-pass-42!")


@pytest.fixture
def signed_in(client, user):
    client.force_login(user)
    return client
