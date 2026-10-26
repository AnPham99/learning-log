from functools import wraps

from django.http import Http404

from journal.exceptions import JournalNotFound


def resource_errors(view):
    """Translate a domain lookup failure into an HTTP response at the web boundary."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        try:
            return view(*args, **kwargs)
        except JournalNotFound as error:
            raise Http404("Không tìm thấy nội dung này.") from error

    return wrapped
