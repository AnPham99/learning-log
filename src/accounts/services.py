"""Account creation uses Django's user model and password policy."""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction


@transaction.atomic
def register_user(*, username: str, password: str):
    user = get_user_model()(username=username.strip())
    validate_password(password, user)
    user.set_password(password)
    user.full_clean()
    user.save()
    return user
